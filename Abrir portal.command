#!/bin/bash
# Doble clic aquí para abrir el portal.
# Arranca un servidor local y abre el navegador. Cierra esta ventana para pararlo.
cd "$(dirname "$0")"
exec /Users/maity/comfy/.venv/bin/python servidor.py
