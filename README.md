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

## 🧠 Arquitectura de IA, Modelos y Lógica de Producción

### 1. Modelos de Lenguaje e Inteligencia Artificial Utilizados
El sistema utiliza una arquitectura híbrida optimizada para ejecutarse localmente sin depender de APIs de pago:

- **`qwen3:8b` (Vía Ollama Local):**
  - **Función:** Generación de guiones, estructuración de investigaciones previas, análisis de relevancia y redacción de metadatos (título, descripción, hashtags).
  - **¿Por qué este modelo?:** Excelente compresión de contexto en español neutro, alta adherencia a restricciones de formato JSON estricto y excelente rendimiento en procesadores Apple Silicon (M-Series).
- **`minicpm-v` (Visión Multimodal Local via Ollama):**
  - **Función:** Inspección visual cuadro por cuadro (QA Pre-Renderizado) y evaluación de concordancia temática contra el guion narrado.
  - **¿Por qué este modelo?:** Es uno de los modelos de visión de código abierto más eficientes del mundo. Permite analizar la composición, iluminación, calidad y relevancia visual de imágenes de 4K en segundos sin consumo excesivo de VRAM.
- **`Pollinations Flux` (Generación de Imágenes IA 8K):**
  - **Función:** Generación de imágenes fotorrealistas verticales (9:16) a partir de prompts estructurados por la IA.
  - **Ventaja:** Generación rápida sin marcas de agua con calidad cinematográfica.

---

### 💡 Lógica de Negocio y Principios Narrativos

1. **Investigación Estructurada Pre-Producción:**
   - Antes de escribir una sola palabra del guion, el módulo `investigacion.py` consulta al modelo de IA para extraer una **Ficha Técnica**: resumen científico, 3 datos cuantitativos verificables, glosario de terminología y 5 conceptos visuales clave.
2. **Español Neutro Panlatino & Moneda en USD:**
   - Todo el contenido está diseñado para maximizar el alcance en los 20+ países de habla hispana. Se evitan modismos locales y todas las cifras económicas se expresan en dólares estadounidenses (USD) por practicidad regional.
3. **Control de Calidad (QA) Pre-Renderizado por Asset (>= 75% Concordancia):**
   - Para evitar perder tiempo renderizando o reescalando imágenes/videos irrelevantes, los videoclips y las imágenes son inspeccionados **ANTES** de entrar a la etapa de montaje. Si un recurso no alcanza el 75% de relevancia temática (`avg_relevance >= 18.75/25`), se descarta de inmediato y se busca/genera una alternativa.

---

## 🛠️ Requisitos Previos

- **Python 3.10+**
- **FFmpeg** instalado en el sistema (`brew install ffmpeg`)
- **Ollama** ejecutándose localmente con los modelos:
  ```bash
  ollama pull qwen3:8b
  ollama pull minicpm-v
  ```

---

## 🚀 Inicio Rápido

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/ByCarlox/tiktok-ai-video-generator.git
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
└── README.md          # Documentación detallada del proyecto
```
