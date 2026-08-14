# obsidian_brain.py - v1.0 — Cerebro Central y Memoria Anti-Duplicación en Obsidian
"""
Módulo del Cerebro Autónomo en Obsidian:
1. Memoria persistente a largo plazo de temas, conceptos y ángulos tratados.
2. Motor Anti-Duplicación (Jaccard + Keyword Overlap + Detección Semántica).
3. Inyección de memoria histórica en los prompts del LLM.
4. Generación automática de notas enriquecidas en Markdown con enlaces bidireccionales y metadatos YAML.
5. Dashboard interactivo para Obsidian con Dataview.
"""
import re
import json
import difflib
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path("TikTok-AI-Passive")

def inicializar_estructura_cerebro():
    """Crea la arquitectura de carpetas y notas maestras del Cerebro en Obsidian."""
    carpetas = [
        "00_Brain_Center",
        "01_Memory_Vault/Topics_Memory",
        "01_Memory_Vault/Winning_Hooks",
        "01_Memory_Vault/Character_Profile",
        "02_Production_Logs/Scripts_Archive",
        "02_Production_Logs/Published_Videos",
        "03_Analytics_Feedback",
        "04_Knowledge_Base/Tech_Research",
        "04_Knowledge_Base/Hardware_Benchmarks",
        "Templates"
    ]
    for c in carpetas:
        (VAULT_DIR / c).mkdir(parents=True, exist_ok=True)
        
    # Crear o actualizar el Dashboard Maestro
    dashboard_file = VAULT_DIR / "00_Brain_Center/🧠_CENTRAL_DASHBOARD.md"
    if not dashboard_file.exists():
        dashboard_file.write_text("""---
title: "🧠 CEREBRO CENTRAL - TIKTOK AI PASSIVE"
date: "2026-08-14"
type: dashboard
---

# 🧠 CEREBRO CENTRAL — TIKTOK AI PASSIVE

> **Estado del Sistema:** 🟢 ACTIVO & AUTÓNOMO
> **Presentadora Oficial:** 🌸 **Nova (Kawaii Waifu VTuber)** — Cabello Rosa / Auriculares Neón
> **Voz Neural:** `es-MX-DaliaNeural` (Dulce, juvenil y ultra expresiva)
> **GPU Server:** RTX 5090 (ComfyUI + Qwen 36B)

---

## 📊 Métricas y Memoria de Producción

```dataview
TABLE date as "Fecha", topic as "Tema", duration as "Duración (s)", qa_score as "QA Score", status as "Estado"
FROM "02_Production_Logs/Scripts_Archive"
SORT date DESC
LIMIT 15
```

---

## 🧬 Temas en Memoria (Anti-Duplicación)

```dataview
TABLE category as "Categoría", times_covered as "Veces Tratado", date_last as "Última Fecha"
FROM "01_Memory_Vault/Topics_Memory"
SORT date_last DESC
LIMIT 20
```

---

## ⚡ Enlaces Rápidos del Cerebro
- [[🧬_PROYECTO_LORE|Perfil y Lore de la Presentadora Waifu]]
- [[01_Memory_Vault/Winning_Hooks/formulas_gancho|Fórmulas de Ganchos Virales]]
- [[04_Knowledge_Base/Tech_Research/index|Base de Conocimiento Tecnológico]]
""", encoding="utf-8")

    # Lore de la Presentadora
    lore_file = VAULT_DIR / "00_Brain_Center/🧬_PROYECTO_LORE.md"
    if not lore_file.exists():
        lore_file.write_text("""---
character: "Nova"
role: "AI Tech & Science Presenter"
style: "Kawaii Anime VTuber"
hair: "Pastel Pink Twin-tails"
voice: "es-MX-DaliaNeural"
---

# 🌸 Perfil y Lore: Nova (AI VTuber Host)

## Identidad
- **Nombre:** Nova / Aiko
- **Rol:** Presentadora oficial carismática de tecnología, inteligencia artificial y ciencia futurista.
- **Personalidad:** Curiosa, hiper-enérgica, inteligente, dulce y apasionada por los avances de la humanidad.
- **Look:** Cabello rosa pastel en dos coletas, ojos violeta brillantes, auriculares futuristas con orejas de gato neón y micrófono holográfico.
- **Tono de Voz:** Entusiasta, directo, sin tecnicismos aburridos, explicando conceptos complejos con metáforas sorprendentes.

## Fórmulas de Apertura (Hooks)
1. *"¡Paren todo! Lo que acaba de pasar con la IA no tiene ningún sentido..."*
2. *"El 99% de las personas todavía no se ha enterado de esta locura tecnológica..."*
3. *"Si creías que el futuro tardaría 10 años en llegar, mira esto..."*
""", encoding="utf-8")

def _obtener_archivo_indice() -> Path:
    idx_p = VAULT_DIR / "01_Memory_Vault/Topics_Memory/topics_index.json"
    idx_p.parent.mkdir(parents=True, exist_ok=True)
    if not idx_p.exists():
        idx_p.write_text("{}", encoding="utf-8")
    return idx_p

def cargar_memoria_temas() -> dict:
    """Carga el diccionario en memoria de todos los temas históricos tratados."""
    inicializar_estructura_cerebro()
    idx_p = _obtener_archivo_indice()
    try:
        return json.loads(idx_p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def guardar_memoria_temas(memoria: dict):
    """Guarda el índice de temas en JSON para consultas ultra rápidas."""
    idx_p = _obtener_archivo_indice()
    idx_p.write_text(json.dumps(memoria, ensure_ascii=False, indent=2), encoding="utf-8")

def normalizar_texto(texto: str) -> str:
    """Limpia puntuación y mayúsculas para comparación semántica."""
    t = texto.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())

def verificar_duplicado(tema: str, categoria: str = "") -> tuple:
    """
    Comprueba si un tema ya fue tratado o si tiene alta similitud con temas pasados.
    Retorna: (es_duplicado: bool, motivo: str, tema_existente: str)
    """
    memoria = cargar_memoria_temas()
    if not memoria:
        return False, "", ""
        
    tema_norm = normalizar_texto(tema)
    palabras_nuevas = set(tema_norm.split())
    # Palabras vacías a ignorar
    stopwords = {"de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "unos", "unas", "por", "para", "con", "que", "es", "su", "al", "del"}
    palabras_nuevas = palabras_nuevas - stopwords
    
    for id_tema, datos in memoria.items():
        tema_guardado = datos.get("tema", "")
        guardado_norm = normalizar_texto(tema_guardado)
        palabras_guardadas = set(guardado_norm.split()) - stopwords
        
        # 1. Similitud de Levenshtein en cadena completa
        ratio = difflib.SequenceMatcher(None, tema_norm, guardado_norm).ratio()
        if ratio > 0.65:
            return True, f"Similitud de texto alta ({int(ratio * 100)}%) con tema previo", tema_guardado
            
        # 2. Coincidencia de palabras clave (Jaccard Index)
        if palabras_nuevas and palabras_guardadas:
            interseccion = palabras_nuevas.intersection(palabras_guardadas)
            union = palabras_nuevas.union(palabras_guardadas)
            jaccard = len(interseccion) / len(union)
            if jaccard > 0.45 or len(interseccion) >= 3:
                return True, f"Palabras clave repetidas: {', '.join(interseccion)}", tema_guardado
                
    return False, "", ""

def obtener_temas_recientes_para_prompt(limite: int = 15) -> str:
    """Devuelve un bloque de texto con los temas recientes para inyectar en el prompt del LLM."""
    memoria = cargar_memoria_temas()
    if not memoria:
        return "No hay temas previos registrados."
        
    ordenados = sorted(memoria.values(), key=lambda x: x.get("date_last", ""), reverse=True)
    lista = [f"- {d.get('tema')} ({d.get('category', 'General')})" for d in ordenados[:limite]]
    return "\n".join(lista)

def registrar_produccion_en_obsidian(
    tema: str,
    categoria: str,
    guion: str,
    duracion_audio: float,
    qa_score: float,
    video_path: Path,
    hashtags: str = "",
    investigacion: str = ""
):
    """
    Registra de forma atómica la producción en el Cerebro de Obsidian:
    1. Actualiza el Topics_Memory index.
    2. Crea la tarjeta de tema individual con enlaces bidireccionales.
    3. Crea la nota completa del Guión de Producción en Scripts_Archive.
    """
    inicializar_estructura_cerebro()
    memoria = cargar_memoria_temas()
    
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_slug = datetime.now().strftime("%Y%m%d_%H%M")
    
    slug_tema = re.sub(r"[^\w\s-]", "", tema.lower()).strip().replace(" ", "_")[:35]
    id_tema = f"{fecha_slug}_{slug_tema}"
    
    # 1. Actualizar índice de memoria
    memoria[id_tema] = {
        "tema": tema,
        "category": categoria or "Tecnología",
        "date_last": ahora,
        "times_covered": memoria.get(id_tema, {}).get("times_covered", 0) + 1,
        "qa_score": round(qa_score, 1),
        "duracion": round(duracion_audio, 1),
        "video_file": str(video_path.name if video_path else "")
    }
    guardar_memoria_temas(memoria)
    
    # 2. Guardar Nota del Guión en Scripts_Archive
    script_note_path = VAULT_DIR / f"02_Production_Logs/Scripts_Archive/{id_tema}.md"
    nota_contenido = f"""---
id: "{id_tema}"
topic: "{tema}"
category: "{categoria or 'Tecnología'}"
date: "{ahora}"
duration: {duracion_audio:.1f}
qa_score: {qa_score:.1f}
video_file: "{video_path.name if video_path else ''}"
host: "Nova (Kawaii Waifu VTuber)"
status: "READY_TO_PUBLISH"
tags:
  - video_tiktok
  - {categoria.lower().replace(' ', '_') if categoria else 'tecnologia'}
  - produccion_ia
---

# 🎬 Guión Master: {tema}

> **Presentadora:** 🌸 Nova (VTuber Host)
> **Duración Audio:** {duracion_audio:.1f} segundos | **Calidad QA:** {qa_score:.1f}/100
> **Archivo de Video:** `output/videos/{video_path.name if video_path else ''}`

---

## 📜 Guión Completo (Narración)

```text
{guion}
```

---

## 🏷️ Hashtags y Metadatos para TikTok / Reels
{hashtags if hashtags else f"#{categoria.replace(' ', '')} #InteligenciaArtificial #Tecnologia #Futuro #Curiosidades"}

---

## 🔬 Investigación y Fuentes Base
{investigacion if investigacion else "Generado autónomamente con Qwen 36B + RTX 5090."}

---

## 🔗 Relaciones en el Cerebro
- Tema tratado en: [[01_Memory_Vault/Topics_Memory/{slug_tema}|Ficha de Tema: {tema}]]
- Ver panel general: [[00_Brain_Center/🧠_CENTRAL_DASHBOARD|Dashboard Central]]
"""
    script_note_path.write_text(nota_contenido, encoding="utf-8")
    
    # 3. Guardar Ficha de Tema en Topics_Memory
    topic_card_path = VAULT_DIR / f"01_Memory_Vault/Topics_Memory/{slug_tema}.md"
    topic_card = f"""---
title: "{tema}"
category: "{categoria}"
date_first: "{ahora}"
date_last: "{ahora}"
times_covered: {memoria[id_tema]['times_covered']}
---

# 📌 Ficha de Memoria: {tema}

- **Categoría:** `{categoria}`
- **Última Producción:** [[02_Production_Logs/Scripts_Archive/{id_tema}|{id_tema}]]

## Historial de Guiones Asociados
- [[02_Production_Logs/Scripts_Archive/{id_tema}|Guión del {ahora[:10]}]]
"""
    topic_card_path.write_text(topic_card, encoding="utf-8")
    print(f"      🧠 Memoria actualizada en Obsidian: [[{id_tema}]]")
