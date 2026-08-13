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
import sys
import threading
import urllib.parse
import webbrowser

PROY = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.join(PROY, "sitio")
PUERTO = 8765


class Manejador(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITIO, **kw)

    def do_POST(self):
        """Guarda un pedido editado en el estudio.

        Escribe SOLO dentro de `pedidos/` y solo ficheros .yaml: el nombre se
        reduce a su base y se comprueba que la ruta resuelta siga cayendo
        dentro de la carpeta. Que el servidor sea local no es excusa para
        aceptar cualquier ruta.

        Y valida antes de escribir: un pedido inválido no llega a disco.
        """
        import json as _j
        if self.path != "/guardar-pedido":
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = _j.loads(self.rfile.read(n).decode("utf-8"))
            nombre = os.path.basename(d.get("archivo") or "")
            if not nombre.endswith(".yaml") or nombre.startswith("."):
                raise ValueError("solo se guardan ficheros .yaml")
            carpeta = os.path.realpath(os.path.join(PROY, "pedidos"))
            destino = os.path.realpath(os.path.join(carpeta, nombre))
            if not destino.startswith(carpeta + os.sep):
                raise ValueError("ruta fuera de pedidos/")

            if os.path.join(PROY, "herramientas") not in sys.path:
                sys.path.insert(0, os.path.join(PROY, "herramientas"))
            import contrato
            import yaml
            ped = d["pedido"]
            voz = contrato.cargar_voz(ped.get("voz", "fuente-primaria"))
            errs = contrato.validar(ped, voz)
            if errs:
                raise ValueError(errs[0])
            with open(destino, "w", encoding="utf-8") as f:
                yaml.safe_dump(ped, f, allow_unicode=True, sort_keys=False)
            cuerpo = _j.dumps({"ok": True,
                               "huella": contrato.huella(contrato.resolver(ped, voz))})
        except Exception as e:
            cuerpo = _j.dumps({"ok": False, "error": str(e)[:200]})
        b = cuerpo.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

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
