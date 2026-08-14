# 🎬 TikTok & Shorts AI Autonomous Broadcast Studio (v5.5)

Un estudio autónomo de producción audiovisual multiplataforma diseñado para generar videos virales en formato **9:16 (4K Ultra HD y 1080p)** para **TikTok, YouTube Shorts e Instagram Reels**. 

Combina investigación científica estructurada, control de calidad visual con **IA de Visión Multimodal**, subtítulos cinemáticos dinámicos (estilo MrBeast) y una **arquitectura distribuida** que permite delegar el cómputo pesado a servidores GPU dedicados (**NVIDIA RTX 5090 / 4090 / Servidores Cloud**) mediante redes VPN seguras (Tailscale).

---

## 📑 Tabla de Contenidos
- [🌟 Características Principales](#-características-principales)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [🌐 Modos de Despliegue](#-modos-de-despliegue)
- [🛠️ Tutorial 1: Configuración del Servidor GPU Remoto](#️-tutorial-1-configuración-del-servidor-gpu-remoto)
- [💻 Tutorial 2: Configuración de la Máquina Cliente (macOS / Linux / Windows)](#-tutorial-2-configuración-de-la-máquina-cliente-macos--linux--windows)
- [⚙️ Guía de Personalización (`config.yaml`)](#️-guía-de-personalización-configyaml)
- [🧠 Flujo de Producción Paso a Paso](#-flujo-de-producción-paso-a-paso)
- [🔧 Solución de Problemas Comunes (Troubleshooting)](#-solución-de-problemas-comunes-troubleshooting)

---

## 🌟 Características Principales

- 📡 **Radar de Tendencias Global (5 Pilares):** Rastreo continuo de noticias en tiempo real sobre Inteligencia Artificial, Ciencia Espacial (NASA/James Webb), Hardware y Superchips, Misterios Científicos y Startups Tech en Google News y 15+ feeds RSS internacionales.
- 📈 **Algoritmo de Virality Potential Score (0-100):** Filtra y clasifica automáticamente los temas con mayor probabilidad de retención, debate y viralidad en audiencias hispanohablantes.
- 🔬 **Investigación Técnica Estructurada (`investigacion.py`):** Antes de redactar el guion, el sistema compila una ficha técnica con resumen, datos numéricos verificables en USD, glosario y mapa de conceptos visuales.
- 🎙️ **Masterización de Audio Broadcast:** Voz neural hiper-expresiva (`es-US-AlonsoNeural`), ecualización dinámica, compresión multibanda, normalización EBU R128 (-14 LUFS) y efectos SFX (*Whoosh & Pop*) en puntos de impacto.
- 💥 **Subtítulos Virales Inteligentes (Estilo MrBeast / Hormozi):** Renderizado en alta definición con tipografía *Impact / Arial Black*, resaltado dinámico de palabras clave en **Amarillo Neón (`#FFE600`)** y **Cian Eléctrico**, con contorno 3D negro para legibilidad sobre cualquier fondo.
- 🎥 **Motor Híbrido de Video e Imágenes:**
  - Síntesis de videoclips por IA mediante **ComfyUI API** en GPU remota.
  - Descargador multi-fuente open source (*Pixabay, Pexels, Wikimedia Commons*).
  - Generación de imágenes 8K fotorrealistas con **Pollinations Flux** y movimiento dinámico **Ken Burns** en 4K.
- 🧠 **Control de Calidad (QA) con IA de Visión (`qa_review.py`):** Inspección visual previa con modelos multimodales (`minicpm-v`). Descarta cualquier fotograma con concordancia temática inferior al 75%.
- 📓 **Gestión Editorial Automatizada en Obsidian:** Programación automática de tandas de videos en slots estratégicos (Mañana 08:30 AM, Tarde 02:30 PM, Noche 08:30 PM) con títulos optimizados, descripciones y hashtags.
- 🧹 **Saneamiento Automático:** Purga inteligente de archivos de trabajo temporales para mantener el almacenamiento siempre limpio.

---

## 🏗️ Arquitectura del Sistema

```text
       [ MÁQUINA CLIENTE (Cualquier SO) ]
        macOS / Ubuntu / Linux / Windows
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
 [ trends.py ]                [ pipeline.py ]
  Radar 5 Pilares              Orquestador Central
       │                               │
       │ (Tailscale VPN Encriptada)    │ (Tailscale VPN Encriptada)
       ▼                               ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            [ NODO SERVIDOR GPU DEDICADO ]                   │
 │       (NVIDIA RTX 5090 / 4090 / A100 / Servidor LAN)        │
 │                                                             │
 │  🧠 Ollama Server (:11434)  ➔ Qwen 3.6 35B / Llama 3.3 70B │
 │  🎬 ComfyUI API (:8188)     ➔ LTX-Video / Hunyuan / Flux   │
 └─────────────────────────────────────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   PRODUCCIÓN FINAL Y RENDER   │
       │   - FFmpeg 4K Ultra HD        │
       │   - Subtítulos Pillow Neón    │
       │   - Audio EBU R128 Masterizado│
       │   - Sincronización Obsidian   │
       └───────────────────────────────┘
```

---

## 🌐 Modos de Despliegue

| Modo | Descripción | Requisitos |
|---|---|---|
| 🚀 **1. Distribuido GPU Remota (Recomendado)** | La máquina cliente ejecuta la orquestación y delega el cómputo de IA (LLM 35B + ComfyUI Video) a una PC con GPU NVIDIA a través de Tailscale VPN. | Laptop o PC + Servidor GPU con NVIDIA RTX |
| 💻 **2. Local All-in-One** | Todo el flujo corre en la misma máquina local usando Ollama local (`qwen2.5:14b` / `qwen3:8b`) y stock multi-fuente. | Apple Silicon (M1/M2/M3/M4) o PC con GPU local |
| ☁️ **3. Nube / API Serverless** | Utiliza APIs en la nube para el razonamiento (NVIDIA NIM API gratuita con `llama-3.1-70b` o OpenAI). | Conexión a internet básica |

---

## 🛠️ Tutorial 1: Configuración del Servidor GPU Remoto

Este tutorial permite transformar cualquier PC con tarjeta gráfica NVIDIA (ej. RTX 5090, 4090, 3090) en un super-servidor de IA accesible desde cualquier parte del mundo.

### Paso 1: Conectar el Servidor a la Red Tailscale
1. Descarga e instala [Tailscale](https://tailscale.com/download) en el servidor.
2. Inicia sesión para unir el servidor a tu red privada.
3. Copia la IP de Tailscale asignada (ejemplo: `100.95.107.65`).

### Paso 2: Configurar Ollama (Cerebro LLM 35B)
1. Instala [Ollama](https://ollama.com).
2. Configura Ollama para escuchar en todas las interfaces de red:
   - **En Windows (CMD como Administrador):**
     ```cmd
     setx OLLAMA_HOST "0.0.0.0:11434"
     ```
   - **En Linux:**
     ```bash
     sudo systemctl edit ollama.service
     # Añadir: Environment="OLLAMA_HOST=0.0.0.0:11434"
     sudo systemctl restart ollama
     ```
3. Descarga el modelo de razonamiento de alta capacidad:
   ```bash
   ollama pull qwen3.6:35b
   ```

### Paso 3: Configurar ComfyUI (Generador de Video IA)
1. Descarga la versión portable oficial: [ComfyUI Windows Portable NVIDIA](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z).
2. Descomprime la carpeta `ComfyUI_windows_portable`.
3. Edita el archivo `run_nvidia_gpu.bat` para añadir los parámetros de red:
   ```bat
   .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --listen 0.0.0.0 --port 8188 --highvram
   pause
   ```
4. Ejecuta `run_nvidia_gpu.bat` y déjalo abierto.

### Paso 4: Habilitar Puertos en el Firewall
- **En Windows (PowerShell Administrador):**
  ```powershell
  netsh advfirewall firewall add rule name="Ollama 11434" dir=in action=allow protocol=TCP localport=11434
  netsh advfirewall firewall add rule name="ComfyUI 8188" dir=in action=allow protocol=TCP localport=8188
  ```
- **En Linux (UFW):**
  ```bash
  sudo ufw allow 11434/tcp
  sudo ufw allow 8188/tcp
  ```

---

## 💻 Tutorial 2: Configuración de la Máquina Cliente

La máquina cliente es donde ejecutas el generador (puede ser cualquier laptop o desktop con macOS, Linux o Windows).

### 1. Clonar el Repositorio
```bash
git clone https://github.com/ByCarlox/tiktok-ai-video-generator.git
cd tiktok-ai-video-generator
```

### 2. Instalar FFmpeg
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install -y ffmpeg`
- **Arch Linux:** `sudo pacman -S ffmpeg`
- **Windows:** `winget install Gyan.FFmpeg`

### 3. Crear Entorno Virtual e Instalar Dependencias
```bash
python3 -m venv .venv

# En macOS / Linux:
source .venv/bin/activate

# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 4. Ejecutar la Producción
```bash
python pipeline.py
```

---

## ⚙️ Guía de Personalización (`config.yaml`)

El archivo `config.yaml` permite personalizar todo el comportamiento del estudio:

```yaml
# Idioma y geolocalización de audiencia
idioma_tendencia: "es-419"       # Español neutro panlatino
pais_tendencia: [MX, AR, CO, CL, PE]

# Producción
numero_videos: 3                 # Cantidad de videos a producir por tanda
resolucion: "4k"                 # "4k" (2160x3840) o "1080p" (1080x1920)
calidad_crf: 14                  # 14 = Ultra alta fidelidad visual sin artefactos
voz: "es-US-AlonsoNeural"        # Voz principal

# Configuración de Servidor Remoto
ia:
  proveedor: "ollama_remote"     # ollama_remote | ollama | nvidia | openai
  host_remoto: "http://100.95.107.65:11434"
  modelo: "qwen3.6:35b"

video_ia:
  proveedor: "comfyui_remote"    # comfyui_remote | stock_multi_fuente
  host_remoto: "http://100.95.107.65:8188"
  modelo: "ltx_video"

# Bóveda editorial
obsidian_vault: "TikTok-AI-Passive"
salida_videos: "output/videos"
```

---

## 🧠 Flujo de Producción Paso a Paso

1. **[0/10] Detección de Tendencia:** El radar consulta los 5 pilares RSS y Google News; clasifica por *Virality Score*.
2. **[1/10] Ficha Técnica de Investigación:** El modelo 35B en la GPU remota sintetiza datos verificables y mapa visual.
3. **[2/10] Redacción de Guion:** Creación de guion narrativo estructurado en 3 actos con gancho inicial en menos de 5 palabras.
4. **[3/10] Tarjeta de Hook:** Renderizado de portada con alto impacto visual.
5. **[4/10] Locución y Masterización:** Síntesis neural con ecualización de voz y mezcla de efectos sonoros (SFX).
6. **[5/10] Pistas Musicales:** Selección y ducking automático de música de fondo libre de derechos.
7. **[6/10] Subtitulado Rápido:** Transcripción precisa con Whisper e identificación de palabras clave.
8. **[7/10] Generación y QA Visual:** Petición a ComfyUI / Stock 4K / Pollinations Flux con inspección multimodal `minicpm-v` (>= 75% concordancia).
9. **[8/10] Montaje y Render 4K:** Renderizado FFmpeg con subtítulos quemados en amarillo neón y movimiento Ken Burns.
10. **[9/10] Sincronización y Limpieza:** Creación de ficha de publicación en Obsidian y saneamiento de archivos temporales.

---

## 🔧 Solución de Problemas Comunes (Troubleshooting)

### 1. "Servidor ComfyUI ausente. Usando descargas multi-fuente..."
- **Causa:** La ventana de `run_nvidia_gpu.bat` en la PC remota está cerrada o el puerto 8188 está bloqueado por el firewall.
- **Solución:** Ejecuta `netsh advfirewall firewall add rule name="ComfyUI 8188" dir=in action=allow protocol=TCP localport=8188` en el servidor y asegúrate de iniciar ComfyUI con `--listen 0.0.0.0`.

### 2. "Conexión con Ollama remoto falló. Conmutando a Ollama local..."
- **Comportamiento normal de resiliencia:** Si la máquina de tu servidor se apaga o pierde conexión a Tailscale, el pipeline conmuta automáticamente a tu Ollama local sin interrumpir la producción.

### 3. Subtítulos no encuentran la fuente Impact
- El sistema utiliza fuentes nativas del sistema operativo (`Impact`, `Arial Black` o `Arial Bold`). Si estás en Linux y deseas instalarlas: `sudo apt install ttf-mscorefonts-installer`.

---

## 🛡️ Licencia
Distribuido bajo licencia **MIT**. Diseñado para creadores de contenido, divulgadores de ciencia y desarrolladores de automatizaciones multimedia de alta calidad.
