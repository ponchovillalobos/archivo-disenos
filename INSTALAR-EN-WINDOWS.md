# Instalar Fuente Primaria en Windows

Este proyecto se escribió y se ejecuta en un Mac mini M4. **Migrarlo a Windows es
posible y la generación de imágenes incluso mejora**, pero hay tres piezas que no
funcionan tal cual y hay que sustituir. Aquí está todo medido, no supuesto.

Lo que sigue está verificado contra el código de este repositorio el 13 de agosto
de 2026: 44 módulos, 7.632 líneas de Python.

---

## Resumen honesto en una tabla

| Pieza | En Windows | Qué hay que hacer |
|---|---|---|
| Generación de imágenes (ComfyUI + SDXL) | ✅ **mejor** | Nada. Con NVIDIA va 4-5× más rápido |
| Composición de láminas (Chromium) | ✅ | Cambiar la ruta del navegador |
| Montaje de vídeo (ffmpeg + PIL) | ✅ | Nada |
| Carrusel PDF y ZIP | ✅ | Nada |
| Portal y estudio visual | ✅ | Nada |
| Contrato, paletas, disposiciones | ✅ | Nada |
| **Transcripción de audio** | ❌ | Sustituir `mlx-whisper` por `faster-whisper` |
| **Guardián de salud** | ❌ | Sustituir `sysctl` por la API de Windows |
| **Rutas del proyecto** | ⚠️ | 17 de 44 módulos llevan rutas de este Mac |

**Esfuerzo estimado: 2-3 días de trabajo.** No es un port, son tres sustituciones
y una capa de configuración.

---

## 1 · Requisitos

| | Mínimo | Recomendado |
|---|---|---|
| SO | Windows 10 x64 | Windows 11 |
| GPU | Cualquiera (irá por CPU, muy lento) | **NVIDIA con 8 GB de VRAM o más** |
| RAM | 16 GB | 32 GB |
| Disco | 25 GB libres | 50 GB |
| Python | **3.12** | 3.12 |

La GPU importa mucho más que el resto. En este M4 con Metal cada imagen tarda
**57 segundos**; una NVIDIA de gama media hace lo mismo en **10-15**.

Sobre la RAM: con 16 GB este Mac sufre presión de memoria constante y hubo que
escribir un guardián que reinicia ComfyUI cuando la generación se degrada —
llegó a pasar de 57 s a **17 minutos por imagen**. Con 32 GB ese problema
desaparece.

---

## 2 · Lo que hay que instalar

### 2.1 · ComfyUI

```powershell
python -m venv %USERPROFILE%\comfy-env
%USERPROFILE%\comfy-env\Scripts\pip install "comfy-cli>=1.16.0"
%USERPROFILE%\comfy-env\Scripts\comfy --skip-prompt --workspace %USERPROFILE%\comfy install --nvidia
```

`--nvidia` en vez de `--m-series`. Si no hay NVIDIA, usa `--cpu` y asume que
cada imagen tardará varios minutos.

Arrancarlo:

```powershell
%USERPROFILE%\comfy-env\Scripts\comfy --workspace %USERPROFILE%\comfy launch --background -- --listen 127.0.0.1 --port 8188
```

Comprobar que vive de verdad, no que "parece que sí":

```powershell
curl http://127.0.0.1:8188/system_stats
```

Debe devolver `"device_type": "cuda"`. En el Mac dice `"mps"`, y varias pruebas
del proyecto comprueban ese valor — hay que cambiarlas (ver §5.3).

### 2.2 · Los tres modelos

**No están en el repositorio**: pesan 7,3 GB y `.gitignore` los excluye. Se
descargan una vez y se colocan en estas carpetas exactas.

| Fichero | Peso | Carpeta | Origen |
|---|---|---|---|
| `juggernautXL_v9.safetensors` | 6,62 GB | `comfy\models\checkpoints\` | Civitai — Juggernaut XL v9 |
| `sdxl_lightning_8step_lora.safetensors` | 0,37 GB | `comfy\models\loras\` | Hugging Face — ByteDance/SDXL-Lightning |
| `sdxl_vae_fp16fix.safetensors` | 0,31 GB | `comfy\models\vae\` | Hugging Face — madebyollin/sdxl-vae-fp16-fix |

Descárgalos con reanudación. Ya nos pasó que una descarga de 7 GB se cortó al
88 % y `comfy model download` **no reanuda**: hubo que empezar de cero.

```powershell
curl.exe -L -C - --retry 8 --retry-all-errors -o juggernautXL_v9.safetensors <URL>
```

### 2.3 · Dependencias de Python

Todo se ejecuta con el intérprete de ComfyUI (`comfy\.venv\Scripts\python.exe`),
no con el Python del sistema. Versiones verificadas en este proyecto:

```
pillow          12.3.0
numpy           2.5.2
av              18.0.0
imageio-ffmpeg  0.6.0     ← trae su propio ffmpeg, no hace falta instalarlo aparte
pyyaml          6.0.3
fonttools       4.63.0
```

`imageio-ffmpeg` es importante: **el proyecto nunca llama a un ffmpeg del
sistema**, siempre al binario que trae ese paquete. Eso funciona igual en
Windows y ahorra una instalación.

### 2.4 · Chromium

La composición tipográfica se hace con **Chromium headless, no con Pillow**.
Es una decisión de diseño, no un capricho: Pillow no tiene raqm, así que no
aplica kerning ni ejes de fuente variable, y este proyecto usa `opsz`, `WONK` y
`SOFT` de Fraunces.

En el Mac apunta a Brave. En Windows vale Brave, Chrome o Edge:

```
C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**Aviso medido:** un cambio de versión del navegador mueve el kerning y el
`text-wrap: balance`. Las láminas cacheadas con una versión no coinciden con las
nuevas. Si migras a mitad de una serie, borra `herramientas\cache-texto`.

---

## 3 · Lo que NO funciona y hay que sustituir

### 3.1 · La transcripción de audio — **bloqueante**

`herramientas\transcribir.py` usa **`mlx-whisper`**, que corre sobre el
framework MLX de Apple. **No existe en Windows.** Afecta a 3 ficheros:
`transcribir.py`, `banco_asr.py`, `prueba_sistema.py`.

El sustituto natural es **`faster-whisper`** (CTranslate2), que además aprovecha
la NVIDIA:

```powershell
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel
modelo = WhisperModel("large-v3", device="cuda", compute_type="float16")
segmentos, _ = modelo.transcribe(audio, language="es",
                                 word_timestamps=True,
                                 condition_on_previous_text=False,
                                 initial_prompt=CONTEXTO,
                                 temperature=0.0)
```

**Vuelve a medir el WER.** El 5,70 % que documenta este proyecto está medido con
MLX sobre este Mac; no es transferible. El banco de pruebas ya existe
(`herramientas\banco_asr.py`, ocho frases de verdad conocida) — solo hay que
cambiar el motor y ejecutarlo. Y cambia `say` por SAPI o por audio grabado: el
banco genera las muestras con la voz del sistema macOS.

Dos parámetros que **no** son opcionales, medidos aquí:

- `condition_on_previous_text=False` — sin esto un error se arrastra y contamina
  todo lo que viene detrás.
- `initial_prompt` — bajó el error de 9,17 % a 5,70 %. Es la mejora más barata
  del proyecto y no cuesta ni un byte de disco.

### 3.2 · El guardián de salud — **bloqueante**

`herramientas\guardian.py` lee la presión de memoria con `sysctl -n
vm.swapusage`, que es de macOS. También lo usan `alimentador.py` y
`reto30_producir.py`.

Existe porque **tres veces la generación se degradó de 57 s a más de 10 minutos
por imagen** y las tres lo descubrió el usuario, no el sistema.

En Windows, el equivalente:

```python
import psutil
def swap_mb():
    return psutil.swap_memory().used / 1e6
```

**Pero lo importante no es esa función.** El guardián vigila el **ritmo**, no el
swap: compara los segundos por imagen contra su propia mediana. Ese diseño
funciona igual en cualquier sistema; solo cambia la lectura de memoria, que es
informativa. Con 32 GB de RAM probablemente no salte nunca.

### 3.3 · Las rutas — **molesto pero mecánico**

**17 de los 44 módulos** llevan rutas absolutas de este Mac:

```
/Users/maity/Desktop/Confy Imagenes     el proyecto
/Users/maity/comfy                      ComfyUI
/Users/maity/comfy/output/reels         donde ComfyUI deja las imágenes
/Users/maity/comfy-env/bin              el ejecutable comfy
/Users/maity/asr/.venv                  el entorno de transcripción
```

Ficheros afectados: `audio.py`, `catalogo.py`, `reel2.py`, `montar_serie.py`,
`recetario.py`, `banco_asr.py`, `buzon.py`, `transcribir.py`, `estudio2.py`,
`guardian.py`, `lote.py`, `alimentador.py`, `prueba_sistema.py`, `recursos.py`,
`reto30_producir.py`, `armar_idea1.py`, `tipografia.py`.

**Lo correcto es una capa de configuración** que los centralice y lea variables
de entorno. Eso además arregla algo que ya duele en el Mac: hoy no se puede
mover el proyecto de carpeta sin romper diecisiete ficheros.

Mientras no exista, un buscar-y-reemplazar funciona.

---

## 4 · Lo que sí es portable tal cual

Y es la mayor parte del valor:

- **La configuración completa del modelo**, en `voz\fuente-primaria.yaml`:
  checkpoint, LoRA y su peso, VAE, pasos, CFG, muestreador, planificador y
  semilla. No hay que adivinar nada.
- **El contrato** (`contrato.py`): pedir lo mismo dos veces da lo mismo, y
  `huella()` lo demuestra en 16 caracteres.
- **Las 16 paletas con su veto** y los 10 ánimos. El veto es lo que hace que el
  color funcione: a CFG 1.0 el modelo casi no obedece una instrucción de color
  en positivo, y solo con el positivo cinco de ocho paletas caían en la franja
  azul-cian.
- **Las 10 disposiciones de lámina** y las 5 voces tipográficas.
- **Los montadores**: Ken Burns con velocidad constante, texto palabra a palabra,
  sincronía con audio.
- **El portal y el estudio visual**, HTML estático servido por `servidor.py`.
- **El recetario**: 371 recetas recuperadas de los metadatos de los propios PNG.
  ComfyUI escribe el flujo entero dentro de cada imagen — eso funciona igual en
  cualquier sistema.

---

## 5 · Pasos concretos, en orden

1. **Clona el repositorio** y crea la estructura: `out\`, `sitio\descargas\`,
   `audio\ENTRADA\`.
2. **Instala ComfyUI** con `--nvidia` y comprueba `"device_type": "cuda"`.
3. **Descarga los tres modelos** a sus carpetas exactas (§2.2).
4. **Sustituye las rutas** de los 17 módulos, o escribe la capa de
   configuración.
5. **Cambia el navegador** en `estudio2.py` y `reel2.py`.
6. **Adapta las pruebas**: `prueba_sistema.py` exige `"mps"` en dos sitios y
   `sysctl` en uno. Cámbialos por `"cuda"` y `psutil`.
7. **Ejecuta la prueba de humo**:
   ```powershell
   comfy\.venv\Scripts\python.exe herramientas\prueba_sistema.py
   ```
   Debe dar verde en todo menos transcripción hasta que hagas el §3.1.
8. **Genera una imagen de prueba** con un pedido existente antes de tocar nada
   más.
9. **Sustituye la transcripción** (§3.1) y vuelve a correr el banco.

---

## 6 · Reglas del proyecto que hay que respetar, vengas de donde vengas

No son estilo: cada una viene de un fallo que ya se pagó.

- **Ningún dato sin verificar en fuente primaria.** Si una cita no aguanta, se
  cambia el tema o se publica el desmentido, que suele ser mejor gancho.
- **Cero caras y cero manos.** SDXL falla ahí de forma estructural. Los humanos
  van como siluetas lejanas, de espaldas o en niebla. El negativo lleva pesos:
  `(face:1.6) (hands:1.6) (fingers:1.6)`.
- **Verificar en pantalla antes de decir que algo está listo.** Renderizar con
  Chromium headless y mirar la captura. Nunca dar por bueno porque el archivo se
  abrió o el script terminó sin error.
- **El portal se actualiza en el mismo turno en que nace el archivo.** Terminar
  un vídeo y no publicarlo cuenta como no haberlo terminado.
- **No editar módulos de un proceso que está corriendo.** Python los carga al
  arrancar: una hora de ediciones no llegó nunca al productor vivo y publicó 17
  vídeos que nadie veía.

---

## 7 · Rendimiento medido, para que compares

En el Mac mini M4 de 16 GB, con Metal:

| | |
|---|---|
| Una imagen 720×1280, 8 pasos | **57 s** (mediana de 54 muestras) |
| Seis imágenes de un tema | 5,4 min |
| Composición de 6 láminas (Chromium) | 13 s |
| Montaje de un reel (ffmpeg) | 40 s |
| Música con loudness en dos pasadas | 1 s |
| **Un reel completo** | **≈ 8 min de máquina** |
| Transcripción | 2,6× tiempo real |
| Reconstrucción del catálogo | 0,0 s con caché (47,5 s sin ella) |

El cuello de botella nunca fue la GPU: es escribir el guion y auditar las
imágenes.
