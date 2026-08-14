# 🎬 TikTok & Shorts AI Autonomous Studio (v6.0)

Un estudio autónomo multiplataforma de producción audiovisual diseñado para crear videos virales en formato vertical **9:16 (4K Ultra HD y 1080p)** para **TikTok, YouTube Shorts e Instagram Reels**.

El proyecto incluye **dos versiones listas para usar**:
1. 🚀 **Edición Broadcast Studio PRO (Flagship):** Arquitectura distribuida para GPUs potentes (**NVIDIA RTX 5090 / 32 GB VRAM**) vía Tailscale VPN, con presentador virtual faceless, fotos reales de productos, compositor anti-stretch y render 4K ultra-bitrate (40 Mbps).
2. ⚡ **Edición Lite / Bajos Recursos (Plug-and-Play):** Versión 100% autónoma y ligera que corre en **cualquier laptop o PC estándar con CPU**, sin requerir GPU dedicada, VPN ni configuraciones complejas.

---

## 📑 Tabla de Contenidos
- [✨ Comparativa de Versiones](#-comparativa-de-versiones)
- [⚡ Inicio Rápido: Edición Lite (Bajos Recursos)](#-inicio-rápido-edición-lite-bajos-recursos)
- [🚀 Inicio Rápido: Edición Broadcast Studio PRO (RTX 5090)](#-inicio-rápido-edición-broadcast-studio-pro-rtx-5090)
- [🌟 Características Destacadas](#-características-destacadas)
- [🛠️ Tutorial: Conectar Servidor Remoto GPU (Tailscale VPN)](#️-tutorial-conectar-servidor-remoto-gpu-tailscale-vpn)
- [⚙️ Configuración (`config.yaml` vs `config.lite.yaml`)](#️-configuración-configyaml-vs-configliteyaml)
- [🔧 Solución de Problemas Comunes](#-solución-de-problemas-comunes)

---

## ✨ Comparativa de Versiones

| Característica | ⚡ Edición Lite (`pipeline_lite.py`) | 🚀 Edición Broadcast PRO (`pipeline.py`) |
|---|---|---|
| **Requisitos de Hardware** | Cualquier PC / Laptop con CPU (4GB+ RAM) | Laptop/PC + Servidor GPU (RTX 5090/4090) |
| **Cerebro LLM** | Ollama local ligero (`qwen2.5:7b` / `llama3.2`) o NVIDIA NIM | **Qwen 3.6 35B** en GPU remota vía VPN |
| **Presentador Virtual** | Desactivado (Rápido y ligero) | **Cyber Tech Host Faceless** generado por IA en GPU |
| **Fotos Reales de Producto** | ✅ Sí (Wikipedia / Wikimedia) | ✅ Sí (Wikipedia / Wikimedia en 4K) |
| **Compositor Anti-Stretch** | ✅ Sí (Fondo Blur + Sombra 3D) | ✅ Sí (Fondo Blur + Sombra 3D en 4K) |
| **Subtítulos Virales** | ✅ Estilo MrBeast (Amarillo Neón) | ✅ Estilo MrBeast (Amarillo Neón / Cian 3D) |
| **Resolución & Bitrate** | 1080p Full HD (Render rápido CPU) | **4K Ultra HD a 40 Mbps (CRF 13)** |
| **Comando de Ejecución** | `python pipeline_lite.py` | `python pipeline.py` |

---

## ⚡ Inicio Rápido: Edición Lite (Bajos Recursos)

Ideal si quieres generar videos virales inmediatamente en tu ordenador sin configurar servidores ni VPNs.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/ByCarlox/tiktok-ai-video-generator.git
cd tiktok-ai-video-generator
```

### 2. Instalar FFmpeg
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install -y ffmpeg`
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

### 4. Lanzar la Edición Lite
```bash
python pipeline_lite.py
```
*(El video final optimizado en 1080p se guardará en `output/videos/` junto con su archivo de metadatos SEO).*

---

## 🚀 Inicio Rápido: Edición Broadcast Studio PRO (Flagship)

Aprovecha el poder masivo de una **NVIDIA RTX 5090** (o 4090) para renderizar modelos de 35B y presentadores virtuales con calidad de televisión digital.

### 1. Requisitos
- Red privada **Tailscale VPN** conectando tu cliente y el servidor GPU.
- En el servidor: Ollama con `qwen3.6:35b` en puerto `11434` y ComfyUI Portable en puerto `8188`.

### 2. Ejecutar la Suite Flagship
```bash
python pipeline.py
```

---

## 🌟 Características Destacadas

- 📡 **Radar de 5 Pilares de Tendencias Globales (`trends.py`):** Rastreo en tiempo real de Inteligencia Artificial, Ciencia Espacial, Superchips y Hardware, Misterios Científicos y Startups Tech con algoritmo de *Virality Score (0-100)*.
- 🔬 **Investigación Científica Previa (`investigacion.py`):** Compilación de fichas técnicas con datos numéricos verificables en USD antes de generar guiones.
- 📸 **Extractor de Fotos Reales de Producto (`product_fetcher.py`):** Descarga fotos oficiales y verídicas de productos y gadgets de Wikipedia y Wikimedia Commons.
- 🖼️ **Compositor Anti-Stretch (`compositor.py`):** Encuadre inteligente para fotos 16:9, 4:3 o 1:1 con fondo desenfocado cinemático (`sigma=35`) y el producto al centro con bordes redondeados y sombra 3D flotante.
- 👤 **Presentador Virtual Faceless (`avatar_host.py`):** Síntesis de presentador tecnológico con visor cibernético holográfico para abrir los videos en los primeros 3.5 segundos.
- 💥 **Subtítulos Dinámicos MrBeast / Hormozi:** Renderizado en Pillow con resaltado en **Amarillo Neón (`#FFE600`)** y contorno 3D negro.
- 🎙️ **Audio Broadcast Masterizado:** Voz neural `es-US-AlonsoNeural`, ecualización, compresor y efectos SFX (*Whoosh & Pop*).
- 📓 **Gestión en Obsidian:** Programación automática de 3 episodios al día (Mañana, Tarde y Noche).

---

## 🛠️ Tutorial: Conectar Servidor Remoto GPU (Tailscale VPN)

### En la PC Servidor (Windows con GPU NVIDIA):
1. **Instalar Tailscale:** Descargar [Tailscale para Windows](https://tailscale.com/download/windows) e iniciar sesión.
2. **Iniciar Ollama en Red:**
   ```cmd
   setx OLLAMA_HOST "0.0.0.0:11434"
   ollama serve
   ollama pull qwen3.6:35b
   ```
3. **Iniciar ComfyUI Portable:**
   - Descargar [ComfyUI Windows Portable NVIDIA](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z).
   - Colocar el checkpoint base `v1-5-pruned-emaonly.safetensors` en `ComfyUI/models/checkpoints/`.
   - Editar `run_nvidia_gpu.bat` y asegurarse de incluir `--listen 0.0.0.0 --port 8188 --highvram`.
4. **Habilitar Puertos en Firewall:**
   ```powershell
   netsh advfirewall firewall add rule name="Ollama 11434" dir=in action=allow protocol=TCP localport=11434
   netsh advfirewall firewall add rule name="ComfyUI 8188" dir=in action=allow protocol=TCP localport=8188
   ```

### En tu Máquina Cliente:
Configura en `config.yaml` la IP de Tailscale de tu servidor:
```yaml
ia:
  proveedor: "ollama_remote"
  host_remoto: "http://100.95.107.65:11434"
  modelo: "qwen3.6:35b"

video_ia:
  proveedor: "comfyui_remote"
  host_remoto: "http://100.95.107.65:8188"
```

---

## ⚙️ Configuración (`config.yaml` vs `config.lite.yaml`)

- **`config.yaml`:** Configuración completa para la edición Broadcast PRO con 4K Ultra-Bitrate (40 Mbps), 3 videos diarios, presentador virtual y GPU remota.
- **`config.lite.yaml`:** Configuración ligera para la edición Lite en 1080p, optimizada para procesadores estándar sin GPU.

---

## 🔧 Solución de Problemas Comunes

1. **¿Qué versión debo usar?**
   - Si estás en una laptop sin GPU dedicada o quieres generar un video rápido sin conectar servidores externos, usa `python pipeline_lite.py`.
   - Si tienes tu servidor remoto con la RTX 5090 activo, usa `python pipeline.py`.
2. **Error al abrir clips de fondo:**
   - El sistema cuenta con resiliencia total: si un clip no se descarga a tiempo, conmuta automáticamente a las imágenes del producto con movimiento Ken Burns sin interrumpir la producción.

---

## 🛡️ Licencia
Distribuido bajo licencia **MIT**. Código abierto para creadores de contenido, divulgadores de tecnología y desarrolladores de automatizaciones multimedia de alta calidad.
