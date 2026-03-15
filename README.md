# ⛅ Buscador de Clima Pro en Python (Terminal)

Un script interactivo y avanzado para la terminal de macOS/Linux que permite consultar el clima actual y el pronóstico de 2 días. Diseñado para ser **100% nativo**, sin dependencias externas (`pip`).

## ✨ Novedades de esta versión
* **Interfaz a todo Color:** Uso de códigos de escape ANSI para colorear textos y crear "etiquetas" de fondo dinámicas según la temperatura (Rojo=Calor, Azul=Frío, Verde=Templado).
* **Animaciones Multihilo:** Implementación de `threading` para crear un "spinner" de carga estilo braille mientras se descargan los datos, evitando que la terminal se congele.
* **Menú Interactivo Anti-Errores:** Si existen múltiples ciudades con el mismo nombre en el mundo, el script despliega un menú numerado para que el usuario elija la correcta.
* **Datos Extendidos:** Ahora muestra Índice UV máximo, Humedad y horas exactas de Amanecer y Atardecer.
* **Parche SSL para macOS:** Contexto de seguridad integrado para evitar bloqueos nativos de Mac al consultar APIs.

## 🚀 Cómo ejecutarlo
```bash
python el_tiempo.py


PD: Estoy partiendo en la programaciòn