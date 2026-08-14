# avatar_host.py - v1.0 — Presentador Virtual Faceless por IA en GPU RTX 5090
"""
Módulo para sintetizar y componer un Presentador Virtual Faceless (Cyber Tech Host):
1. Generación del presentador mediante ComfyUI en la RTX 5090 (o Pollinations Flux como resguardo).
2. Composición de clip de Introducción (Intro Host: primeros 3.5 segundos con gancho).
3. Composición de Badge Flotante (Corner Host PIP) con aura cian/neón.
"""
import time
import requests
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

PROMPT_AVATAR_KAWAII = (
    "masterpiece, best quality, ultra-detailed 8k anime aesthetic 3D render, cute kawaii anime girl tech vtuber, "
    "expressive large bright sparkling violet eyes, gentle charming smile, pastel pink and silver twin-tails hair, "
    "wearing futuristic white and sakura pink tech headset with cat-ear neon antennas and holographic mini-mic, "
    "modern anime tech news anchor outfit, vibrant soft studio broadcast lighting, sakura blossom particle aura, "
    "sharp focus, octane render, unreal engine 5 anime style, highly charismatic"
)

PROMPT_AVATAR_CYBER = (
    "cinematic 4k vertical tech news anchor, sleek black tactical hoodie, glowing holographic cyan visor "
    "with subtle digital data reflection, minimalist faceless silhouette, modern futuristic broadcast studio "
    "with soft neon blue and amber rim lighting, masterfully composed, 8k resolution, hyperrealistic details"
)

def generar_avatar_en_rtx5090(output_path: Path, host: str = "http://100.95.107.65:8188", tema: str = "", estilo: str = "kawaii_waifu") -> bool:
    """Envía la petición a ComfyUI en la RTX 5090 para renderizar la presentadora Kawaii Waifu o Cyber Host."""
    print(f"      🌸 Generando Presentadora Virtual [{estilo.upper()}] en la GPU RTX 5090...")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    prompt_base = PROMPT_AVATAR_KAWAII if estilo == "kawaii_waifu" else PROMPT_AVATAR_CYBER
    
    # 1. Intentar con ComfyUI en la GPU
    try:
        r_info = requests.get(f"{host}/object_info/CheckpointLoaderSimple", timeout=4)
        if r_info.status_code == 200:
            ckpts = r_info.json().get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
            if ckpts:
                ckpt_name = ckpts[0]
                prompt_text = f"{prompt_base}, discussing {tema[:40]}" if tema else prompt_base
                
                workflow = {
                    "prompt": {
                        "3": {
                            "class_type": "KSampler",
                            "inputs": {
                                "cfg": 7.0, "denoise": 1.0, "latent_image": ["5", 0], "model": ["4", 0],
                                "positive": ["6", 0], "negative": ["7", 0], "sampler_name": "euler", "scheduler": "normal", "seed": 9999, "steps": 20
                            }
                        },
                        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}},
                        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 1024, "width": 576}},
                        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt_text}},
                        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry, low quality, distortion, ugly, text, watermark"}},
                        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "HostAvatar", "images": ["8", 0]}}
                    }
                }
                
                res = requests.post(f"{host}/prompt", json=workflow, timeout=10)
                if res.status_code == 200:
                    p_id = res.json().get("prompt_id")
                    for _ in range(25):
                        time.sleep(0.5)
                        h = requests.get(f"{host}/history/{p_id}", timeout=5).json()
                        if p_id in h:
                            img_info = h[p_id].get("outputs", {}).get("9", {}).get("images", [{}])[0]
                            fname = img_info.get("filename")
                            if fname:
                                view_url = f"{host}/view?filename={fname}&subfolder={img_info.get('subfolder', '')}&type=output"
                                v_res = requests.get(view_url, timeout=20)
                                if v_res.status_code == 200:
                                    output_path.write_bytes(v_res.content)
                                    print("      ✅ Presentadora Virtual generada exitosamente en la RTX 5090.")
                                    return True
    except Exception as e:
        print(f"      ⚠️ ComfyUI no disponible para avatar ({e}). Usando fallback de Flux...")

    # 2. Fallback de alta resolución con Pollinations Flux
    try:
        from urllib.parse import quote
        url = f"https://image.pollinations.ai/prompt/{quote(prompt_base)}?width=1080&height=1920&model=flux&seed=8888&nologo=true"
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            output_path.write_bytes(r.content)
            print("      ✅ Presentadora Virtual generada exitosamente con Flux.")
            return True
    except Exception:
        pass
        
    return False

def crear_clip_intro_presentador(avatar_img_path: Path, output_clip: Path, duracion: float = 3.5, width: int = 1080, height: int = 1920) -> bool:
    """Crea un clip de introducción vertical de 3.5 segundos con movimiento dinámico hacia la presentadora."""
    output_clip = Path(output_clip)
    output_clip.parent.mkdir(parents=True, exist_ok=True)
    
    if not avatar_img_path.exists():
        return False
        
    try:
        fps = 30
        frames = int(duracion * fps)
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(avatar_img_path.resolve()),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
                   f"zoompan=z='min(zoom+0.0018,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            "-t", f"{duracion:.2f}", "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(output_clip.resolve())
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_clip.exists() and output_clip.stat().st_size > 0
    except Exception as e:
        print(f"      ⚠️ Error creando clip de intro de presentadora: {e}")
        return False

def crear_badge_presentador_flotante(avatar_img_path: Path, output_png: Path, size: int = 240) -> bool:
    """Crea un badge circular transparente con aura brillante para colocar en esquina (PIP)."""
    return crear_overlay_pip_avatar_animado(avatar_img_path, output_png, size=size)

def crear_overlay_pip_avatar_animado(avatar_img_path: Path, output_png: Path, size: int = 280, halo_color=(255, 105, 180)) -> bool:
    """Crea una insignia PIP circular futurista con la Waifu en 3D, anillo de neón sakura pink y etiqueta '♥ AI WAIFU'."""
    try:
        with Image.open(avatar_img_path) as orig:
            img = orig.convert("RGBA")
            w, h = img.size
            crop_size = min(w, int(h * 0.45))
            left = (w - crop_size) // 2
            top = int(h * 0.08)  # Enfoque en rostro y auriculares de gato
            cropped = img.crop((left, top, left + crop_size, top + crop_size))
            cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)
            
            # Máscara circular
            mask = Image.new("L", (size, size), 0)
            draw_m = ImageDraw.Draw(mask)
            draw_m.ellipse((8, 8, size - 8, size - 8), fill=255)
            
            badge_canvas = Image.new("RGBA", (size + 40, size + 60), (0, 0, 0, 0))
            draw_b = ImageDraw.Draw(badge_canvas)
            
            # Sombra profunda
            draw_b.ellipse((16, 20, size + 24, size + 28), fill=(0, 0, 0, 180))
            badge_canvas = badge_canvas.filter(ImageFilter.GaussianBlur(radius=8))
            draw_b = ImageDraw.Draw(badge_canvas)
            
            # Anillo de neón rosa sakura / lavanda
            draw_b.ellipse((16, 16, size + 24, size + 24), outline=halo_color, width=4)
            
            # Pegar el avatar circular
            avatar_circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            avatar_circ.paste(cropped, (0, 0), mask)
            badge_canvas.paste(avatar_circ, (20, 20), mask)
            
            # Etiqueta "♥ AI WAIFU"
            lbl_w, lbl_h = 120, 28
            lbl_x = (size + 40 - lbl_w) // 2
            lbl_y = size + 16
            draw_b.rounded_rectangle([lbl_x, lbl_y, lbl_x + lbl_w, lbl_y + lbl_h], radius=8, fill=(25, 15, 35, 230), outline=(255, 105, 180), width=2)
            draw_b.ellipse([lbl_x + 8, lbl_y + 8, lbl_x + 18, lbl_y + 18], fill=(255, 60, 150, 255))
            
            badge_canvas.save(output_png, "PNG")
            return True
    except Exception as e:
        print(f"      ⚠️ Error creando badge PIP: {e}")
        return False
