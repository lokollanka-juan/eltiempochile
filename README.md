# ⛅ Buscador de Clima Interactivo en Python

Un script interactivo para la terminal que permite consultar el clima actual, la hora local y el pronóstico de los próximos 2 días para cualquier comuna o ciudad del mundo. 

Diseñado específicamente para funcionar de manera **100% nativa**, evitando problemas con `pip`, librerías externas o bloqueos de certificados en macOS.

## ✨ Características Principales

* **Bucle Interactivo:** El programa se mantiene abierto permitiendo múltiples consultas seguidas sin tener que volver a ejecutar el script.
* **Pronóstico Extendido:** Muestra la temperatura actual y el pronóstico de temperaturas mínimas y máximas para los próximos 2 días.
* **Anti-Errores de Mac (SSL):** Incluye un parche nativo que evita los comunes errores de "Connection Reset" o validación de certificados SSL al hacer peticiones web en macOS.
* **Sin Claves ni Registros:** Utiliza la API pública de *Open-Meteo*, por lo que no necesitas registrarte ni configurar API Keys.
* **Zonas Horarias Automáticas:** Calcula y muestra la hora exacta local dependiendo de la ciudad que busques (ej. si buscas "Tokio", mostrará la hora de Japón).

## 🛠️ Requisitos

* **Python 3.9 o superior** (Probado en Python 3.14).
* Conexión a internet.
* *No requiere ninguna instalación externa mediante `pip`.*

Librerías nativas utilizadas: `urllib`, `json`, `ssl`, `datetime`, `zoneinfo`.

## 🚀 Cómo ejecutarlo

1. Abre tu terminal.
2. Navega hasta la carpeta donde guardaste el archivo `.py`.
3. Ejecuta el siguiente comando:

   ```bash
   python tiempo_valpo.py


📖 Uso
Una vez iniciado, el programa te pedirá que ingreses el nombre de una ciudad o comuna:

Plaintext
🌎 Escribe la comuna o ciudad: Valparaíso
El script devolverá un reporte detallado con la temperatura actual (con un margen de error estándar de ±2°C debido a los modelos matemáticos globales) y el estado del clima.

Para cerrar el programa, simplemente escribe salir, quit, exit o cerrar cuando te pida una ciudad.