#!/usr/bin/env python3
"""Servidor local del portal.

Un navegador no puede abrir Finder por sí solo: se lo impide el aislamiento
de seguridad, y no hay forma de saltárselo. Lo que sí puede es pedírselo a un
servidor que corra en tu propio Mac. Eso es lo que hace este archivo.

Además, servir la página por HTTP (en vez de abrirla como archivo suelto)
arregla de paso el portapapeles y la reproducción de vídeo.

Se arranca con doble clic en «Abrir portal.command».
Para pararlo: cierra la ventana de Terminal, o pulsa Ctrl-C.
"""
import http.server
import os
import socketserver
import subprocess
import threading
import urllib.parse
import webbrowser

PROY = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.join(PROY, "sitio")
PUERTO = 8765


class Manejador(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITIO, **kw)

    def do_GET(self):
        if self.path.startswith("/abrir?"):
            return self._abrir_en_finder()
        return super().do_GET()

    def end_headers(self):
        # Sin esto el navegador REPRODUCE el MP4 en vez de descargarlo: al
        # servirse como video/mp4 se abre en el reproductor y no hay archivo.
        # Con esta cabecera, pulsar la descarga guarda el fichero siempre.
        ruta = urllib.parse.urlparse(self.path).path
        if ruta.startswith("/descargas/") and not self.path.endswith("?ver"):
            nombre = os.path.basename(urllib.parse.unquote(ruta))
            self.send_header("Content-Disposition",
                             'attachment; filename="%s"' % nombre)
        super().end_headers()

    def _abrir_en_finder(self):
        consulta = urllib.parse.urlparse(self.path).query
        ruta = urllib.parse.parse_qs(consulta).get("ruta", [""])[0]
        ruta = os.path.realpath(ruta)

        # Solo se abre lo que esté dentro del proyecto. Sin esto, cualquier
        # página del navegador podría pedirle a este servidor que abriera
        # cualquier carpeta del Mac.
        dentro = os.path.commonpath([ruta, os.path.realpath(PROY)]) == \
            os.path.realpath(PROY)
        if not dentro or not os.path.exists(ruta):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"ruta fuera del proyecto o inexistente")
            return

        subprocess.run(["open", "-R" if os.path.isfile(ruta) else "", ruta],
                       check=False)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(("abierto: " + ruta).encode())

    def log_message(self, *a):
        pass                      # sin ruido en la terminal


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    url = "http://127.0.0.1:%d/" % PUERTO
    print("\n  Portal servido en  %s" % url)
    print("  Carpeta            %s" % SITIO)
    print("\n  Los botones «Abrir en Finder» ya funcionan.")
    print("  Para parar: Ctrl-C, o cierra esta ventana.\n")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        # 127.0.0.1, no 0.0.0.0: nadie de la red puede alcanzarlo
        with Servidor(("127.0.0.1", PUERTO), Manejador) as s:
            s.serve_forever()
    except KeyboardInterrupt:
        print("  Portal detenido.\n")
