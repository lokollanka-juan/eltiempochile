import urllib.request
import urllib.parse
import json
import ssl
import time
import sys
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

# --- PALETA DE COLORES Y FONDOS ANSI ---
RESET = "\033[0m"
NEGRITA = "\033[1m"
BLANCO = "\033[97m"

# Colores de Texto
ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CIAN = "\033[96m"

# Colores de Fondo (Nuevos)
FONDO_ROJO = "\033[41m"
FONDO_VERDE = "\033[42m"
FONDO_AZUL = "\033[44m"

animando = False

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
    """Devuelve la temperatura como una ETIQUETA con color de fondo"""
    try:
        t = float(temp)
        # Usamos texto Blanco + Fondo de Color + Negrita + Espacios para que parezca un botón
        if t >= 25: return f"{FONDO_ROJO}{BLANCO}{NEGRITA} {t}°C {RESET}"
        elif t <= 12: return f"{FONDO_AZUL}{BLANCO}{NEGRITA} {t}°C {RESET}"
        else: return f"{FONDO_VERDE}{BLANCO}{NEGRITA} {t}°C {RESET}"
    except:
        return f"{temp}°C"

def obtener_estado_clima(codigo):
    if codigo == 0: return "☀️ Despejado"
    elif codigo in [1, 2, 3]: return "⛅ Nublado / Parcial"
    elif codigo in [45, 48]: return "🌫️ Neblina"
    elif codigo in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️ Lluvia"
    elif codigo in [71, 73, 75, 85, 86]: return "❄️ Nieve"
    elif codigo in [95, 96, 99]: return "⛈️ Tormenta"
    else: return "☁️ Variable"

def extraer_hora(fecha_iso):
    try:
        return fecha_iso.split("T")[1]
    except:
        return "--:--"

def consultar_clima_infinito():
    global animando
    contexto_ssl = ssl._create_unverified_context()
    
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    print(f"{CIAN}{NEGRITA}⛅ BIENVENIDO AL BUSCADOR DE CLIMA PRO (FONDOS & ANIMACIÓN){RESET}")
    print(f"{AMARILLO}💡 Truco: Escribe 'San Felipe, Chile' para filtrar directo.{RESET}")
    print(f"{ROJO}🛑 Escribe 'salir' para cerrar el programa.{RESET}")
    print(f"{CIAN}{NEGRITA}" + "="*60 + f"{RESET}")
    
    while True:
        print("\n" + f"{CIAN}" + "-"*60 + f"{RESET}")
        entrada = input(f"{VERDE}🌎 Escribe la comuna o ciudad: {RESET}").strip()
        
        if entrada.lower() in ['salir', 'quit', 'exit', 'cerrar']:
            print(f"{AMARILLO}¡Nos vemos! 👋 Programa terminado.{RESET}")
            break
            
        if not entrada:
            continue
            
        pais_filtro = None
        if "," in entrada:
            partes = entrada.split(",")
            ciudad_busqueda = partes[0].strip()
            pais_filtro = partes[1].strip().lower()
        else:
            ciudad_busqueda = entrada
            
        animando = True
        hilo_animacion = threading.Thread(target=animacion_carga, args=(f"Buscando '{ciudad_busqueda}' en la base de datos...",))
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
                print(f"{ROJO}❌ No encontré ninguna ciudad llamada '{ciudad_busqueda}'.{RESET}")
                continue
                
            if pais_filtro:
                resultados = []
                for res in resultados_crudos:
                    pais = res.get("country", "").lower()
                    if pais_filtro in pais:
                        resultados.append(res)
            else:
                resultados = resultados_crudos
                
            if not resultados:
                print(f"{ROJO}❌ Encontré '{ciudad_busqueda}', pero ninguna coincide con '{pais_filtro}'.{RESET}")
                continue
                
            ubicacion = None
            if len(resultados) == 1:
                ubicacion = resultados[0]
            else:
                print(f"\n{AMARILLO}🔎 Encontré {len(resultados)} opciones. Elige la correcta:{RESET}")
                for i, res in enumerate(resultados):
                    nombre = res.get("name", "")
                    pais = res.get("country", "País desconocido")
                    region = res.get("admin1", "Sin región")
                    print(f"   {CIAN}[{i+1}]{RESET} {NEGRITA}{nombre}{RESET}, {region} ({pais})")
                
                while True:
                    seleccion = input(f"\n{VERDE}👉 Escribe el número de tu opción (o Enter para cancelar): {RESET}").strip()
                    if not seleccion:
                        break
                    if seleccion.isdigit() and 1 <= int(seleccion) <= len(resultados):
                        ubicacion = resultados[int(seleccion)-1]
                        break
                    print(f"{ROJO}❌ Número inválido. Intenta de nuevo.{RESET}")
                    
            if not ubicacion:
                print(f"{ROJO}❌ Búsqueda cancelada.{RESET}")
                continue
                
            lat = ubicacion["latitude"]
            lon = ubicacion["longitude"]
            nombre_oficial = ubicacion["name"]
            pais_oficial = ubicacion.get("country", "País desconocido")
            region_oficial = ubicacion.get("admin1", "")
            zona_horaria_str = ubicacion.get("timezone", "America/Santiago")
            
        except Exception as e:
            animando = False
            hilo_animacion.join()
            print(f"{ROJO}❌ Error al buscar: {e}{RESET}")
            continue

        try:
            zona_horaria = ZoneInfo(zona_horaria_str)
            hora_formateada = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            hora_formateada = "No disponible"

        animando = True
        hilo_clima = threading.Thread(target=animacion_carga, args=(f"Descargando clima de {nombre_oficial}...",))
        hilo_clima.start()

        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset&timezone=auto&forecast_days=3"
        
        try:
            respuesta_clima = urllib.request.urlopen(url_clima, context=contexto_ssl)
            datos_clima = json.loads(respuesta_clima.read().decode('utf-8'))
            
            animando = False
            hilo_clima.join()
            
            clima_actual = datos_clima['current']
            pronostico = datos_clima['daily']
            
            print("\n" + f"{CIAN}" + "="*50 + f"{RESET}")
            lugar = f"{nombre_oficial}, {region_oficial}" if region_oficial else f"{nombre_oficial}"
            print(f"📍 {NEGRITA}REPORTE DE: {lugar} ({pais_oficial}){RESET}")
            print(f"🕒 Hora local: {AMARILLO}{hora_formateada}{RESET}")
            print(f"{CIAN}" + "="*50 + f"{RESET}")
            
            print(f"{VERDE}{NEGRITA}🟢 CLIMA ACTUAL:{RESET}")
            print(f"   🌡️ Temperatura: {colorear_temp(clima_actual['temperature_2m'])}")
            print(f"   💧 Humedad:     {CIAN}{clima_actual['relative_humidity_2m']}%{RESET}")
            print(f"   🌤️ Estado:      {obtener_estado_clima(clima_actual['weather_code'])}")
            print(f"   💨 Viento:      {CIAN}{clima_actual['wind_speed_10m']} km/h{RESET}")
            print(f"   ☀️ Índice UV:   {AMARILLO}{pronostico['uv_index_max'][0]} (Máx hoy){RESET}")
            print(f"   🌅 Sol:         Sube {AMARILLO}{extraer_hora(pronostico['sunrise'][0])}{RESET} | Baja {AMARILLO}{extraer_hora(pronostico['sunset'][0])}{RESET}")
            
            print(f"{CIAN}" + "-" * 50 + f"{RESET}")
            
            print(f"{VERDE}{NEGRITA}📅 PRONÓSTICO PRÓXIMOS 2 DÍAS:{RESET}")
            print(f"   ▶ Mañana ({pronostico['time'][1]}):")
            print(f"      Mín: {colorear_temp(pronostico['temperature_2m_min'][1])} | Máx: {colorear_temp(pronostico['temperature_2m_max'][1])} | {obtener_estado_clima(pronostico['weather_code'][1])}")
            print(f"   ▶ Pasado ({pronostico['time'][2]}):")
            print(f"      Mín: {colorear_temp(pronostico['temperature_2m_min'][2])} | Máx: {colorear_temp(pronostico['temperature_2m_max'][2])} | {obtener_estado_clima(pronostico['weather_code'][2])}")
            
            print(f"{CIAN}" + "="*50 + f"{RESET}")
            
        except Exception as e:
            animando = False
            hilo_clima.join()
            print(f"{ROJO}❌ Error al descargar el clima: {e}{RESET}")

if __name__ == "__main__":
    consultar_clima_infinito()