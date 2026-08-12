# 🎬 TikTok AI Passive Video Generator (v4.2)

Un sistema autónomo de producción de videos virales en formato 9:16 (4K) para TikTok, Reels y Shorts con investigación científica estructurada y control de calidad visual mediante **IA de Visión (Multimodal)**.

---

## ⚡ Características Principales

- 🔍 **Tendencias Multinegocio para LATAM:** Descubre y filtra noticias de tech, IA y ciencia de 9 fuentes RSS internacionales y Google News en 5 países LATAM (MX, AR, CO, CL, PE), excluyendo política, deportes y desastres.
- 🔬 **Investigación Científica Estructurada (`investigacion.py`):** Realiza un estudio técnico previo antes de guionar para extraer hechos verificados, datos cuantitativos en dólares (USD) y conceptos visuales.
- 🎙️ **Narración y Subtítulos Dinámicos:** Guion en español neutro panlatino, voz Edge-TTS normalizada y subtítulos acelerados quemados en Pillow estilo TikTok.
- 🎥 **Recursos Open Source Múltiples (`media_fetcher.py`):** Integración de Pixabay, Pexels, Wikimedia Commons (CC/Public Domain) y Pollinations.ai (Flux) para imágenes y videoclips 4K.
- 🧠 **QA Visual con IA de Visión (`qa_review.py`):** Inspecciona fotogramas en tiempo real usando el modelo multimodal `minicpm-v` en Ollama. Descarta assets irrelevantes (<75% concordancia) antes de renderizar.
- 📓 **Dashboard Automático en Obsidian:** Organiza metadatos, slots de publicación sin colisión y métricas en una bóveda estructurada.

---

## 🛠️ Requisitos Previos

- **Python 3.10+**
- **FFmpeg** instalado en el sistema (`brew install ffmpeg`)
- **Ollama** con los modelos:
  - `qwen3:8b` (Texto y guion)
  - `minicpm-v` (Visión multimodal)

---

## 🚀 Inicio Rápido

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/tiktok-ai-generator.git
   cd tiktok-ai-generator
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecutar el Pipeline Unificado en una sola corrida:**
   ```bash
   .venv/bin/python pipeline.py
   ```

---

## 📊 Arquitectura del Proyecto

```text
├── pipeline.py        # Orquestador principal del flujo unificado
├── trends.py          # Buscador de tendencias tech/IA para LATAM
├── investigacion.py   # Investigador técnico pre-producción
├── ia_client.py       # Generador de guiones e imágenes Flux
├── media_fetcher.py   # Descargador multi-fuente (Pixabay/Pexels/Wikimedia)
├── qa_review.py       # Inspector visual con minicpm-v (Visión IA)
├── metadata.py        # Generador semántico y sincronizador de Obsidian
├── publisher.py       # Publicador multi-plataforma
├── analytics.py       # Actualizador de métricas en Obsidian
├── config.yaml        # Configuración central del canal
└── README.md          # Documentación del proyecto
```
