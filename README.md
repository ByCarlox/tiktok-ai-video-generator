# 🎬 TikTok & Shorts AI Autonomous Studio (v7.0 Ultimate Suite)

Un estudio autónomo multiplataforma de producción audiovisual diseñado para crear videos virales en formato vertical **9:16 (4K Ultra HD y 1080p)** para **TikTok, YouTube Shorts e Instagram Reels**.

Cuenta con una **arquitectura distribuida** que delega el cómputo masivo de IA a servidores GPU dedicados (**NVIDIA RTX 5090 / 32 GB VRAM**) vía VPN privada (Tailscale), con **presentador virtual con sincronización labial (Lip-Sync)**, **recorte y tarjetas 3D Glassmorphism para productos reales**, **formas de onda reactivas** y **render 4K a 40 Mbps**.

---

## 📑 Tabla de Contenidos
- [✨ Comparativa de Ediciones (PRO vs Lite)](#-comparativa-de-ediciones-pro-vs-lite)
- [🌟 Características de la Suite Broadcast v7.0](#-características-de-la-suite-broadcast-v70)
- [⚡ Inicio Rápido: Edición Lite (Bajos Recursos)](#-inicio-rápido-edición-lite-bajos-recursos)
- [🚀 Inicio Rápido: Edición Broadcast Studio PRO (RTX 5090)](#-inicio-rápido-edición-broadcast-studio-pro-rtx-5090)
- [🛠️ Tutorial: Conectar Servidor Remoto GPU (Tailscale VPN)](#️-tutorial-conectar-servidor-remoto-gpu-tailscale-vpn)
- [📂 Estructura Modular del Proyecto](#-estructura-modular-del-proyecto)
- [⚙️ Guía de Configuración Central](#️-guía-de-configuración-central)
- [🔧 Solución de Problemas Comunes](#-solución-de-problemas-comunes)

---

## ✨ Comparativa de Ediciones (PRO vs Lite)

| Característica | ⚡ Edición Lite (`pipeline_lite.py`) | 🚀 Edición Broadcast PRO (`pipeline.py`) |
|---|---|---|
| **Requisitos de Hardware** | Cualquier PC / Laptop con CPU (4GB+ RAM) | Laptop/PC + Servidor GPU (**RTX 5090 / 4090**) |
| **Cerebro LLM** | Ollama local ligero (`qwen2.5:7b` / `llama3.2`) o NVIDIA NIM | **Qwen 3.6 35B** en GPU remota vía VPN |
| **Presentador Virtual** | Desactivado (Rápido y ligero) | **Cyber Tech Host con Sincronización Labial (Lip-Sync)** |
| **Fotos Reales de Producto** | ✅ Sí (Wikipedia / Wikimedia) | ✅ Sí (Wikipedia / Wikimedia en 4K) |
| **Tarjetas 3D Glassmorphism** | Modo básico 2D | **Cristal esmerilado con aura neón y levitación 3D** |
| **Motion Graphics** | Subtítulos virales MrBeast | **Onda de audio reactiva + Subtítulos con rebote cinético** |
| **Resolución & Bitrate** | 1080p Full HD (Render rápido CPU) | **4K Ultra HD a 40 Mbps (CRF 13)** |
| **Comando de Ejecución** | `python pipeline_lite.py` | `python pipeline.py` |

---

## 🌟 Características de la Suite Broadcast v7.0

- 🗣️ **Presentador Virtual con Lip-Sync (`lip_sync.py`):** Analiza la energía RMS del audio para animar la gesticulación del presentador, las micro-inclinaciones de cabeza y el brillo holográfico de datos en el visor cibernético en perfecta sincronía con la voz.
- 💎 **Tarjetas 3D Glassmorphism (`product_3d.py`):** Aísla productos reales (gadgets, microchips, naves, hardware) y los monta sobre paneles flotantes de cristal esmerilado con borde cian brillante y sombras de contacto 3D.
- ⚡ **Ondas de Audio Reactivas (`compositor.py`):** Visualizador dinámico de 28 barras con gradiente Neón Cian / Amarillo Neón que late al compás de la voz y la música.
- 📸 **Extractor de Fotos Reales de Producto (`product_fetcher.py`):** Descarga fotografías verídicas de alta resolución y notas de prensa oficiales desde Wikipedia y Wikimedia Commons.
- 🖼️ **Compositor Anti-Stretch (`compositor.py`):** Encuadre inteligente para fotos 16:9, 4:3 o 1:1 con fondo desenfocado cinemático (`sigma=35`) y el producto al centro sin distorsión.
- 📡 **Radar de 5 Pilares de Tendencias Globales (`trends.py`):** Rastreo continuo de noticias en tiempo real con algoritmo de *Virality Score (0-100)*.
- 🔬 **Investigación Científica Previa (`investigacion.py`):** Compilación previa de datos duros cuantitativos en USD antes de generar guiones.
- 💥 **Subtítulos Dinámicos MrBeast / Hormozi:** Palabras clave resaltadas en Amarillo Neón (`#FFE600`) y Cian con contorno 3D negro.
- 🎙️ **Audio Broadcast Masterizado:** Voz neural `es-US-AlonsoNeural`, ecualización, compresor y efectos SFX (*Whoosh & Pop*).
- 📓 **Gestión Editorial en Obsidian:** Programación automática de 3 episodios al día (Mañana, Tarde y Noche).

---

## ⚡ Inicio Rápido: Edición Lite (Bajos Recursos)

Para generar videos virales inmediatamente en cualquier ordenador sin configurar servidores ni VPNs:

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

## 🚀 Inicio Rápido: Edición Broadcast Studio PRO (Flagship)

Aprovecha el poder masivo de una **NVIDIA RTX 5090** para renderizar modelos de 35B y presentadores virtuales con calidad televisiva:

```bash
# 1. Asegúrate de tener Tailscale conectado al servidor GPU
# 2. Ejecutar la Suite Flagship
python pipeline.py
```

---

## 🛠️ Tutorial: Conectar Servidor Remoto GPU (Tailscale VPN)

### En la PC Servidor (Windows con GPU NVIDIA RTX):
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
Crea un archivo local `config.local.yaml` (ignorado por Git para proteger tu privacidad) con la IP de tu servidor:
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

## 📂 Estructura Modular del Proyecto

```text
├── pipeline.py          # Orquestador Flagship Broadcast Pro 4K (40 Mbps)
├── pipeline_lite.py     # Orquestador Lite 1080p para PCs de bajos recursos
├── product_3d.py        # Tarjetas 3D Glassmorphism y animación de levitación
├── lip_sync.py          # Sincronización labial y visor reactivo del presentador
├── product_fetcher.py   # Extractor de fotos reales en Wikipedia / Wikimedia
├── compositor.py        # Compositor Anti-Stretch y ondas de audio reactivas
├── avatar_host.py       # Generador de Cyber Host Faceless en RTX 5090
├── trends.py            # Radar de 5 pilares RSS y algoritmo de Virality Score
├── investigacion.py     # Ficha técnica estructurada previa a guion
├── ia_client.py         # Cliente LLM con soporte de razonamiento (Qwen 35B)
├── media_fetcher.py     # Motor híbrido de video (ComfyUI API + Stock Multi-Fuente)
├── qa_review.py         # Inspector de control de calidad visual con IA de Visión
├── metadata.py          # Generador de metadatos SEO y programador en Obsidian
├── musica.py            # Selector inteligente de pistas de música libre
├── config.yaml          # Configuración principal de la suite
├── config.lite.yaml     # Configuración para edición ligera
└── README.md            # Documentación completa de la suite v7.0
```

---

## 🛡️ Licencia
Distribuido bajo licencia **MIT**. Diseñado para creadores de contenido, divulgadores de ciencia y desarrolladores de automatizaciones multimedia de alta calidad.
