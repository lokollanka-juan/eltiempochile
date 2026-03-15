# ⛅ Asistente de Clima CLI - Nivel Dios (V5.0)

Un buscador meteorológico interactivo, asíncrono y de nivel profesional para la terminal. Diseñado para funcionar de manera **100% nativa con Python** (sin instalar librerías externas mediante `pip`) y potenciado con integración profunda para macOS.

Este no es un simple script de consola; es un asistente virtual completo que te habla, te notifica, dibuja mapas de progreso solar y te abre radares interactivos en tiempo real.

## ✨ Características Principales

* **⚡ Multihilo (Threading):** Descargas asíncronas con animaciones de carga fluidas (spinner Braille) que evitan que la terminal se congele.
* **⚔️ Modo Batalla (`vs`):** Compara el clima de dos ciudades simultáneamente. Descarga los datos en paralelo y genera una tabla comparativa resaltando al ganador en temperatura, viento y humedad.
* **🗣️ Integración Nativa con macOS:** Utiliza `subprocess` para enviar Notificaciones de Escritorio (AppleScript) y leer el reporte en voz alta usando el sintetizador de voz del sistema (`say`) en segundo plano.
* **🎨 Interfaz UI Rica en Texto:** Uso avanzado de Códigos de Escape ANSI para colores dinámicos, fondos (etiquetas de temperatura según si hace calor o frío) y texto parpadeante.
* **🖼️ Arte ASCII y Gráficos:** Dibuja un ícono gigante según el estado del clima y calcula matemáticamente una barra de progreso (`[███☀️-------]`) que muestra la posición exacta del sol entre el amanecer y el atardecer.
* **🚨 Sistema de Alerta Temprana:** Detecta y advierte con alarmas visuales sobre radiación UV peligrosa, vientos huracanados o temperaturas extremas.
* **🌐 Radar Interactivo Web:** Se conecta con el módulo `webbrowser` para abrir automáticamente **Windy.com** en tus coordenadas exactas y mostrarte el radar meteorológico en vivo.
* **🚀 Modo Hacker (Argumentos):** Permite saltar el menú interactivo pasando la ciudad directamente por consola (Ej: `clima "Tokio"`).

## 🛠️ Requisitos

* **Python 3.x** (Módulos usados: `urllib`, `json`, `ssl`, `threading`, `subprocess`, `webbrowser`, `zoneinfo`).
* **Sistema Operativo:** Optimizado para **macOS / Linux**. *(Nota: Funciona en Windows, pero las funciones de voz nativa y notificaciones de AppleScript se omitirán de forma segura).*

## 🚀 Instalación y Configuración (macOS/Linux)

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/lokollanka-juan/eltiempochile.git](https://github.com/lokollanka-juan/eltiempochile.git)
   cd eltiempochile