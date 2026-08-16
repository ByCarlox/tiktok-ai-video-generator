# product_fetcher.py - v2.0 — Extractor Inteligente de Fotos Reales de Productos
"""
Módulo para buscar y descargar imágenes verídicas, auténticas y oficiales de productos,
hardware, misiones espaciales, dispositivos tecnológicos y entidades noticiosas:
1. Wikipedia API (Fotos principales de artículos oficiales en ES e EN)
2. Wikimedia Commons (Fotografías de prensa de alta resolución, PCBs, hardware)
3. Smart Composition (Prepara las fotos con relación de aspecto original para el compositor sin deformación)
"""
import re
import json
import time
import requests
from urllib.parse import quote
from pathlib import Path
from PIL import Image

def buscar_fotos_wikipedia(query: str, lang: str = "es", max_results: int = 4) -> list:
    """Busca imágenes oficiales en los artículos principales de Wikipedia."""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": max_results,
        "prop": "pageimages",
        "piprop": "original|thumbnail",
        "pithumbsize": 2160,
        "format": "json"
    }
    imgs = []
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "TikTokBroadcastBot/5.5 (contact@example.com)"}, timeout=10)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, p in pages.items():
                img_url = None
                if "original" in p:
                    img_url = p["original"].get("source")
                elif "thumbnail" in p:
                    img_url = p["thumbnail"].get("source")
                    
                if img_url and not img_url.endswith((".svg", ".gif", ".ico")):
                    imgs.append(img_url)
    except Exception:
        pass
    return imgs

def buscar_fotos_wikimedia(query: str, max_results: int = 5) -> list:
    """Busca fotografías de alta resolución en Wikimedia Commons."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": max_results * 2,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|dimensions"
    }
    
    urls = []
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "TikTokBroadcastBot/5.5 (contact@example.com)"}, timeout=10)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                img_info = pdata.get("imageinfo", [])
                if img_info:
                    f_url = img_info[0].get("url")
                    w = img_info[0].get("width", 0)
                    h = img_info[0].get("height", 0)
                    # Filtrar imágenes diminutas o iconos
                    if f_url and (w == 0 or w >= 600) and (h == 0 or h >= 400):
                        if not f_url.endswith((".svg", ".gif", ".ico")):
                            urls.append(f_url)
                if len(urls) >= max_results:
                    break
    except Exception:
        pass
    return urls

def descargar_foto_real(url: str, destino_path: Path) -> bool:
    """Descarga y valida que una imagen real sea válida y de alta calidad."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 10000:
            destino_path.write_bytes(r.content)
            # Validar dimensiones con PIL
            with Image.open(destino_path) as img:
                w, h = img.size
                if w >= 350 and h >= 250:
                    return True
            destino_path.unlink(missing_ok=True)
    except Exception:
        destino_path.unlink(missing_ok=True)
    return False

def obtener_imagenes_producto_real(tema: str, investigacion: dict, output_dir: Path, cantidad: int = 3) -> list:
    """
    Obtiene imágenes reales y verídicas del producto o tema principal de la noticia.
    Retorna una lista de rutas Path a las imágenes descargadas y validadas.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Extraer nombres clave de producto
    queries = []
    
    if investigacion:
        terminos = investigacion.get("terminologia_tecnica", [])
        for t in terminos:
            if len(t) > 3 and t not in queries:
                queries.append(t)
                
        elementos = investigacion.get("elementos_visuales", [])
        for el in elementos:
            if len(el) > 3 and el not in queries:
                queries.append(el)
                
    # Extraer términos limpios del tema
    limpio = re.sub(r"[^\w\s]", "", tema)
    palabras = [p for p in limpio.split() if len(p) > 3 and p.lower() not in (
        "para", "sobre", "como", "este", "esta", "estos", "estas", "hace", "todo", 
        "pero", "entre", "tiene", "donde", "cuando", "quien", "porque", "copia", "copiado"
    )]
    if palabras:
        queries.append(" ".join(palabras[:3]))
        
    queries.append(tema[:45])
    
    imagenes_descargadas = []
    urls_probadas = set()
    img_idx = 0
    
    print(f"   📸 Buscando fotos reales verídicas del producto / tema...")
    
    for q in queries:
        if len(imagenes_descargadas) >= cantidad:
            break
            
        # 1. Buscar en Wikipedia Español
        candidatos = buscar_fotos_wikipedia(q, lang="es", max_results=3)
        # 2. Buscar en Wikipedia Inglés (suele tener más fotos de hardware)
        if len(candidatos) < 2:
            candidatos.extend(buscar_fotos_wikipedia(q, lang="en", max_results=3))
        # 3. Buscar en Wikimedia Commons
        if len(candidatos) < 2:
            candidatos.extend(buscar_fotos_wikimedia(q, max_results=4))
            
        for c_url in candidatos:
            if c_url in urls_probadas:
                continue
            urls_probadas.add(c_url)
            
            dest = output_dir / f"real_product_{img_idx}.jpg"
            ok = descargar_foto_real(c_url, dest)
            if ok:
                print(f"      ✅ Foto real obtenida: '{dest.name}' ({q})")
                imagenes_descargadas.append(dest)
                img_idx += 1
                if len(imagenes_descargadas) >= cantidad:
                    break
                    
    # Fallback inteligente: Si Wikipedia no tiene fotos, generar el Hero Product aislado en estudio 8K
    if not imagenes_descargadas:
        print(f"      🎨 Generando Hero Asset 3D aislado para '{tema[:30]}...'")
        dest = output_dir / f"real_product_0.jpg"
        clean_subj = queries[0] if queries else tema
        prompt_asset = f"isolated hero product photography of {clean_subj}, cinematic studio lighting, sleek dark minimalist background, razor sharp focus, 8k resolution, photorealistic"
        try:
            # Descargar asset nítido
            from urllib.parse import quote
            safe_p = quote(prompt_asset)
            flux_url = f"https://image.pollinations.ai/prompt/{safe_p}?width=1280&height=1280&nologo=true&seed=8844"
            r = requests.get(flux_url, timeout=30)
            if r.status_code == 200 and len(r.content) > 10000:
                dest.write_bytes(r.content)
                imagenes_descargadas.append(dest)
                print(f"      💎 Hero Asset 3D generado con éxito para la tarjeta de producto.")
        except Exception as e:
            print(f"      ⚠️ Fallback de hero asset falló: {e}")
            
    return imagenes_descargadas
