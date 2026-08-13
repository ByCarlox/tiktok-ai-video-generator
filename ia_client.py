# ia_client.py
import json
import requests
import yaml
from pathlib import Path

def cargar_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

PROMPT_GUION = """Eres un divulgador y creador viral de TikTok especializado en ciencia, tecnología e inteligencia artificial.
Crea un guion educativo de {duracion} segundos sobre el tema: "{tema}".

DATOS DE INVESTIGACIÓN TÉCNICA ESTRUCTURADA:
- Resumen Técnico: {resumen_tecnico}
- Hechos Científicos Clave: {hechos_clave}
- Términos Clave: {terminologia}
- Enfoque Narrativo: {angulo}

REGLAS ESTRICTAS:
- Gancho brutal en los primeros 2 segundos (que detenga el scroll).
- Lenguaje simple, fascinante, pero con alta rigurosidad científica y precisión.
- Estructura la historia alrededor de los hechos técnicos investigados.
- Cierre con frase memorable y llamado a la acción suave.
- NADA de contenido sexual, violento, odio, marcas registradas protegidas, ni desinformación.

REGLAS DE IDIOMA Y AUDIENCIA:
- Usa español NEUTRO latinoamericano (sin modismos ni regionalismos).
- NO menciones países específicos a menos que sea parte del dato histórico.
- Si mencionas valores o precios, usa SIEMPRE dólares (USD).
- Tu audiencia es toda Latinoamérica.

REGLAS DE FORMATO IMPRESCINDIBLES:
- Devuelve exclusivamente el texto que debe ser leído en voz alta.
- NO incluyas introducciones, preámbulos, saludos ni comentarios.
- NO incluyas etiquetas de sección como "HOOK:", "NARRADOR:", "VISUAL:".
- NO incluyas acotaciones entre corchetes [...] ni paréntesis (...).
- NO uses formato markdown (nada de negritas o numerales).

Solo devuelve el texto listo para ser leído."""

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
    
    if ia["proveedor"] in ("openai", "groq", "nvidia"):
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
            timeout=120
        )
        res = r.json().get("response", "").strip()
        if res:
            return res
    except Exception:
        pass

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3:8b", "prompt": prompt, "stream": False},
        timeout=120
    )
    return r.json().get("response", "").strip()
    
    return ""


def generar_prompts_imagenes(tema: str) -> list:
    config = cargar_config()
    ia = config["ia"]
    prompt = PROMPT_IMAGENES.format(tema=tema)
    
    try:
        if ia["proveedor"] == "ollama":
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=120
            )
            data = json.loads(r.json().get("response", "{}"))
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
            data = json.loads(r.json()["choices"][0]["message"]["content"])
        
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
        if ia["proveedor"] == "ollama":
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=120
            )
            data = json.loads(r.json().get("response", "{}"))
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
            data = json.loads(r.json()["choices"][0]["message"]["content"])
        
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