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
    """Envía la petición a ComfyUI en la RTX 5090 o reutiliza el modelo master recortado oficial."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 0. Si existe el modelo master recortado en assets/avatar, reutilizarlo para consistencia de marca
    master_cutout = Path("assets/avatar/waifu_master_cutout.png")
    master_jpg = Path("assets/avatar/waifu_master.jpg")
    if estilo == "kawaii_waifu":
        import shutil
        if master_cutout.exists():
            shutil.copy2(master_cutout, output_path)
            print("      💎 Usando Presentadora Master Oficial de la marca (assets/avatar/waifu_master_cutout.png).")
            return True
        elif master_jpg.exists():
            shutil.copy2(master_jpg, output_path)
            print("      💎 Usando Presentadora Master Oficial de la marca (assets/avatar/waifu_master.jpg).")
            return True
            
    print(f"      🌸 Generando Presentadora Virtual [{estilo.upper()}] en la GPU RTX 5090...")
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

def animar_personaje_neuronal_comfyui(avatar_img_path: Path, audio_path: Path, output_clip: Path, host: str = "http://100.95.107.65:8188", duracion: float = 3.5, width: int = 1080, height: int = 1920) -> bool:
    """
    Envía el modelo de la Waifu a ComfyUI en la RTX 5090 para sintetizar
    animación facial y corporal por IA (Wan 2.1 I2V / LivePortrait) con movimiento orgánico completo.
    """
    output_clip = Path(output_clip)
    output_clip.parent.mkdir(parents=True, exist_ok=True)
    
    if not avatar_img_path.exists():
        return False
        
    try:
        r_info = requests.get(f"{host}/object_info", timeout=4)
        if r_info.status_code == 200:
            nodes = r_info.json()
            if "WanImageToVideo" in nodes or "WanInfiniteTalkToVideo" in nodes or "KSampler" in nodes:
                print(f"      🎭 [WAN 2.1 I2V NEURAL ENGINE] Enviando personaje a la GPU RTX 5090...")
                with open(avatar_img_path, 'rb') as f:
                    up_res = requests.post(f"{host}/upload/image", files={'image': f}, timeout=15)
                if up_res.status_code == 200:
                    img_name = up_res.json().get("name", avatar_img_path.name)
                    
                    prompt_workflow = {
                        "prompt": {
                            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors", "weight_dtype": "fp8_e4m3fn"}},
                            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
                            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
                            "4": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
                            "5": {"class_type": "LoadImage", "inputs": {"image": img_name}},
                            "6": {"class_type": "CLIPVisionEncode", "inputs": {"clip_vision": ["4", 0], "image": ["5", 0], "crop": "center"}},
                            "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "masterpiece, best quality, ultra-detailed anime girl news presenter, talking enthusiastically, natural mouth movement, blinking eyes, expressive smile, moving head, dynamic lighting, 8k, fluid motion"}},
                            "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "blurry, low quality, static, deformed, glitch, distortion"}},
                            "9": {"class_type": "WanImageToVideo", "inputs": {"positive": ["7", 0], "negative": ["8", 0], "vae": ["3", 0], "width": 720, "height": 1280, "length": 81, "batch_size": 1, "start_image": ["5", 0], "clip_vision_output": ["6", 0]}},
                            "10": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["9", 0], "negative": ["9", 1], "latent_image": ["9", 2], "seed": 7777, "steps": 25, "cfg": 6.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
                            "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
                            "12": {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "fps": 24.0, "compress_level": 4, "filename_prefix": "WanAvatar"}}
                        }
                    }
                    
                    q_res = requests.post(f"{host}/prompt", json=prompt_workflow, timeout=10)
                    if q_res.status_code == 200:
                        prompt_id = q_res.json().get("prompt_id")
                        print(f"      ⏳ Generando animación IA con Wan 2.1 en RTX 5090 (ID: {prompt_id[:8]})...")
                        for _ in range(60):
                            time.sleep(5)
                            h_res = requests.get(f"{host}/history/{prompt_id}", timeout=5).json()
                            if prompt_id in h_res:
                                outputs = h_res[prompt_id].get("outputs", {})
                                for node_out in outputs.values():
                                    if "images" in node_out or "gifs" in node_out:
                                        file_info = (node_out.get("images") or node_out.get("gifs"))[0]
                                        view_url = f"{host}/view?filename={file_info['filename']}&subfolder={file_info.get('subfolder','')}&type={file_info.get('type','output')}"
                                        vid_bytes = requests.get(view_url, timeout=30).content
                                        tmp_res = output_clip.parent / "wan_raw_anim.png"
                                        tmp_res.write_bytes(vid_bytes)
                                        subprocess.run(["ffmpeg", "-y", "-i", str(tmp_res.resolve()), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(output_clip.resolve())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                        tmp_res.unlink(missing_ok=True)
                                        if output_clip.exists() and output_clip.stat().st_size > 10000:
                                            print("      ✅ ¡Video de Personaje Wan 2.1 14B completado exitosamente en RTX 5090!")
                                            return True
    except Exception as e:
        print(f"      ℹ️ ComfyUI Wan 2.1 I2V fallback: {e}")
        
    return False

def obtener_clip_motion_vault(tema: str = "", guion: str = "") -> Path:
    """Selecciona inteligentemente el clip animado de la presentadora según el tono del guion."""
    vault_dir = Path("assets/avatar/motion_vault")
    if not vault_dir.exists():
        return None
        
    t = (tema + " " + guion).lower()
    if any(k in t for k in ["misterio", "conspiracion", "secreto", "dark", "revelado", "alien", "oculto", "peligro"]):
        p = vault_dir / "04_mystery_conspiracy.mp4"
    elif any(k in t for k in ["impactante", "locura", "alerta", "urgente", "increible", "millones", "prohibido", "brutal"]):
        p = vault_dir / "03_shock_mindblown.mp4"
    elif any(k in t for k in ["lanzamiento", "nuevo", "gadget", "nvidia", "apple", "hardware", "chip", "robot", "ia"]):
        p = vault_dir / "02_explaining_tech.mp4"
    else:
        p = vault_dir / "01_intro_greeting.mp4"
        
    if p.exists() and p.stat().st_size > 1000:
        return p
        
    p_def = vault_dir / "01_intro_greeting.mp4"
    return p_def if (p_def.exists() and p_def.stat().st_size > 1000) else None

def crear_clip_intro_presentador(avatar_img_path: Path, output_clip: Path, duracion: float = 3.5, width: int = 1080, height: int = 1920, audio_path: Path = None, host: str = "http://100.95.107.65:8188", tema: str = "", guion: str = "") -> bool:
    """Crea el clip de introducción vertical de la presentadora con animación cinematográfica 3D fluida."""
    output_clip = Path(output_clip)
    output_clip.parent.mkdir(parents=True, exist_ok=True)
    
    # 0. Usar Motion Vault si está disponible
    mv_clip = obtener_clip_motion_vault(tema=tema, guion=guion)
    if mv_clip:
        import shutil
        shutil.copy2(mv_clip, output_clip)
        print(f"      🌸 Usando Escenario Animado del Motion Vault: [{mv_clip.name}]")
        return True
        
    if not avatar_img_path.exists():
        return False
        
    # 1. Intentar animación neuronal en la GPU RTX 5090 (LivePortrait / Wan 2.1 I2V)
    if audio_path and Path(audio_path).exists():
        ok_neural = animar_personaje_neuronal_comfyui(avatar_img_path, audio_path, output_clip, host=host, duracion=duracion, width=width, height=height)
        if ok_neural and output_clip.exists() and output_clip.stat().st_size > 5000:
            return True
            
    # 2. Composición Cinematográfica 3D en Set Anime (Limpia, elegante, sin parches 2D)
    try:
        comp_path = output_clip.parent / "intro_comp_stage.jpg"
        source_img = avatar_img_path
        with Image.open(avatar_img_path) as av_img:
            if av_img.mode == "RGBA":
                # Crear fondo degradado anime estudio (azul marino profundo a lavanda)
                stage_bg = Image.new("RGBA", (width, height), (15, 12, 28, 255))
                draw_st = ImageDraw.Draw(stage_bg)
                # Iluminación de foco de estudio volumétrico
                draw_st.ellipse([width//2 - 450, height//2 - 550, width//2 + 450, height//2 + 550], fill=(75, 40, 110, 255))
                draw_st.ellipse([width//2 - 250, height//2 - 350, width//2 + 250, height//2 + 350], fill=(120, 65, 160, 255))
                stage_bg = stage_bg.filter(ImageFilter.GaussianBlur(radius=50))
                
                # Escalar la waifu centrada
                av_w, av_h = av_img.size
                scale_f = min((width * 0.95) / av_w, (height * 0.90) / av_h)
                nw, nh = int(av_w * scale_f), int(av_h * scale_f)
                av_resized = av_img.resize((nw, nh), Image.Resampling.LANCZOS)
                
                pos_x = (width - nw) // 2
                pos_y = height - nh - int(height * 0.04)
                stage_bg.paste(av_resized, (pos_x, pos_y), av_resized)
                stage_bg.convert("RGB").save(comp_path, "JPEG", quality=98)
                source_img = comp_path
                
        fps = 30
        frames = int(duracion * fps)
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(source_img.resolve()),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
                   f"zoompan=z='min(zoom+0.002,1.15)':d={frames}:x='iw/2-(iw/zoom/2)+sin(on/8)*12':y='ih/2-(ih/zoom/2)+cos(on/10)*8':s={width}x{height}",
            "-t", f"{duracion:.2f}", "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(output_clip.resolve())
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        comp_path.unlink(missing_ok=True)
        return output_clip.exists() and output_clip.stat().st_size > 0
    except Exception as e:
        print(f"      ⚠️ Error creando clip de intro de presentadora: {e}")
        return False

def crear_video_pip_badge_animado(video_source_path: Path, output_pip_video: Path, duracion_total: float = 40.0, size: int = 280) -> bool:
    """
    Toma el clip de video animado de la Waifu y lo transforma en un Badge Circular PIP Animado
    continuo en bucle con anillo de neón rosa y canal alfa para la esquina del video.
    """
    output_pip_video = Path(output_pip_video)
    output_pip_video.parent.mkdir(parents=True, exist_ok=True)
    
    if not video_source_path.exists():
        return False
        
    try:
        work_dir = output_pip_video.parent
        mask_png = work_dir / "pip_circ_mask.png"
        ring_png = work_dir / "pip_neon_ring.png"
        
        # 1. Máscara circular
        mask = Image.new("L", (size, size), 0)
        d_m = ImageDraw.Draw(mask)
        d_m.ellipse((8, 8, size - 8, size - 8), fill=255)
        mask.save(mask_png)
        
        # 2. Anillo de Neón con etiqueta "♥ AI WAIFU"
        ring_canvas = Image.new("RGBA", (size + 40, size + 60), (0, 0, 0, 0))
        d_r = ImageDraw.Draw(ring_canvas)
        # Sombra
        d_r.ellipse((16, 20, size + 24, size + 28), fill=(0, 0, 0, 180))
        ring_canvas = ring_canvas.filter(ImageFilter.GaussianBlur(radius=6))
        d_r = ImageDraw.Draw(ring_canvas)
        # Anillo rosa neón
        d_r.ellipse((16, 16, size + 24, size + 24), outline=(255, 105, 180), width=4)
        # Etiqueta
        lbl_w, lbl_h = 120, 28
        lbl_x = (size + 40 - lbl_w) // 2
        lbl_y = size + 16
        d_r.rounded_rectangle([lbl_x, lbl_y, lbl_x + lbl_w, lbl_y + lbl_h], radius=8, fill=(25, 15, 35, 230), outline=(255, 105, 180), width=2)
        d_r.ellipse([lbl_x + 8, lbl_y + 8, lbl_x + 18, lbl_y + 18], fill=(255, 60, 150, 255))
        ring_canvas.save(ring_png)
        
        # 3. Componer Video con QuickTime Animation (canal alfa intacto)
        fc = (
            f"[0:v]crop=min(iw\\,ih*0.5):min(iw\\,ih*0.5):iw/2-min(iw\\,ih*0.5)/2:ih*0.08,scale={size}:{size}[v_sq];"
            f"[v_sq][1:v]alphamerge[v_circ];"
            f"[2:v][v_circ]overlay=20:20[outv]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", str(video_source_path.resolve()),
            "-loop", "1", "-i", str(mask_png.resolve()),
            "-loop", "1", "-i", str(ring_png.resolve()),
            "-filter_complex", fc,
            "-map", "[outv]",
            "-t", f"{duracion_total:.2f}",
            "-c:v", "qtrle",
            str(output_pip_video.resolve())
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mask_png.unlink(missing_ok=True)
        ring_png.unlink(missing_ok=True)
        
        if output_pip_video.exists() and output_pip_video.stat().st_size > 1000:
            print(f"      🌸 Badge PIP de Video Animado generado ({output_pip_video.stat().st_size // 1024} KB).")
            return True
    except Exception as e:
        print(f"      ⚠️ Error creando video badge PIP: {e}")
        
    return False
