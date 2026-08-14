# 🎬 TikTok & Shorts AI Autonomous Studio (v8.0 Flagship Suite)

Un estudio autónomo de producción audiovisual diseñado para crear videos virales en formato vertical **9:16 (4K Ultra HD y 1080p)** para **TikTok, YouTube Shorts e Instagram Reels**.

Cuenta con una **arquitectura distribuida** que delega el cómputo masivo de IA a servidores GPU dedicados (**NVIDIA RTX 5090 / 32 GB VRAM**) vía VPN privada (Tailscale), con **presentadora virtual Kawaii VTuber animada por IA**, **motor de video SOTA Wan 2.1 (Alibaba 14B DiT)**, **Cerebro Central Autónomo en Obsidian con memoria anti-duplicación**, **tarjetas 3D Glassmorphism** y **renderizado 4K a 40 Mbps**.

---

## 📑 Tabla de Contenidos
- [✨ Comparativa de Ediciones (PRO vs Lite)](#-comparativa-de-ediciones-pro-vs-lite)
- [🌸 Características Principales v8.0](#-características-principales-v80)
- [🧠 Cerebro Central y Memoria en Obsidian](#-cerebro-central-y-memoria-en-obsidian)
- [⚡ Inicio Rápido: Edición Lite (Bajos Recursos)](#-inicio-rápido-edición-lite-bajos-recursos)
- [🚀 Inicio Rápido: Edición Broadcast Studio PRO (RTX 5090)](#-inicio-rápido-edición-broadcast-studio-pro-rtx-5090)
- [🛠️ Instalador Automático Wan 2.1 en la GPU (PowerShell)](#️-instalador-automático-wan-21-en-la-gpu-powershell)
- [📂 Estructura del Repositorio](#-estructura-del-repositorio)
- [⚙️ Guía de Configuración](#️-guía-de-configuración)

---

## ✨ Comparativa de Ediciones (PRO vs Lite)

| Característica | ⚡ Edición Lite (`pipeline_lite.py`) | 🚀 Edición Broadcast PRO (`pipeline.py`) |
|---|---|---|
| **Requisitos de Hardware** | Cualquier PC / Laptop con CPU (4GB+ RAM) | Laptop/PC + Servidor GPU (**RTX 5090 / 4090**) |
| **Cerebro LLM** | Ollama local ligero (`qwen2.5:7b` / `llama3.2`) o NVIDIA NIM | **Qwen 3.6 35B** en GPU remota vía Tailscale |
| **Presentadora Virtual** | Desactivado (Rápido y ligero) | **Nova (Kawaii VTuber) con animación por video IA & PIP continuo** |
| **Motor de Video IA** | Stock B-Roll dinámico | **Wan 2.1 (Alibaba 14B DiT) / ComfyUI en RTX 5090** |
| **Memoria Anti-Duplicación** | Básico | **Obsidian Neural Brain (Deduplicación semántica & Dataview)** |
| **Fotos Reales de Producto** | ✅ Sí (Wikipedia / Wikimedia) | ✅ Sí (Wikipedia + Hero Assets 3D 8K) |
| **Tarjetas 3D Glassmorphism** | Modo básico 2D | **Cristal esmerilado con aura neón y levitación 3D** |
| **Motion Graphics** | Subtítulos virales MrBeast | **Onda de audio reactiva + Subtítulos sincronizados al milisegundo** |
| **Resolución & Bitrate** | 1080p Full HD (Render rápido CPU) | **4K Ultra HD a 40 Mbps (CRF 13)** |
| **Comando de Ejecución** | `python pipeline_lite.py` | `python pipeline.py` |

---

## 🌸 Características Principales v8.0

- 🎀 **Presentadora Virtual Kawaii VTuber ("Nova"):** 
  - **Identidad Fija:** Modelo oficial recortado con Chroma Key en [`assets/avatar/waifu_master_cutout.png`](assets/avatar/waifu_master_cutout.png).
  - **Voz Neural:** `es-MX-DaliaNeural` (dulce, juvenil, enérgica y altamente expresiva).
  - **Intro a Pantalla Completa (0 - 3.5s):** Apertura en set de estudio anime con partículas sakura.
  - **Badge de Esquina PIP Animado Continuo:** Insignia circular con anillo de neón rosa `♥ AI WAIFU` que reproduce video dinámico con canal alfa durante todo el video.
- 👑 **Motor de Video SOTA Wan 2.1 (Alibaba 14B DiT):** Integración nativa con ComfyUI en la RTX 5090 para sintetizar secuencias de video cinemáticas 9:16 a 24/30 FPS reales con física de cámara y movimiento 3D.
- 💎 **Tarjetas 3D Glassmorphism (`product_3d.py`):** Recorte automático de gadgets, microchips, naves y hardware, montados sobre paneles flotantes de cristal esmerilado con aura cian y levitación senoidal (`v_product_3d.mp4`).
- ⏱️ **Sincronización Labial y Subtítulos Milimétricos:** Línea de tiempo monótona estricta ($\sum \Delta t = \text{duración audio}$) que erradica por completo cualquier retraso o desfase acumulativo.
- ⚡ **Ondas de Audio Reactivas (`compositor.py`):** Visualizador de audio neón que pulsa en tiempo real al ritmo de la voz.
- 📸 **Extractor de Hero Assets y Fotos Reales (`product_fetcher.py`):** Consulta Wikipedia/Wikimedia o sintetiza Hero Assets 3D aislados en 8K si no existen fotos públicas.

---

## 🧠 Cerebro Central y Memoria en Obsidian

El proyecto cuenta con un sistema de **Segundo Cerebro Autónomo** dentro de [`TikTok-AI-Passive/`](TikTok-AI-Passive):

```text
TikTok-AI-Passive/
├── 00_Brain_Center/
│   ├── 🧠_CENTRAL_DASHBOARD.md      # Panel interactivo con tablas dinámicas Dataview
│   └── 🧬_PROYECTO_LORE.md          # Identidad, tono y lore de Nova (Kawaii VTuber)
├── 01_Memory_Vault/
│   ├── Topics_Memory/               # Índice JSON + Fichas de cada tema tratado
│   ├── Winning_Hooks/               # Fórmulas de ganchos virales probadas
│   └── Character_Profile/           # Reglas de animación, voz y visemas
├── 02_Production_Logs/
│   ├── Scripts_Archive/             # Notas automáticas de cada guión con metadatos YAML
│   └── Published_Videos/            # Registro de videos listos para subir
└── 04_Knowledge_Base/
    └── Tech_Research/               # Papers científicos y fuentes investigadas
```

- **Filtro Anti-Duplicación:** Antes de generar guiones, [`trends.py`](trends.py) y [`pipeline.py`](pipeline.py) consultan el índice de Obsidian para descartar automáticamente temas repetidos o con similitud $> 45\%$.
- **Notas de Producción Atómicas:** Cada video renderizado genera automáticamente una nota con enlaces bidireccionales `[[Tema]]`, hashtags, score de QA y métricas para Dataview.

---

## ⚡ Inicio Rápido: Edición Lite (Bajos Recursos)

Para generar videos de inmediato en cualquier computadora sin necesidad de servidores ni GPU externa:

```bash
# 1. Clonar el repositorio
git clone https://github.com/ByCarlox/tiktok-ai-video-generator.git
cd tiktok-ai-video-generator

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Ejecutar la Edición Lite
python pipeline_lite.py
```

---

## 🚀 Inicio Rápido: Edición Broadcast Studio PRO (RTX 5090)

Aprovecha el poder masivo de tu **NVIDIA RTX 5090** para renderizar videos con Wan 2.1, Qwen 35B y la presentadora virtual:

```bash
# Ejecutar el pipeline completo
python pipeline.py
```

---

## 🛠️ Instalador Automático Wan 2.1 en la GPU (PowerShell)

En tu PC con la **RTX 5090**, abre **PowerShell** y ejecuta este comando de una sola línea para instalar **Wan 2.1 (14B)** en ComfyUI automáticamente:

```powershell
irm https://raw.githubusercontent.com/ByCarlox/tiktok-ai-video-generator/main/install_wan21_rtx5090.ps1 | iex
```

El script descargará e instalará automáticamente:
- `ComfyUI-WanVideoWrapper`
- Pesos oficiales `Wan2_1_T2V_14B_fp8_e4m3fn.safetensors`
- `umt5_xxl_fp8_e4m3fn.safetensors` y `Wan2_1_VAE_bf16.safetensors`

---

## 📂 Estructura del Repositorio

- [`pipeline.py`](pipeline.py): Orquestador maestro de la Suite Flagship Broadcast.
- [`pipeline_lite.py`](pipeline_lite.py): Versión ligera y autónoma para PCs de bajos recursos.
- [`avatar_host.py`](avatar_host.py): Motor de presentadora virtual y generador de badges de video PIP.
- [`vtuber_engine.py`](vtuber_engine.py): Motor de animación 2D/3D con visemas anatómicos y físicas a 30 FPS.
- [`obsidian_brain.py`](obsidian_brain.py): Cerebro de memoria persistente y motor anti-duplicación.
- [`media_fetcher.py`](media_fetcher.py): Descarga y sintetizador de video Wan 2.1 en GPU remota.
- [`product_3d.py`](product_3d.py): Generador de tarjetas 3D Glassmorphism y levitación senoidal.
- [`product_fetcher.py`](product_fetcher.py): Extractor de fotos oficiales de Wikipedia y Hero Assets 3D.
- [`qa_review.py`](qa_review.py): Agente de control de calidad autónomo.
- [`compositor.py`](compositor.py): Motor anti-stretch y generador de ondas reactivas neón.
- [`trends.py`](trends.py): Radar de tendencias y noticias con cálculo de Virality Score.
- [`investigacion.py`](investigacion.py): Compilación de datos cuantitativos y contexto técnico.
- [`config.yaml`](config.yaml): Configuración general del estudio.
- [`config.local.yaml`](config.local.yaml): Configuración privada local (ignorado por Git).

---

## ⚙️ Guía de Configuración

En [`config.yaml`](config.yaml) puedes personalizar:
- **`voz`:** `es-MX-DaliaNeural` (VTuber Kawaii), `es-CO-SalomeNeural`, `es-US-AlonsoNeural`.
- **`avatar_presentador`:** `activado: true`, `estilo: "kawaii_waifu"`.
- **`video_ia`:** `modelo: "wan2.1"`, `resolucion_video: "720x1280"`.
- **`resolucion`:** `"4k"` (2160x3840) o `"1080p"` (1080x1920).
- **`numero_videos`:** Cantidad de videos a producir por corrida.
