# 🎬 TikTok AI Autonomous Broadcast Studio (v5.0)

Un sistema autónomo de producción audiovisual en formato **9:16 (4K Ultra HD)** para TikTok, YouTube Shorts e Instagram Reels. Cuenta con investigación científica estructurada, control de calidad visual con **IA de Visión Multimodal**, subtítulos virales dinámicos (estilo MrBeast) y arquitectura híbrida compatible con **GPUs Remotas vía Tailscale VPN (RTX 5090 / 32GB VRAM)**.

---

## ⚡ Características Principales (Features v5.0)

- 📡 **Radar de Tendencias Global (5 Pilares):** Rastrea en tiempo real noticias de IA, Ciencia Espacial (James Webb/NASA), Hardware Extremo (RTX 5090/M4), Misterios Científicos y Startups Millonarias en USD mediante Google News LATAM y 15+ fuentes RSS mundiales.
- 📈 **Virality Potential Score (0-100):** Algoritmo propio que puntúa el potencial viral de cada noticia analizando disparadores de curiosidad, debate, impacto cuantitativo y urgencia.
- 🔬 **Investigación Científica Estructurada (`investigacion.py`):** Genera una ficha técnica previa antes de guionar (resumen técnico, 3 datos duros comprobables, terminología y mapa de conceptos visuales).
- 🎙️ **Narración Broadcast Masterizada:** Narración con voz neural hiper-expresiva (`es-US-AlonsoNeural`), ecualizada con filtro pasaaltos/pasabajos, compresión dinámica, normalización EBU R128 y efectos de sonido (SFX Whoosh/Pop).
- 💥 **Subtítulos Virales Dinámicos (Estilo MrBeast / Alex Hormozi):** Renderizado acelerado en Pillow con tipografía *Impact / Arial Black*, resaltado inteligente de palabras clave en **Amarillo Neón (`#FFE600`)** y **Cian Eléctrico**, con contorno 3D negro para máxima legibilidad.
- 🎥 **Motor Híbrido de Video e Imágenes:**
  - Generación de videoclips sintéticos en GPU remota con **ComfyUI API**.
  - Descargador multi-fuente open source (*Pixabay, Pexels, Wikimedia Commons*).
  - Imágenes fotorrealistas en 8K con **Pollinations Flux** animadas con efecto **Ken Burns Dinámico** en resolución 4K (CRF 14).
- 🧠 **Control de Calidad (QA) con IA de Visión (`qa_review.py`):** Evalúa fotogramas antes de renderizar con `minicpm-v`, descartando automáticamente cualquier recurso con concordancia inferior al 75%.
- 📓 **Sincronización Total con Obsidian:** Agenda automáticamente tandas de 3 videos al día (Mañana 08:30 AM, Tarde 02:30 PM, Noche 08:30 PM) con títulos optimizados, descripciones SEO y hashtags.
- 🧹 **Saneamiento Automático:** Purga archivos temporales y fragmentos de video al finalizar para mantener el almacenamiento optimizado.

---

## 🌐 Modos de Ejecución Disponibles

El proyecto soporta 3 modos de operación configurables en `config.yaml`:

```yaml
# config.yaml
ia:
  proveedor: "ollama_remote"     # ollama_remote | ollama | nvidia | openai
  host_remoto: "http://100.95.107.65:11434"
  modelo: "qwen3.6:35b"

video_ia:
  proveedor: "comfyui_remote"    # comfyui_remote | stock_multi_fuente
  host_remoto: "http://100.95.107.65:8188"
```

| Modo | Descripción | Ideal para |
|---|---|---|
| 🚀 **1. Servidor Remoto GPU (Tailscale VPN)** | Delega el LLM (35B) y ComfyUI a una PC remota con GPU dedicada (ej. **NVIDIA RTX 5090 con 32 GB VRAM**). 0% consumo en tu laptop. | Producción profesional sin calentamiento ni uso de batería local. |
| 💻 **2. Local Standalone (Apple Silicon / PC)** | Ejecuta todo localmente en tu Mac o PC con Ollama (`qwen2.5:14b` o `qwen3:8b`) y stock multi-fuente. | Trabajo offline o sin red externa. |
| ☁️ **3. Cloud API (NVIDIA NIM / OpenAI)** | Utiliza modelos de 70B en la nube (como `meta/llama-3.1-70b-instruct` vía NVIDIA NIM API gratuita). | Máquinas ligeras sin Ollama local. |

---

## 🛠️ Guía de Puesta en Marcha: Servidor Remoto (RTX 5090 + Tailscale)

Si tienes una PC secundaria o la máquina de un amigo con una tarjeta gráfica NVIDIA potente, sigue estos pasos para conectarla a tu Mac:

### 1. En la PC Remota (Windows con NVIDIA GPU):
1. **Instalar Tailscale:** Descargar [Tailscale para Windows](https://tailscale.com/download/windows) e iniciar sesión con la misma cuenta.
2. **Iniciar Ollama en red:**
   En una consola CMD (Administrador):
   ```cmd
   set OLLAMA_HOST=0.0.0.0:11434
   ollama serve
   ollama pull qwen3.6:35b
   ```
3. **Iniciar ComfyUI Portable para Video IA:**
   - Descargar la versión portable: [ComfyUI Windows Portable NVIDIA](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z).
   - Extraer la carpeta `ComfyUI_windows_portable`.
   - Editar `run_nvidia_gpu.bat` y asegurarse de que la primera línea incluya `--listen 0.0.0.0 --port 8188 --highvram`:
     ```bat
     .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --listen 0.0.0.0 --port 8188 --highvram
     pause
     ```
   - Ejecutar `run_nvidia_gpu.bat`.

---

### 2. En tu Mac (Cliente de Producción):
1. **Instalar Tailscale:** Iniciar sesión para unirte a la misma red segura.
2. **Obtener la IP de Tailscale de la PC remota:** (ejemplo: `100.95.107.65`).
3. **Configurar `config.yaml`:**
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

## 🚀 Inicio Rápido en tu Mac

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/ByCarlox/tiktok-ai-video-generator.git
   cd tiktok-ai-video-generator
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Asegurar FFmpeg instalado:**
   ```bash
   brew install ffmpeg
   ```

4. **Lanzar la producción autónoma de videos:**
   ```bash
   .venv/bin/python pipeline.py
   ```

Tus videos terminados en resolución 4K se guardarán en `output/para_subir/` y quedarán catalogados en tu bóveda de **Obsidian (`TikTok-AI-Passive/`)**.

---

## 📂 Estructura del Proyecto

```text
├── pipeline.py          # Orquestador del flujo broadcast, render y subtítulos virales
├── trends.py            # Radar de 5 pilares RSS, Google News y algoritmo de virality score
├── investigacion.py     # Ficha técnica estructurada previa a guion
├── ia_client.py         # Cliente LLM con soporte de razonamiento (Qwen 35B / NVIDIA NIM)
├── media_fetcher.py     # Motor híbrido de video (ComfyUI API + Stock Multi-Fuente)
├── qa_review.py         # Inspector de control de calidad visual con IA de Visión
├── metadata.py          # Generador de metadatos SEO y programador de slots en Obsidian
├── musica.py            # Descargador y selector inteligente de pistas de música libre
├── publisher.py         # Módulo de publicación multiplataforma
├── analytics.py         # Analítica y registro de métricas
├── config.yaml          # Archivo de configuración central del estudio
└── README.md            # Documentación completa del sistema
```

---

## 🛡️ Licencia y Uso
Desarrollado para la creación autónoma de contenido educativo, científico y tecnológico con altos estándares de retención y calidad visual. Código 100% de código abierto bajo licencia MIT.
