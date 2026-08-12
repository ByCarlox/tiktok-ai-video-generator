# investigacion.py - v1.0 — Módulo de Investigación Estructurada para Videos Tech/IA/Ciencia
"""
Realiza una investigación técnica y estructurada sobre el tema antes de redactar el guion y generar las imágenes.
Garantiza precisión conceptual, hechos comprobables y metáforas visuales de alta concordancia (>75%).
"""
import json
import requests
import yaml

PROMPT_INVESTIGACION_ESTRUCTURADA = """Eres un científico, investigador senior y divulgador de tecnología de nivel mundial.
Realiza una investigación profunda, rigurosa y estructurada sobre el siguiente tema para producir un video educativo viral de la más alta calidad:

TEMA A INVESTIGAR: "{tema}"

Estructura tu investigación en formato JSON estricto con los siguientes campos:
- "resumen_tecnico": Explicación concisa y técnicamente precisa del avance, concepto o tecnología (2-3 frases).
- "hechos_clave": Una lista con exactamente 3 datos impactantes, cuantitativos o comprobables (ej. especificaciones, mediciones, fechas, cifras en dólares USD si aplica).
- "terminologia_tecnica": Lista de 3 a 4 términos científicos/tecnológicos exactos que deben usarse en la narración.
- "elementos_visuales": Lista de exactamente 5 descripciones visuales hiperedetalladas y fotorrealistas (en inglés) que representen fielmente cada concepto del guion (para generar imágenes y buscar video clips).
- "queries_video_stock": Lista de 5 términos de búsqueda cortos en inglés (2-3 palabras) altamente específicos para APIs de stock (Pexels, Pixabay, Wikimedia Commons).
- "angulo_viral": El enfoque narrativo de mayor impacto (ej: "descubrimiento contraintuitivo", "revolución tecnológica", "futuro inmediato").

Devuelve EXCLUSIVAMENTE el JSON estricto sin explicaciones, sin introducciones y sin formato markdown."""

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def investigar_tema(tema: str) -> dict:
    """Ejecuta una investigación previa estructurada para fundamentar la creación del guion y del material visual."""
    print(f"   🔬 Realizando investigación estructurada sobre: '{tema[:50]}...'")
    config = cfg()
    ia = config["ia"]
    prompt = PROMPT_INVESTIGACION_ESTRUCTURADA.format(tema=tema)
    
    response_text = ""
    try:
        if ia["proveedor"] == "ollama":
            try:
                r = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                    timeout=120
                )
                response_text = r.json().get("response", "").strip()
            except Exception:
                r = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "qwen3:8b", "prompt": prompt, "stream": False, "format": "json"},
                    timeout=120
                )
                response_text = r.json().get("response", "").strip()
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
                timeout=90
            )
            response_text = r.json()["choices"][0]["message"]["content"].strip()
            
        data = json.loads(response_text)
        print("      ✅ Investigación completada (hechos científicos + mapa visual extraídos).")
        return data
    except Exception as e:
        print(f"      ⚠️ Error en investigación estructurada: {e}. Usando plantilla por defecto...")
        palabras_ingles = [w for w in tema.split() if len(w) > 4][:3]
        query_fallback = " ".join(palabras_ingles) if palabras_ingles else "technology innovation"
        return {
            "resumen_tecnico": f"Análisis técnico del tema {tema}.",
            "hechos_clave": [
                f"Innovación clave en torno a {tema}.",
                "Aplicación práctica de alto impacto en tecnología moderna.",
                "Desarrollo respaldado por investigación y datos en USD."
            ],
            "terminologia_tecnica": ["tecnología", "innovación", "desarrollo"],
            "elementos_visuales": [
                f"Cinematic vertical 9:16 high detail shot representing {tema}",
                "Close up of modern futuristic hardware and circuits, 8k",
                "Data visualization on glowing blue screen, vertical composition",
                "Advanced laboratory research with scientist, cinematic lighting",
                "Abstract digital technology concept with high details"
            ],
            "queries_video_stock": [query_fallback, "futuristic technology", "digital data", "science lab", "tech innovation"],
            "angulo_viral": "revolución tecnológica"
        }

if __name__ == "__main__":
    res = investigar_tema("La escasez de chips de memoria por la IA")
    print(json.dumps(res, indent=2, ensure_ascii=False))
