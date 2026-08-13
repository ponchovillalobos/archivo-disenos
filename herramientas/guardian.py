"""Vigila la salud de la generación y actúa antes de que alguien lo note.

Tres veces se ha degradado la generación por presión de memoria, y las tres lo
descubrió el usuario, no el sistema. Medido en la última: de 57 s por imagen a
**17 minutos**, un factor de 18. Las 180 imágenes pasaban de 3 horas a 33.

El fallo de diseño no era el swap: era que **nadie estaba mirando**. Cada
productor traía su propio bucle de espera, y ninguno medía si el trabajo
avanzaba al ritmo que debería.

Esto lo centraliza. Un productor no vuelve a escribir `time.sleep()` a pelo:
llama a `Guardian.esperar()`, que además de esperar mide, decide y actúa.

Qué vigila y por qué ése y no otro:

  · **El RITMO, no el swap.** El swap es la causa, pero medirlo lleva a
    umbrales inventados —¿12 GB? ¿16?— que cambian con la máquina y con lo que
    haya abierto. El síntoma que de verdad importa es cuánto tarda una imagen,
    y ése se compara contra su propia mediana, no contra un número fijo.
  · **El estancamiento.** Si en N minutos no sale ni una imagen, algo está
    parado aunque la cola diga que hay trabajo.
  · **La cola vacía con trabajo pendiente.** Ha pasado: encolar falla en
    silencio y el productor espera para siempre a que salga algo.

Y deja rastro: `salud.jsonl` guarda una línea por medición, así que después se
puede ver cuándo empezó a torcerse y no hay que reconstruirlo de memoria.
"""
import glob
import json
import os
import re
import subprocess
import time
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.dirname(S)
BIN = "/Users/maity/comfy-env/bin"
ENV = dict(os.environ, PATH=BIN + ":" + os.environ.get("PATH", ""))


def swap_mb():
    s = subprocess.run(["sysctl", "-n", "vm.swapusage"],
                       capture_output=True, text=True).stdout
    m = re.search(r"used\s*=\s*([\d.]+)M", s)
    return float(m.group(1)) if m else 0.0


def cola():
    """-1 si ComfyUI no responde. Distinguirlo de 0 importa: cero significa
    'sin trabajo' y menos uno significa 'no hay con quién hablar'."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=10) as r:
            q = json.load(r)
        return len(q.get("queue_running", [])) + len(q.get("queue_pending", []))
    except Exception:
        return -1


def viva():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats",
                                    timeout=8) as r:
            return json.load(r)["devices"][0]["type"] == "mps"
    except Exception:
        return False


def reiniciar(espera=45):
    """Para y levanta ComfyUI. Devuelve cuánto swap se liberó."""
    antes = swap_mb()
    subprocess.run([BIN + "/comfy", "stop"], capture_output=True, env=ENV)
    time.sleep(8)
    subprocess.Popen(
        [BIN + "/comfy", "--workspace", "/Users/maity/comfy", "launch",
         "--background", "--", "--listen", "127.0.0.1", "--port", "8188",
         "--use-pytorch-cross-attention"],
        env=dict(ENV, PYTORCH_ENABLE_MPS_FALLBACK="1"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(espera):
        if viva():
            return antes - swap_mb()
        time.sleep(5)
    return None


class Guardian:
    """Mide, decide y actúa. Un productor no vuelve a dormir a ciegas.

    patron: glob de las imágenes que este trabajo produce, para contar avance.
    normal: segundos por imagen esperados. Solo se usa hasta tener mediciones
            propias; a partir de la quinta manda la mediana real.
    """

    def __init__(self, patron, normal=60.0, factor=3.0, registro=None,
                 al_avisar=print):
        self.patron = patron
        self.normal = normal
        self.factor = factor
        self.tiempos = []
        self.reinicios = 0
        self.avisar = al_avisar
        self.registro = registro or os.path.join(PROY, "salud.jsonl")
        self.n = self._cuenta()
        self.t0 = time.time()

    def _cuenta(self):
        return len(glob.glob(self.patron))

    def _anota(self, **kw):
        try:
            with open(self.registro, "a", buffering=1) as f:
                f.write(json.dumps(dict(kw, t=time.strftime("%H:%M:%S"),
                                        swap=round(swap_mb())),
                                   ensure_ascii=False) + "\n")
        except OSError:
            pass

    @property
    def ritmo(self):
        """Mediana de segundos por imagen. La mediana y no la media: un solo
        reinicio de 400 s desplazaría la media y taparía la degradación."""
        if len(self.tiempos) < 3:
            return self.normal
        t = sorted(self.tiempos[-12:])
        return t[len(t) // 2]

    def esperar(self, segundos=60):
        """Duerme, mide y actúa. Devuelve cuántas imágenes salieron."""
        time.sleep(segundos)
        n = self._cuenta()
        salidas = n - self.n
        ahora = time.time()

        if salidas > 0:
            for _ in range(salidas):
                self.tiempos.append((ahora - self.t0) / salidas)
            self.n, self.t0 = n, ahora
            self._anota(evento="avance", salidas=salidas,
                        ritmo=round(self.ritmo))
            return salidas

        parado = ahora - self.t0
        umbral = max(self.normal, self.ritmo) * self.factor

        if not viva():
            self.avisar("ComfyUI no responde · reinicio")
            self._anota(evento="caido")
            self._reiniciar()
            return 0

        if cola() == 0:
            self._anota(evento="cola vacia", parado=round(parado))
            return 0                      # el productor decidirá si encolar

        if parado > umbral:
            self.avisar("sin avance en %.0f s (umbral %.0f) · swap %.0f MB"
                        % (parado, umbral, swap_mb()))
            self._anota(evento="degradado", parado=round(parado),
                        umbral=round(umbral))
            self._reiniciar()
        return 0

    def _reiniciar(self):
        liberado = reiniciar()
        self.reinicios += 1
        self.t0 = time.time()
        self.tiempos.clear()
        if liberado is None:
            self.avisar("ComfyUI no volvió del reinicio")
            self._anota(evento="reinicio fallido")
        else:
            self.avisar("reiniciado · %.0f MB liberados" % liberado)
            self._anota(evento="reiniciado", liberado=round(liberado))

    def resumen(self):
        return {"hechas": self._cuenta(), "ritmo_s": round(self.ritmo, 1),
                "reinicios": self.reinicios, "swap_mb": round(swap_mb())}


def salud():
    """Foto del estado ahora mismo, para la prueba de humo."""
    return {"comfyui": viva(), "cola": cola(), "swap_mb": round(swap_mb())}


if __name__ == "__main__":
    print("  ", salud())
