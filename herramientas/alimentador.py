"""Mantiene la cola de ComfyUI llena sin que nadie la vigile.

Existe porque la GPU se quedó ociosa dos veces y lo notó el usuario antes que
yo. La regla es simple: **encolar el siguiente bloque antes de que se vacíe el
anterior**, nunca después.

Además reinicia ComfyUI cuando el swap aprieta. Medido en este M4: al pasar de
~16 GB de swap la generación se degradó de 52 s a 541 s por imagen, y reiniciar
liberó entre 4 y 12 GB. Reiniciar a tiempo sale diez veces más barato que
descubrirlo tres horas después.
"""
import os
import subprocess
import sys
import time
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

BIN = "/Users/maity/comfy-env/bin"
ENV = dict(os.environ, PATH=BIN + ":" + os.environ.get("PATH", ""))
UMBRAL = 10          # cuando queden menos, se mete el siguiente bloque
SWAP_MAX = 12_000    # MB de swap usado que disparan el reinicio


def cola():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=10) as r:
            import json
            q = json.load(r)
        return len(q.get("queue_running", [])) + len(q.get("queue_pending", []))
    except Exception:
        return -1


def swap_mb():
    """MB de swap EN USO. Va por expresión regular a propósito: la primera
    versión buscaba el token a mano y devolvía 8914 cuando el real era 5445."""
    import re
    s = subprocess.run(["sysctl", "-n", "vm.swapusage"],
                       capture_output=True, text=True).stdout
    m = re.search(r"used\s*=\s*([\d.]+)M", s)
    return float(m.group(1)) if m else 0.0


def reiniciar():
    subprocess.run([BIN + "/comfy", "stop"], capture_output=True, env=ENV)
    time.sleep(6)
    subprocess.Popen(
        [BIN + "/comfy", "--workspace", "/Users/maity/comfy", "launch", "--background",
         "--", "--listen", "127.0.0.1", "--port", "8188",
         "--use-pytorch-cross-attention"],
        env=dict(ENV, PYTORCH_ENABLE_MPS_FALLBACK="1"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if cola() >= 0:
            return True
        time.sleep(5)
    return False


def correr(bloques, registro):
    """bloques: lista de listas de temas. Se van soltando de uno en uno."""
    from temas3 import encolar
    with open(registro, "a", buffering=1) as log:
        def di(m):
            log.write("%s  %s\n" % (time.strftime("%H:%M"), m))

        for i, bloque in enumerate(bloques, 1):
            # esperar a que baje, NO a que se vacíe
            while True:
                n = cola()
                if n < 0:
                    di("ComfyUI no responde; reiniciando")
                    reiniciar()
                elif n <= UMBRAL:
                    break
                time.sleep(30)

            if swap_mb() > SWAP_MAX:
                di("swap en %.0f MB; reinicio preventivo" % swap_mb())
                # la cola en curso se pierde al parar, así que se espera a vaciar
                while cola() > 0:
                    time.sleep(20)
                reiniciar()
                di("ComfyUI de vuelta, swap %.0f MB" % swap_mb())

            rutas, rep = encolar(bloque)
            ok = sum(subprocess.run(
                [BIN + "/comfy", "--skip-prompt", "run", "--workflow", r],
                capture_output=True, env=ENV, timeout=300).returncode == 0
                for r in rutas)
            di("bloque %d/%d · %d/%d encolados · %s"
               % (i, len(bloques), ok, len(rutas),
                  " ".join("%s(%s/%s)" % (t, rep[t][0], rep[t][2]) for t in bloque)))

        while cola() > 0:
            time.sleep(30)
        di("terminado")


if __name__ == "__main__":
    BLOQUES = [
        ["el-tono", "escasez", "jerga", "la-brevedad", "la-memoria"],
        ["la-prueba", "primera-impresion", "primeras-palabras", "reciprocidad", "repeticion"],
    ]
    correr(BLOQUES, os.path.join(S, "..", "alimentador.log"))
