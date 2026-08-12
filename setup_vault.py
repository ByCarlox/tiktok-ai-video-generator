from pathlib import Path

VAULT = Path("TikTok-AI-Passive")

folders = [
    "00-Inbox",
    "01-Estrategia",
    "02-Cuenta",
    "03-Contenidos/Ideas",
    "03-Contenidos/Episodios",
    "03-Contenidos/Guiones",
    "03-Contenidos/Assets",
    "03-Contenidos/Render",
    "03-Contenidos/Programados",
    "03-Contenidos/Publicados",
    "04-Produccion",
    "05-Automatizacion/scripts",
    "05-Automatizacion/logs",
    "05-Automatizacion/config",
    "06-Recursos",
    "07-Analiticas",
    "08-Monetizacion",
    "09-Legal",
    "Templates",
    "Attachments/logos",
    "Attachments/imagenes",
    "Attachments/audios",
    "Attachments/videos",
]

files = {
    "00-Inbox/ideas-rapidas.md": """
# Ideas rápidas

Escribe aquí ideas sueltas.

- 
- 
- 
""",

    "01-Estrategia/nicho.md": """
# Nicho

## Nicho principal
Curiosidades / tendencias explicadas con IA.

## Subnichos
- Tecnología
- Psicología
- Historia
- Ciencia
- Dinero
- IA
- Hábitos

## Ángulo
Explicar tendencias, datos curiosos y conceptos interesantes de forma rápida y visual.
""",

    "01-Estrategia/propuesta-de-valor.md": """
# Propuesta de valor

## Promesa
Videos cortos que enseñan algo interesante, curioso o útil en menos de 60 segundos.

## Estilo
- Directo
- Visual
- Claro
- Sin relleno
- Con gancho fuerte

## Frase de marca
"Aprende algo interesante en 30 segundos".
""",

    "01-Estrategia/pilares-de-contenido.md": """
# Pilares de contenido

1. Datos curiosos
2. Tendencias explicadas
3. IA y herramientas útiles
4. Psicología / hábitos
5. Dinero / decisiones inteligentes
6. Ciencia / futuro
""",

    "01-Estrategia/objetivos.md": """
# Objetivos

## 30 días
- Crear cuenta
- Publicar 20-30 videos
- Encontrar 3 formatos ganadores
- Medir retención y ganchos

## 90 días
- Conseguir audiencia estable
- Activar monetización si está disponible
- Crear primer producto/afiliado
- Sistematizar producción
""",

    "01-Estrategia/plan-30-dias.md": """
# Plan 30 días

## Semana 1
- Crear cuenta
- Configurar Obsidian
- Crear identidad visual
- Producir 10 videos

## Semana 2
- Publicar 1 video diario
- Probar ganchos
- Medir retención

## Semana 3
- Repetir formatos ganadores
- Crear series
- Optimizar subtítulos y ritmo

## Semana 4
- Producir en lote
- Crear funnel de afiliado/producto
- Analizar métricas
""",

    "02-Cuenta/cuenta-tiktok.md": """
# Cuenta TikTok

## Datos
- Correo:
- Usuario:
- Nombre:
- Idioma:
- País:
- Categoría:

## Estado
- [ ] Correo creado
- [ ] Cuenta TikTok creada
- [ ] 2FA activado
- [ ] Perfil completado
- [ ] Bio optimizada
- [ ] Foto de perfil lista
- [ ] Cuenta revisada en Creator Tools
""",

    "02-Cuenta/branding.md": """
# Branding

## Nombre de cuenta
Ejemplos:
- @dato.ia
- @trend.explicado
- @curiosidad.flash
- @ia.en.simple
- @micro.saber

## Estilo visual
- Colores: negro/azul oscuro + blanco
- Tipografía grande
- Subtítulos llamativos
- Imágenes cinematográficas o futuristas

## Tono
Curioso, rápido, inteligente, sin exageraciones.
""",

    "02-Cuenta/bio.md": """
# Bio

## Opción 1
Datos curiosos y tendencias explicadas en segundos.

## Opción 2
Aprende algo nuevo cada día con IA.

## Opción 3
Tendencias, tecnología y curiosidades en menos de 60 segundos.

## CTA
Sígueme para aprender algo nuevo hoy.
""",

    "02-Cuenta/checklist-publicacion.md": """
# Checklist antes de publicar

- [ ] El hook funciona en los primeros 2 segundos
- [ ] No hay información falsa o peligrosa
- [ ] No hay material con copyright
- [ ] No hay música comercial no permitida
- [ ] Subtítulos visibles
- [ ] Formato 9:16
- [ ] Duración adecuada
- [ ] CTA claro
- [ ] Etiqueta de IA si aplica
- [ ] Descripción con keywords
- [ ] Video revisado completo
""",

    "03-Contenidos/Ideas/.gitkeep": "",
    "03-Contenidos/Episodios/.gitkeep": "",
    "03-Contenidos/Guiones/.gitkeep": "",
    "03-Contenidos/Assets/.gitkeep": "",
    "03-Contenidos/Render/.gitkeep": "",
    "03-Contenidos/Programados/.gitkeep": "",
    "03-Contenidos/Publicados/.gitkeep": "",

    "04-Produccion/prompts-guion.md": """
# Prompts para guiones

## Prompt base
Actúa como creador de contenido viral para TikTok. Crea un guion de 30-45 segundos sobre el tema: [TEMA].

Debe tener:
1. Gancho fuerte en los primeros 2 segundos.
2. Explicación simple.
3. 3 datos o puntos rápidos.
4. Cierre con frase memorable.
5. CTA suave.

Estilo:
- Directo
- Claro
- Sin relleno
- Sin exageraciones
- Apto para todo público
- Sin copyright
- Sin afirmaciones médicas/financieras peligrosas

Devuelve el guion en formato:
HOOK:
CUERPO:
CIERRE:
CTA:
""",

    "04-Produccion/prompts-visuales.md": """
# Prompts visuales

## Estilo base
Vertical 9:16, cinematic, clean, high detail, no text, no logos, no real celebrities, no copyrighted characters, safe for work, dramatic lighting.

## Ejemplo
A futuristic digital brain floating in dark blue space, glowing particles, cinematic lighting, vertical 9:16, no text.

## Variaciones
- Minimalista
- Documental
- Futurista
- Histórico
- Científico
- Misterioso
""",

    "04-Produccion/estilo-voz.md": """
# Estilo de voz

## Voz recomendada
Español neutro o español latino claro.

## Tono
- Seguro
- Curioso
- Dinámico
- No excesivamente publicitario

## Velocidad
Ligeramente rápida, pero clara.
""",

    "04-Produccion/estilo-subtitulos.md": """
# Estilo de subtítulos

- Tamaño grande
- Color blanco
- Borde negro
- Máximo 4-7 palabras por línea
- Resaltar palabras clave
- Evitar tapar elementos importantes
""",

    "04-Produccion/plantilla-video.md": """
# Plantilla de video

## Duración
30-45 segundos.

## Estructura
0-2s: Hook
2-5s: Contexto
5-25s: Desarrollo
25-32s: Dato final/giro
32-35s: CTA

## Ejemplo hook
"Esto parece falso, pero es real".

## Ejemplo CTA
"Sígueme si quieres aprender algo nuevo mañana".
""",

    "05-Automatizacion/pipeline.md": """
# Pipeline automático

## Flujo
1. Detectar tendencia o tema.
2. Guardar idea en Obsidian.
3. Generar guion con IA.
4. Generar voz con IA.
5. Generar subtítulos.
6. Generar imágenes/clips.
7. Renderizar video.
8. Revisión humana.
9. Programar/publicar.
10. Medir métricas.
""",

    "06-Recursos/herramientas-ia.md": """
# Herramientas IA

## Texto
- Qwen
- ChatGPT
- Claude
- Ollama local

## Voz
- Edge-TTS
- ElevenLabs
- Azure Speech
- OpenAI TTS

## Imagen
- Leonardo AI
- Ideogram
- Stable Diffusion
- Flux
- DALL·E

## Video
- Runway
- Pika
- Kling
- Luma
- Stable Video Diffusion
- ComfyUI

## Subtítulos
- Whisper
- Faster-Whisper
- CapCut

## Edición/render
- FFmpeg
- MoviePy
- Remotion
- Creatomate

## Programación
- TikTok Web
- Metricool
- Later
- Publer
- Buffer
""",

    "07-Analiticas/metricas-semanales.md": """
# Métricas semanales

## Semana
- Videos publicados:
- Visualizaciones totales:
- Seguidores ganados:
- Retención media:
- Likes:
- Comentarios:
- Compartidos:
- Guardados:
- Mejor video:
- Peor video:
- Aprendizaje:
""",

    "08-Monetizacion/afiliados.md": """
# Afiliados

## Ideas
- Amazon Afiliados
- Hotmart
- Herramientas IA
- Apps de productividad
- Cursos
- Plantillas

## Regla
Solo recomendar productos relacionados con el contenido y que aporten valor real.
""",

    "08-Monetizacion/productos.md": """
# Productos propios

## Ideas
- Pack de prompts
- Plantilla de organización
- Guía para crear videos con IA
- Mini curso de automatización
- Lista de herramientas útiles
""",

    "09-Legal/checklist-legal.md": """
# Checklist legal

- [ ] No usar contenido sexual explícito
- [ ] No usar menores en contextos inapropiados
- [ ] No usar música con copyright sin permiso
- [ ] No usar marcas famosas de forma engañosa
- [ ] No hacer deepfakes de personas reales
- [ ] No prometer resultados financieros garantizados
- [ ] No dar consejos médicos peligrosos
- [ ] Indicar uso de IA si la plataforma lo requiere
- [ ] Usar material original o con licencia adecuada
""",

    "Templates/idea-video.md": """
---
id: {{date}}
titulo: 
estado: idea
tema: 
tendencia: 
hook: 
publicar: 
duracion: 35
views: 
likes: 
comentarios: 
compartidos: 
retencion_3s: 
monetizable: true
riesgo: bajo
---

# Idea

## Hook

## Desarrollo

## CTA

## Checklist
- [ ] Guion aprobado
- [ ] Voz generada
- [ ] Visuales generados
- [ ] Subtítulos generados
- [ ] Render terminado
- [ ] QC legal
- [ ] Listo para publicar
""",

    "Templates/guion-video.md": """
---
titulo: 
estado: guion
duracion: 35
hook: 
---

# Guion

## Hook

## Cuerpo

## Cierre

## CTA

## Prompts visuales
1. 
2. 
3. 
4. 
5. 
""",

    "Templates/metricas-diarias.md": """
# Métricas del día

- Fecha:
- Videos publicados:
- Visualizaciones:
- Seguidores:
- Mejor video:
- Retención:
- Aprendizaje:
"""
}

for folder in folders:
    path = VAULT / folder
    path.mkdir(parents=True, exist_ok=True)

for file_path, content in files.items():
    path = VAULT / file_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content.strip() + "\n", encoding="utf-8")

print(f"Vault creado en: {VAULT.resolve()}")