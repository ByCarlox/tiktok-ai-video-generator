# musica.py - v3.0 PREMIUM (Música Lo-Fi / Chillhop con fallbacks de alta calidad)
import json
import re
import subprocess
import requests
import yaml
from hashlib import md5
from pathlib import Path
from urllib.parse import quote

HEADERS = {"User-Agent": "TikTokAIStudio/6.0 (https://github.com/ByCarlox/tiktok-ai-video-generator)"}

# Lista curada de música premium de fondo (Wikimedia Commons CC-BY)
FALLBACK_TRACKS = [
    {
        "titulo": "Sappheiros - Perspective (Lofi Hip Hop)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/09/Sappheiros_-_Perspective_%28Lofi_Hip_Hop%29.ogg",
        "licencia": "CC-BY 3.0",
        "artista": "Sappheiros"
    },
    {
        "titulo": "Lofi by Caden Currie",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Lofi_by_Caden_Currie.mp3",
        "licencia": "CC-BY-SA 4.0",
        "artista": "Caden Currie"
    },
    {
        "titulo": "Lo-fi by PetroVenus",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Lo-fi_by_PetroVenus.mp3",
        "licencia": "CC-BY-SA 4.0",
        "artista": "PetroVenus"
    },
    {
        "titulo": "Kuromaru ft hereafter - laxin (Lo Fi)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Kuromaru_ft_.hereafter_-_%E2%80%99laxin_%28Lo_Fi_Background_Music%29.ogg",
        "licencia": "CC-BY 3.0",
        "artista": "Kuromaru ft hereafter"
    },
    {
        "titulo": "Alexi Action - I Am a Robot (Dark Synthwave)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/17/Alexi_Action_-_I_Am_a_Robot_%28Dark_Synthwave%29.ogg",
        "licencia": "CC-BY-SA 4.0",
        "artista": "Alexi Action"
    },
    {
        "titulo": "Raspberrymusic - Lofi Hip Hop Upbeat",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/ad/Raspberrymusic_-_Lofi_Hip_Hop_Upbeat.ogg",
        "licencia": "CC-BY 3.0",
        "artista": "Raspberrymusic"
    },
    {
        "titulo": "Eighties Action",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eighties_Action_%28ISRC_USUAN1100243%29.mp3",
        "licencia": "CC-BY 3.0",
        "artista": "Kevin MacLeod"
    }
]

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def slugify(t):
    t = re.sub(r"[^\w\s-]", "", t.lower())
    return re.sub(r"[\s_-]+", "-", t)[:40]

# ---------- FUENTE 1: WIKIMEDIA COMMONS ----------
def buscar_commons(genero):
    """Busca audio libre en Wikimedia Commons con descarga directa."""
    # Mapear géneros a búsquedas específicas de lofi/chillhop/synthwave
    mapped = "lofi OR chillhop OR synthwave"
    gl = genero.lower()
    if "ambient" in gl or "relax" in gl:
        mapped = "lofi OR chillhop OR ambient chill"
    elif "electronic" in gl or "tech" in gl or "futur" in gl:
        mapped = "lofi OR synthwave OR electronic beat"
    elif "cine" in gl or "drama" in gl:
        mapped = "synthwave OR cinematic track"

    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:audio ({mapped})",
        "gsrnamespace": 6, "gsrlimit": 20,
        "prop": "imageinfo", "iiprop": "url|extmetadata",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         timeout=20, headers=HEADERS)
        pages = r.json().get("query", {}).get("pages", {})
        tracks = []
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            lic = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
            lic_l = lic.lower()
            # Permitir licencias CC-BY y CC-BY-SA, además de public domain / CC0
            if any(k in lic_l for k in ["public domain", "cc0", "cc zero", "pdm", "cc-by", "attribution", "sharealike"]):
                url = info.get("url", "")
                if url:
                    tracks.append({
                        "titulo": page.get("title", "audio").replace("File:", ""),
                        "url": url,
                        "licencia": lic,
                        "artista": "Wikimedia Commons",
                    })
        return tracks
    except Exception as e:
        print(f"      ⚠️ buscar_commons falló: {e}")
        return []

# ---------- FUENTE 2: INTERNET ARCHIVE (CC0/PD) ----------
def buscar_internet_archive(genero):
    """Busca audio en Internet Archive."""
    q = (
        f'mediatype:(audio) AND (subject:(lofi) OR title:(lofi) OR subject:(synthwave) OR subject:(chillhop)) '
        'AND licenseurl:(*publicdomain*)'
    )
    params = [("q", q), ("fl[]", "identifier"), ("rows", 8), ("page", 1), ("output", "json")]
    try:
        r = requests.get("https://archive.org/advancedsearch.php", params=params,
                         timeout=20, headers=HEADERS)
        docs = r.json().get("response", {}).get("docs", [])
        tracks = []
        for doc in docs:
            ident = doc.get("identifier")
            if ident:
                tracks.extend(tracks_de_archive_item(ident))
            if len(tracks) >= 6:
                break
        return tracks
    except Exception as e:
        print(f"      ⚠️ buscar_internet_archive falló: {e}")
        return []

def tracks_de_archive_item(ident):
    try:
        r = requests.get(f"https://archive.org/metadata/{ident}", timeout=20, headers=HEADERS)
        data = r.json()
        out = []
        for f in data.get("files", []):
            name = f.get("name", "")
            if not name.lower().endswith(".mp3"):
                continue
            dur = float(f.get("length") or 0)
            if not (20 <= dur <= 300):
                continue
            out.append({
                "titulo": name.replace(".mp3", ""),
                "url": f"https://archive.org/download/{ident}/{quote(name)}",
                "licencia": "Public Domain / CC0 (Internet Archive)",
                "artista": str(data.get("metadata", {}).get("creator", "Internet Archive")),
            })
            if len(out) >= 2:
                break
        return out
    except Exception as e:
        return []

# ---------- DESCARGA CON VALIDACIÓN ----------
def descargar_track(url, destino, min_seg=15):
    try:
        print(f"      ⬇️  Descargando...")
        r = requests.get(url, timeout=90, stream=True, headers=HEADERS)
        if r.status_code != 200:
            print(f"      ❌ HTTP {r.status_code}")
            return False
        with open(destino, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        if destino.stat().st_size < 50000:
            destino.unlink(missing_ok=True)
            print(f"      ❌ Archivo demasiado pequeño")
            return False
        # Validar duración real con ffprobe
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(destino)],
            capture_output=True, text=True)
        dur = float(p.stdout.strip() or 0)
        if dur < min_seg:
            destino.unlink(missing_ok=True)
            print(f"      ❌ Demasiado corto ({dur:.0f}s)")
            return False
        print(f"      ✅ Descargado ({dur:.0f}s, {destino.stat().st_size//1024} KB)")
        return True
    except Exception as e:
        print(f"      ❌ Error: {e}")
        destino.unlink(missing_ok=True)
        return False

# ---------- FUNCIÓN PRINCIPAL ----------
def obtener_musica_para(tema, indice=0):
    """Busca, descarga y cachea música de fondo premium de alta calidad."""
    config = cfg()
    mcfg = config.get("musica", {})
    generos = mcfg.get("generos", ["electronic", "ambient", "cinematic"])
    carpeta = Path(mcfg.get("carpeta", "assets/musica"))
    carpeta.mkdir(parents=True, exist_ok=True)
    genero = generos[indice % len(generos)]

    # Determinar extensión del archivo según la caché existente
    cache_prefix = f"track_{slugify(tema)}_{indice}"
    for ext in [".mp3", ".ogg", ".opus", ".wav", ".flac"]:
        cache_test = carpeta / f"{cache_prefix}{ext}"
        if cache_test.exists() and cache_test.stat().st_size > 50000:
            print(f"   ✅ Música en caché: {cache_test.name}")
            return cache_test

    print(f"   🎵 Buscando música premium '{genero}'...")

    # Intentar buscar en Commons primero
    tracks = buscar_commons(genero)
    if not tracks:
        tracks = buscar_internet_archive(genero)

    # Si todo falla, usar los fallbacks premium curados
    if not tracks:
        print("      ⚠️ Buscadores sin resultados -> Usando fallbacks curados")
        tracks = FALLBACK_TRACKS

    # Selección determinista según el tema
    h = int(md5(f"{tema}{indice}".encode()).hexdigest(), 16)
    for offset in range(len(tracks)):
        track = tracks[(h + offset) % len(tracks)]
        url = track["url"]
        
        # Extraer extensión original
        ext = ".mp3"
        url_lower = url.lower()
        for e in [".mp3", ".ogg", ".opus", ".wav", ".flac"]:
            if e in url_lower:
                ext = e
                break
                
        cache_path = carpeta / f"{cache_prefix}{ext}"
        print(f"      🎶 Intentando: '{track['titulo']}' — {track['licencia']}")
        
        if descargar_track(url, cache_path):
            # Guardar metadatos
            (carpeta / f"{cache_prefix}.json").write_text(
                json.dumps(track, ensure_ascii=False, indent=2), encoding="utf-8")
            return cache_path

    # Fallback físico de última instancia
    fallback_track = FALLBACK_TRACKS[indice % len(FALLBACK_TRACKS)]
    ext = ".mp3" if ".mp3" in fallback_track["url"] else ".ogg"
    cache_path = carpeta / f"{cache_prefix}{ext}"
    descargar_track(fallback_track["url"], cache_path)
    return cache_path

if __name__ == "__main__":
    import sys
    tema = sys.argv[1] if len(sys.argv) > 1 else "tecnologia futurista"
    resultado = obtener_musica_para(tema)
    print(f"\n🎉 Música lista en: {resultado}")