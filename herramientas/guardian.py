"""Vigila la generación. Y sobre todo: NO ESTORBA.

## La noche que el vigilante rompió lo que vigilaba

La versión anterior de este módulo destruyó un estudio de seis horas. Merece
estar escrito aquí entero, porque el fallo no fue un descuido: fue un error de
criterio, y sin el relato se repite.

El umbral se calculaba así:

    umbral = max(normal, ritmo) * factor  =  max(150, 150) * 3  =  450 s

Y las imágenes de aquella noche tardaban entre 18 y 50 minutos. O sea que el
Guardián **mataba cada imagen a los 7 minutos y medio**, siempre, antes de que
pudiera terminar nunca. Reiniciaba ComfyUI, la cola se vaciaba, el productor
reencolaba, y a los 7 minutos y medio volvía a matarla. Trece veces en seis
horas. Ocho imágenes de 36.

La prueba de que la causa era él: el estudio murió a las 03:56 y las seis
imágenes que faltaban salieron **después**, entre las 04:13 y las 07:40. En
cuanto dejó de vigilar, la máquina produjo.

Y el `ritmo` no podía corregirse solo, porque solo se actualiza cuando algo
avanza — y nada avanzaba nunca. Un bucle cerrado sobre sí mismo.

## Las tres reglas que salen de ahí

**1. Medir de verdad, no estimar.** ComfyUI guarda `execution_start` y
`execution_success` de cada trabajo en `/history`. El tiempo real por imagen
estaba ahí todo el tiempo, y el Guardián se inventaba un número teniéndolo a
mano. Ahora la mediana sale de ahí.

**2. No matar a quien está trabajando.** Antes de reiniciar hay que comprobar
que ComfyUI está de verdad atascado y no simplemente lento. Se miran dos cosas
que el reloj no ve: si el historial creció (terminó algo) y si el proceso está
quemando CPU. Cualquiera de las dos significa «está vivo, no lo toques».

**3. Reiniciar es la última opción, no la primera.** Un reinicio tira la imagen
en curso, vacía la cola y obliga a recargar el modelo. Cuesta caro y casi nunca
arregla nada: de trece reinicios, once liberaron menos de 60 MB. Ahora hay un
suelo absoluto —media hora— por debajo del cual no se reinicia jamás, por muy
mal que pinte la aritmética.

## Qué vigila

  · **El RITMO real**, de `/history`, contra su propia mediana.
  · **El estancamiento de verdad**: cola con trabajo, historial que no crece y
    proceso sin CPU. Las tres a la vez.
  · **ComfyUI caído**, que es el único caso donde reiniciar es obviamente
    correcto.

Deja rastro en `salud.jsonl`: una línea por medición, para poder reconstruir
después cuándo empezó a torcerse sin depender de la memoria de nadie.
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

# Suelo absoluto del umbral, en segundos. Por debajo de esto NO se reinicia
# jamás, pase lo que pase con la aritmética.
#
# Media hora no es un número redondo elegido al azar: es más del doble de la
# imagen más lenta que hemos visto terminar bien (50 min fue con el sistema ya
# roto; en sano, 130 s). Si algo lleva media hora sin dar señales Y sin CPU,
# está muerto de verdad. Cualquier cosa por debajo corre el riesgo de matar
# trabajo bueno, que es justo lo que pasó.
SUELO = 1800.0


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


def historial(n=20):
    """Duración REAL de los últimos trabajos, en segundos.

    ComfyUI apunta `execution_start` y `execution_success` en milisegundos por
    cada trabajo. Es la única medida que no es una estimación mía, y estaba
    disponible desde el principio."""
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:8188/history?max_items=%d" % n, timeout=10) as r:
            h = json.load(r)
    except Exception:
        return []
    ds = []
    for v in h.values():
        t = {}
        for m in v.get("status", {}).get("messages", []):
            if m[0] in ("execution_start", "execution_success"):
                t[m[0]] = m[1].get("timestamp", 0)
        if len(t) == 2:
            d = (t["execution_success"] - t["execution_start"]) / 1000.0
            if d > 0:
                ds.append(d)
    return ds


def terminados():
    """Cuántos trabajos hay en el historial. Si sube, algo terminó de verdad."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/history?max_items=200",
                                    timeout=10) as r:
            return len(json.load(r))
    except Exception:
        return -1


def cpu_de_comfy(muestra=3.0):
    """% de CPU del proceso de ComfyUI, medido en un intervalo.

    `ps` a secas da la media desde que arrancó, que no sirve para saber si está
    trabajando AHORA. Hay que muestrear dos veces y restar."""
    try:
        pid = subprocess.run(["pgrep", "-f", "main.py --listen"],
                             capture_output=True, text=True).stdout.split()
        if not pid:
            return -1.0
        pid = pid[0]

        def t():
            o = subprocess.run(["ps", "-o", "time=", "-p", pid],
                               capture_output=True, text=True).stdout.strip()
            p = [float(x) for x in o.replace("-", ":").split(":")] if o else [0]
            s = 0.0
            for x in p:
                s = s * 60 + x
            return s
        a = t()
        time.sleep(muestra)
        return (t() - a) / muestra * 100.0
    except Exception:
        return -1.0


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

    def __init__(self, patron, normal=60.0, factor=4.0, registro=None,
                 al_avisar=print, suelo=SUELO):
        self.patron = patron
        self.normal = normal
        self.factor = factor
        self.suelo = suelo
        self.tiempos = []
        self.reinicios = 0
        self.avisar = al_avisar
        self.registro = registro or os.path.join(PROY, "salud.jsonl")
        self.n = self._cuenta()
        self.hechos = terminados()
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
        """Mediana real de segundos por trabajo, sacada de ComfyUI.

        Se prefiere el historial de ComfyUI a mis propias mediciones: él sabe
        cuándo empezó y acabó cada trabajo, yo solo veo aparecer ficheros. La
        mediana y no la media, porque un trabajo largo suelto desplazaría la
        media y taparía el ritmo normal."""
        ds = historial(20) or self.tiempos[-12:]
        if len(ds) < 3:
            return self.normal
        t = sorted(ds)
        return t[len(t) // 2]

    @property
    def umbral(self):
        """Nunca por debajo del suelo. Ésta es la línea que evitó el desastre:
        con la fórmula sola, 150 s × 4 = 600 s, y una imagen de 18 minutos moría
        igual que antes."""
        return max(self.ritmo * self.factor, self.suelo)

    def _atascado(self):
        """¿Parado de verdad, o solo lento? Dos señales que el reloj no ve.

        Basta con que UNA diga que está vivo para no tocarlo. Prefiero esperar
        de más a matar una imagen que iba por el paso 28 de 30."""
        h = terminados()
        if h > self.hechos:               # terminó algo, aunque no sea lo mío
            self.hechos = h
            return False, "el historial creció"
        c = cpu_de_comfy()
        if c > 20.0:
            return False, "quemando CPU (%.0f%%)" % c
        return True, "historial parado y CPU al %.0f%%" % c

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
            self.hechos = terminados()
            self._anota(evento="avance", salidas=salidas,
                        ritmo=round(self.ritmo))
            return salidas

        parado = ahora - self.t0

        if not viva():
            self.avisar("ComfyUI no responde · reinicio")
            self._anota(evento="caido")
            self._reiniciar()
            return 0

        if cola() == 0:
            self._anota(evento="cola vacia", parado=round(parado))
            return 0                      # el productor decidirá si encolar

        if parado <= self.umbral:
            return 0                      # lento no es roto: se espera

        # Pasado el umbral, todavía NO se reinicia. Primero se pregunta si está
        # trabajando. Saltarse este paso es exactamente lo que costó una noche.
        atascado, motivo = self._atascado()
        if not atascado:
            self.avisar("lento (%.0f s) pero vivo: %s · lo dejo en paz"
                        % (parado, motivo))
            self._anota(evento="lento_pero_vivo", parado=round(parado),
                        motivo=motivo, ritmo=round(self.ritmo))
            self.t0 = ahora               # se le concede otro plazo entero
            return 0

        self.avisar("ATASCADO %.0f s (umbral %.0f · ritmo %.0f) · %s · swap %.0f MB"
                    % (parado, self.umbral, self.ritmo, motivo, swap_mb()))
        self._anota(evento="atascado", parado=round(parado),
                    umbral=round(self.umbral), motivo=motivo)
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
                "umbral_s": round(self.umbral), "reinicios": self.reinicios,
                "swap_mb": round(swap_mb())}


def salud():
    """Foto del estado ahora mismo, para la prueba de humo."""
    ds = historial(20)
    med = sorted(ds)[len(ds) // 2] if len(ds) >= 3 else None
    return {"comfyui": viva(), "cola": cola(), "swap_mb": round(swap_mb()),
            "ritmo_s": round(med) if med else None,
            "cpu_comfy": round(cpu_de_comfy(1.5))}


if __name__ == "__main__":
    print("  ", salud())
