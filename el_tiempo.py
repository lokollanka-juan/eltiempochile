import urllib.request
import urllib.parse
import json
import ssl
import time
import sys
import threading
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# 🏠 CONFIGURACIÓN DE TU CIUDAD
# ==========================================
CIUDAD_CASA = "chincolco" 

# --- PALETA DE COLORES, FONDOS Y EFECTOS ANSI ---
RESET = "\033[0m"
NEGRITA = "\033[1m"
PARPADEO = "\033[5m"  # Efecto de alerta
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
# 🚀 FUNCIONES DE NIVEL DIOS
# ==========================================

def hablar_mac(texto):
    """Hace que la Mac lea el texto en voz alta en segundo plano (sin congelar el programa)"""
    try:
        # Popen lo ejecuta de fondo. 'say' es el comando nativo de voz de Apple.
        subprocess.Popen(["say", texto])
    except:
        pass

def calcular_barra_sol(amanecer_iso, atardecer_iso, zona_horaria_str):
    """Dibuja una barra de progreso calculando dónde está el sol en este momento exacto"""
    try:
        zh = ZoneInfo(zona_horaria_str)
        ahora = datetime.now(zh)
        
        # Convertimos los textos de la API (ej: 2026-03-15T07:15) a objetos de tiempo reales
        amanecer = datetime.fromisoformat(amanecer_iso).replace(tzinfo=zh)
        atardecer = datetime.fromisoformat(atardecer_iso).replace(tzinfo=zh)
        
        hora_am = amanecer.strftime('%H:%M')
        hora_pm = atardecer.strftime('%H:%M')

        if ahora < amanecer:
            return f"🌌 {hora_am} [--------------------] {hora_pm} (Esperando el alba)"
        elif ahora > atardecer:
            return f"🌃 {hora_am} [████████████████████] {hora_pm} (De noche)"

        # Matemáticas: Qué porcentaje del día de luz ha pasado
        total_seg_luz = (atardecer - amanecer).total_seconds()
        seg_pasados = (ahora - amanecer).total_seconds()
        porcentaje = seg_pasados / total_seg_luz

        longitud_barra = 20
        llenos = int(longitud_barra * porcentaje)
        vacios = max(0, longitud_barra - llenos - 1)

        # Dibujar la barra
        barra = "█" * llenos + "☀️" + "-" * vacios
        return f"🌅 {hora_am} [{AMARILLO}{barra}{RESET}] {hora_pm} 🌇"
    except Exception as e:
        return f"🌅 {amanecer_iso.split('T')[1]} / 🌇 {atardecer_iso.split('T')[1]}"

def verificar_alertas(temp, viento, uv):
    """Dispara advertencias si el clima es peligroso"""
    alertas = []
    if temp >= 32: alertas.append("🔥 CALOR EXTREMO (≥32°C). ¡Evita el sol e hidrátate!")
    elif temp <= 0: alertas.append("❄️ FRÍO EXTREMO (≤0°C). ¡Abrígate muy bien!")
    if viento >= 40: alertas.append("🌪️ VIENTO FUERTE (≥40km/h). ¡Precaución afuera!")
    if uv >= 8: alertas.append("☢️ RADIACIÓN UV PELIGROSA (≥8). ¡Usa bloqueador solar sí o sí!")
    
    if alertas:
        print(f"\n{PARPADEO}{FONDO_ROJO}{BLANCO}{NEGRITA} ⚠️ ALERTAS METEOROLÓGICAS ACTIVAS ⚠️ {RESET}")
        for alerta in alertas:
            print(f"{ROJO}{NEGRITA}  ▶ {alerta}{RESET}")

# ==========================================
# 🛠️ FUNCIONES CLÁSICAS
# ==========================================

def animacion_carga(mensaje):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    while animando:
        sys.stdout.write(f'\r{CIAN}{mensaje}{RESET} {AMARILLO}{spinner[i % len(spinner)]}{RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write('\r' + ' ' * (len(mensaje) + 5) + '\r')

def notificar_mac(ciudad, temp, estado):
    try:
        mensaje = f"{temp}°C y {estado}"
        comando = f'display notification "{mensaje}" with title "⛅ Clima en {ciudad}"'
        subprocess.run(["osascript", "-e", comando], check=False)
    except: pass

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

# ==========================================
# ⚙️ MOTOR PRINCIPAL
# ==========================================

def procesar_ciudad(entrada, modo_hacker=False):
    global animando
    contexto_ssl = ssl._create_unverified_context()
    
    pais_filtro = None
    if "," in entrada:
        partes = entrada.split(",")
        ciudad_busqueda = partes[0].strip()
        pais_filtro = partes[1].strip().lower()
    else:
        ciudad_busqueda = entrada
        
    animando = True
    hilo_animacion = threading.Thread(target=animacion_carga, args=(f"Buscando '{ciudad_busqueda}'...",))
    hilo_animacion.start()
    
    ciudad_codificada = urllib.parse.quote(ciudad_busqueda)
    url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad_codificada}&count=20&language=es&format=json"
    
    try:
        respuesta_geo = urllib.request.urlopen(url_geo, context=contexto_ssl)
        datos_geo = json.loads(respuesta_geo.read().decode('utf-8'))
        animando = False
        hilo_animacion.join()
        
        resultados_crudos = datos_geo.get("results", [])
        if not resultados_crudos:
            print(f"{ROJO}❌ No encontré '{ciudad_busqueda}'.{RESET}")
            return
            
        if pais_filtro:
            resultados = [res for res in resultados_crudos if pais_filtro in res.get("country", "").lower()]
        else:
            resultados = resultados_crudos
            
        if not resultados:
            print(f"{ROJO}❌ Encontré '{ciudad_busqueda}', pero no en '{pais_filtro}'.{RESET}")
            return
            
        ubicacion = resultados[0] if (len(resultados) == 1 or modo_hacker) else None
        
        if not ubicacion:
            print(f"\n{AMARILLO}🔎 Encontré {len(resultados)} opciones. Elige la correcta:{RESET}")
            for i, res in enumerate(resultados):
                nombre = res.get("name", "")
                pais = res.get("country", "?")
                region = res.get("admin1", "-")
                print(f"   {CIAN}[{i+1}]{RESET} {NEGRITA}{nombre}{RESET}, {region} ({pais})")
            
            while True:
                seleccion = input(f"\n{VERDE}👉 Escribe el número (o Enter para cancelar): {RESET}").strip()
                if not seleccion: return
                if seleccion.isdigit() and 1 <= int(seleccion) <= len(resultados):
                    ubicacion = resultados[int(seleccion)-1]
                    break
                print(f"{ROJO}❌ Inválido.{RESET}")
                
        lat, lon = ubicacion["latitude"], ubicacion["longitude"]
        nombre_oficial = ubicacion["name"]
        pais_oficial = ubicacion.get("country", "?")
        region_oficial = ubicacion.get("admin1", "")
        zona_horaria_str = ubicacion.get("timezone", "America/Santiago")
        
    except Exception as e:
        animando = False
        hilo_animacion.join()
        print(f"{ROJO}❌ Error al buscar: {e}{RESET}")
        return

    try:
        zona_horaria = ZoneInfo(zona_horaria_str)
        hora_formateada = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M:%S")
    except: hora_formateada = "--"

    animando = True
    hilo_clima = threading.Thread(target=animacion_carga, args=(f"Descargando clima...",))
    hilo_clima.start()

    url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset&timezone=auto&forecast_days=3"
    
    try:
        respuesta_clima = urllib.request.urlopen(url_clima, context=contexto_ssl)
        datos_clima = json.loads(respuesta_clima.read().decode('utf-8'))
        animando = False
        hilo_clima.join()
        
        clima_actual = datos_clima['current']
        pronostico = datos_clima['daily']
        estado_texto = obtener_estado_clima(clima_actual['weather_code'])
        temp_actual = clima_actual['temperature_2m']
        viento_actual = clima_actual['wind_speed_10m']
        uv_hoy = pronostico['uv_index_max'][0]
        
        # --- LANZAR LA MAGIA NATIVA DE MAC ---
        notificar_mac(nombre_oficial, temp_actual, estado_texto)
        # 🗣️ LA MAC HABLA AQUÍ (Sube el volumen)
        mensaje_voz = f"El clima en {nombre_oficial} es de {temp_actual} grados, y está {estado_texto.split(' ')[1]}."
        hablar_mac(mensaje_voz)
        
        print("\n" + f"{CIAN}" + "="*50 + f"{RESET}")
        lugar = f"{nombre_oficial}, {region_oficial}" if region_oficial else f"{nombre_oficial}"
        print(f"📍 {NEGRITA}REPORTE DE: {lugar} ({pais_oficial}){RESET}")
        print(f"🕒 Hora local: {AMARILLO}{hora_formateada}{RESET}")
        print(f"{CIAN}" + "="*50 + f"{RESET}\n")
        
        # Arte y alertas
        print(obtener_ascii_clima(clima_actual['weather_code']))
        verificar_alertas(temp_actual, viento_actual, uv_hoy)
        print("")
        
        print(f"{VERDE}{NEGRITA}🟢 CLIMA ACTUAL:{RESET}")
        print(f"   🌡️ Temperatura: {colorear_temp(temp_actual)}")
        print(f"   💧 Humedad:     {CIAN}{clima_actual['relative_humidity_2m']}%{RESET}")
        print(f"   🌤️ Estado:      {estado_texto}")
        print(f"   💨 Viento:      {CIAN}{viento_actual} km/h{RESET}")
        print(f"   ☀️ Índice UV:   {AMARILLO}{uv_hoy} (Máx hoy){RESET}")
        
        # ⏳ LA MEGA BARRA DEL SOL
        barra_sol = calcular_barra_sol(pronostico['sunrise'][0], pronostico['sunset'][0], zona_horaria_str)
        print(f"\n   {barra_sol}\n")
        
        print(f"{CIAN}" + "-" * 50 + f"{RESET}")
        print(f"{VERDE}{NEGRITA}📅 PRONÓSTICO 2 DÍAS:{RESET}")
        print(f"   ▶ Mañana: Mín {colorear_temp(pronostico['temperature_2m_min'][1])} | Máx {colorear_temp(pronostico['temperature_2m_max'][1])} | {obtener_estado_clima(pronostico['weather_code'][1])}")
        print(f"   ▶ Pasado: Mín {colorear_temp(pronostico['temperature_2m_min'][2])} | Máx {colorear_temp(pronostico['temperature_2m_max'][2])} | {obtener_estado_clima(pronostico['weather_code'][2])}")
        print(f"{CIAN}" + "="*50 + f"{RESET}")
        
    except Exception as e:
        animando = False
        hilo_clima.join()
        print(f"{ROJO}❌ Error al descargar el clima: {e}{RESET}")

def main():
    if len(sys.argv) > 1:
        busqueda = " ".join(sys.argv[1:])
        procesar_ciudad(busqueda, modo_hacker=True)
        return
        
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    print(f"{CIAN}{NEGRITA}⛅ ASISTENTE DE CLIMA IA - NIVEL DIOS{RESET}")
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    
    print(f"\n{AMARILLO}🏠 Hablando con satélites para {CIUDAD_CASA}...{RESET}")
    procesar_ciudad(CIUDAD_CASA, modo_hacker=False)
    
    while True:
        print("\n" + f"{CIAN}" + "-"*60 + f"{RESET}")
        entrada = input(f"{VERDE}🌎 Escribe otra ciudad (o presiona Enter para salir): {RESET}").strip()
        
        if not entrada or entrada.lower() in ['salir', 'quit', 'exit', 'cerrar']:
            print(f"{AMARILLO}¡Nos vemos! 👋{RESET}")
            break
            
        procesar_ciudad(entrada, modo_hacker=False)

if __name__ == "__main__":
    main()