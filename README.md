# Fuente Primaria

Sistema local de producción de carruseles y vídeos. Genera sus propias imágenes
con SDXL, compone tipografía editorial con Chromium, monta vídeo con ffmpeg y
publica todo en un portal navegable. **Nada sale de la máquina.**

44 módulos de Python, 7.632 líneas. Sin servicios externos en el camino de
producción.

---

## Qué produce

| Salida | Formato |
|---|---|
| Reel vertical | 1080×1920, con o sin audio |
| Vídeo apaisado | 1920×1080 |
| Carrusel PDF | 6-7 páginas verticales |
| Láminas sueltas | PNG con texto |
| Fondos | PNG sin texto, reutilizables |
| ZIP | las láminas empaquetadas |

Y a partir de tres entradas distintas: un **guion escrito**, un **audio** (se
transcribe y se trocea solo) o un **tema**.

---

## Cómo se pide

Dos ficheros y una regla.

```
voz/<nombre>.yaml      la identidad — se elige UNA VEZ y se hereda
pedidos/<slug>.yaml    la pieza — solo declara en qué se desvía
```

El criterio de reparto: **si cambiarlo hace que la pieza deje de parecer nuestra,
es voz; si solo hace que sea otra pieza, es pedido.** Que haya que elegir el
color de acento en cada vídeo no es una funcionalidad: es un fallo de producto.

Un pedido de ejemplo:

```yaml
contrato: 1
voz: fuente-primaria

pieza:
  id: com-silencio
  titulo: Cuatro segundos

entrada:
  tipo: guion
  laminas:
    - titular: Cuatro segundos que nadie nota.
      escena: a vast snow field at dawn with no tracks at all

salidas:
  - {tipo: carrusel_pdf, lienzo: reel-9-16}
  - {tipo: reel, lienzo: reel-9-16, montaje: texto-vivo}
```

`contrato.resolver()` sustituye cada `auto` por un valor concreto y `huella()`
lo resume en 16 caracteres: **misma huella, mismo resultado**. Cada entrega deja
un `pedido-efectivo.yaml` con lo que realmente se ejecutó.

También se puede editar visualmente: `sitio/estudio.html` enseña las paletas por
su franja de color en vez de por su nombre, y calcula en vivo lo que saldrá.

---

## Puesta en marcha

**macOS (Apple Silicon)** — es donde está desarrollado. Ver `COMANDOS.md`.

**Windows** — funciona, y la generación va más rápido con NVIDIA, pero hay tres
piezas que sustituir. Está todo medido en **[`INSTALAR-EN-WINDOWS.md`](INSTALAR-EN-WINDOWS.md)**.

En los dos casos hacen falta tres modelos que **no vienen en el repositorio**
porque pesan 7,3 GB:

| Fichero | Peso | Carpeta |
|---|---|---|
| `juggernautXL_v9.safetensors` | 6,62 GB | `comfy/models/checkpoints/` |
| `sdxl_lightning_8step_lora.safetensors` | 0,37 GB | `comfy/models/loras/` |
| `sdxl_vae_fp16fix.safetensors` | 0,31 GB | `comfy/models/vae/` |

Su configuración exacta —pasos, CFG, muestreador, semilla— está en
`voz/fuente-primaria.yaml`. No hay que adivinar nada.

---

## Antes de dar nada por terminado

```bash
python herramientas/prueba_sistema.py
```

17 comprobaciones en cuatro segundos: ComfyUI vivo y sin degradar, los vetos del
negativo, las paletas y sus ejes tipográficos, la composición con Chromium, el
carrusel PDF, la transcripción, el troceo, el ritmo del audio, los montadores en
los dos formatos, el catálogo sin enlaces rotos, el guardián que impide borrar
trabajo, el contrato reproducible, y que **ningún archivo entregable exista sin
aparecer en el portal**.

Cada una nació de un fallo real. La última existe porque 17 vídeos vivieron en
disco sin que nadie los viera.

---

## Reglas duras

No son estilo. Cada una viene de algo que ya se pagó.

1. **Ningún dato sin verificar en fuente primaria.** Si la cita no aguanta, se
   cambia el tema o se publica el desmentido —que suele ser mejor gancho.
2. **Cero caras y cero manos.** SDXL falla ahí de forma estructural. Siluetas
   lejanas, de espaldas, a contraluz. Negativo con pesos: `(face:1.6)
   (hands:1.6) (fingers:1.6)`.
3. **Auditar cada imagen** antes de montar. Se regenera la imagen, no el lote.
4. **Verificar en pantalla** antes de decir que algo está listo. Renderizar con
   Chromium y mirar la captura. Nunca dar por bueno porque el script terminó sin
   error.
5. **El portal se actualiza en el mismo turno** en que nace el archivo.
6. **No editar módulos de un proceso vivo.** Python los carga al arrancar.

---

## Estructura

```
herramientas/     44 módulos: generación, composición, montaje, catálogo
voz/              identidades de marca
pedidos/          los encargos
out/              material de trabajo por proyecto
sitio/            el portal y el estudio (HTML estático)
fuentes/          tipografías OFL y música CC-BY
workflows/        el flujo de ComfyUI
pruebas/          el banco de transcripción con su verdad conocida
```

Piezas centrales:

| Módulo | Qué hace |
|---|---|
| `contrato.py` | resuelve un pedido y garantiza que sea reproducible |
| `lote.py` | construye el flujo de ComfyUI con sus vetos |
| `paletas.py` | 16 paletas con veto, 10 ánimos, sorteo estable por tema |
| `disposiciones.py` | 10 maquetaciones de lámina en tres familias |
| `estudio2.py` | composición tipográfica con Chromium |
| `reel3.py` · `montar_flujo.py` | montaje de vídeo |
| `transcribir.py` · `bloques.py` | audio a bloques con marcas por palabra |
| `guardian.py` | vigila el ritmo y reinicia si se degrada |
| `catalogo.py` | construye el portal, con guardianes contra el borrado |
| `recetario.py` | recupera de cada PNG su receta completa |
| `prueba_sistema.py` | las 17 comprobaciones |

---

## Dos cosas medidas que conviene saber

**El color va por veto, no por instrucción.** A CFG 1.0 —que impone el LoRA
Lightning— el modelo casi no obedece una orden de color en positivo: de ocho
paletas probadas, cinco caían en la franja azul-cian porque mandaba la escena.
Metiendo los colores rivales en el **negativo**, la mostaza pasó de 156° (verde)
a 36° (ámbar) y su saturación de 10,7 a 42,5.

**El ritmo de un vídeo lo lleva el texto, no los cortes.** Medido: el subtítulo
palabra a palabra genera 150-210 cambios visuales por minuto, contra unos 40 de
todos los efectos juntos. Y con imágenes fijas **nunca se corta dentro de una
imagen**: el ojo ve los mismos píxeles reescalados y lo lee como un fallo de
reproducción.
