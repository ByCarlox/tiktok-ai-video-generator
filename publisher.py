# publisher.py - v1.0
import json
import shutil
import datetime
import requests
import yaml
from pathlib import Path

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _publicar_manual(video_path, meta):
    print("   📝 Copiando a carpeta de publicación manual...")
    video_path = Path(video_path)
    output_dir = Path("output/para_subir")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    dest_video = output_dir / video_path.name
    shutil.copy2(video_path, dest_video)
    
    dest_txt = output_dir / f"{video_path.stem}.txt"
    dest_txt.write_text(meta.get("texto_completo", ""), encoding="utf-8")
    
    print(f"\n{'*' * 60}")
    print(f"📢 PUBLICACIÓN MANUAL REQUERIDA:")
    print(f"   🎥 Video: {dest_video.resolve()}")
    print(f"   🕒 Hora de publicación sugerida: {meta.get('fecha_publicacion_programada')}")
    print(f"   📝 Texto para pegar en TikTok:")
    print(f"{meta.get('texto_completo')}")
    print(f"{'*' * 60}\n")
    return True

def _publicar_metricool(video_path, meta, pub_cfg):
    print("   🌐 Publicando vía Metricool API...")
    api_key = pub_cfg.get("metricool_api_key")
    if not api_key:
        print("      ⚠️ Falta metricool_api_key en config.yaml, usando fallback manual...")
        return _publicar_manual(video_path, meta)
        
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        with open(video_path, "rb") as f:
            files = {"file": f}
            r_upload = requests.post("https://api.metricool.com/v1/upload", headers=headers, files=files, timeout=120)
            
        if r_upload.status_code != 200:
            raise RuntimeError(f"Fallo en la subida a Metricool: HTTP {r_upload.status_code} - {r_upload.text}")
            
        media_url = r_upload.json().get("url")
        if not media_url:
            raise RuntimeError("La subida a Metricool no retornó una URL de media válida.")
            
        dt_prog = datetime.datetime.strptime(meta["fecha_publicacion_programada"], "%Y-%m-%d %H:%M")
        publish_date_str = dt_prog.strftime("%Y-%m-%d %H:%M:%S")
        
        post_data = {
            "text": meta["texto_completo"],
            "publishDate": publish_date_str,
            "mediaUrls": [media_url]
        }
        r_post = requests.post("https://api.metricool.com/v1/posts", headers=headers, json=post_data, timeout=30)
        if r_post.status_code != 200:
            raise RuntimeError(f"Fallo en la creación del post en Metricool: HTTP {r_post.status_code} - {r_post.text}")
            
        print("      ✅ Video programado con éxito en Metricool!")
        return True
    except Exception as e:
        print(f"      ❌ Falló Metricool API: {e}. Usando fallback manual...")
        return _publicar_manual(video_path, meta)

def _publicar_tiktok_oficial(video_path, meta, pub_cfg):
    print("   🎵 Publicando vía TikTok Content Posting API...")
    client_key = pub_cfg.get("tiktok_client_key")
    client_secret = pub_cfg.get("tiktok_client_secret")
    tokens_file = pub_cfg.get("tiktok_tokens_file") or "tokens.json"
    
    if not client_key or not client_secret:
        print("      ⚠️ Faltan claves de API de TikTok en config.yaml, usando fallback manual...")
        return _publicar_manual(video_path, meta)
        
    try:
        tokens_path = Path(tokens_file)
        if not tokens_path.exists():
            raise RuntimeError(f"No existe el archivo de tokens: {tokens_file}")
            
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
        access_token = tokens.get("access_token")
        if not access_token:
            raise RuntimeError("Falta access_token en tokens.json")
            
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        video_size = Path(video_path).stat().st_size
        
        post_body = {
            "post_info": {
                "title": meta.get("titulo", "")[:150],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1
            }
        }
        
        r_init = requests.post(init_url, headers=headers, json=post_body, timeout=30)
        if r_init.status_code != 200:
            raise RuntimeError(f"Fallo en TikTok Init Upload: HTTP {r_init.status_code} - {r_init.text}")
            
        init_data = r_init.json().get("data", {})
        upload_url = init_data.get("upload_url")
        
        if not upload_url:
            raise RuntimeError(f"TikTok Init no devolvió una upload_url válida. Respuesta: {r_init.text}")
            
        headers_upload = {
            "Content-Range": f"bytes 0-{video_size-1}/{video_size}",
            "Content-Length": str(video_size),
            "Content-Type": "video/mp4"
        }
        with open(video_path, "rb") as f:
            r_upload = requests.put(upload_url, headers=headers_upload, data=f, timeout=300)
            
        if r_upload.status_code not in (200, 201, 204):
            raise RuntimeError(f"Fallo subiendo video a TikTok: HTTP {r_upload.status_code} - {r_upload.text}")
            
        print("      ✅ Video subido e iniciado procesamiento en TikTok!")
        return True
    except Exception as e:
        print(f"      ❌ Falló TikTok API oficial: {e}. Usando fallback manual...")
        return _publicar_manual(video_path, meta)

def publicar_video(video_path, meta):
    config = cfg()
    pub_cfg = config.get("publisher", {})
    estrategia = pub_cfg.get("estrategia", "manual").lower()
    
    if estrategia == "metricool":
        return _publicar_metricool(video_path, meta, pub_cfg)
    elif estrategia == "tiktok":
        return _publicar_tiktok_oficial(video_path, meta, pub_cfg)
    else:
        return _publicar_manual(video_path, meta)
