# compositor.py - v1.0 — Compositor Visual Anti-Stretch con Smart Backdrop Blur
"""
Compositor broadcast para encuadrar imágenes y videos de cualquier relación de aspecto
(16:9 horizontal, 4:3, 1:1 cuadrado) en formato vertical 9:16 (4K y 1080p) sin deformación:
1. Capa de Fondo (Backdrop): Imagen escalada a 9:16, desenfocada con Gaussiano cinemático y oscurecida.
2. Capa Principal (Hero Product): Imagen en su relación de aspecto original perfecta, centrada con bordes redondeados y sombra 3D flotante.
3. Movimiento Dinámico: Zoom flotante suave para dar dinamismo televisivo.
"""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageDraw

def componer_smart_backdrop(imagen_input: Path, imagen_output: Path, width: int = 1080, height: int = 1920, blur_sigma: int = 35) -> bool:
    """
    Crea una composición vertical 9:16 profesional a partir de cualquier imagen:
    - Fondo desenfocado y ambientado.
    - Imagen del producto en el centro con su aspecto nativo y sombra suave.
    """
    try:
        with Image.open(imagen_input) as img_orig:
            img = img_orig.convert("RGBA")
            orig_w, orig_h = img.size
            aspect_orig = orig_w / orig_h
            aspect_target = width / height  # 0.5625 (9:16)
            
            # Si la imagen ya es vertical (aspecto muy cercano a 9:16), sólo reescalar
            if abs(aspect_orig - aspect_target) < 0.05:
                img_resized = ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)
                img_resized.convert("RGB").save(imagen_output, "JPEG", quality=96)
                return True
                
            # 1. CREAR CAPA DE FONDO DESENFOCADO (BACKDROP)
            # Escalar para llenar todo el marco vertical 9:16
            bg = ImageOps.fit(img, (width, height), Image.Resampling.BILINEAR)
            # Aplicar desenfoque gaussiano cinematográfico
            bg = bg.filter(ImageFilter.GaussianBlur(radius=blur_sigma))
            
            # Oscurecer sutilmente el fondo para que el producto resalte
            dimmer = Image.new("RGBA", (width, height), (0, 0, 0, 85))
            bg = Image.alpha_composite(bg, dimmer)
            
            # 2. CREAR CAPA DE PRIMER PLANO (HERO PRODUCT)
            # El producto ocupará el 88% del ancho de la pantalla
            hero_target_w = int(width * 0.88)
            hero_target_h = int(hero_target_w / aspect_orig)
            
            # Si por altura supera el 65% de la pantalla, limitar por altura
            if hero_target_h > int(height * 0.65):
                hero_target_h = int(height * 0.65)
                hero_target_w = int(hero_target_h * aspect_orig)
                
            hero = img.resize((hero_target_w, hero_target_h), Image.Resampling.LANCZOS)
            
            # 3. CREAR SOMBRA 3D FLOTANTE
            shadow_margin = 40
            shadow_w = hero_target_w + shadow_margin * 2
            shadow_h = hero_target_h + shadow_margin * 2
            shadow = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            
            # Dibujar rectángulo redondeado oscuro para la sombra
            shadow_draw.rounded_rectangle(
                [shadow_margin, shadow_margin + 10, shadow_margin + hero_target_w, shadow_margin + hero_target_h + 10],
                radius=24,
                fill=(0, 0, 0, 160)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=25))
            
            # 4. CREAR MÁSCARA CON ESQUINAS REDONDEADAS PARA EL HERO PRODUCT
            mask = Image.new("L", (hero_target_w, hero_target_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, hero_target_w, hero_target_h], radius=24, fill=255)
            
            # 5. PEGAR EN EL LIENZO FINAL
            center_x = (width - hero_target_w) // 2
            center_y = int(height * 0.42) - (hero_target_h // 2)  # Ligeramente arriba del centro para dejar espacio a subtítulos
            
            # Pegar sombra
            bg.paste(shadow, (center_x - shadow_margin, center_y - shadow_margin), shadow)
            # Pegar hero product con máscara redondeada
            bg.paste(hero, (center_x, center_y), mask)
            
            # Guardar en calidad broadcast
            bg.convert("RGB").save(imagen_output, "JPEG", quality=96)
            return True
    except Exception as e:
        print(f"      ⚠️ Error en composición smart backdrop: {e}")
        return False

def generar_overlay_onda_audio(amplitud: float, output_path: Path, width: int = 1080, height: int = 1920, num_barras: int = 28) -> bool:
    """Genera una barra visualizadora de audio reactiva y transparente en la parte inferior con brillo neón cian."""
    try:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bar_w = int(width * 0.018)
        gap = int(width * 0.008)
        total_w = num_barras * bar_w + (num_barras - 1) * gap
        start_x = (width - total_w) // 2
        base_y = int(height * 0.88)
        
        for i in range(num_barras):
            # Altura reactiva con curva senoidal
            factor = math.sin((i / num_barras) * math.pi)
            h_bar = int(12 + (amplitud * 90 * factor) + (math.sin(i * 1.5 + amplitud * 10) * 8))
            x0 = start_x + i * (bar_w + gap)
            y0 = base_y - h_bar
            x1 = x0 + bar_w
            y1 = base_y
            
            # Gradiente de color Neón Cian a Dorado
            color = (0, 240, 255, int(160 + amplitud * 95)) if i % 2 == 0 else (255, 230, 0, int(150 + amplitud * 100))
            draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=color)
            
        # Brillo suave
        glow = img.filter(ImageFilter.GaussianBlur(radius=5))
        final_img = Image.alpha_composite(glow, img)
        final_img.save(output_path, "PNG")
        return True
    except Exception:
        return False

def generar_pista_sfx_master(dur_total: float, output_wav: Path, timestamps_cortes: list = None, sample_rate: int = 44100) -> bool:
    """
    Genera una pista masterizada de efectos de sonido (Auto-SFX) perfectamente sincronizada con los cambios de escena:
    - 0.0s: Sub-Impact Boom para retención instantánea en el gancho.
    - 3.5s: Pop holográfico + Whoosh al revelar la tarjeta 3D del producto.
    - Cortes posteriores: Transiciones Whoosh dinámicas.
    """
    output_wav = Path(output_wav)
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    
    import wave
    import numpy as np
    
    sfx_dir = Path("assets/sfx")
    sub_path = sfx_dir / "sub_impact_hook.wav"
    pop_path = sfx_dir / "hologram_pop.wav"
    whoosh_path = sfx_dir / "whoosh_transition.wav"
    
    total_samples = int(dur_total * sample_rate) + sample_rate
    master_audio = np.zeros(total_samples, dtype=np.float32)
    
    def read_wav(p):
        if not p.exists():
            return None
        with wave.open(str(p), "r") as wf:
            n = wf.getnframes()
            data = wf.readframes(n)
            return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            
    sub_data = read_wav(sub_path)
    pop_data = read_wav(pop_path)
    whoosh_data = read_wav(whoosh_path)
    
    # 1. Inyectar Sub-Impact al inicio (0.0s)
    if sub_data is not None:
        l = min(len(sub_data), total_samples)
        master_audio[:l] += sub_data[:l] * 0.75
        
    # 2. Inyectar Pop Holográfico en el corte del producto (3.5s)
    if pop_data is not None and total_samples > int(3.5 * sample_rate):
        start = int(3.5 * sample_rate)
        l = min(len(pop_data), total_samples - start)
        master_audio[start:start+l] += pop_data[:l] * 0.65
        
    # 3. Inyectar Whooshes en los cortes
    cortes = timestamps_cortes if timestamps_cortes else [3.5, 8.5, 16.0]
    if whoosh_data is not None:
        for t_sec in cortes:
            start = max(0, int((t_sec - 0.15) * sample_rate))
            if start < total_samples:
                l = min(len(whoosh_data), total_samples - start)
                master_audio[start:start+l] += whoosh_data[:l] * 0.50
                
    # Normalizar para evitar clipping
    max_val = np.max(np.abs(master_audio))
    if max_val > 0.95:
        master_audio = master_audio * (0.95 / max_val)
        
    audio_int16 = (master_audio[:int(dur_total * sample_rate)] * 32767).astype(np.int16)
    
    with wave.open(str(output_wav), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
        
    return output_wav.exists() and output_wav.stat().st_size > 0

