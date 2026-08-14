# pipeline_lite.py - Versión Standalone Ligera para PCs de Bajos Recursos
"""
Edición Lite del Generador Autónomo:
- 100% Funcional en cualquier ordenador (Windows, Linux, macOS con CPU o laptop básica).
- No requiere GPU dedicada, servidores remotos, ComfyUI ni VPN Tailscale.
- Utiliza fuentes gratuitas (Pollinations Flux, Pixabay Videos, Wikipedia Real Photos, Edge-TTS).
- Incluye subtítulos virales dinámicos (MrBeast) y compositor Anti-Stretch con Smart Backdrop Blur.
"""
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

from ia_client import generar_guion, generar_prompts_para_guion
from musica import obtener_musica_para
from metadata import generar_metadata
from investigacion import investigar_tema
from product_fetcher import obtener_imagenes_producto_real
from compositor import componer_smart_backdrop
import trends as trends_module

FPS = 30

def cfg():
    config_file = "config.lite.yaml" if Path("config.lite.yaml").exists() else "config.yaml"
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def slugify(t):
    t = re.sub(r"[^\w\s-]", "", t.lower())
    return re.sub(r"[\s_-]+", "-", t)[:50]

def run_ffmpeg(cmd, desc="ffmpeg", cwd=None):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error ({desc}): {res.stderr[-200:]}")
    return res

def get_audio_duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 30)

def sanear_guion(texto, max_palabras=90):
    texto = re.sub(r"```.*?```", " ", texto, flags=re.S)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"\[.*?\]", " ", texto, flags=re.S)
    texto = re.sub(r"\(.*?\)", " ", texto, flags=re.S)
    texto = re.sub(r"\{.*?\}", " ", texto, flags=re.S)
    texto = re.sub(r"[\w./\\_-]+\.(mp3|mp4|py|srt|jpg|jpeg|png|md|yaml|json|txt)", " ", texto, flags=re.I)
    texto = re.sub(r"\b(HOOK|CUERPO|CIERRE|CTA|GUIÓN|GUION|Narrador|Locutor|Voz en off|Visual|Audio|Escena \d+)\s*:", " ", texto, flags=re.I)
    texto = re.sub(r"[#*_<>`|~•■●\-+*]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    palabras = texto.split()
    if len(palabras) > max_palabras:
        texto = " ".join(palabras[:max_palabras])
    texto = texto.strip()
    if texto and not texto[-1] in ".!?":
        texto += "."
    return texto

def crear_tarjeta_hook(texto, ruta):
    img = Image.new("RGB", (1080, 1920), (10, 13, 25))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 780, 1080, 800], fill=(255, 200, 0))
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "arialbd.ttf", "Arial"]:
        try:
            font = ImageFont.truetype(fp, 88)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
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

async def paso_voz(texto, audio, voz):
    print(f"   🎙️  Generando voz neural ({voz})...")
    comm = edge_tts.Communicate(texto, voz, rate="+6%", pitch="+2Hz")
    raw = audio.parent / "raw.mp3"
    await comm.save(str(raw))
    af_filter = "highpass=f=80,lowpass=f=12000,loudnorm=I=-16:TP=-1.5:LRA=11"
    run_ffmpeg(["ffmpeg", "-y", "-i", str(raw.name), "-af", af_filter, "-ar", "44100", "-b:a", "192k", audio.name], "voz", cwd=audio.parent)
    raw.unlink(missing_ok=True)

def paso_subtitulos(audio, srt):
    print("   📝 Generando subtítulos rápidos...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), language="es", vad_filter=True, word_timestamps=True)
    
    words_list = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words_list.append(w)
                
    srt_entries = []
    current_group = []
    for w in words_list:
        word_text = w.word.strip().upper()
        if not word_text:
            continue
        if current_group and (len(current_group) >= 3 or len(" ".join([x.word.strip().upper() for x in current_group]) + " " + word_text) > 22):
            srt_entries.append((current_group[0].start, current_group[-1].end, " ".join([x.word.strip().upper() for x in current_group])))
            current_group = []
        current_group.append(w)
    if current_group:
        srt_entries.append((current_group[0].start, current_group[-1].end, " ".join([x.word.strip().upper() for x in current_group])))
        
    lines = []
    for idx, (start, end, text) in enumerate(srt_entries, 1):
        s_m, s_s = divmod(start, 60); s_h, s_m = divmod(s_m, 60); s_ms = int((s_s % 1) * 1000)
        e_m, e_s = divmod(end, 60); e_h, e_m = divmod(e_m, 60); e_ms = int((e_s % 1) * 1000)
        t_start = f"{int(s_h):02d}:{int(s_m):02d}:{int(s_s):02d},{s_ms:03d}"
        t_end = f"{int(e_h):02d}:{int(e_m):02d}:{int(e_s):02d},{e_ms:03d}"
        lines += [str(idx), f"{t_start} --> {t_end}", text, ""]
    srt.write_text("\n".join(lines), encoding="utf-8")

PALABRAS_CLAVE_LITE = {"ia", "ai", "chatgpt", "gpu", "apple", "google", "usd", "dolares", "secreto", "impacto", "nuevo", "increible", "robot", "nasa"}

def draw_transparent_subtitle_lite(text, output_path, width=1080, height=1920):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    if not text:
        img.save(output_path, "PNG")
        return
    draw = ImageDraw.Draw(img)
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Impact.ttf", "/System/Library/Fonts/Supplemental/Arial Black.ttf", "impact.ttf", "Arial"]:
        try:
            font = ImageFont.truetype(fp, 68)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
        
    words = text.split()
    y = int(height * 0.72)
    line_str = " ".join(words)
    bbox = draw.textbbox((0, 0), line_str, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    
    cur_x = x
    for w in words:
        w_clean = re.sub(r"[^\w]", "", w.lower())
        color = "#FFE600" if (w_clean in PALABRAS_CLAVE_LITE or any(c.isdigit() for c in w)) else "#FFFFFF"
        # Contorno 3D negro
        for ox in range(-5, 6):
            for oy in range(-5, 6):
                draw.text((cur_x + ox, y + oy), w, font=font, fill="#000000")
        draw.text((cur_x, y), w, font=font, fill=color)
        w_bbox = draw.textbbox((0, 0), w + " ", font=font)
        cur_x += (w_bbox[2] - w_bbox[0])
    img.save(output_path, "PNG")

def paso_imagenes_lite(prompts, work, n, tema="", investigacion=None):
    print(f"   🎨 Generando {n} recursos visuales (Edición Lite)...")
    config = cfg()
    w, h = 1080, 1920
    rutas = []
    
    # 1. Fotos reales de producto
    if config.get("fotos_reales", {}).get("activado", True):
        fotos_reales = obtener_imagenes_producto_real(tema, investigacion, work, cantidad=2)
        for idx, f_real in enumerate(fotos_reales):
            salida_comp = work / f"i{len(rutas)}.jpg"
            if componer_smart_backdrop(f_real, salida_comp, width=w, height=h):
                rutas.append(f"i{len(rutas)}.jpg")
                print(f"      🖼️ [Producto Real {idx+1}] Composición Anti-Stretch lista.")
                
    # 2. Generación Flux para el resto
    import requests, urllib.parse
    restantes = n - len(rutas)
    for i in range(restantes):
        idx_act = len(rutas)
        prompt_txt = prompts[i % len(prompts)] if prompts else "cinematic tech scene"
        p_enc = urllib.parse.quote(f"{prompt_txt}, hyperrealistic vertical 8k")
        url = f"https://image.pollinations.ai/prompt/{p_enc}?width={w}&height={h}&seed={1000+idx_act*37}&model=flux&nologo=true"
        tmp_p = work / f"tmp_{idx_act}.jpg"
        try:
            r = requests.get(url, timeout=40)
            if r.status_code == 200 and len(r.content) > 5000:
                tmp_p.write_bytes(r.content)
                run_ffmpeg(["ffmpeg", "-y", "-i", f"tmp_{idx_act}.jpg", "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1", f"i{idx_act}.jpg"], "scale", cwd=work)
                tmp_p.unlink(missing_ok=True)
                rutas.append(f"i{idx_act}.jpg")
                print(f"      ✅ Imagen {idx_act+1}/{n} lista")
        except Exception:
            pass
            
    return rutas

def paso_render_lite(imagenes, audio, srt_path, musica, salida, work):
    print("   🎬 Renderizando video 1080p con subtítulos virales en Pillow...")
    dur_audio = get_audio_duration(audio)
    w, h = 1080, 1920
    
    # 1. Crear fondo de imágenes con Ken Burns suave
    imgs_validas = [work / img for img in imagenes if (work / img).exists()]
    if not imgs_validas:
        imgs_validas = [work / "i0.jpg"]
    D = max(3.5, (dur_audio + 1) / len(imgs_validas))
    
    with open(work / "concat_imgs.txt", "w", encoding="utf-8") as f:
        for img_p in imgs_validas:
            f.write(f"file '{img_p.resolve()}'\nduration {D:.2f}\n")
        f.write(f"file '{imgs_validas[-1].resolve()}'\n")
        
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_imgs.txt",
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1",
        "-r", "30", "-pix_fmt", "yuv420p", "background.mp4"
    ], "fondo", cwd=work)
    
    # 2. Generar subtítulos quemados en Pillow
    srt_content = Path(srt_path).read_text(encoding="utf-8")
    blocks = [b.strip() for b in srt_content.split("\n\n") if b.strip()]
    entries = []
    for b in blocks:
        lines = b.split("\n")
        if len(lines) >= 3:
            times = lines[1].split(" --> ")
            def parse_time(ts):
                h, m, s = ts.strip().split(":")
                s, ms = s.split(",")
                return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
            entries.append((parse_time(times[0]), parse_time(times[1]), " ".join(lines[2:])))
            
    concat_subs = []
    cur_t = 0.0
    for idx, (st, en, txt) in enumerate(entries):
        if st > cur_t + 0.05:
            f_empty = f"sub_empty_{idx}.png"
            draw_transparent_subtitle_lite("", work / f_empty, width=w, height=h)
            concat_subs.append(f"file '{f_empty}'\nduration {st - cur_t:.3f}\n")
        f_sub = f"sub_{idx:03d}.png"
        draw_transparent_subtitle_lite(txt, work / f_sub, width=w, height=h)
        concat_subs.append(f"file '{f_sub}'\nduration {en - st:.3f}\n")
        cur_t = en
    if dur_audio > cur_t:
        concat_subs.append(f"file 'sub_empty_end.png'\nduration {dur_audio - cur_t:.3f}\n")
        draw_transparent_subtitle_lite("", work / "sub_empty_end.png", width=w, height=h)
    (work / "concat_subtitles.txt").write_text("".join(concat_subs), encoding="utf-8")
    
    # 3. Mezclar video final
    cmd = [
        "ffmpeg", "-y", "-i", "background.mp4",
        "-f", "concat", "-safe", "0", "-i", "concat_subtitles.txt",
        "-i", str(audio.resolve())
    ]
    if musica and Path(musica).exists():
        cmd += ["-stream_loop", "-1", "-i", str(Path(musica).resolve())]
        fc = "[0:v][1:v]overlay=0:0[outv];[3:a]volume=0.20[m];[m][2:a]sidechaincompress=threshold=0.03:ratio=8[md];[2:a][md]amix=inputs=2:duration=first[outa]"
    else:
        fc = "[0:v][1:v]overlay=0:0[outv];[2:a]anull[outa]"
        
    cmd += ["-filter_complex", fc, "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(salida.resolve())]
    run_ffmpeg(cmd, "render final lite", cwd=work)

async def ejecutar_lite():
    print("\n" + "="*65 + "\n⚡ INICIANDO TIKTOK AI GENERATOR (EDICIÓN LITE / BAJOS RECURSOS)\n" + "="*65)
    config = cfg()
    temas = trends_module.obtener_noticias_filtradas(cantidad=1)
    if not temas:
        print("❌ No se obtuvieron noticias de tendencias.")
        return
        
    tema = temas[0]
    print(f"\n🎯 TEMA SELECCIONADO: {tema}\n")
    slug = slugify(tema)
    work = Path("output/work") / slug
    work.mkdir(parents=True, exist_ok=True)
    
    # 1. Investigación estructurada
    print("   [1/6] Investigando tema...")
    investigacion = investigar_tema(tema)
    
    # 2. Guion
    print("   [2/6] Redactando guion optimizado...")
    guion_raw = generar_guion(tema, duracion_segundos=35, investigacion=investigacion)
    guion = sanear_guion(guion_raw, max_palabras=85)
    print(f"   ✅ Guion: {len(guion.split())} palabras")
    
    # 3. Hook Card & Audio
    print("   [3/6] Sintetizando voz y tarjeta de impacto...")
    crear_tarjeta_hook(guion.split(". ")[0][:65], work / "i0.jpg")
    audio_path = work / "voz.mp3"
    await paso_voz(guion, audio_path, config.get("voz", "es-US-AlonsoNeural"))
    
    # 4. Subtítulos
    print("   [4/6] Transcribiendo subtítulos...")
    srt_path = work / "subs.srt"
    paso_subtitulos(audio_path, srt_path)
    
    # 5. Imágenes (Fotos reales + Flux)
    print("   [5/6] Descargando fotos reales y arte Flux...")
    prompts = generar_prompts_para_guion(guion, 5, investigacion=investigacion)
    fotos = paso_imagenes_lite(prompts, work, 5, tema=tema, investigacion=investigacion)
    imagenes = ["i0.jpg"] + fotos
    
    # 6. Música y Render
    print("   [6/6] Ensamblando y masterizando video...")
    musica = obtener_musica_para(tema, 0)
    salida = Path(config["salida_videos"]) / f"{datetime.now():%Y%m%d_%H%M}_{slug}.mp4"
    salida.parent.mkdir(parents=True, exist_ok=True)
    
    paso_render_lite(imagenes, audio_path, srt_path, musica, salida, work)
    
    if salida.exists() and salida.stat().st_size > 100000:
        print(f"\n🎉 ¡VIDEO LITE GENERADO CON ÉXITO!")
        print(f"   📁 Ruta: {salida}")
        print(f"   ⚖️ Tamaño: {salida.stat().st_size // (1024*1024)} MB")
        
        # Metadatos SEO
        generar_metadata(tema, guion, salida, 0)
    else:
        print("❌ Error: Video no se pudo renderizar.")

if __name__ == "__main__":
    asyncio.run(ejecutar_lite())
