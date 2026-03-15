import urllib.request
import urllib.parse
import json
import ssl
import time
import sys
import threading
import subprocess
import webbrowser  # <-- NUEVO: Para controlar tu navegador
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# 🏠 CONFIGURACIÓN DE TU CIUDAD
# ==========================================
CIUDAD_CASA = "chincolco" 

# --- PALETA DE COLORES Y EFECTOS ANSI ---
RESET = "\033[0m"
NEGRITA = "\033[1m"
PARPADEO = "\033[5m"
BLANCO = "\033[97m"
ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CIAN = "\033[96m"
FONDO_ROJO = "\033[41m"
FONDO_VERDE = "\033[42m"
FONDO_AZUL = "\033[44m"

animando = False

# ==========================================
# 🚀 FUNCIONES DE SISTEMA Y GRÁFICOS
# ==========================================

def hablar_mac(texto):
    try: subprocess.Popen(["say", texto])
    except: pass

def notificar_mac(titulo, mensaje):
    try:
        comando = f'display notification "{mensaje}" with title "{titulo}"'
        subprocess.run(["osascript", "-e", comando], check=False)
    except: pass

def animacion_carga(mensaje):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    while animando:
        sys.stdout.write(f'\r{CIAN}{mensaje}{RESET} {AMARILLO}{spinner[i % len(spinner)]}{RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write('\r' + ' ' * (len(mensaje) + 5) + '\r')

def colorear_temp(temp):
    try:
        t = float(temp)
        if t >= 25: return f"{FONDO_ROJO}{BLANCO}{NEGRITA} {t}°C {RESET}"
        elif t <= 12: return f"{FONDO_AZUL}{BLANCO}{NEGRITA} {t}°C {RESET}"
        else: return f"{FONDO_VERDE}{BLANCO}{NEGRITA} {t}°C {RESET}"
    except: return f"{temp}°C"

def obtener_estado_clima(codigo):
    if codigo == 0: return "☀️ Despejado"
    elif codigo in [1, 2, 3]: return "⛅ Nublado / Parcial"
    elif codigo in [45, 48]: return "🌫️ Neblina"
    elif codigo in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️ Lluvia"
    elif codigo in [71, 73, 75, 85, 86]: return "❄️ Nieve"
    elif codigo in [95, 96, 99]: return "⛈️ Tormenta"
    else: return "☁️ Variable"

def obtener_ascii_clima(codigo):
    if codigo == 0:
        return f"{AMARILLO}      \\  /    \n    _ /\"\".\\ _ \n      \\__/    \n      /  \\    {RESET}"
    elif codigo in [1, 2, 3]:
        return f"{BLANCO}       .--.   \n    .-(    ). \n   (___.__)__){RESET}"
    elif codigo in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return f"{CIAN}       .--.   \n    .-(    ). \n   (___.__)__)\n    / / / / / {RESET}"
    elif codigo in [71, 73, 75, 85, 86]:
        return f"{BLANCO}       .--.   \n    .-(    ). \n   (___.__)__)\n    * * * *{RESET}"
    elif codigo in [95, 96, 99]:
        return f"{AMARILLO}       .--.   \n    .-(    ). \n   (___.__)__)\n      ⚡  ⚡   {RESET}"
    else: return f"{BLANCO}       .--.   \n    .-(    ). \n   (___.__)__){RESET}"

def verificar_alertas(temp, viento, uv):
    alertas = []
    if temp >= 32: alertas.append("🔥 CALOR EXTREMO (≥32°C). ¡Evita el sol e hidrátate!")
    elif temp <= 0: alertas.append("❄️ FRÍO EXTREMO (≤0°C). ¡Abrígate muy bien!")
    if viento >= 40: alertas.append("🌪️ VIENTO FUERTE (≥40km/h). ¡Precaución afuera!")
    if uv >= 8: alertas.append("☢️ RADIACIÓN UV PELIGROSA (≥8). ¡Usa bloqueador solar sí o sí!")
    
    if alertas:
        print(f"\n{PARPADEO}{FONDO_ROJO}{BLANCO}{NEGRITA} ⚠️ ALERTAS METEOROLÓGICAS ACTIVAS ⚠️ {RESET}")
        for alerta in alertas:
            print(f"{ROJO}{NEGRITA}  ▶ {alerta}{RESET}")

def calcular_barra_sol(amanecer_iso, atardecer_iso, zona_horaria_str):
    try:
        zh = ZoneInfo(zona_horaria_str)
        ahora = datetime.now(zh)
        amanecer = datetime.fromisoformat(amanecer_iso).replace(tzinfo=zh)
        atardecer = datetime.fromisoformat(atardecer_iso).replace(tzinfo=zh)
        
        hora_am = amanecer.strftime('%H:%M')
        hora_pm = atardecer.strftime('%H:%M')

        if ahora < amanecer: return f"🌌 {hora_am} [--------------------] {hora_pm} (Esperando el alba)"
        elif ahora > atardecer: return f"🌃 {hora_am} [████████████████████] {hora_pm} (De noche)"

        porcentaje = (ahora - amanecer).total_seconds() / (atardecer - amanecer).total_seconds()
        llenos = int(20 * porcentaje)
        vacios = max(0, 20 - llenos - 1)
        return f"🌅 {hora_am} [{AMARILLO}{'█' * llenos}☀️{'-' * vacios}{RESET}] {hora_pm} 🌇"
    except: return f"🌅 {amanecer_iso.split('T')[1]} / 🌇 {atardecer_iso.split('T')[1]}"

# ==========================================
# ⚔️ MODO BATALLA (MOTOR DOBLE)
# ==========================================

def descargar_datos_silencioso(busqueda, diccionario_resultados, clave):
    contexto_ssl = ssl._create_unverified_context()
    try:
        ciudad_cod = urllib.parse.quote(busqueda)
        url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad_cod}&count=1&language=es&format=json"
        res_geo = json.loads(urllib.request.urlopen(url_geo, context=contexto_ssl).read().decode('utf-8'))
        
        if not res_geo.get("results"):
            diccionario_resultados[clave] = {"error": f"No se encontró {busqueda}"}
            return
            
        ubi = res_geo["results"][0]
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={ubi['latitude']}&longitude={ubi['longitude']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto"
        res_clima = json.loads(urllib.request.urlopen(url_clima, context=contexto_ssl).read().decode('utf-8'))
        
        clima = res_clima['current']
        diccionario_resultados[clave] = {
            "nombre": ubi["name"], "pais": ubi.get("country", ""), "temp": clima['temperature_2m'],
            "humedad": clima['relative_humidity_2m'], "viento": clima['wind_speed_10m'],
            "estado": obtener_estado_clima(clima['weather_code'])
        }
    except Exception as e: diccionario_resultados[clave] = {"error": str(e)}

def batalla_ciudades(ciudad1, ciudad2):
    global animando
    print(f"\n{PARPADEO}{ROJO}{NEGRITA}⚔️  INICIANDO BATALLA METEOROLÓGICA ⚔️{RESET}")
    hablar_mac(f"Batalla iniciada. {ciudad1} versus {ciudad2}")
    
    animando = True
    hilo_anim = threading.Thread(target=animacion_carga, args=("Conectando satélites simultáneos...",))
    hilo_anim.start()
    
    resultados = {}
    hilo1 = threading.Thread(target=descargar_datos_silencioso, args=(ciudad1, resultados, 'c1'))
    hilo2 = threading.Thread(target=descargar_datos_silencioso, args=(ciudad2, resultados, 'c2'))
    hilo1.start()
    hilo2.start()
    hilo1.join()
    hilo2.join()
    
    animando = False
    hilo_anim.join()
    
    d1, d2 = resultados.get('c1', {}), resultados.get('c2', {})
    if "error" in d1 or "error" in d2:
        print(f"{ROJO}❌ Error: Uno de los lugares no existe.{RESET}")
        return

    nom1, nom2 = f"{d1['nombre']} ({d1['pais']})"[:25], f"{d2['nombre']} ({d2['pais']})"[:25]
    print(f"\n{CIAN}" + "="*60 + f"{RESET}")
    print(f"{AMARILLO}{NEGRITA}{nom1:<28} 🆚 {nom2:>28}{RESET}")
    print(f"{CIAN}" + "-"*60 + f"{RESET}")
    
    t1, t2 = d1['temp'], d2['temp']
    print(f"🌡️ {colorear_temp(t1)} {'🔥' if t1>t2 else '':<13} | 🌡️ {colorear_temp(t2)} {'🔥' if t2>t1 else ''}")
    h1, h2 = d1['humedad'], d2['humedad']
    print(f"💧 Humedad: {h1}% {'💧' if h1>h2 else '':<11} | 💧 Humedad: {h2}% {'💧' if h2>h1 else ''}")
    v1, v2 = d1['viento'], d2['viento']
    print(f"💨 Viento: {v1} km/h {'🌪️' if v1>v2 else '':<7} | 💨 Viento: {v2} km/h {'🌪️' if v2>v1 else ''}")
    print(f"🌤️ {d1['estado']:<25} | 🌤️ {d2['estado']}")
    print(f"{CIAN}" + "="*60 + f"{RESET}\n")
    notificar_mac("Batalla Finalizada ⚔️", f"{d1['nombre']} ({t1}°C) vs {d2['nombre']} ({t2}°C)")

# ==========================================
# ⚙️ MODO NORMAL (CON WEB Y TODO EL ARTE)
# ==========================================

def procesar_ciudad(entrada, modo_hacker=False):
    global animando
    contexto_ssl = ssl._create_unverified_context()
    pais_filtro = None
    if "," in entrada:
        partes = entrada.split(",")
        ciudad_busqueda, pais_filtro = partes[0].strip(), partes[1].strip().lower()
    else: ciudad_busqueda = entrada
        
    animando = True
    hilo_animacion = threading.Thread(target=animacion_carga, args=(f"Buscando '{ciudad_busqueda}'...",))
    hilo_animacion.start()
    
    try:
        ciudad_cod = urllib.parse.quote(ciudad_busqueda)
        url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad_cod}&count=20&language=es&format=json"
        res_geo = json.loads(urllib.request.urlopen(url_geo, context=contexto_ssl).read().decode('utf-8'))
        animando = False
        hilo_animacion.join()
        
        resultados_crudos = res_geo.get("results", [])
        if not resultados_crudos:
            print(f"{ROJO}❌ No encontré '{ciudad_busqueda}'.{RESET}"); return
            
        resultados = [r for r in resultados_crudos if pais_filtro in r.get("country", "").lower()] if pais_filtro else resultados_crudos
        if not resultados:
            print(f"{ROJO}❌ No encontré '{ciudad_busqueda}' en '{pais_filtro}'.{RESET}"); return
            
        ubicacion = resultados[0] if (len(resultados) == 1 or modo_hacker) else None
        if not ubicacion:
            print(f"\n{AMARILLO}🔎 Encontré {len(resultados)} opciones. Elige la correcta:{RESET}")
            for i, res in enumerate(resultados):
                print(f"   {CIAN}[{i+1}]{RESET} {NEGRITA}{res.get('name','')}{RESET}, {res.get('admin1','-')} ({res.get('country','?')})")
            while True:
                seleccion = input(f"\n{VERDE}👉 Escribe el número (o Enter para cancelar): {RESET}").strip()
                if not seleccion: return
                if seleccion.isdigit() and 1 <= int(seleccion) <= len(resultados):
                    ubicacion = resultados[int(seleccion)-1]; break
                print(f"{ROJO}❌ Inválido.{RESET}")
                
        lat, lon = ubicacion["latitude"], ubicacion["longitude"]
        nom, pais, reg = ubicacion["name"], ubicacion.get("country", "?"), ubicacion.get("admin1", "")
        zh_str = ubicacion.get("timezone", "America/Santiago")
    except Exception as e:
        animando = False; hilo_animacion.join(); print(f"{ROJO}❌ Error al buscar: {e}{RESET}"); return

    try: hora_formateada = datetime.now(ZoneInfo(zh_str)).strftime("%d/%m/%Y %H:%M:%S")
    except: hora_formateada = "--"

    animando = True
    hilo_clima = threading.Thread(target=animacion_carga, args=(f"Descargando clima...",))
    hilo_clima.start()

    url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset&timezone=auto&forecast_days=3"
    
    try:
        res_clima = json.loads(urllib.request.urlopen(url_clima, context=contexto_ssl).read().decode('utf-8'))
        animando = False
        hilo_clima.join()
        
        c = res_clima['current']
        p = res_clima['daily']
        est_txt = obtener_estado_clima(c['weather_code'])
        temp, viento, uv = c['temperature_2m'], c['wind_speed_10m'], p['uv_index_max'][0]
        
        notificar_mac("Clima Listo", f"{nom}: {temp}°C y {est_txt.split(' ')[1]}")
        hablar_mac(f"El clima en {nom} es de {temp} grados.")
        
        print("\n" + f"{CIAN}" + "="*50 + f"{RESET}")
        print(f"📍 {NEGRITA}REPORTE DE: {nom}, {reg} ({pais}){RESET}")
        print(f"🕒 Hora local: {AMARILLO}{hora_formateada}{RESET}")
        print(f"{CIAN}" + "="*50 + f"{RESET}\n")
        
        print(obtener_ascii_clima(c['weather_code']))
        verificar_alertas(temp, viento, uv)
        print("")
        
        print(f"{VERDE}{NEGRITA}🟢 CLIMA ACTUAL:{RESET}")
        print(f"   🌡️ Temperatura: {colorear_temp(temp)}")
        print(f"   💧 Humedad:     {CIAN}{c['relative_humidity_2m']}%{RESET}")
        print(f"   🌤️ Estado:      {est_txt}")
        print(f"   💨 Viento:      {CIAN}{viento} km/h{RESET}")
        print(f"   ☀️ Índice UV:   {AMARILLO}{uv} (Máx hoy){RESET}")
        
        print(f"\n   {calcular_barra_sol(p['sunrise'][0], p['sunset'][0], zh_str)}\n")
        
        print(f"{CIAN}" + "-" * 50 + f"{RESET}")
        print(f"{VERDE}{NEGRITA}📅 PRONÓSTICO 2 DÍAS:{RESET}")
        print(f"   ▶ Mañana: Mín {colorear_temp(p['temperature_2m_min'][1])} | Máx {colorear_temp(p['temperature_2m_max'][1])} | {obtener_estado_clima(p['weather_code'][1])}")
        print(f"   ▶ Pasado: Mín {colorear_temp(p['temperature_2m_min'][2])} | Máx {colorear_temp(p['temperature_2m_max'][2])} | {obtener_estado_clima(p['weather_code'][2])}")
        print(f"{CIAN}" + "="*50 + f"{RESET}")
        
        # --- 🌐 MAGIA DE NAVEGADOR WEB ---
        print(f"\n{AMARILLO}🌐 Abriendo radar interactivo en tu navegador...{RESET}")
        # Abre Windy.com centrado exactamente en la ciudad buscada, con zoom nivel 10
        webbrowser.open(f"https://www.windy.com/?{lat},{lon},10")
        
    except Exception as e:
        animando = False; hilo_clima.join(); print(f"{ROJO}❌ Error al descargar el clima: {e}{RESET}")

def main():
    if len(sys.argv) > 1:
        busqueda = " ".join(sys.argv[1:])
        if " vs " in busqueda.lower():
            partes = busqueda.lower().split(" vs ")
            batalla_ciudades(partes[0].strip(), partes[1].strip())
        else:
            procesar_ciudad(busqueda, modo_hacker=True)
        return
        
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    print(f"{CIAN}{NEGRITA}⛅ ASISTENTE DE CLIMA V5.0 - RADAR WEB{RESET}")
    print(f"{AMARILLO}💡 Truco: Escribe 'Madrid vs Londres' para compararlos.{RESET}")
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    
    procesar_ciudad(CIUDAD_CASA)
    
    while True:
        print(f"{CIAN}" + "-"*60 + f"{RESET}")
        entrada = input(f"{VERDE}🌎 Escribe una ciudad o un VS (ej: Tokio vs Miami): {RESET}").strip()
        
        if not entrada or entrada.lower() in ['salir', 'quit', 'exit']:
            print(f"{AMARILLO}¡Nos vemos! 👋{RESET}")
            break
            
        if " vs " in entrada.lower():
            partes = entrada.lower().split(" vs ")
            batalla_ciudades(partes[0].strip(), partes[1].strip())
        else:
            procesar_ciudad(entrada)

if __name__ == "__main__":
    main()