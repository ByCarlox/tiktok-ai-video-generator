# metadata.py - v1.0
import json
import re
import shutil
import datetime
import requests
import yaml
from pathlib import Path

PROMPT_METADATA = """Analiza este tema y guion de TikTok, y genera la metadata de publicación en formato JSON.

TEMA: "{tema}"
GUION: "{guion}"

IMPORTANTE: La audiencia es TODA Latinoamérica, no un país en particular. Usa español neutro.

Devuelve un objeto JSON con los siguientes campos estrictamente formateados:
- "titulo": Un título corto de 40 a 60 caracteres. Debe ser muy llamativo, tener un gancho, incluir la palabra clave principal, y NO tener hashtags. Sin mencionar países específicos.
- "descripcion": 2 o 3 líneas de descripción del video con un llamado a la acción (CTA) suave y exactamente 1 emoji. Español neutro latinoamericano.
- "hashtags": Una lista (array) de entre 5 y 8 hashtags en español que sean muy relevantes para toda Latinoamérica. Queda terminantemente PROHIBIDO incluir hashtags genéricos como "fyp", "parati", "viral", "foryou", "foryoupage". NO incluir hashtags de un solo país.
- "cta_texto": Frase final muy corta para colocar en pantalla (máximo 25 caracteres).
- "nicho": Una o dos palabras que describan el tema principal. Ejemplos válidos: "inteligencia artificial", "ciencia de datos", "neurociencia", "tecnología", "astronomía", "productividad", "innovación", "biología", "programación", "gadgets", "ciencia", "psicología cognitiva", "ciberseguridad". Sé específico, no genérico.
- "gancho_visual": Una palabra clave para la portada o gancho visual del video.
- "score_viral": Un número entero del 0 al 100 estimando el potencial viral del tema.
- "audiencia_objetivo": Una frase de exactamente 5 palabras que describa "edad + interés" (ej. "jóvenes interesados en tecnología moderna").

Devuelve exclusivamente el JSON sin ninguna explicación ni texto adicional."""

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def calcular_fecha_programada(config, vault_path):
    # 1. Leer todas las fechas programadas existentes en Obsidian
    fechas_ocupadas = set()
    if vault_path.exists():
        for p in vault_path.iterdir():
            if p.is_dir():
                idx_md = p / "index.md"
                if idx_md.exists():
                    try:
                        content = idx_md.read_text(encoding="utf-8")
                        for line in content.splitlines():
                            if "fecha_publicacion_programada:" in line:
                                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                                try:
                                    dt = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M")
                                    fechas_ocupadas.add(dt)
                                except ValueError:
                                    pass
                    except Exception:
                        pass

    # 2. Buscar el siguiente slot libre
    slots = ["08:00", "13:30", "19:00", "21:30"]
    ahora = datetime.datetime.now()
    
    dia_busqueda = ahora.date()
    for _ in range(365):  # Buscar hasta 1 año en el futuro
        for slot in slots:
            sh, sm = map(int, slot.split(":"))
            slot_dt = datetime.datetime.combine(dia_busqueda, datetime.time(sh, sm))
            
            # El slot debe ser en el futuro
            if slot_dt <= ahora:
                continue
                
            # El slot no debe estar ocupado
            if slot_dt in fechas_ocupadas:
                continue
                
            return slot_dt
            
        dia_busqueda += datetime.timedelta(days=1)
        
    return ahora + datetime.timedelta(days=1)

def generar_metadata(tema, guion, video_path, indice):
    config = cfg()
    ia = config["ia"]
    prompt = PROMPT_METADATA.format(tema=tema, guion=guion)
    
    response_text = ""
    if ia["proveedor"] in ("ollama_remote", "ollama"):
        host = ia.get("host_remoto", "http://100.95.107.65:11434") if ia["proveedor"] == "ollama_remote" else "http://localhost:11434"
        try:
            r = requests.post(
                f"{host}/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False},
                timeout=90
            )
            if r.status_code == 200:
                response_text = r.json().get("response", "").strip()
        except Exception as e:
            print(f"   ⚠️ Conexión de metadatos con {ia['proveedor']} ({host}) falló ({e}). Conmutando a Ollama local...")

    elif ia["proveedor"] in ("openai", "groq", "nvidia"):
        try:
            base = ia.get("base_url", "https://integrate.api.nvidia.com/v1" if ia["proveedor"] == "nvidia" else "https://api.openai.com/v1")
            headers = {"Content-Type": "application/json"}
            if "api_key" in ia:
                headers["Authorization"] = f"Bearer {ia['api_key']}"
            r = requests.post(
                f"{base}/chat/completions",
                headers=headers,
                json={
                    "model": ia["modelo"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5
                },
                timeout=60
            )
            if r.status_code == 200:
                response_text = r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"   ⚠️ Conexión de metadatos con {ia['proveedor']} falló ({e}). Conmutando a Ollama local...")

    if not response_text:
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:14b", "prompt": prompt, "stream": False, "format": "json"},
                timeout=30
            )
            if r.status_code == 200:
                response_text = r.json().get("response", "").strip()
        except Exception:
            pass

    if not response_text:
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen3:8b", "prompt": prompt, "stream": False, "format": "json"},
                timeout=30
            )
            if r.status_code == 200:
                response_text = r.json().get("response", "").strip()
        except Exception:
            pass

    meta = {}
    try:
        import re
        cleaned_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL | re.IGNORECASE).strip()
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
            
        ini = cleaned_text.find("{")
        fin = cleaned_text.rfind("}")
        if ini != -1 and fin != -1 and fin > ini:
            cleaned_text = cleaned_text[ini:fin+1]
            
        meta = json.loads(cleaned_text)
    except Exception as e:
        print(f"⚠️ Error decodificando JSON de metadatos: {e}")
        # Fallback manual robusto
        meta = {
            "titulo": f"Aprende sobre {tema} hoy mismo",
            "descripcion": f"Esto es lo que necesitas saber sobre {tema}. ¿Qué opinas tú? 😉",
            "hashtags": ["tecnologia", "aprendizaje", "curiosidades", "interesante"],
            "cta_texto": "Sígueme para más videos",
            "nicho": "curiosidades",
            "gancho_visual": tema,
            "score_viral": 75,
            "audiencia_objetivo": "personas interesadas en datos curiosos"
        }
        
    video_path = Path(video_path)
    meta_json_path = video_path.parent / f"{video_path.stem}.meta.json"
    
    vault_path = Path(config["obsidian_vault"]) / "03-Contenidos" / "Episodios"
    slot_dt = calcular_fecha_programada(config, vault_path)
    fecha_prog_str = slot_dt.strftime("%Y-%m-%d %H:%M")
    
    meta["fecha_publicacion_programada"] = fecha_prog_str
    
    # Formatear hashtags
    hashtags_cleaned = []
    for h in meta.get("hashtags", []):
        h_clean = h.strip().replace("#", "").replace(" ", "")
        if h_clean:
            hashtags_cleaned.append(f"#{h_clean}")
    
    meta["hashtags"] = [h.replace("#", "") for h in hashtags_cleaned]
    
    hashtags_str = " ".join(hashtags_cleaned)
    texto_completo = f"{meta.get('titulo')}\n\n{meta.get('descripcion')}\n\n{hashtags_str}"
    meta["texto_completo"] = texto_completo
    
    # Escribir JSON al lado del video
    meta_json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"   ✅ Metadatos guardados en: {meta_json_path}")
    
    return meta

def actualizar_obsidian_con_metadata(tema, guion, video_path, prompts, meta):
    config = cfg()
    vault = Path(config["obsidian_vault"]) / "03-Contenidos" / "Episodios"
    ahora = datetime.datetime.now()
    
    carpeta = vault / f"{ahora:%Y-%m-%d}-{slugify(tema)}"
    carpeta.mkdir(parents=True, exist_ok=True)
    
    video_path = Path(video_path)
    video_local = carpeta / video_path.name
    if not video_local.exists() and video_path.exists():
        shutil.copy2(video_path, video_local)
        
    safe_title = meta.get("titulo", tema).replace('"', '\\"')
    safe_desc = meta.get("descripcion", "").replace('"', '\\"')
    
    prompts_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompts)]) if prompts else "No se generaron prompts."
    
    markdown_content = f"""---
titulo: "{safe_title}"
descripcion: "{safe_desc}"
estado: programado
fecha_publicacion_programada: "{meta.get('fecha_publicacion_programada')}"
hashtags: {meta.get('hashtags', [])}
nicho: "{meta.get('nicho', '')}"
score_viral: {meta.get('score_viral', 50)}
cta_texto: "{meta.get('cta_texto', '')}"
video: "{video_local.name}"
gancho_visual: "{meta.get('gancho_visual', '')}"
audiencia_objetivo: "{meta.get('audiencia_objetivo', '')}"
qa_score: {meta.get('qa_score', 'N/A')}
qa_intentos: {meta.get('qa_intentos', 1)}
qa_aprobado: {meta.get('qa_aprobado', True)}
fecha_creacion: "{ahora:%Y-%m-%d %H:%M}"
---

# {tema}

## Texto para Copiar a TikTok
```text
{meta.get('texto_completo')}
```

## Guion Narrado
{guion}

## Prompts de Imágenes
{prompts_text}

## Control de Calidad (QA)
- **Score QA:** {meta.get('qa_score', 'N/A')}/100
- **Intentos:** {meta.get('qa_intentos', 1)}
- **Aprobado:** {'✅ Sí' if meta.get('qa_aprobado', True) else '⚠️ Publicado con advertencia'}

## Checklist
- [x] Generado automáticamente (v4 + QA)
- [{'x' if meta.get('qa_aprobado', False) else ' '}] Revisión de calidad aprobada
- [ ] Listo para publicar
- [ ] Publicado
"""
    
    (carpeta / "index.md").write_text(markdown_content, encoding="utf-8")
    print(f"   📓 Obsidian actualizado con metadatos en: {carpeta / 'index.md'}")
