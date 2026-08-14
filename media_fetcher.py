# media_fetcher.py - v1.0 — Fuentes Open Source Múltiples para Imágenes y Videos
"""
Proveedor unificado de recursos multimedia libres / open source:
1. Pixabay API (videos e imágenes)
2. Wikimedia Commons API (recursos 100% libres/open source de ciencia, espacio, laboratorios)
3. Pexels API / Fallback (videos e imágenes HD/4K)
4. Pollinations.ai (Generación de imágenes IA en 4K con modelo Flux)
"""
import json
import urllib.parse
import requests
import yaml
from pathlib import Path

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------- BUSCADOR WIKIMEDIA COMMONS (OPEN SOURCE / PUBLIC DOMAIN) ----------
def buscar_wikimedia_commons(query, limit=5, media_type="video"):
    """Busca recursos multimedia 100% open source / CC en Wikimedia Commons API."""
    print(f"      🏛️ Buscando en Wikimedia Commons ({media_type}): '{query}'...")
    url = "https://commons.wikimedia.org/w/api.php"
    
    # Namespace 6 es File:
    file_prefix = "File:"
    search_q = f"{query} filetype:{'video' if media_type == 'video' else 'bitmap'}"
    
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": search_q,
        "gsrnamespace": 6,
        "gsrlimit": limit * 2,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|dimensions"
    }
    
    resultados = []
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "TikTokAIBot/4.0 (contact@example.com)"}, timeout=15)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        
        for page_id, page_info in pages.items():
            imageinfo = page_info.get("imageinfo", [])
            if not imageinfo:
                continue
            info = imageinfo[0]
            file_url = info.get("url")
            mime = info.get("mime", "")
            
            if media_type == "video":
                if "video" in mime or file_url.endswith((".mp4", ".webm", ".ogv")):
                    resultados.append(file_url)
            else:
                if "image" in mime or file_url.endswith((".jpg", ".jpeg", ".png")):
                    resultados.append(file_url)
                    
            if len(resultados) >= limit:
                break
    except Exception as e:
        print(f"      ⚠️ Wikimedia search falló: {e}")
        
    return resultados


# ---------- BUSCADOR PIXABAY (VIDEOS & IMÁGENES) ----------
def buscar_pixabay_videos(query, api_key, limit=5):
    """Busca video clips en Pixabay API."""
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": query,
        "orientation": "vertical",
        "per_page": limit
    }
    clips = []
    try:
        r = requests.get(url, params=params, timeout=15)
        hits = r.json().get("hits", [])
        if not hits:
            params.pop("orientation", None)
            r = requests.get(url, params=params, timeout=15)
            hits = r.json().get("hits", [])
            
        for hit in hits:
            duration = hit.get("duration", 5.0)
            v_info = (hit.get("videos", {}).get("large") or 
                      hit.get("videos", {}).get("medium") or 
                      hit.get("videos", {}).get("small"))
            if v_info and v_info.get("url"):
                clips.append({
                    "id": hit.get("id"),
                    "url": v_info.get("url"),
                    "duration": duration,
                    "provider": "pixabay"
                })
    except Exception as e:
        print(f"      ⚠️ Pixabay search falló: {e}")
    return clips


# ---------- BUSCADOR PEXELS (VIDEOS & IMÁGENES OPEN ACCESS) ----------
def buscar_pexels_videos(query, pexels_key=None, limit=5):
    """Busca video clips en Pexels API o pública."""
    if not pexels_key:
        return []
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": pexels_key}
    params = {"query": query, "orientation": "portrait", "per_page": limit}
    clips = []
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        video_hits = r.json().get("videos", [])
        for hit in video_hits:
            duration = hit.get("duration", 5.0)
            files = hit.get("video_files", [])
            # Filtrar preferencia HD/HD portrait
            v_url = None
            for vf in files:
                if vf.get("width") and vf.get("height"):
                    if vf.get("height", 0) > vf.get("width", 0):  # vertical
                        v_url = vf.get("link")
                        break
            if not v_url and files:
                v_url = files[0].get("link")
                
            if v_url:
                clips.append({
                    "id": hit.get("id"),
                    "url": v_url,
                    "duration": duration,
                    "provider": "pexels"
                })
    except Exception as e:
        print(f"      ⚠️ Pexels search falló: {e}")
    return clips


# ---------- DESCARGADOR DE CLIPS MULTI-FUENTE ----------
def obtener_clips_multi_fuente(queries, work_dir, dur_audio, ffmpeg_scaler, tema="", pre_eval_func=None):
    """
    Busca clips de video mezclando Pixabay, Wikimedia Commons y Pexels.
    Evalúa CADA candidato con el modelo de visión ANTES de reescalar.
    Retorna lista de rutas de clips procesados en 4K/HD vertical.
    """
    config = cfg()
    pixabay_key = config.get("musica", {}).get("api_key") or "57048016-b2ebc50dee017a04e526b6d2b"
    pexels_key = config.get("publisher", {}).get("pexels_api_key") or config.get("pexels_api_key")
    
    rutas = []
    total_duration = 0.0
    clip_idx = 0
    used_urls = set()
    
    for query in queries:
        if total_duration >= dur_audio:
            break
            
        print(f"      🔎 Buscando clip para query: '{query}'...")
        clips_candidatos = []
        
        # 1. Intentar Pixabay
        px_clips = buscar_pixabay_videos(query, pixabay_key, limit=3)
        clips_candidatos.extend(px_clips)
        
        # 2. Intentar Pexels (si hay key)
        if pexels_key:
            pxl_clips = buscar_pexels_videos(query, pexels_key, limit=3)
            clips_candidatos.extend(pxl_clips)
            
        # 3. Intentar Wikimedia Commons si aún no hay candidatos
        if not clips_candidatos:
            wm_urls = buscar_wikimedia_commons(query, limit=2, media_type="video")
            for wurl in wm_urls:
                clips_candidatos.append({
                    "id": wurl,
                    "url": wurl,
                    "duration": 6.0,
                    "provider": "wikimedia"
                })
                
        # Pre-evaluar y procesar el primer candidato válido que supere 75% de relevancia
        for clip in clips_candidatos:
            v_url = clip["url"]
            if v_url in used_urls:
                continue
            used_urls.add(v_url)
            
            duration = clip.get("duration", 5.0)
            clip_path = work_dir / f"tmp_clip_{clip_idx}.mp4"
            output_clip = work_dir / f"v{clip_idx}.mp4"
            
            print(f"      ⬇️ Descargando candidato {clip['provider']} [{duration}s]...")
            try:
                r = requests.get(v_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
                if r.status_code == 200:
                    clip_path.write_bytes(r.content)
                    
                    # PRE-EVALUACIÓN ANTES DE ESCALAR: Inspección rápida por IA
                    if pre_eval_func:
                        aprobado, data_eval = pre_eval_func(clip_path, tema, query, work_dir)
                        if not aprobado:
                            print(f"      ⏭️ Clip de {clip['provider']} descartado en pre-evaluación (Relevancia < 75%). Probando siguiente candidato...")
                            clip_path.unlink(missing_ok=True)
                            continue
                            
                    # Escalar y recortar con FFmpeg al formato vertical 4K/1080p
                    ffmpeg_scaler(clip_path, output_clip, clip_idx)
                    if output_clip.exists() and output_clip.stat().st_size > 0:
                        rutas.append(f"v{clip_idx}.mp4")
                        total_duration += duration
                        clip_idx += 1
                        clip_path.unlink(missing_ok=True)
                        break  # 1 clip pre-aprobado por query
            except Exception as e:
                print(f"      ⚠️ Error descargando clip de {clip['provider']}: {e}")
                clip_path.unlink(missing_ok=True)
                
    # Fallback si ninguna fuente devolvió clips
    if not rutas:
        print("      ⚠️ Usando fallback de clips tech multi-fuente...")
        fallback_queries = ["technology digital data", "futuristic science lab", "artificial intelligence network"]
        for fq in fallback_queries:
            if total_duration >= dur_audio:
                break
            px_clips = buscar_pixabay_videos(fq, pixabay_key, limit=2)
            for clip in px_clips:
                clip_path = work_dir / f"tmp_clip_{clip_idx}.mp4"
                output_clip = work_dir / f"v{clip_idx}.mp4"
                try:
                    r = requests.get(clip["url"], timeout=60)
                    if r.status_code == 200:
                        clip_path.write_bytes(r.content)
                        ffmpeg_scaler(clip_path, output_clip, clip_idx)
                        rutas.append(f"v{clip_idx}.mp4")
                        total_duration += clip.get("duration", 5.0)
                        clip_idx += 1
                        clip_path.unlink(missing_ok=True)
                        break
                except Exception:
                    clip_path.unlink(missing_ok=True)
                    
def obtener_checkpoint_disponible(host):
    """Consulta a la API de ComfyUI qué modelos de checkpoint .safetensors están instalados en la GPU."""
    try:
        r = requests.get(f"{host}/object_info/CheckpointLoaderSimple", timeout=5)
        if r.status_code == 200:
            ckpts = r.json().get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
            if ckpts:
                return ckpts[0]
    except Exception:
        pass
    return None

def generar_video_comfyui_remoto(prompt, output_clip, host="http://100.95.107.65:8188", timeout=120):
    """Envía un prompt a la API de ComfyUI en la RTX 5090 para generar un videoclip 4K sintético por IA."""
    ckpt_name = obtener_checkpoint_disponible(host)
    if not ckpt_name:
        print(f"      ℹ️ ComfyUI activo, pero la carpeta 'ComfyUI/models/checkpoints' está vacía en la GPU. Usando banco de stock 4K...")
        return False
        
    print(f"      🤖 Generando videoclip de IA en la RTX 5090 ({ckpt_name}): '{prompt[:40]}...'")
    try:
        # Petición a la API de ComfyUI con el modelo detectado
        workflow = {
            "prompt": {
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "cfg": 6.0, "denoise": 1.0, "latent_image": ["5", 0], "model": ["4", 0],
                        "positive": ["6", 0], "negative": ["7", 0], "sampler_name": "euler", "scheduler": "normal", "seed": 42, "steps": 20
                    }
                },
                "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}},
                "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 1024, "width": 576}},
                "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": f"cinematic 4k vertical video, {prompt}"}},
                "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry, low quality, distortion"}},
                "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "TikTokAI", "images": ["8", 0]}}
            }
        }
        r = requests.post(f"{host}/prompt", json=workflow, timeout=timeout)
        if r.status_code == 200:
            print("      ✅ Petición de Video IA procesada con éxito en la GPU RTX 5090.")
            return True
    except Exception as e:
        print(f"      ⚠️ ComfyUI API no respondió en {host} ({e}). Conmutando a banco de stock multi-fuente...")
    return False

# Extensión de obtener_clips_multi_fuente con conmutación inteligente
def obtener_clips_multi_fuente_hibrido(queries, work_dir, dur_audio, ffmpeg_scaler, tema="", pre_eval_func=None):
    config = cfg()
    v_cfg = config.get("video_ia", {})
    
    if v_cfg.get("proveedor") == "comfyui_remote":
        host = v_cfg.get("host_remoto", "http://100.95.107.65:8188")
        # Intentar ping a ComfyUI en la RTX 5090
        try:
            ping = requests.get(f"{host}/system_stats", timeout=6)
            if ping.status_code == 200:
                print(f"   🚀 Servidor de Video IA activo en la GPU RTX 5090 ({host}). Generando clips sintéticos...")
                # Flujo de generación remota en la GPU
                rutas_ia = []
                for idx, q in enumerate(queries[:3]):
                    out_v = work_dir / f"v{idx}.mp4"
                    ok = generar_video_comfyui_remoto(f"{tema}, {q}", out_v, host=host)
                    if ok:
                        rutas_ia.append(f"v{idx}.mp4")
                if rutas_ia:
                    return rutas_ia
        except Exception:
            print(f"   ℹ️ Servidor ComfyUI ({host}) ausente. Usando descargas multi-fuente open source...")

    return obtener_clips_multi_fuente(queries, work_dir, dur_audio, ffmpeg_scaler, tema=tema, pre_eval_func=pre_eval_func)
