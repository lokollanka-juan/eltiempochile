import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime
from zoneinfo import ZoneInfo

# Función auxiliar para traducir los códigos numéricos de la API a texto
def obtener_estado_clima(codigo):
    if codigo == 0: return "☀️ Despejado"
    elif codigo in [1, 2, 3]: return "⛅ Nublado / Parcial"
    elif codigo in [45, 48]: return "🌫️ Neblina"
    elif codigo in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️ Lluvia"
    elif codigo in [71, 73, 75, 85, 86]: return "❄️ Nieve"
    elif codigo in [95, 96, 99]: return "⛈️ Tormenta"
    else: return "☁️ Variable"

def consultar_clima_infinito():
    # Contexto para evitar el error de certificados SSL en Mac
    contexto_ssl = ssl._create_unverified_context()
    
    print("="*50)
    print("⛅ BIENVENIDO AL BUSCADOR DE CLIMA")
    print("💡 Nota: Las temperaturas tienen un margen de error de ±2°C app.")
    print("🛑 Escribe 'salir' en cualquier momento para cerrar el programa.")
    print("="*50)
    
    # Bucle infinito para que siga preguntando
    while True:
        print("\n" + "-"*50)
        comuna = input("🌎 Escribe la comuna o ciudad: ")
        
        # Condición para cerrar el programa
        if comuna.lower() in ['salir', 'quit', 'exit', 'cerrar']:
            print("¡Nos vemos! 👋 Programa terminado.")
            break
            
        # Evitar que el usuario presione Enter sin escribir nada
        if not comuna.strip():
            continue
            
        print(f"Buscando datos para '{comuna}'... ⏳")
        
        # 1. Convertir el nombre a coordenadas (Geocoding)
        comuna_codificada = urllib.parse.quote(comuna)
        url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={comuna_codificada}&count=1&language=es&format=json"
        
        try:
            respuesta_geo = urllib.request.urlopen(url_geo, context=contexto_ssl)
            datos_geo = json.loads(respuesta_geo.read().decode('utf-8'))
            
            if "results" not in datos_geo:
                print(f"❌ No pude encontrar '{comuna}'. Intenta de nuevo.")
                continue # Volver a preguntar en lugar de detener el script
                
            ubicacion = datos_geo["results"][0]
            lat = ubicacion["latitude"]
            lon = ubicacion["longitude"]
            nombre_oficial = ubicacion["name"]
            pais = ubicacion.get("country", "País desconocido")
            zona_horaria_str = ubicacion.get("timezone", "America/Santiago")
            
        except Exception as e:
            print(f"❌ Error al buscar la ubicación: {e}")
            continue

        # 2. Obtener la hora exacta
        try:
            zona_horaria = ZoneInfo(zona_horaria_str)
            hora_actual = datetime.now(zona_horaria)
            hora_formateada = hora_actual.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            hora_formateada = "No disponible"

        # 3. Obtener el clima ACTUAL y el PRONÓSTICO (forecast_days=3 trae hoy, mañana y pasado)
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto&forecast_days=3"
        
        try:
            respuesta_clima = urllib.request.urlopen(url_clima, context=contexto_ssl)
            datos_clima = json.loads(respuesta_clima.read().decode('utf-8'))
            
            # Datos actuales
            clima_actual = datos_clima['current_weather']
            temp_actual = clima_actual['temperature']
            viento_actual = clima_actual['windspeed']
            estado_actual = obtener_estado_clima(clima_actual['weathercode'])
            
            # Datos del pronóstico (Índice 1 es Mañana, Índice 2 es Pasado Mañana)
            pronostico = datos_clima['daily']
            
            fecha_manana = pronostico['time'][1]
            max_manana = pronostico['temperature_2m_max'][1]
            min_manana = pronostico['temperature_2m_min'][1]
            estado_manana = obtener_estado_clima(pronostico['weathercode'][1])
            
            fecha_pasado = pronostico['time'][2]
            max_pasado = pronostico['temperature_2m_max'][2]
            min_pasado = pronostico['temperature_2m_min'][2]
            estado_pasado = obtener_estado_clima(pronostico['weathercode'][2])
            
            # Imprimir el reporte final
            print("\n" + "="*45)
            print(f"📍 REPORTE DE: {nombre_oficial}, {pais}")
            print(f"🕒 Hora local: {hora_formateada}")
            print("="*45)
            print("🟢 CLIMA ACTUAL:")
            print(f"   🌡️ Temperatura: {temp_actual}°C (±2°C)")
            print(f"   🌤️ Estado:      {estado_actual}")
            print(f"   💨 Viento:      {viento_actual} km/h")
            print("-" * 45)
            print("📅 PRONÓSTICO PRÓXIMOS 2 DÍAS:")
            print(f"   ▶ Mañana ({fecha_manana}):")
            print(f"      Mín: {min_manana}°C | Máx: {max_manana}°C | {estado_manana}")
            print(f"   ▶ Pasado ({fecha_pasado}):")
            print(f"      Mín: {min_pasado}°C | Máx: {max_pasado}°C | {estado_pasado}")
            print("="*45)
            
        except Exception as e:
            print(f"❌ Error al consultar el clima: {e}")

if __name__ == "__main__":
    consultar_clima_infinito()