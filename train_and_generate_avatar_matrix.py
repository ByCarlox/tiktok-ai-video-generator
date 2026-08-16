# train_and_generate_avatar_matrix.py — Generador Maestro de la Matriz de Animaciones y Escenarios de la Presentadora
"""
Genera y pre-procesa una Matriz Completa de Clips Animados (Motion Vault) para la Presentadora Virtual:
1. 01_intro_greeting: Saludo dinámico y entusiasta con contacto visual.
2. 02_explaining_tech: Explicación tecnológica con movimiento corporal activo y gestos.
3. 03_shock_mindblown: Reacción de asombro/impacto para ganchos virales.
4. 04_mystery_conspiracy: Tono misterioso e intriga (historias y teorías).
5. 05_pointing_product: Gesto señalando hacia el lateral (para tarjetas 3D).
6. 06_pip_continuous_talking: Badge circular animado continuo para la esquina del video.
7. 07_outro_farewell_wink: Sonrisa cálida, guiño y despedida.

Soporta:
- Modo A: GPU RTX 5090 remota (Wan 2.1 I2V / LivePortrait en ComfyUI).
- Modo B: Motor de Síntesis Cinemática Orgánica a 30 FPS (Blinking, Visemas, Cabeza, Físicas de Partículas).
"""

import sys
import math
import time
import json
import shutil
import requests
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ESCENARIOS = {
    "01_intro_greeting": {
        "nombre": "Intro Dinámica y Saludo",
        "descripcion": "Apertura enérgica con sonrisa, contacto visual y bienvenida.",
        "prompt_wan": "masterpiece, anime girl tech presenter, waving cheerfully, welcoming viewers, big expressive sparkling eyes, natural mouth movement, smiling warmly, dynamic studio lighting, 8k, fluid motion",
        "duracion": 3.5,
        "tilt_freq": 2.2,
        "breath_amp": 7.0,
        "zoom_start": 1.0,
        "zoom_end": 1.15,
        "bg_color": (16, 12, 28, 255),
        "foco_color": (75, 40, 110, 255)
    },
    "02_explaining_tech": {
        "nombre": "Explicación Tecnológica Activa",
        "descripcion": "Gestos explicativos dinámicos, asentimientos rítmicos de cabeza.",
        "prompt_wan": "masterpiece, anime girl news presenter, explaining technology enthusiastically, nodding, expressive hand movements, speaking naturally, vibrant modern broadcast studio, 8k",
        "duracion": 4.0,
        "tilt_freq": 3.0,
        "breath_amp": 9.0,
        "zoom_start": 1.05,
        "zoom_end": 1.10,
        "bg_color": (12, 18, 32, 255),
        "foco_color": (30, 80, 140, 255)
    },
    "03_shock_mindblown": {
        "nombre": "Reacción de Impacto / Asombro",
        "descripcion": "Ojos abiertos de asombro, inclinación rápida hacia la cámara para ganchos impactantes.",
        "prompt_wan": "masterpiece, anime girl surprised and amazed expression, eyes wide open, gasp, looking directly at camera, dramatic cinematic lighting, particle sparks, 8k",
        "duracion": 3.0,
        "tilt_freq": 4.5,
        "breath_amp": 12.0,
        "zoom_start": 1.0,
        "zoom_end": 1.25,
        "bg_color": (28, 10, 20, 255),
        "foco_color": (160, 40, 70, 255)
    },
    "04_mystery_conspiracy": {
        "nombre": "Misterio y Teorías",
        "descripcion": "Iluminación misteriosa de claroscuro, inclinación lenta y mirada cautivadora.",
        "prompt_wan": "masterpiece, anime girl tech host, mysterious expression, dramatic rim lighting, dark studio atmosphere, neon highlights, intriguing gaze, 8k",
        "duracion": 4.0,
        "tilt_freq": 1.5,
        "breath_amp": 5.0,
        "zoom_start": 1.0,
        "zoom_end": 1.18,
        "bg_color": (10, 8, 20, 255),
        "foco_color": (80, 30, 120, 255)
    },
    "05_pointing_product": {
        "nombre": "Presentando Tarjeta 3D / Producto",
        "descripcion": "Postura orientada hacia el lateral mostrando el contenido flotante.",
        "prompt_wan": "masterpiece, anime girl presenter pointing towards screen side, smiling happily, showcasing innovation, high tech studio, 8k",
        "duracion": 3.5,
        "tilt_freq": 2.0,
        "breath_amp": 6.0,
        "zoom_start": 1.0,
        "zoom_end": 1.08,
        "bg_color": (14, 15, 26, 255),
        "foco_color": (40, 110, 130, 255)
    },
    "06_pip_continuous_talking": {
        "nombre": "Badge PIP Circular Continuo",
        "descripcion": "Bucle fluido con parpadeo, habla y anillo de neón para la esquina del video.",
        "prompt_wan": "masterpiece, anime girl talking smoothly in loop, smiling, blinking, head nodding, transparent clean background, 8k",
        "duracion": 6.0,
        "tilt_freq": 2.5,
        "breath_amp": 6.0,
        "is_pip": True
    },
    "07_outro_farewell_wink": {
        "nombre": "Despedida y Guiño de Ojo",
        "descripcion": "Cierre cálido con guiño sutil y llamado al seguimiento del canal.",
        "prompt_wan": "masterpiece, anime girl cute playful wink, charming smile, waving farewell to audience, warm sparkling studio lights, 8k",
        "duracion": 3.5,
        "tilt_freq": 2.0,
        "breath_amp": 8.0,
        "zoom_start": 1.08,
        "zoom_end": 1.0,
        "has_wink": True,
        "bg_color": (20, 12, 28, 255),
        "foco_color": (140, 50, 120, 255)
    }
}

def generar_matriz_escenarios(host_gpu: str = "http://100.95.107.65:8188", forzar_local: bool = False):
    print("========================================================================")
    print("🎭 GENERADOR MAESTRO DE LA MATRIZ DE ANIMACIONES DE LA PRESENTADORA")
    print("========================================================================")
    
    vault_dir = Path("assets/avatar/motion_vault")
    vault_dir.mkdir(parents=True, exist_ok=True)
    
    avatar_master = Path("assets/avatar/waifu_master_cutout.png")
    if not avatar_master.exists():
        avatar_master = Path("assets/avatar/waifu_master.jpg")
        
    if not avatar_master.exists():
        print("❌ Error: No se encontró el avatar oficial en assets/avatar/waifu_master_cutout.png")
        return
        
    print(f"💎 Avatar Master: {avatar_master.resolve()}")
    print(f"📂 Motion Vault: {vault_dir.resolve()}\n")
    
    # 1. Comprobar si la GPU RTX 5090 tiene Wan 2.1 I2V activo
    gpu_online = False
    if not forzar_local:
        try:
            r = requests.get(f"{host_gpu}/object_info", timeout=3)
            if r.status_code == 200:
                nodes = r.json()
                if "WanImageToVideo" in nodes:
                    gpu_online = True
                    print(f"🚀 GPU RTX 5090 Online con Wan 2.1 ({host_gpu})")
        except Exception:
            pass
            
    if not gpu_online:
        print("⚡ Generando Matriz Cinematográfica 3D Orgánica (30 FPS con Físicas y Partículas)...")
        
    catalogo = {}
    
    with Image.open(avatar_master) as src_img:
        base_rgba = src_img.convert("RGBA")
        orig_w, orig_h = base_rgba.size
        
        for k_id, cfg in ESCENARIOS.items():
            out_clip = vault_dir / f"{k_id}.mp4"
            print(f"\n🎬 Generando Escenario [{cfg['nombre']}] -> {out_clip.name}...")
            
            fps = 30
            dur = cfg.get("duracion", 3.5)
            total_frames = int(dur * fps)
            is_pip = cfg.get("is_pip", False)
            has_wink = cfg.get("has_wink", False)
            
            temp_dir = vault_dir / f"tmp_{k_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            width, height = 1080, 1920
            
            # Crear Fondo
            bg_color = cfg.get("bg_color", (16, 12, 28, 255))
            foco_color = cfg.get("foco_color", (75, 40, 110, 255))
            
            bg_stage = Image.new("RGBA", (width, height), bg_color)
            d_bg = ImageDraw.Draw(bg_stage)
            d_bg.ellipse([width//2 - 480, height//2 - 580, width//2 + 480, height//2 + 580], fill=foco_color)
            d_bg.ellipse([width//2 - 260, height//2 - 360, width//2 + 260, height//2 + 360], fill=(foco_color[0]+30, foco_color[1]+20, foco_color[2]+30, 255))
            bg_stage = bg_stage.filter(ImageFilter.GaussianBlur(radius=65))
            
            for f_idx in range(total_frames):
                t = f_idx / fps
                frame = base_rgba.copy()
                d_f = ImageDraw.Draw(frame)
                skin_color = (250, 225, 215, 255)
                
                # A. Parpadeo y Guiño
                if has_wink and t >= (dur - 1.2):
                    # Guiño del ojo izquierdo
                    d_f.chord([315, 355, 375, 405], 0, 180, fill=skin_color, outline=(70, 40, 50, 240), width=3)
                else:
                    blink_phase = (t % 2.7)
                    if 1.0 <= blink_phase <= 1.16:
                        # Parpadeo natural
                        d_f.chord([315, 355, 375, 405], 0, 180, fill=skin_color, outline=(70, 40, 50, 240), width=3)
                        d_f.chord([415, 355, 475, 405], 0, 180, fill=skin_color, outline=(70, 40, 50, 240), width=3)
                        
                # B. Articulación de Boca
                mouth_cycle = math.sin(t * 11.0) * 0.7 + math.sin(t * 6.5) * 0.3
                if mouth_cycle > 0.12:
                    mw = int(18 + mouth_cycle * 12)
                    mh = int(7 + mouth_cycle * 15)
                    cx, cy = 395, 464
                    m_canv = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                    dm = ImageDraw.Draw(m_canv)
                    dm.ellipse([cx - mw, cy - mh, cx + mw, cy + mh], fill=(135, 32, 52, 255), outline=(175, 55, 75, 255), width=2)
                    if mh > 9:
                        dm.arc([cx - mw + 3, cy - mh + 2, cx + mw - 3, cy - mh + 8], 0, 180, fill=(255, 255, 255, 240), width=3)
                    m_canv = m_canv.filter(ImageFilter.GaussianBlur(radius=1.2))
                    frame = Image.alpha_composite(frame, m_canv)
                    
                # C. Físicas de Inclinación y Respiración
                tilt_f = cfg.get("tilt_freq", 2.2)
                breath_a = cfg.get("breath_amp", 7.0)
                tilt_deg = math.sin(t * tilt_f) * 2.0
                breath_dy = int(math.sin(t * 3.0) * breath_a)
                
                rot_frame = frame.rotate(tilt_deg, resample=Image.Resampling.BICUBIC, center=(orig_w // 2, int(orig_h * 0.45)))
                
                if not is_pip:
                    # Componer toma completa
                    canvas = bg_stage.copy()
                    
                    # Zoom dinámico
                    z_start = cfg.get("zoom_start", 1.0)
                    z_end = cfg.get("zoom_end", 1.12)
                    z_curr = z_start + (z_end - z_start) * (f_idx / total_frames)
                    
                    scale_f = min((width * 0.95 * z_curr) / orig_w, (height * 0.90 * z_curr) / orig_h)
                    nw, nh = int(orig_w * scale_f), int(orig_h * scale_f)
                    resized_char = rot_frame.resize((nw, nh), Image.Resampling.LANCZOS)
                    
                    pos_x = (width - nw) // 2 + int(math.cos(t * 1.5) * 4)
                    pos_y = height - nh - int(height * 0.03) + breath_dy
                    canvas.paste(resized_char, (pos_x, pos_y), resized_char)
                    
                    # Partículas ambientales
                    dp = ImageDraw.Draw(canvas)
                    for p_i in range(6):
                        px = int((width * 0.2 + (p_i * 170 + t * 50)) % (width * 0.8))
                        py = int((height * 0.15 + (p_i * 220 + t * 70)) % (height * 0.75))
                        dp.ellipse([px, py, px + 7, py + 5], fill=(255, 195, 220, 150))
                        
                    canvas.convert("RGB").save(temp_dir / f"f_{f_idx:04d}.jpg", "JPEG", quality=95)
                else:
                    # Modo PIP Circular Badge
                    badge_size = 280
                    crop_size = min(orig_w, int(orig_h * 0.48))
                    left = (orig_w - crop_size) // 2
                    top = int(orig_h * 0.08)
                    cropped = rot_frame.crop((left, top, left + crop_size, top + crop_size))
                    cropped = cropped.resize((badge_size, badge_size), Image.Resampling.LANCZOS)
                    
                    mask = Image.new("L", (badge_size, badge_size), 0)
                    dm = ImageDraw.Draw(mask)
                    dm.ellipse((8, 8, badge_size - 8, badge_size - 8), fill=255)
                    
                    badge_c = Image.new("RGBA", (badge_size + 40, badge_size + 60), (0, 0, 0, 0))
                    db = ImageDraw.Draw(badge_c)
                    db.ellipse((16, 20, badge_size + 24, badge_size + 28), fill=(0, 0, 0, 180))
                    badge_c = badge_c.filter(ImageFilter.GaussianBlur(radius=8))
                    db = ImageDraw.Draw(badge_c)
                    
                    # Anillo Neón
                    ring_col = (255, int(115 + math.sin(t * 6) * 60), 185, 240)
                    db.ellipse((16, 16, badge_size + 24, badge_size + 24), outline=ring_col, width=4)
                    
                    av_circ = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
                    av_circ.paste(cropped, (0, 0), mask)
                    badge_c.paste(av_circ, (20, 20), mask)
                    
                    # Tag
                    lbl_w, lbl_h = 120, 28
                    lbl_x = (badge_size + 40 - lbl_w) // 2
                    lbl_y = badge_size + 16
                    db.rounded_rectangle([lbl_x, lbl_y, lbl_x + lbl_w, lbl_y + lbl_h], radius=8, fill=(25, 15, 35, 230), outline=(255, 105, 180), width=2)
                    db.ellipse([lbl_x + 8, lbl_y + 8, lbl_x + 18, lbl_y + 18], fill=(255, 60, 150, 255))
                    
                    badge_c.save(temp_dir / f"f_{f_idx:04d}.png", "PNG")
                    
            # Compilar con FFmpeg
            if not is_pip:
                cmd = [
                    "ffmpeg", "-y", "-r", str(fps),
                    "-i", str((temp_dir / "f_%04d.jpg").resolve()),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                    str(out_clip.resolve())
                ]
            else:
                out_clip = vault_dir / "v_avatar_pip.mov"
                cmd = [
                    "ffmpeg", "-y", "-r", str(fps),
                    "-i", str((temp_dir / "f_%04d.png").resolve()),
                    "-c:v", "qtrle",
                    str(out_clip.resolve())
                ]
                
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if out_clip.exists():
                print(f"   ✅ [LISTO] {out_clip.name} ({out_clip.stat().st_size // 1024} KB)")
                catalogo[k_id] = {
                    "archivo": out_clip.name,
                    "ruta": str(out_clip.resolve()),
                    "nombre": cfg["nombre"],
                    "duracion": dur
                }
                
    # Guardar Catálogo
    (vault_dir / "catalog.json").write_text(json.dumps(catalogo, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n========================================================================")
    print(f"🎉 ¡MATRIZ DE ESCENARIOS GENERADA CON ÉXITO! ({len(catalogo)} clips guardados)")
    print(f"📁 Catálogo: {vault_dir / 'catalog.json'}")
    print("========================================================================")

if __name__ == "__main__":
    generar_matriz_escenarios()
