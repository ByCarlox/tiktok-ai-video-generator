# ia_client.py
import json
import requests
import yaml
from pathlib import Path

import re

def cargar_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def limpiar_respuesta_llm(texto: str) -> str:
    """Elimina etiquetas de razonamiento <think>...</think> de modelos como qwen3.6 / deepseek."""
    if not texto:
        return ""
    return re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL | re.IGNORECASE).strip()

def extraer_json_valido(texto: str) -> dict:
    """Extrae y parsea un diccionario JSON válido eliminando tags <think> y bloques markdown."""
    texto = limpiar_respuesta_llm(texto)
    if "```json" in texto:
        texto = texto.split("```json")[1].split("```")[0].strip()
    elif "```" in texto:
        texto = texto.split("```")[1].split("```")[0].strip()
    
    ini = texto.find("{")
    fin = texto.rfind("}")
    if ini != -1 and fin != -1 and fin > ini:
        texto = texto[ini:fin+1]
    return json.loads(texto)

PROMPT_GUION = """Eres un divulgador y guionista viral experto en tecnología, ciencia e inteligencia artificial para TikTok y Reels.
Crea un guion impecable de {duracion} segundos sobre el tema: "{tema}".

DATOS DE INVESTIGACIÓN TÉCNICA ESTRUCTURADA:
- Resumen Técnico: {resumen_tecnico}
- Hechos Científicos Clave: {hechos_clave}
- Términos Clave: {terminologia}
- Enfoque Narrativo: {angulo}

REGLAS NARRATIVAS DE ALTA CONVERSIÓN:
- Gancho disruptivo en las primeras 5 palabras (debe congelar el scroll al instante).
- Historia dividida en 3 actos fluidos: Gancho -> 2 a 3 datos impactantes en USD/cifras -> Cierre de alto valor + CTA sutil.
- Puntuación PERFECTA: Usa puntos y comas de forma estratégica para dictar el ritmo y las pausas naturales de la voz.
- Lenguaje fascinante, claro y 100% riguroso. Cada oración debe estar completa y terminar en punto.

REGLAS DE IDIOMA Y AUDIENCIA:
- Español NEUTRO panlatino (sin modismos ni regionalismos).
- Todas las cifras o referencias económicas deben estar expresadas en dólares estadounidenses (USD).

REGLAS DE FORMATO LIMPIO:
- Devuelve exclusivamente el texto final que será narrado en voz alta.
- PROHIBIDO incluir encabezados, etiquetas ("HOOK:", "NARRADOR:"), paréntesis, corchetes o símbolos markdown (#, *, _).
- PROHIBIDO dejar oraciones inconclusas o cortar el texto a la mitad."""

PROMPT_IMAGENES = """Genera 4 prompts en inglés para imágenes verticales 9:16 sobre este tema de TikTok: "{tema}".

Cada prompt debe ser:
- Cinematic, high detail, dramatic lighting
- Vertical 9:16 composition
- Sin texto, sin logos, sin personas reales famosas, sin copyright
- Safe for work

Devuelve SOLO un JSON válido con formato:
{{"prompts": ["prompt1", "prompt2", "prompt3", "prompt4"]}}"""


def generar_guion(tema: str, duracion: int = 40, investigacion: dict = None) -> str:
    config = cargar_config()
    ia = config["ia"]
    
    if not investigacion:
        resumen_tecnico = f"Conceptos avanzados sobre {tema}"
        hechos_clave = [f"Desarrollo clave en {tema}", "Innovación técnica comprobada", "Impacto cuantitativo relevante en USD"]
        terminologia = "tecnología, innovación, avance"
        angulo = "revolución tecnológica"
    else:
        resumen_tecnico = investigacion.get("resumen_tecnico", tema)
        hechos_clave = investigacion.get("hechos_clave", [])
        terminologia = ", ".join(investigacion.get("terminologia_tecnica", []))
        angulo = investigacion.get("angulo_viral", "innovación")
        
    prompt = PROMPT_GUION.format(
        tema=tema,
        duracion=duracion,
        resumen_tecnico=resumen_tecnico,
        hechos_clave=json.dumps(hechos_clave, ensure_ascii=False),
        terminologia=terminologia,
        angulo=angulo
    )
    
    if ia["proveedor"] in ("ollama_remote", "ollama"):
        host = ia.get("host_remoto", "http://100.95.107.65:11434") if ia["proveedor"] == "ollama_remote" else "http://localhost:11434"
        try:
            r = requests.post(
                f"{host}/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False},
                timeout=90
            )
            if r.status_code == 200:
                res = r.json().get("response", "").strip()
                if res:
                    return res
        except Exception as e:
            print(f"   ⚠️ Conexión con {ia['proveedor']} ({host}) falló ({e}). Conmutando a Ollama local...")

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
                    "temperature": 0.7
                },
                timeout=60
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"].strip()
                if content:
                    return content
        except Exception as e:
            print(f"   ⚠️ Conexión con {ia['proveedor']} falló ({e}). Conmutando a Ollama local...")
            
    # Fallback local a Ollama (qwen2.5:14b o qwen3:8b)
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:14b", "prompt": prompt, "stream": False},
            timeout=30
        )
        if r.status_code == 200:
            res = r.json().get("response", "").strip()
            if res:
                return res
    except Exception:
        pass

    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen3:8b", "prompt": prompt, "stream": False},
            timeout=30
        )
        if r.status_code == 200:
            res = r.json().get("response", "").strip()
            res = limpiar_respuesta_llm(r.json().get("response", "")).strip()
            if res:
                return res
    except Exception:
        pass
        
    print("   ⚠️ Todas las llamadas de IA fallaron. Usando plantilla de guion de emergencia.")
    return f"¿Sabías esto sobre {tema}? Los últimos datos demuestran un avance revolucionario con un impacto directo en dólares USD. La tecnología sigue transformando nuestro mundo a pasos agigantados. Síguenos para descubrir más noticias e innovaciones hoy mismo."


def generar_prompts_imagenes(tema: str) -> list:
    config = cargar_config()
    ia = config["ia"]
    prompt = PROMPT_IMAGENES.format(tema=tema)
    
    try:
        if ia["proveedor"] in ("ollama", "ollama_remote"):
            host = ia.get("host_remoto", "http://100.95.107.65:11434") if ia["proveedor"] == "ollama_remote" else "http://localhost:11434"
            r = requests.post(
                f"{host}/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=90
            )
            data = extraer_json_valido(r.json().get("response", "{}"))
        else:
            base = ia.get("base_url", "https://api.openai.com/v1")
            r = requests.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {ia['api_key']}"},
                json={
                    "model": ia["modelo"],
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            data = extraer_json_valido(r.json()["choices"][0]["message"]["content"])
        
        return data.get("prompts", [])[:4]
    except Exception as e:
        print(f"⚠️ Error generando prompts de imagen: {e}")
        return [f"Cinematic vertical 9:16 image about {tema}, dramatic lighting, no text"] * 4


PROMPT_IMAGENES_GUION = """Analiza este guion de TikTok y sus datos de investigación técnica para generar exactamente {n} prompts de imágenes (en inglés) que tengan un 100% de coherencia y concordancia visual con el tema tratado.

TEMA Y GUION:
"{guion}"

ELEMENTOS VISUALES INVESTIGADOS:
{elementos_visuales}

REQUISITOS DE CONCORDANCIA Y CALIDAD:
- Cada prompt debe describir de forma ultra-precisa el objeto, tecnología, entorno o concepto específico mencionado en esa escena (MÍNIMO 75% de concordancia directa).
- Estilo visual: photorealistic, 8k resolution, cinematic lighting, masterfully composed, 9:16 vertical orientation, hyperrealistic details.
- PROHIBIDO: animales fuera de contexto, objetos irrelevantes, personas famosas reales, texto superpuesto, agua o marcas.
- Idioma: Inglés.

Devuelve SOLO un JSON válido con formato:
{{"prompts": ["prompt_escena_1", "prompt_escena_2", ..., "prompt_escena_{n}"]}}"""

def generar_prompts_para_guion(guion: str, n: int, investigacion: dict = None) -> list:
    config = cargar_config()
    ia = config["ia"]
    
    elementos_str = "N/A"
    if investigacion and "elementos_visuales" in investigacion:
        elementos_str = json.dumps(investigacion["elementos_visuales"], ensure_ascii=False)
        
    prompt = PROMPT_IMAGENES_GUION.format(guion=guion, n=n, elementos_visuales=elementos_str)
    
    try:
        if ia["proveedor"] in ("ollama", "ollama_remote"):
            host = ia.get("host_remoto", "http://100.95.107.65:11434") if ia["proveedor"] == "ollama_remote" else "http://localhost:11434"
            r = requests.post(
                f"{host}/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=90
            )
            data = extraer_json_valido(r.json().get("response", "{}"))
        else:
            base = ia.get("base_url", "https://api.openai.com/v1")
            headers = {}
            if "api_key" in ia:
                headers["Authorization"] = f"Bearer {ia['api_key']}"
            r = requests.post(
                f"{base}/chat/completions",
                headers=headers,
                json={
                    "model": ia["modelo"],
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            data = extraer_json_valido(r.json()["choices"][0]["message"]["content"])
        
        prompts = data.get("prompts", [])
        if len(prompts) < n:
            while len(prompts) < n:
                prompts.append(prompts[-1] if prompts else "Cinematic vertical 9:16 high detail image, photorealistic, 8k")
        return prompts[:n]
    except Exception as e:
        print(f"⚠️ Error generando prompts secuenciales: {e}")
        return ["Cinematic vertical 9:16 high detail image, photorealistic, 8k"] * n

def descargar_imagen(prompt: str, ruta: Path):
    """Usa Pollinations.ai (gratis, sin API key)."""
    config = cargar_config()
    prov = config["imagenes"]["proveedor"]
    
    if prov == "pollinations":
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true&seed=42"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            ruta.write_bytes(r.content)
            return True
    
    # Aquí puedes añadir Stability AI, Replicate, etc.
    return False

PROMPT_REVISION = """Eres un editor experto de TikTok. Revisa este guion y devuelveme JSON:

GUION:
{guion}

Evalúa:
1. ¿El hook detiene el scroll en 2 segundos? (0-25)
2. ¿Es claro y simple? (0-25)
3. ¿Tiene ritmo y datos interesantes? (0-25)
4. ¿El cierre es memorable + CTA? (0-25)

Devuelve SOLO JSON válido:
{{
  "score": 75,
  "aprobado": true,
  "feedback": "el hook es débil, empieza con una pregunta impactante",
  "guion_mejorado": "versión mejorada del guion completo"
}}

Si score >= 70, aprobado=true. Si no, aprobado=false y guion_mejorado debe ser una versión mejor."""

def revisar_guion(guion: str) -> dict:
    config = cargar_config()
    ia = config["ia"]
    prompt = PROMPT_REVISION.format(guion=guion)
    
    try:
        if ia["proveedor"] == "ollama":
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=120
            )
            return json.loads(r.json().get("response", "{}"))
        else:
            base = ia.get("base_url", "https://api.openai.com/v1")
            r = requests.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {ia['api_key']}"},
                json={
                    "model": ia["modelo"],
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            return json.loads(r.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"      ⚠️ Revisión falló: {e}")
        return {"aprobado": True, "guion_mejorado": guion, "score": 70}