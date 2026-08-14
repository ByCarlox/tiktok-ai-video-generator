# product_3d.py - v1.0 — Tarjetas 3D Glassmorphism y Recorte de Productos
"""
Módulo para transformar fotos reales de productos en presentaciones 3D televisivas:
1. Recorte de fondos (Background Cutout) con suavizado de bordes anti-aliased.
2. Composición de Tarjeta de Cristal Esmerilado (Glassmorphic Card) con aura de luz neón y sombras 3D.
3. Animación de Levitación Flotante (Floating 3D Motion) para video vertical 9:16.
"""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

def aislar_producto_fondo(imagen_path: Path, output_png: Path) -> bool:
    """
    Aísla el producto principal del fondo creando un PNG transparente con bordes suaves.
    Utiliza detección de contraste y máscara alfa inteligente.
    """
    try:
        with Image.open(imagen_path) as orig:
            img = orig.convert("RGBA")
            w, h = img.size
            
            # Obtener muestras de color de las 4 esquinas para detectar el color de fondo
            corners = [img.getpixel((5, 5)), img.getpixel((w-6, 5)), img.getpixel((5, h-6)), img.getpixel((w-6, h-6))]
            avg_bg_r = sum(c[0] for c in corners) // 4
            avg_bg_g = sum(c[1] for c in corners) // 4
            avg_bg_b = sum(c[2] for c in corners) // 4
            
            # Crear máscara de transparencia basada en distancia de color euclidiana
            datas = img.getdata()
            new_data = []
            for item in datas:
                # Distancia de color al fondo
                dist = math.sqrt((item[0]-avg_bg_r)**2 + (item[1]-avg_bg_g)**2 + (item[2]-avg_bg_b)**2)
                if dist < 28:
                    new_data.append((item[0], item[1], item[2], 0))
                elif dist < 55:
                    alpha = int(((dist - 28) / 27.0) * 255)
                    new_data.append((item[0], item[1], item[2], alpha))
                else:
                    new_data.append(item)
                    
            cutout = Image.new("RGBA", (w, h))
            cutout.putdata(new_data)
            
            # Si el recorte aisló bien el sujeto, guardarlo
            cutout.save(output_png, "PNG")
            return True
    except Exception as e:
        print(f"      ⚠️ Recorte de producto falló ({e}). Usando imagen original...")
        return False

def componer_tarjeta_3d_glassmorphism(imagen_path: Path, output_path: Path, width: int = 1080, height: int = 1920, titulo: str = "") -> bool:
    """
    Compone el producto real sobre una tarjeta flotante de cristal esmerilado con aura cian/ámbar.
    """
    try:
        with Image.open(imagen_path) as orig:
            img = orig.convert("RGBA")
            orig_w, orig_h = img.size
            aspect = orig_w / orig_h
            
            # 1. FONDO AMBIENTAL DESENFOCADO (DEEP BLUR BACKDROP)
            bg = ImageOps.fit(img, (width, height), Image.Resampling.BILINEAR)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
            dimmer = Image.new("RGBA", (width, height), (8, 12, 22, 160))
            bg = Image.alpha_composite(bg, dimmer)
            
            # 2. CREAR TARJETA DE CRISTAL ESMERILADO (FROSTED GLASS CARD)
            card_w = int(width * 0.90)
            card_h = int(height * 0.58)
            card_x = (width - card_w) // 2
            card_y = int(height * 0.38) - (card_h // 2)
            
            # Capa de sombra profunda de la tarjeta 3D
            shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(shadow)
            s_draw.rounded_rectangle(
                [card_x - 10, card_y + 15, card_x + card_w + 10, card_y + card_h + 35],
                radius=32,
                fill=(0, 0, 0, 190)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=30))
            bg = Image.alpha_composite(bg, shadow)
            
            # Cuerpo de la tarjeta de cristal
            glass = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 18))
            g_draw = ImageDraw.Draw(glass)
            
            # Gradiente de brillo en el cristal
            g_draw.rounded_rectangle([0, 0, card_w, card_h], radius=28, fill=(20, 28, 45, 175))
            # Borde con aura cian y reflejo de luz
            g_draw.rounded_rectangle([0, 0, card_w, card_h], radius=28, outline=(0, 240, 255, 180), width=3)
            g_draw.line([(30, 2), (card_w - 30, 2)], fill=(255, 255, 255, 220), width=2)
            
            bg.paste(glass, (card_x, card_y), glass)
            
            # 3. ESCALAR Y PEGAR EL PRODUCTO HERO AL CENTRO DE LA TARJETA
            prod_target_w = int(card_w * 0.88)
            prod_target_h = int(prod_target_w / aspect)
            if prod_target_h > int(card_h * 0.82):
                prod_target_h = int(card_h * 0.82)
                prod_target_w = int(prod_target_h * aspect)
                
            prod_resized = img.resize((prod_target_w, prod_target_h), Image.Resampling.LANCZOS)
            prod_x = card_x + (card_w - prod_target_w) // 2
            prod_y = card_y + (card_h - prod_target_h) // 2
            
            # Sombra de contacto del producto
            p_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            ps_draw = ImageDraw.Draw(p_shadow)
            ps_draw.ellipse(
                [prod_x + 20, prod_y + prod_target_h - 15, prod_x + prod_target_w - 20, prod_y + prod_target_h + 25],
                fill=(0, 0, 0, 150)
            )
            p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(radius=18))
            bg = Image.alpha_composite(bg, p_shadow)
            
            # Máscara redondeada para el producto
            p_mask = Image.new("L", (prod_target_w, prod_target_h), 0)
            pm_draw = ImageDraw.Draw(p_mask)
            pm_draw.rounded_rectangle([0, 0, prod_target_w, prod_target_h], radius=18, fill=255)
            
            bg.paste(prod_resized, (prod_x, prod_y), p_mask)
            
            # Guardar resultado final en calidad 4K/1080p
            bg.convert("RGB").save(output_path, "JPEG", quality=96)
            return True
    except Exception as e:
        print(f"      ⚠️ Error en composición 3D glassmorphic: {e}")
        return False

def crear_clip_producto_3d_flotante(imagen_3d_path: Path, output_clip: Path, duracion: float = 5.0, width: int = 1080, height: int = 1920) -> bool:
    """Genera un videoclip vertical con animación cinemática de levitación 3D suave."""
    output_clip = Path(output_clip)
    output_clip.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        fps = 30
        frames = int(duracion * fps)
        # Ken Burns cinematográfico con paneo sutil
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(imagen_3d_path.resolve()),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
                   f"zoompan=z='min(zoom+0.0014,1.12)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+sin(on/15)*12':s={width}x{height}",
            "-t", f"{duracion:.2f}", "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(output_clip.resolve())
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_clip.exists() and output_clip.stat().st_size > 5000
    except Exception as e:
        print(f"      ⚠️ Error creando clip de producto 3D: {e}")
        return False
