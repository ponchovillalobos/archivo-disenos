# Chuleta — ComfyUI en tu Mac mini M4

Copia y pega en **Terminal.app**. No necesitas entender nada más que esto.

> 👉 **¿Quieres VER y editar el flujo tú mismo?** Está todo explicado paso a paso en
> **`GUIA-VISUAL.md`** (abrir la interfaz, dónde está el prompt, dónde está la semilla).

## Encender ComfyUI
```bash
export PATH="$HOME/comfy-env/bin:$PATH"; export PYTORCH_ENABLE_MPS_FALLBACK=1
comfy launch --background -- --listen 127.0.0.1 --port 8188 --use-pytorch-cross-attention
```
Luego abre **http://127.0.0.1:8188** en el navegador.

## Generar una imagen
```bash
export PATH="$HOME/comfy-env/bin:$PATH"
comfy run --workflow ~/reels/workflows/01-rapido.json --wait
```
O simplemente pídemelo a mí: yo lo hago por el MCP y te traigo la imagen a `out/`.

## ¿Está vivo?
```bash
curl -s http://127.0.0.1:8188/system_stats | head -c 200
```
Si responde texto → sí. Si no responde nada → está apagado.

## Apagar
```bash
export PATH="$HOME/comfy-env/bin:$PATH"; comfy stop
```

## Ver qué hay instalado
```bash
export PATH="$HOME/comfy-env/bin:$PATH"; comfy env
```

---

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Motor ComfyUI (+ su propio Python y PyTorch) | `~/comfy` |
| Herramientas `comfy` y `comfy-mcp` | `~/comfy-env/bin` |
| **Modelos** (aquí van los checkpoints) | `~/comfy/models/checkpoints` |
| Salidas por defecto de ComfyUI | `~/comfy/output` |
| Tu proyecto | `~/Desktop/Confy Imagenes` (atajo sin espacios: `~/reels`) |

## Rendimiento REAL medido en esta máquina (11-ago-2026)

M4 base (GPU 10 núcleos), 16 GB unificados, 768×1344, Juggernaut XL v9:

| Flujo | Pasos | Tiempo | Para qué |
|---|---|---|---|
| `01-rapido.json` | 8 | **37 s** | Explorar ideas, muchas variantes |
| `02-calidad.json` | 30 | **144 s** | Toma final |

- Coste base: **~4,8 s por paso**. Primera imagen tras encender: +10 s por cargar el modelo.
- **`--use-pytorch-cross-attention` da un 27% de mejora** (37 s con flag vs 51 s sin él).
  Medido dos veces, en caliente, misma escena. Ya está fijado como valor por defecto.
- A 30 pasos el Mac usa **swap** (~2,8 GB). Cierra navegadores pesados antes de una tanda larga.

## Notas técnicas (por si algún día alguien más lo toca)

- `comfy-cli` 1.16 crea **su propio entorno** en `~/comfy/.venv` — ahí vive PyTorch 2.13.0,
  no en `~/comfy-env`.
- `comfy launch --background` se re-invoca a sí mismo por nombre → **siempre hay que tener
  `~/comfy-env/bin` en el PATH** o falla con `FileNotFoundError: 'comfy'`.
- El MCP está registrado en ámbito **usuario** en `~/.claude.json` con rutas absolutas y PATH
  explícito, precisamente por lo anterior.
- Hardware: M4, 16 GB unificados. Evitar fp8 (roto en Metal). No tocar
  `sysctl iogpu.wired_limit_mb`.
