"""Inyecta el sistema tipográfico real en el sitio.

Tres roles, tres familias variables, todas OFL y todas incrustadas en el HTML
(hace falta base64: al abrir la página como archivo local, el navegador bloquea
la carga de fuentes desde rutas relativas).

  Display   Fraunces    opsz 9–144 · wght 100–900 · WONK 0–1
  Texto     Newsreader  opsz 6–72  · wght 200–800
  Interfaz  Recursive   wght 300–1000 · CASL 0–1 · MONO 0–1

El eje `opsz` es el que marca la diferencia: la letra cambia de DIBUJO según el
tamaño, no solo de escala. Y `MONO` de Recursive da la monoespaciada de la
misma familia, así que las rutas y el código no desentonan.
"""
import base64, os, re

FU = "/Users/maity/Desktop/Confy Imagenes/fuentes"
IDX = "/Users/maity/Desktop/Confy Imagenes/sitio/index.html"


def b64(n):
    with open(os.path.join(FU, n), "rb") as f:
        return base64.b64encode(f.read()).decode()


CARAS = f"""
@font-face{{font-family:Fraunces;font-weight:100 900;font-display:swap;
  src:url(data:font/woff2;base64,{b64('Fraunces-sub.woff2')})format("woff2")}}
@font-face{{font-family:Newsreader;font-weight:200 800;font-display:swap;
  src:url(data:font/woff2;base64,{b64('Newsreader-sub.woff2')})format("woff2")}}
@font-face{{font-family:Recursive;font-weight:300 1000;font-display:swap;
  src:url(data:font/woff2;base64,{b64('Recursive-ui.woff2')})format("woff2")}}
"""

TOKENS = """  --display:Fraunces,"Didot",Georgia,serif;
  --texto:Newsreader,"Iowan Old Style",Georgia,serif;
  --ui:Recursive,-apple-system,"Segoe UI",Helvetica,sans-serif;
  --mono:Recursive,ui-monospace,Menlo,monospace;"""

# Ajustes por rol. La interfaz lleva CASL 0.28: un punto de calidez que
# despega a Recursive del look de sistema operativo sin volverse informal.
REGLAS = """
body{font-family:var(--ui);font-variation-settings:"CASL" .28,"MONO" 0}
h1{font-family:var(--display);font-variation-settings:"opsz" 144,"WONK" 1,"SOFT" 0}
.lema{font-family:var(--texto);font-variation-settings:"opsz" 24}
.gt h2{font-family:var(--display);font-variation-settings:"opsz" 96,"WONK" 1}
.col h2{font-family:var(--display);font-variation-settings:"opsz" 60,"WONK" 1}
.res{font-family:var(--texto);font-variation-settings:"opsz" 18}
.nota{font-family:var(--texto);font-variation-settings:"opsz" 14}
.eyebrow,.meta,.et,.gn,.mas{font-variation-settings:"CASL" .1,"MONO" 0}
.db,.chip,.cuenta,.buscar input{font-variation-settings:"CASL" .3,"MONO" 0}
code,.ru code{font-family:var(--mono);font-variation-settings:"MONO" 1,"CASL" .2}
.visor figcaption b{font-family:var(--display);font-variation-settings:"opsz" 48,"WONK" 1}
.gsub{font-family:var(--texto);font-variation-settings:"opsz" 16}
"""


def main():
    s = open(IDX, encoding="utf-8").read()

    # 1) las caras, justo al abrir el <style>
    if "@font-face{font-family:Fraunces" not in s:
        s = s.replace("<style>\n:root{", "<style>" + CARAS + "\n:root{", 1)

    # 2) los tokens de familia dentro de :root
    s = re.sub(r'  --serif:[^\n]*\n  --sans:[^\n]*\n', TOKENS + "\n", s, count=1)
    s = s.replace("var(--serif)", "var(--display)").replace("var(--sans)", "var(--ui)")

    # 3) los ajustes por rol, al final de la hoja
    if "/* sistema tipográfico */" not in s:
        s = s.replace("</style>", "/* sistema tipográfico */" + REGLAS + "</style>", 1)

    open(IDX, "w", encoding="utf-8").write(s)
    print("  sistema tipográfico inyectado · %.0f KB de fuentes"
          % (os.path.getsize(IDX) / 1024))


if __name__ == "__main__":
    main()
