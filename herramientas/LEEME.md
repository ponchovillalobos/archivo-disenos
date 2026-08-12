# Herramientas de producción

El pipeline completo. Se ejecutan con el Python de ComfyUI:
`/Users/maity/comfy/.venv/bin/python`

| Archivo | Qué hace |
|---|---|
| `lote.py` | Construye flujos de ComfyUI con las reglas duras (sin caras ni manos) |
| `temas1.py` `temas2.py` | Definiciones de escenas por tema |
| `estudio2.py` | Compone láminas 1080×1350 con Chromium y fuentes variables |
| `reel2.py` | Maquetación del texto del reel + duración por tiempo de lectura |
| `reel3.py` | Montaje del vídeo: fundidos suaves, deriva lineal, ffmpeg |
| `audio.py` | Música: recorte, fundidos y normalización en dos pasadas |
| `montar_serie.py` | Un tema completo: fondos → láminas → reel → música |
| `paralelo.py` | Varios temas a la vez. **Hilos, no procesos** (spawn falla en macOS) |
| `recursos.py` | Láminas sueltas, PDF y ZIP de cada proyecto |
| `catalogo.py` | Construye el catálogo del portal, un proyecto = una ficha |
| `guiones1.py` `guiones2.py` | Los textos, con sus datos verificados |
| `tipografia.py` | Inyecta el sistema tipográfico en el sitio |
