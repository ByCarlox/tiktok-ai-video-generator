# trends.py
import json
import yaml
from datetime import datetime
from pathlib import Path
from pytrends.request import TrendReq
import feedparser

def cargar_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def tendencias_google_news(paises) -> list:
    """Obtiene noticias en tendencia desde Google News RSS para múltiples países LATAM."""
    if isinstance(paises, str):
        paises = [paises]
    
    titulos = []
    vistos = set()
    
    for pais in paises:
        pais = pais.upper()
        idioma = "es-419" if pais in ("MX", "AR", "CO", "PE", "CL", "VE") else "es"
        url = f"https://news.google.com/rss?hl={idioma}&gl={pais}&ceid={pais}:{idioma}"
        
        print(f"   📡 Google News RSS ({pais})...")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                titulo = entry.title
                if " - " in titulo:
                    titulo = titulo.rsplit(" - ", 1)[0]
                titulo = titulo.strip()
                # Deduplicar títulos muy parecidos entre países
                titulo_key = titulo.lower()[:40]
                if titulo_key not in vistos:
                    vistos.add(titulo_key)
                    titulos.append(titulo)
        except Exception as e:
            print(f"   ⚠️ Google News RSS ({pais}) falló: {e}")
    
    return titulos

def tendencias_google(paises, categorias):
    """Obtiene búsquedas en aumento desde Google News RSS (principal) y pytrends (fallback)."""
    news_trends = tendencias_google_news(paises)
    if news_trends:
        return news_trends
        
    # Fallback: related queries de las categorías (usa primer país)
    resultados = []
    pais_principal = paises[0] if isinstance(paises, list) else paises
    try:
        pytrends = TrendReq(hl="es", tz=360)
        for cat in categorias[:3]:
            pytrends.build_payload([cat], timeframe="now 7-d", geo=pais_principal)
            related = pytrends.related_queries()
            if cat in related and related[cat]["top"] is not None:
                top = related[cat]["top"]["query"].head(5).tolist()
                resultados.extend(top)
    except Exception as e:
        print(f"⚠️ Related queries falló: {e}")
    
    return resultados[:20] if resultados else categorias

def tendencias_rss():
    """Fuente principal: RSS especializados en tech, IA, ciencia espacial, hardware y misterios de la ciencia."""
    feeds = [
        # 1. Inteligencia Artificial & Robótica (Español e Inglés)
        "https://www.xataka.com/categoria/inteligencia-artificial/feed",
        "https://www.genbeta.com/categoria/inteligencia-artificial/feed",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://wwwhatsnew.com/feed/",
        
        # 2. Ciencia Espacial, James Webb & Física Cuántica
        "https://feeds.bbci.co.uk/mundo/temas/ciencia/rss.xml",
        "https://elpais.com/ciencia/rss/feed.html",
        "https://feeds.arstechnica.com/arstechnica/science",
        "https://www.space.com/feeds/news",
        "https://phys.org/rss-feed/space-news/",
        "https://phys.org/rss-feed/physics-news/",
        
        # 3. Hardware Extremo, Gadgets & Superchips (RTX, M-series, Cuántica)
        "https://www.xataka.com/feed",
        "https://hipertextual.com/feed",
        "https://wccftech.com/feed/",
        "https://videocardz.com/rss-feed",
        "https://9to5mac.com/feed/",
        
        # 4. Misterios de la Ciencia, Biología & Descubrimientos Fascinantes
        "https://www.nationalgeographic.com.es/medio/rss.xml",
        "https://www.muyinteresante.com/ciencia/feed",
        "https://phys.org/rss-feed/biology-news/",
        
        # 5. Startups, Innovación & Economía del Futuro (USD)
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ]
    titulos = []
    vistos = set()
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                t = entry.title
                if " - " in t:
                    t = t.rsplit(" - ", 1)[0]
                t = t.strip()
                t_key = t.lower()[:35]
                if t_key not in vistos and len(t) > 15:
                    vistos.add(t_key)
                    titulos.append(t)
        except:
            pass
    return titulos

# Palabras clave que indican que un tema es relevante para el canal
PALABRAS_RELEVANTES = [
    # IA y modelos
    "ia", "inteligencia artificial", "ai", "chatgpt", "gpt", "openai", "google", "gemini",
    "deepmind", "anthropic", "claude", "llama", "mistral", "copilot", "perplexity",
    "robot", "tecnolog", "algoritmo", "machine learning", "deep learning", "neural",
    "model", "artificial", "autonom", "generativ",
    # Datos y programación
    "dato", "data", "big data", "nube", "cloud", "servidor", "programar", "código",
    "python", "javascript", "developer", "api", "open source",
    "app", "software", "hardware", "chip", "procesador", "gpu", "nvidia", "amd", "intel",
    # Ciencia
    "ciencia", "científic", "investigación", "descubr", "estudio", "experimento",
    "espacio", "nasa", "spacex", "marte", "luna", "satélite", "telescopio", "astronomía",
    "rocket", "orbit", "launch", "spacecraft",
    "física", "cuánt", "quantum", "partícula", "energía", "fusión",
    # Neuro y psicología
    "cerebro", "neuro", "psicolog", "cognitiv", "mente", "memoria", "aprendizaje",
    # Innovación y negocio tech
    "futuro", "innovación", "startup", "emprendimiento", "disrupt",
    "productividad", "hábito", "eficiencia", "automatiz",
    "cripto", "bitcoin", "blockchain", "fintech",
    # Biotech y salud tech
    "salud", "adn", "gen", "célula", "médic", "biotecnología",
    # Curiosidades científicas
    "curiosidad", "increíble", "misterio", "universo", "evolución",
    # Marcas tech
    "apple", "tesla", "microsoft", "meta", "amazon", "samsung",
    "iphone", "pixel", "android", "ios", "mac",
    "smartphone", "gadget", "wearable", "realidad virtual", "realidad aumentada",
    "drone", "vehículo eléctrico", "electric vehicle",
    # Seguridad
    "ciberseguridad", "hacker", "privacidad", "internet", "hack", "breach",
    "deepfake", "phishing", "malware", "ransomware",
]

# Palabras que indican temas fuera de foco (política local, deportes, farándula, noticias locales)
PALABRAS_IRRELEVANTES = [
    # Política de cualquier país
    "presidente", "presidenta", "senado", "congreso", "diputad", "partido",
    "eleccion", "gobierno", "mañanera", "sheinbaum", "trump", "biden",
    "reforma", "constituc", "ministro", "embajad", "legislat",
    "milei", "petro", "boric", "maduro", "lula",
    # Deportes
    "futbol", "fútbol", "gol ", "liga mx", "champions", "seleccion", "selección",
    "beisbol", "béisbol", "boxeo", "olimpi", "copa américa", "libertadores",
    # Universidades y educación local
    "unam", "universidad", "examen de admisión", "aspirantes", "tu sitio",
    "politécnico", "admision",
    # Farándula
    "telenovela", "reality", "farándula", "influencer",
    # Eventos naturales puntuales
    "eclipse",
    "terremoto", "sismo", "huracán", "inundación",
    "accidente", "tragedia", "incendio",
    # Noticias puramente locales/regionales
    "cdmx", "buenos aires", "bogotá", "santiago",
    "metro ", "transporte público", "vial",
    "peso mexicano", "peso argentino", "peso colombiano",
]

def filtrar_tendencias(trends: list, config: dict) -> list:
    """Filtra tendencias: elimina sensibles + fuera de nicho, prioriza tech/IA/ciencia."""
    filtro = config.get("filtro", {})
    palabras_excluir = [p.lower() for p in filtro.get("palabras_excluir", [])]
    
    trends_filtrados = []
    for trend in trends:
        trend_lower = trend.lower()
        
        # 1. Excluir si contiene palabra prohibida (sensibilidad)
        if any(palabra in trend_lower for palabra in palabras_excluir):
            print(f"   ❌ Filtrado (sensible): {trend[:60]}...")
            continue
        
        # 2. Excluir si contiene palabras claramente irrelevantes
        if any(palabra in trend_lower for palabra in PALABRAS_IRRELEVANTES):
            print(f"   ❌ Filtrado (fuera de nicho): {trend[:60]}...")
            continue
        
        # 3. Solo aceptar temas que tengan al menos una palabra clave de tech/ciencia
        es_relevante = any(palabra in trend_lower for palabra in PALABRAS_RELEVANTES)
        if es_relevante:
            trends_filtrados.append(trend)
        else:
            print(f"   ⏭️  Filtrado (no es tech/ciencia): {trend[:60]}...")
    
    # Si quedaron muy pocas, rellenar con temas universales de tech/ciencia
    if len(trends_filtrados) < 5:
        temas_relleno = [
            "Últimos avances en inteligencia artificial que cambiarán tu vida",
            "Cómo funciona el algoritmo de TikTok según la ciencia de datos",
            "Descubrimientos científicos recientes que deberías conocer",
            "Herramientas de IA que puedes usar gratis hoy mismo",
            "Lo que la neurociencia dice sobre cómo aprendes más rápido",
            "Gadgets y tecnología del futuro que ya existen",
            "Secretos de productividad respaldados por la ciencia",
            "Datos curiosos sobre el universo que nadie te contó",
            "Cómo la inteligencia artificial está revolucionando la medicina",
            "Los trabajos que la IA no podrá reemplazar nunca",
        ]
        print(f"   ⚠️ Pocas tendencias relevantes ({len(trends_filtrados)}), añadiendo temas de nicho...")
        for tema in temas_relleno:
            if tema not in trends_filtrados:
                trends_filtrados.append(tema)
    
    return trends_filtrados

def calcular_score_viralidad(tema: str) -> float:
    """Calcula un puntaje de viralidad (0-100) basado en detonantes psicológicos y términos de alto impacto."""
    score = 50.0
    t_lower = tema.lower()
    
    # Detonantes de curiosidad e impacto positivo
    triggers = {
        "ia": 15, "ai": 15, "chatgpt": 15, "google": 12, "apple": 12, "nvidia": 15, "claude": 15,
        "nuevo": 10, "nueva": 10, "gratis": 12, "futuro": 10, "cambia": 10, "secreto": 12,
        "revolución": 10, "chip": 10, "ciencia": 8, "descubrimiento": 10, "dólares": 8, "usd": 8
    }
    for kw, val in triggers.items():
        if kw in t_lower:
            score += val
            
    # Penalizar títulos demasiado cortos o vagos
    if len(tema.split()) < 4:
        score -= 15.0
        
    return max(0.0, min(100.0, score))


def main():
    config = cargar_config()
    print("🔍 Buscando tendencias tech/IA/ciencia para LATAM...")
    
    # 1. RSS especializados primero (fuente principal, sin sesgo regional)
    print("📡 Consultando RSS de tech, IA y ciencia...")
    trends_rss = tendencias_rss()
    
    # 2. Google News de múltiples países LATAM como complemento
    paises = config["pais_tendencia"]
    if isinstance(paises, str):
        paises = [paises]
    trends_google = tendencias_google(paises, config["categorias"])
    
    # Combinar: RSS primero (más relevantes), Google News después
    trends = trends_rss + trends_google
    
    # 3. Filtrar sensibilidad + relevancia de nicho
    print("🛡️  Filtrando por nicho tech/IA/ciencia...")
    trends = filtrar_tendencias(trends, config)
    
    # 4. Filtro del Cerebro de Obsidian (Cero temas repetidos)
    from obsidian_brain import verificar_duplicado
    print("🧠 Consultando memoria de Obsidian para descartar temas ya tratados...")
    trends_frescos = []
    for t in trends:
        es_dup, motivo, tema_antiguo = verificar_duplicado(t)
        if es_dup:
            print(f"   ⏭️  [Cerebro Obsidian] Descartado ({motivo}): {t[:55]}...")
        else:
            trends_frescos.append(t)
            
    trends = trends_frescos if trends_frescos else trends
    
    # Limpiar y deduplicar
    trends = list(dict.fromkeys([t.strip() for t in trends if t]))
    
    # Ordenar por Scoring de Viralidad (mayor potencia al principio)
    trends.sort(key=lambda t: calcular_score_viralidad(t), reverse=True)
    trends = trends[:20]
    
    salida = {
        "fecha": datetime.now().isoformat(),
        "tendencias": trends
    }
    
    Path("output").mkdir(exist_ok=True)
    with open("output/trends.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(trends)} tendencias guardadas y ordenadas por Virality Score")
    for i, t in enumerate(trends[:8], 1):
        score_v = calcular_score_viralidad(t)
        print(f"   {i}. [{score_v:.0f}/100 🔥] {t}")

if __name__ == "__main__":
    main()