# pipeline.py - v3 CALIDAD
import asyncio
import json
import re
import shutil
import subprocess
import yaml
from datetime import datetime
from hashlib import md5
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

from ia_client import generar_guion, revisar_guion, generar_prompts_imagenes, generar_prompts_para_guion
from musica import obtener_musica_para
from metadata import generar_metadata, actualizar_obsidian_con_metadata
from publisher import publicar_video
from qa_review import revisar_video, MAX_REINTENTOS, evaluar_asset_imagen, evaluar_asset_video
from investigacion import investigar_tema
from media_fetcher import obtener_clips_multi_fuente, obtener_clips_multi_fuente_hibrido
from product_fetcher import obtener_imagenes_producto_real
from compositor import componer_smart_backdrop
from avatar_host import generar_avatar_en_rtx5090, crear_clip_intro_presentador
import trends as trends_module

FPS = 30
TRANS = 0.5  # duración crossfade

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def slugify(t):
    t = re.sub(r"[^\w\s-]", "", t.lower())
    return re.sub(r"[\s_-]+", "-", t)[:50]

def timestamp(s):
    ms = int(s * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def parse_time(t_str):
    h, m, s_ms = t_str.split(':')
    s, ms = s_ms.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def parse_srt(srt_content):
    import re
    entries = []
    blocks = re.split(r'\n\s*\n', srt_content.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
            if match:
                start_str, end_str = match.groups()
                start = parse_time(start_str)
                end = parse_time(end_str)
                text = " ".join(lines[2:]).strip()
                entries.append((start, end, text))
    return entries

def generar_queries_video(tema, guion):
    """Usa la IA local para generar queries de búsqueda de video clips relevantes al tema."""
    import requests as rq
    config = cfg()
    ia = config["ia"]
    
    prompt = f"""Analiza este tema y guion de video y genera exactamente 5 search queries cortas en INGLÉS para buscar video clips de stock que ilustren visualmente este contenido.

TEMA: "{tema}"
GUION: "{guion}"

REGLAS:
- Cada query debe tener 2-3 palabras máximo (ej: "neural network", "space station", "robot arm")
- Deben ser conceptos VISUALES concretos, no abstractos
- Deben estar directamente relacionados con el contenido del guion
- Cada query debe buscar algo DIFERENTE (no repetir conceptos)
- En inglés porque Pixabay funciona mejor en inglés
- NO uses comillas en las queries

Devuelve SOLO un JSON válido: {{"queries": ["query1", "query2", "query3", "query4", "query5"]}}"""

    try:
        if ia["proveedor"] == "ollama":
            r = rq.post(
                "http://localhost:11434/api/generate",
                json={"model": ia["modelo"], "prompt": prompt, "stream": False, "format": "json"},
                timeout=60
            )
            data = json.loads(r.json().get("response", "{}"))
        else:
            base = ia.get("base_url", "https://api.openai.com/v1")
            headers = {}
            if "api_key" in ia:
                headers["Authorization"] = f"Bearer {ia['api_key']}"
            r = rq.post(
                f"{base}/chat/completions",
                headers=headers,
                json={
                    "model": ia["modelo"],
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
            data = json.loads(r.json()["choices"][0]["message"]["content"])
        
        queries = data.get("queries", [])[:5]
        if queries:
            print(f"      🧠 Queries de video generadas por IA: {queries}")
            return queries
    except Exception as e:
        print(f"      ⚠️ IA queries falló: {e}")
    
    # Fallback: extraer palabras clave del tema
    palabras = [w for w in tema.split() if len(w) > 4][:3]
    fallback = [" ".join(palabras[:2])] if len(palabras) >= 2 else [tema[:30]]
    print(f"      🔄 Usando fallback de queries: {fallback}")
    return fallback

def descargar_video_clips(tema, work, dur_audio, guion="", investigacion=None):
    print("   🎥 Obteniendo clips de video (IA ComfyUI / Multi-Fuente Open Source)...")
    config = cfg()
    res_type = config.get("resolucion", "1080p").lower()
    w, h = (2160, 3840) if res_type == "4k" else (1080, 1920)
    
    # 1. Usar queries estructurados de la investigación técnica si existen
    if investigacion and "queries_video_stock" in investigacion:
        queries = investigacion["queries_video_stock"]
    else:
        queries = generar_queries_video(tema, guion)
        
    def ffmpeg_scaler(input_clip, output_clip, idx):
        run_ffmpeg([
            "ffmpeg", "-y", "-i", str(input_clip.resolve()),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1",
            "-r", "30", "-an", str(output_clip.resolve())
        ], f"preparando clip {idx}", cwd=work)

    # 2. Obtener usando flujo híbrido (IA ComfyUI en RTX 5090 + Fallback Stock Multi-Fuente)
    return obtener_clips_multi_fuente_hibrido(queries, work, dur_audio, ffmpeg_scaler, tema=tema, pre_eval_func=evaluar_asset_video)

PALABRAS_CLAVE_HIGHLIGHT = {
    "ia", "ai", "chatgpt", "openai", "gpu", "rtx", "5090", "m4", "apple", "google", "meta",
    "secreto", "millones", "dólares", "usd", "dinero", "impacto", "descubrió", "peligro",
    "nuevo", "nueva", "increíble", "fusión", "cuántica", "universo", "marte", "robot",
    "futuro", "prohibido", "muerte", "revolución", "humano", "cerebro", "nasa", "spacex",
    "4k", "8k", "35b", "100%", "primera", "oficial", "historia", "windows", "mac", "chip"
}

def es_palabra_resaltada(palabra: str) -> bool:
    clean = re.sub(r"[^\w]", "", palabra.lower())
    if any(char.isdigit() for char in clean):
        return True
    if "$" in palabra or "%" in palabra:
        return True
    return clean in PALABRAS_CLAVE_HIGHLIGHT

def obtener_fuente_viral(font_size=60):
    for fpath in [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Black.ttf"
    ]:
        if Path(fpath).exists():
            try:
                return ImageFont.truetype(fpath, font_size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("Arial", font_size)
    except Exception:
        return ImageFont.load_default()

def draw_transparent_subtitle(text, output_path, width=1080, height=1920, font_path=None, font_size=60):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    if W >= 2000:
        font_size = 125
        stroke_width = 12
        spacing = 26
    else:
        font_size = 68
        stroke_width = 7
        spacing = 14
        
    if not text:
        img.save(output_path, "PNG")
        return
        
    font = obtener_fuente_viral(font_size)
            
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w > W * 0.82 and len(current_line) > 1:
            current_line.pop()
            lines.append(current_line)
            current_line = [word]
    if current_line:
        lines.append(current_line)
        
    y_offset = H * 0.70
    
    line_heights = []
    for line_words in lines:
        line_str = " ".join(line_words)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_height = sum(line_heights) + (len(lines) - 1) * spacing
    
    current_y = y_offset - total_height / 2
    
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_w = space_bbox[2] - space_bbox[0]
    
    for line_words in lines:
        line_str = " ".join(line_words)
        line_bbox = draw.textbbox((0, 0), line_str, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        line_h = line_bbox[3] - line_bbox[1]
        
        cur_x = (W - line_w) / 2
        
        # 1. Dibujar contorno grueso negro para todas las palabras
        for word in line_words:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            w_w = w_bbox[2] - w_bbox[0]
            
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        draw.text((cur_x + dx, current_y + dy), word, font=font, fill=(0, 0, 0, 255))
            cur_x += w_w + space_w
            
        # 2. Dibujar relleno con resaltado inteligente (Amarillo Neón / Blanco Brillante / Cian)
        cur_x = (W - line_w) / 2
        for word in line_words:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            w_w = w_bbox[2] - w_bbox[0]
            
            if es_palabra_resaltada(word):
                color = (255, 230, 0, 255)  # Amarillo Neón MrBeast
            else:
                color = (255, 255, 255, 255)  # Blanco Puro Brillante
                
            draw.text((cur_x, current_y), word, font=font, fill=color)
            cur_x += w_w + space_w
            
        current_y += line_h + spacing
        
    img.save(output_path, "PNG")

def draw_subtitle_on_image(image_path, text, output_path, font_path=None, font_size=60):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    if W >= 2000:
        font_size = 125
        stroke_width = 12
        spacing = 26
    else:
        font_size = 68
        stroke_width = 7
        spacing = 14
        
    font = obtener_fuente_viral(font_size)
            
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w > W * 0.82 and len(current_line) > 1:
            current_line.pop()
            lines.append(current_line)
            current_line = [word]
    if current_line:
        lines.append(current_line)
        
    y_offset = H * 0.70
    
    line_heights = []
    for line_words in lines:
        line_str = " ".join(line_words)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_height = sum(line_heights) + (len(lines) - 1) * spacing
    
    current_y = y_offset - total_height / 2
    
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_w = space_bbox[2] - space_bbox[0]
    
    for line_words in lines:
        line_str = " ".join(line_words)
        line_bbox = draw.textbbox((0, 0), line_str, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        line_h = line_bbox[3] - line_bbox[1]
        
        cur_x = (W - line_w) / 2
        for word in line_words:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            w_w = w_bbox[2] - w_bbox[0]
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        draw.text((cur_x + dx, current_y + dy), word, font=font, fill=(0, 0, 0, 255))
            cur_x += w_w + space_w
            
        cur_x = (W - line_w) / 2
        for word in line_words:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            w_w = w_bbox[2] - w_bbox[0]
            color = (255, 230, 0, 255) if es_palabra_resaltada(word) else (255, 255, 255, 255)
            draw.text((cur_x, current_y), word, font=font, fill=color)
            cur_x += w_w + space_w
            
        current_y += line_h + spacing
        
    img.save(output_path, "PNG")
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (W - w) / 2
        
        stroke_width = 6
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width:
                    draw.text((x + dx, current_y + dy), line, font=font, fill=(0, 0, 0))
                    
        draw.text((x, current_y), line, font=font, fill=(255, 255, 0))
        current_y += h + 12
        
    img.save(output_path, quality=95)

def run_ffmpeg(cmd, desc, cwd=None):
    print(f"   🎬 {desc}...")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        print(f"   ❌ FFmpeg falló: {desc}")
        print(r.stderr[-800:])
        raise RuntimeError(desc)

def get_audio_duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 30)

def check_subtitles_support():
    try:
        r = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True, timeout=5)
        return "subtitles" in r.stdout
    except Exception:
        return False

# ---------- 1. GUION LIMPIO ----------
def sanear_guion(texto, max_palabras):
    """Elimina markdown, URLs, acotaciones en corchetes/paréntesis, nombres de archivo y tokens que la voz no debe leer."""
    texto = re.sub(r"```.*?```", " ", texto, flags=re.S)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"\[.*?\]", " ", texto, flags=re.S)
    texto = re.sub(r"\(.*?\)", " ", texto, flags=re.S)
    texto = re.sub(r"\{.*?\}", " ", texto, flags=re.S)
    texto = re.sub(r"[\w./\\_-]+\.(mp3|mp4|py|srt|jpg|jpeg|png|md|yaml|json|txt)", " ", texto, flags=re.I)
    texto = re.sub(r"\b(HOOK|CUERPO|CIERRE|CTA|GUIÓN|GUION|Narrador|Locutor|Voz en off|Visual|Audio|Escena \d+)\s*:", " ", texto, flags=re.I)
    texto = re.sub(r"[#*_<>`|~•■●\-+*]", " ", texto)
    texto = re.sub(r"\b\d{1,2}:\d{2}\b", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    palabras = texto.split()
    texto = texto.strip()
    if texto and not texto[-1] in ".!?":
        texto += "."
    return texto

# ---------- 2. TARJETA DE HOOK (primeros 2.5s) ----------
def crear_tarjeta_hook(texto, ruta):
    """Imagen 1080x1920 con el hook en grande para detener el scroll."""
    img = Image.new("RGB", (1080, 1920), (10, 13, 25))
    d = ImageDraw.Draw(img)
    # barra de acento
    d.rectangle([0, 780, 1080, 800], fill=(255, 200, 0))
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/System/Library/Fonts/Helvetica.ttc",
               "/Library/Fonts/Arial Bold.ttf"]:
        try:
            font = ImageFont.truetype(fp, 88)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    # wrap de texto
    palabras, lineas, linea = texto.split(), [], ""
    for p in palabras:
        if len(linea) + len(p) < 16:
            linea += p + " "
        else:
            lineas.append(linea.strip())
            linea = p + " "
        if len(lineas) == 5:
            break
    if linea and len(lineas) < 5:
        lineas.append(linea.strip())
    y = 900
    for lin in lineas:
        d.text((80, y), lin.upper(), fill=(255, 255, 255), font=font)
        y += 130
    img.save(ruta, quality=95)
    return ruta

# ---------- 3. VOZ PRO ----------
async def paso_voz(texto, audio, voz):
    print(f"   🎙️  Generando voz de alta definición ({voz})...")
    comm = edge_tts.Communicate(texto, voz, rate="+7%", pitch="+2Hz")
    raw = audio.parent / "raw.mp3"
    await comm.save(str(raw))
    # Ecualización y compresión dinámica para voz limpia estilo podcast/TikTok
    af_filter = (
        "highpass=f=85,lowpass=f=11500,"
        "equalizer=f=300:width_type=h:width=200:g=-3,"
        "equalizer=f=3000:width_type=h:width=1000:g=3,"
        "compand=attacks=0.03:decays=0.3:points=-80/-80|-45/-25|-20/-10|0/-3,"
        "loudnorm=I=-15:TP=-1.5:LRA=10"
    )
    run_ffmpeg(["ffmpeg", "-y", "-i", str(raw.name),
                "-af", af_filter,
                "-ar", "44100", "-b:a", "256k", audio.name],
               "masterizando voz", cwd=audio.parent)
    raw.unlink(missing_ok=True)

# ---------- 4. SUBTÍTULOS ----------
def paso_subtitulos(audio, srt):
    print("   📝 Generando subtítulos rápidos estilo TikTok...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), language="es", vad_filter=True, word_timestamps=True)
    
    words_list = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words_list.append(w)
                
    if not words_list:
        print("      ⚠️ Advertencia: No se detectaron timestamps de palabras individuales. Usando fallback de segmentos.")
        lines = []
        segments_fallback, _ = model.transcribe(str(audio), language="es", vad_filter=True)
        for idx, seg in enumerate(segments_fallback, 1):
            t = seg.text.strip().upper()
            if len(t) < 3 or t.count(".") == len(t):
                continue
            if len(t) > 42:
                med = len(t) // 2
                esp = t.find(" ", med)
                if esp > 0:
                    t = t[:esp] + "\n" + t[esp + 1:]
            lines += [str(idx), f"{timestamp(seg.start)} --> {timestamp(seg.end)}", t, ""]
        srt.write_text("\n".join(lines), encoding="utf-8")
        return

    max_words = 3
    max_chars = 22
    max_gap = 0.45
    
    srt_entries = []
    current_group = []
    
    for w in words_list:
        word_text = w.word.strip().upper()
        if not word_text:
            continue
            
        should_split = False
        if current_group:
            if len(current_group) >= max_words:
                should_split = True
            elif len(" ".join([x.word.strip().upper() for x in current_group]) + " " + word_text) > max_chars:
                should_split = True
            elif w.start - current_group[-1].end > max_gap:
                should_split = True
                
        if should_split:
            start_time = current_group[0].start
            end_time = current_group[-1].end
            text = " ".join([x.word.strip().upper() for x in current_group])
            srt_entries.append((start_time, end_time, text))
            current_group = []
            
        current_group.append(w)
        
    if current_group:
        start_time = current_group[0].start
        end_time = current_group[-1].end
        text = " ".join([x.word.strip().upper() for x in current_group])
        srt_entries.append((start_time, end_time, text))
        
    lines = []
    for idx, (start, end, text) in enumerate(srt_entries, 1):
        lines += [str(idx), f"{timestamp(start)} --> {timestamp(end)}", text, ""]
        
    srt.write_text("\n".join(lines), encoding="utf-8")
    print(f"      ✅ {len(srt_entries)} subtítulos rápidos generados con éxito.")

# ---------- 5. IMÁGENES (flux, semillas distintas, sin duplicados) ----------
def descargar_imagen_v3(prompt, ruta, seed):
    url = (f"https://image.pollinations.ai/prompt/{requests_quote(prompt)}"
           f"?width=1080&height=1920&seed={seed}&model=flux&nologo=true")
    import requests as rq
    r = rq.get(url, timeout=90)
    if r.status_code == 200 and len(r.content) > 5000:
        ruta.write_bytes(r.content)
        return md5(r.content).hexdigest()
    return None

def requests_quote(p):
    from urllib.parse import quote
    return quote(p)

def paso_imagenes(prompts, work, n, tema="", investigacion=None):
    print(f"   🎨 Generando/Componiendo {n} recursos visuales de alta fidelidad...")
    config = cfg()
    res_type = config.get("resolucion", "1080p").lower()
    target_w, target_h = (2160, 3840) if res_type == "4k" else (1080, 1920)
    
    rutas = []
    
    # 1. Obtener fotos reales del producto verídico si está activado
    if config.get("fotos_reales", {}).get("activado", True):
        max_reales = config.get("fotos_reales", {}).get("cantidad_maxima", 3)
        fotos_reales = obtener_imagenes_producto_real(tema, investigacion, work, cantidad=max_reales)
        for idx_r, f_real in enumerate(fotos_reales):
            salida_comp = work / f"i{len(rutas)}.jpg"
            ok = componer_smart_backdrop(f_real, salida_comp, width=target_w, height=target_h)
            if ok:
                rutas.append(f"i{len(rutas)}.jpg")
                print(f"      🖼️ [Hero Product {idx_r + 1}] Composición Anti-Stretch lista (Aspecto 100% Nativo + Fondo Blur).")
                
    # 2. Completar las escenas restantes con generación Flux fotorrealista
    restantes = n - len(rutas)
    if restantes > 0:
        vistas = set()
        variantes = ["", ", hyperrealistic 8k details", ", cinematic vertical shot", ", detailed photography",
                     ", studio lighting, 8k resolution", ", golden hour cinematic light", ", ultra detailed macro shot"]
        for i in range(restantes):
            idx_actual = len(rutas)
            base = prompts[i % len(prompts)] if prompts else "cinematic scene"
            for intento in range(3):
                p = base + variantes[(i + intento) % len(variantes)]
                tmp_img = work / f"tmp_{idx_actual}.jpg"
                h = descargar_imagen_v3(p, tmp_img, seed=1000 + idx_actual * 97 + intento * 13)
                
                if h and h not in vistas:
                    vistas.add(h)
                    
                    # PRE-EVALUACIÓN ANTES DE ESCALAR
                    if tema:
                        aprobado, eval_info = evaluar_asset_imagen(tmp_img, tema, base)
                        if not aprobado:
                            print(f"      ⏭️ Imagen {idx_actual+1} descartada en pre-evaluación (Relevancia < 75%). Generando variante {intento+2}...")
                            tmp_img.unlink(missing_ok=True)
                            continue
                            
                    # Escalar con Ken Burns dinámico
                    run_ffmpeg(["ffmpeg", "-y", "-i", f"tmp_{idx_actual}.jpg",
                                "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1",
                                f"i{idx_actual}.jpg"], f"escalando {idx_actual}", cwd=work)
                    tmp_img.unlink(missing_ok=True)
                    rutas.append(f"i{idx_actual}.jpg")
                    print(f"      ✅ imagen {idx_actual + 1}/{n} pre-aprobada")
                    break
                    
            # Fallback si no pasó
            if len(rutas) <= idx_actual:
                if (work / f"tmp_{idx_actual}.jpg").exists():
                    run_ffmpeg(["ffmpeg", "-y", "-i", f"tmp_{idx_actual}.jpg",
                                "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1",
                                f"i{idx_actual}.jpg"], f"escalando {idx_actual}", cwd=work)
                    (work / f"tmp_{idx_actual}.jpg").unlink(missing_ok=True)
                    rutas.append(f"i{idx_actual}.jpg")
                    
    return rutas

# ---------- 6. RENDER PRO ----------
def paso_render_pillow(imagenes, videos, audio, srt_path, musica, salida, work):
    print("   🎬 Render PRO con Subtítulos Quemados en Pillow...")
    
    # 1. Copiar y resolver rutas
    if Path(audio).resolve() != (work / "a.mp3").resolve():
        shutil.copy2(audio, work / "a.mp3")
    tiene_musica = False
    if musica and Path(musica).exists():
        if Path(musica).resolve() != (work / "m.mp3").resolve():
            shutil.copy2(musica, work / "m.mp3")
        tiene_musica = True
        
    dur_audio = get_audio_duration(work / "a.mp3")
    
    config = cfg()
    res_type = config.get("resolucion", "1080p").lower()
    w, h = (2160, 3840) if res_type == "4k" else (1080, 1920)
    crf = config.get("calidad_crf", 15)
    
    # 2. Generar el fondo del video (background.mp4)
    if videos:
        print(f"      🎞️ Concatenando {len(videos)} videoclips para el fondo...")
        with open(work / "concat_videos.txt", "w") as f:
            for v in videos:
                f.write(f"file '{v}'\n")
        run_ffmpeg([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_videos.txt",
            "-c", "copy", "background.mp4"
        ], "concatenando clips de fondo", cwd=work)
    else:
        print("      🖼️ Creando fondo a partir de imágenes estáticas...")
        D = max(4.0, (dur_audio + 1) / len(imagenes))
        with open(work / "concat_imgs.txt", "w") as f:
            for img in imagenes:
                f.write(f"file '{img}'\nduration {D:.2f}\n")
            f.write(f"file '{imagenes[-1]}'\n")
        run_ffmpeg([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_imgs.txt",
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1",
            "-r", "30", "-pix_fmt", "yuv420p", "background.mp4"
        ], "creando fondo de imagenes", cwd=work)

    # 3. Leer subtítulos SRT
    srt_content = Path(srt_path).read_text(encoding="utf-8")
    entries = parse_srt(srt_content)
    if not entries:
        entries = [(0.0, dur_audio, "")]
        
    timeline = []
    current_time = 0.0
    
    if entries[0][0] > 0.0:
        timeline.append((0.0, entries[0][0], ""))
        current_time = entries[0][0]
        
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    
    for idx, (start, end, text) in enumerate(entries):
        if start > current_time + 0.05:
            timeline.append((current_time, start, ""))
        timeline.append((start, end, text))
        current_time = end
        
    if dur_audio > current_time + 0.05:
        timeline.append((current_time, dur_audio, ""))
        
    concat_lines = []
    for f_idx, (start, end, text) in enumerate(timeline):
        duration = end - start
        if duration <= 0.01:
            continue
            
        frame_name = f"sub_{f_idx:03d}.png"
        frame_path = work / frame_name
        
        draw_transparent_subtitle(text, frame_path, width=w, height=h, font_path=font_path)
        
        concat_lines.append(f"file '{frame_name}'\nduration {duration:.3f}\n")
        
    if concat_lines:
        last_line = concat_lines[-1]
        last_frame_name = last_line.split("\n")[0].split("'")[1]
        concat_lines.append(f"file '{last_frame_name}'\n")
        
    (work / "concat_subtitles.txt").write_text("".join(concat_lines), encoding="utf-8")
    
    # 4. Mezclar fondo, subtítulos overlay y audio
    cmd = [
        "ffmpeg", "-y",
        "-i", "background.mp4",
        "-f", "concat", "-safe", "0", "-i", "concat_subtitles.txt",
        "-i", "a.mp3"
    ]
    if tiene_musica:
        cmd += ["-stream_loop", "-1", "-i", "m.mp3"]
        fc = ("[0:v][1:v]overlay=0:0[outv];"
              "[3:a]volume=0.25[m];[m][2:a]sidechaincompress="
              "threshold=0.03:ratio=8:attack=5:release=300[md];"
              "[2:a][md]amix=inputs=2:duration=first:dropout_transition=0[outa]")
    else:
        fc = "[0:v][1:v]overlay=0:0[outv];[2:a]anull[outa]"
        
    cmd += ["-filter_complex", fc, "-map", "[outv]", "-map", "[outa]"]
    max_mbps = config.get("compositor", {}).get("bitrate_max_mbps", 40)
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-maxrate", f"{max_mbps}M", "-bufsize", f"{max_mbps * 2}M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(salida.resolve())]
            
    run_ffmpeg(cmd, "render overlay", cwd=work)

def paso_render(imagenes, audio, srt, musica, salida, work):
    print(f"   🎬 Render PRO ({len(imagenes)} escenas + crossfade + ducking)...")
    # nombres simples en work/ (adiós problema de espacios)
    if Path(audio).resolve() != (work / "a.mp3").resolve():
        shutil.copy2(audio, work / "a.mp3")
    if Path(srt).resolve() != (work / "s.srt").resolve():
        shutil.copy2(srt, work / "s.srt")
    tiene_musica = False
    if musica and Path(musica).exists():
        if Path(musica).resolve() != (work / "m.mp3").resolve():
            shutil.copy2(musica, work / "m.mp3")
        tiene_musica = True

    dur_audio = get_audio_duration(work / "a.mp3")
    D = max(3.0, (dur_audio + 1) / len(imagenes))

    partes, inputs = [], []
    for i, img in enumerate(imagenes):
        inputs += ["-loop", "1", "-t", f"{D:.2f}", "-i", img]
        if i % 2 == 0:
            z = f"zoompan=z='min(zoom+0.0015,1.18)':d={int(D * FPS)}:s=1080x1920:fps={FPS}"
        else:
            z = f"zoompan=z='if(eq(on,1),1.18,max(zoom-0.0015,1.0))':d={int(D * FPS)}:s=1080x1920:fps={FPS}"
        partes.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                      f"crop=1080:1920,setsar=1,{z},format=yuv420p[v{i}]")
    prev = "[v0]"
    for i in range(1, len(imagenes)):
        off = i * (D - TRANS)
        partes.append(f"{prev}[v{i}]xfade=transition=fade:duration={TRANS}:offset={off:.2f}[x{i}]")
        prev = f"[x{i}]"
    estilo = ("Fontname=Arial,Fontsize=38,Bold=1,PrimaryColour=&H00FFFFFF&,"
              "OutlineColour=&H00000000&,BorderStyle=1,Outline=3,Shadow=1,"
              "MarginV=800,Alignment=2")
    if check_subtitles_support():
        partes.append(f"{prev}subtitles=s.srt:force_style='{estilo}'[outv]")
    else:
        print("   ⚠️ ADVERTENCIA: FFmpeg no tiene soporte para subtítulos (libass no habilitado). El video se generará sin subtítulos.")
        partes.append(f"{prev}null[outv]")

    n = len(imagenes)
    inputs += ["-i", "a.mp3"]
    if tiene_musica:
        inputs += ["-stream_loop", "-1", "-i", "m.mp3"]
        partes.append(f"[{n + 1}:a]volume=0.5[m];[m][{n}:a]sidechaincompress="
                      f"threshold=0.03:ratio=8:attack=5:release=300[md];"
                      f"[{n}:a][md]amix=inputs=2:duration=first:dropout_transition=0[outa]")
    else:
        partes.append(f"[{n}:a]anull[outa]")

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(partes),
           "-map", "[outv]", "-map", "[outa]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(salida.resolve())]
    try:
        run_ffmpeg(cmd, "render PRO", cwd=work)
    except RuntimeError:
        print("   ⚠️ Fallback a render simple (con subtítulos y música)...")
        render_fallback(imagenes, dur_audio, tiene_musica, estilo, salida, work, D)

    if salida.exists() and salida.stat().st_size > 100000:
        d = get_audio_duration(salida)
        print(f"   ✅ VIDEO LISTO: {salida.name} ({d:.0f}s, {salida.stat().st_size // 1024} KB)")
    else:
        raise RuntimeError("Video no generado")

def render_fallback(imagenes, dur_audio, tiene_musica, estilo, salida, work, D):
    with open(work / "concat.txt", "w") as f:
        for img in imagenes:
            f.write(f"file '{img}'\nduration {D:.2f}\n")
        f.write(f"file '{imagenes[-1]}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-i", "a.mp3"]
    fc = None
    if tiene_musica:
        cmd += ["-stream_loop", "-1", "-i", "m.mp3"]
        fc = ("[1:a]volume=0.35[m];[m][2:a]sidechaincompress=threshold=0.03:ratio=8[md];"
              "[2:a][md]amix=inputs=2:duration=first[outa]")
    if check_subtitles_support():
        vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles=s.srt:force_style='{estilo}'"
    else:
        print("   ⚠️ ADVERTENCIA: FFmpeg no tiene soporte para subtítulos (libass no habilitado). El video se generará sin subtítulos.")
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    cmd += ["-vf", vf]
    if fc:
        cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[outa]"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(salida.resolve())]
    run_ffmpeg(cmd, "render fallback", cwd=work)

# ---------- 7. OBSIDIAN ----------
def paso_obsidian(tema, guion, video_path, prompts):
    config = cfg()
    vault = Path(config["obsidian_vault"]) / "03-Contenidos" / "Episodios"
    ahora = datetime.now()
    carpeta = vault / f"{ahora:%Y-%m-%d}-{slugify(tema)}"
    carpeta.mkdir(parents=True, exist_ok=True)
    video_local = carpeta / video_path.name
    if not video_local.exists():
        shutil.copy2(video_path, video_local)
    
    safe_title = tema.replace('"', '\\"')
    prompts_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompts)]) if prompts else "No se generaron prompts."
    
    (carpeta / "index.md").write_text(f"""---
titulo: "{safe_title}"
estado: render
fecha_creacion: {ahora:%Y-%m-%d %H:%M}
video: "{video_local.name}"
views: 0
likes: 0
retencion_3s: 0
---

# {tema}

## Guion
{guion}

## Prompts de Imágenes
{prompts_text}

## Checklist
- [x] Generado automáticamente (v3)
- [ ] Revisión humana
- [ ] Publicado
""", encoding="utf-8")
    print(f"   📓 Obsidian actualizado")

# ---------- PIPELINE ----------
async def procesar_tema(tema, indice):
    config = cfg()
    dur_max = config.get("duracion_max_segundos", 40)
    slug = slugify(tema)
    
    # Verificar duplicados en Obsidian para no repetir videos
    vault = Path(config["obsidian_vault"]) / "03-Contenidos" / "Episodios"
    if vault.exists():
        for p in vault.iterdir():
            if p.is_dir() and (p.name.endswith(f"-{slug}") or p.name == slug):
                print(f"\n   ⚠️ OMITIDO: El tema '{tema}' ya tiene un episodio en Obsidian ({p.name}).")
                return None

    print(f"\n{'=' * 60}\n🎯 VIDEO {indice}: {tema}\n{'=' * 60}")
    work = Path("output/work") / slug
    work.mkdir(parents=True, exist_ok=True)
    try:
        # 0 Investigación estructurada
        print("   [0/10] Investigación estructurada...")
        investigacion = investigar_tema(tema)
        
        # 1 guion
        print("   [1/10] Guion estructurado...")
        guion_raw = generar_guion(tema, dur_max, investigacion=investigacion)
        guion = sanear_guion(guion_raw, max_palabras=int(dur_max * 2.6))
        if len(guion.split()) < 30:
            guion = sanear_guion(generar_guion(tema, dur_max, investigacion=investigacion), int(dur_max * 2.6))
        print(f"   ✅ {len(guion.split())} palabras (~{len(guion.split()) // 2.6:.0f}s)")
        # 2 tarjeta hook
        print("   [2/10] Tarjeta de hook...")
        hook = guion.split(". ")[0][:70]
        crear_tarjeta_hook(hook, work / "i0.jpg")
        # 3 voz
        print("   [3/10] Voz...")
        await paso_voz(guion, work / "a_voz.mp3", config["voz"])
        # 4 música
        print("   [4/10] Música...")
        musica = obtener_musica_para(tema, indice)
        # 5 subtítulos
        print("   [5/10] Subtítulos...")
        paso_subtitulos(work / "a_voz.mp3", work / "s.srt")
        
        # === LOOP DE GENERACIÓN + QA ===
        dur_audio = get_audio_duration(work / "a_voz.mp3")
        salida = None
        qa_aprobado = False
        intento = 0
        
        while not qa_aprobado and intento <= MAX_REINTENTOS:
            intento += 1
            if intento > 1:
                print(f"\n   🔄 REINTENTO {intento}/{MAX_REINTENTOS + 1} — Regenerando contenido visual...")
            
            # 6 imágenes y clips de video
            print(f"   [6/10] Imágenes y Clips de Video Multi-Fuente {'(regenerando)' if intento > 1 else ''}...")
            n_fotos = min(7, max(4, dur_max // 5))
            prompts = generar_prompts_para_guion(guion, n_fotos, investigacion=investigacion)
            videos = descargar_video_clips(tema, work, dur_audio, guion=guion, investigacion=investigacion)
            
            # Integrar clip del Presentador Virtual Faceless si está activo
            if config.get("avatar_presentador", {}).get("activado", True):
                avatar_host_img = work / "host_avatar.png"
                intro_host_clip = work / "v_intro_host.mp4"
                if not intro_host_clip.exists():
                    host_host = config.get("avatar_presentador", {}).get("host", "http://100.95.107.65:8188")
                    host_ok = generar_avatar_en_rtx5090(avatar_host_img, host=host_host, tema=tema)
                    if host_ok:
                        ok_intro = crear_clip_intro_presentador(avatar_host_img, intro_host_clip, duracion=3.5)
                        if ok_intro:
                            print(f"      👤 Clip de Presentador Virtual Faceless integrado al inicio.")
                            videos.insert(0, str(intro_host_clip.resolve()))
                            
            fotos = paso_imagenes(prompts, work, n_fotos, tema=tema, investigacion=investigacion)
            imagenes = ["i0.jpg"] + fotos
            
            # 7 render
            print(f"   [7/10] Render {'(regenerando)' if intento > 1 else ''}...")
            salida = Path(config["salida_videos"]) / f"{datetime.now():%Y%m%d_%H%M}_{slugify(tema)}.mp4"
            paso_render_pillow(imagenes, videos, work / "a_voz.mp3", work / "s.srt", musica, salida, work)
            
            # 8 QA — Revisión de calidad con IA
            print("   [8/10] Control de calidad con IA...")
            veredicto = revisar_video(salida, tema, guion, work)
            
            if veredicto.get("aprobado", True):
                qa_aprobado = True
                print(f"   ✅ QA aprobado (Score: {veredicto.get('score_final', '?')}/100)")
            else:
                if intento > MAX_REINTENTOS:
                    print(f"   ⚠️ QA no aprobado después de {intento} intentos. Publicando con advertencia.")
                    qa_aprobado = True  # forzar publicación con lo mejor que tenemos
                else:
                    print(f"   🔄 QA rechazó el video. Regenerando contenido visual...")
                    # Limpiar video anterior para no acumular
                    if salida and salida.exists():
                        salida.unlink(missing_ok=True)
        
        # 9 metadata & publication
        print("   [9/10] Generando metadatos virales...")
        meta = generar_metadata(tema, guion, salida, indice)
        
        # Agregar info de QA a los metadatos
        meta["qa_score"] = veredicto.get("score_final", 0)
        meta["qa_intentos"] = intento
        meta["qa_aprobado"] = veredicto.get("aprobado", True)
        
        print("   [10/10] Actualizando Obsidian y publicando...")
        actualizar_obsidian_con_metadata(tema, guion, salida, prompts, meta)
        
        pub_cfg = config.get("publisher", {})
        if pub_cfg.get("auto_publicar", True):
            publicar_video(salida, meta)
            
        print(f"\n   🎉 LISTO: {salida}")
        saneamiento_automatico(work)
        return salida
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def saneamiento_automatico(work):
    """Elimina automáticamente archivos temporales de trabajo (frames, audios intermedios, concatenaciones) tras finalizar el renderizado."""
    try:
        work_path = Path(work)
        if work_path.exists():
            shutil.rmtree(work_path, ignore_errors=True)
            print("   🧹 Saneamiento automático: carpeta temporal de trabajo eliminada.")
    except Exception as e:
        print(f"   ⚠️ Saneamiento de trabajo omitido: {e}")

async def main():
    config = cfg()
    print("🚀 Iniciando Pipeline Unificado (Tendencias + Producción + QA + Publicación)...")
    
    # 0. Buscar y actualizar tendencias automáticamente
    try:
        trends_module.main()
    except Exception as e:
        print(f"⚠️ Error buscando tendencias automáticamente: {e}")
        
    tf = Path("output/trends.json")
    if not tf.exists():
        print("❌ No se pudo encontrar ni generar output/trends.json")
        return
        
    trends = json.load(open(tf, encoding="utf-8"))["tendencias"][:config["numero_videos"]]
    ok = 0
    for i, t in enumerate(trends, 1):
        if await procesar_tema(t, i):
            ok += 1
            
    # Saneamiento final de la carpeta de trabajo general
    saneamiento_automatico("output/work")
    print(f"\n✅ {ok}/{len(trends)} videos listos en {config['salida_videos']}/ (Entorno saneado y limpio)")

if __name__ == "__main__":
    asyncio.run(main())