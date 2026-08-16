# vtuber_engine.py - v2.0 — Motor Cinemático de Presentadora con Escenarios IA Nativos
"""
Motor de Presentadora que utiliza la biblioteca de Escenarios Nativos Generados por IA:
- 01_intro_greeting: Saludo entusiasta con sonrisa y contacto visual.
- 02_explaining_tech: Explicación tecnológica con interfaz holográfica.
- 03_shock_mindblown: Reacción de asombro/impacto para ganchos virales.
- 04_mystery_conspiracy: Iluminación de misterio y claroscuro.
- 07_outro_farewell_wink: Despedida con guiño y llamado al CTA.
- v_avatar_pip.mov: Badge PIP circular de alta fidelidad con anillo de neón.
"""

import shutil
import subprocess
from pathlib import Path

def renderizar_vtuber_animada(
    base_cutout_path: Path,
    audio_path: Path,
    output_clip: Path,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    duracion_max: float = 3.5,
    modo: str = "full",
    tema: str = "",
    guion: str = ""
) -> bool:
    """
    Carga el clip cinemático pre-renderizado del Motion Vault o compone el escenario nativo sin trazos artificiales.
    """
    output_clip = Path(output_clip)
    output_clip.parent.mkdir(parents=True, exist_ok=True)
    
    vault_dir = Path("assets/avatar/motion_vault")
    scenarios_dir = Path("assets/avatar/scenarios")
    
    # Modo PIP
    if modo == "pip":
        pip_source = vault_dir / "v_avatar_pip.mov"
        if pip_source.exists():
            shutil.copy2(pip_source, output_clip)
            return True
            
    # Modo Full (Intro)
    # Seleccionar escenario por sentimiento/tema
    t = (tema + " " + guion).lower()
    if any(k in t for k in ["misterio", "conspiracion", "secreto", "dark", "revelado", "alien", "oculto"]):
        esc_key = "04_mystery_conspiracy"
    elif any(k in t for k in ["impactante", "locura", "alerta", "urgente", "increible", "millones", "prohibido", "brutal"]):
        esc_key = "03_shock_mindblown"
    elif any(k in t for k in ["lanzamiento", "nuevo", "gadget", "nvidia", "apple", "hardware", "chip", "robot", "ia"]):
        esc_key = "02_explaining_tech"
    else:
        esc_key = "01_intro_greeting"
        
    # Si existe el clip ya renderizado en Motion Vault, copiar directamente
    vid_vault = vault_dir / f"{esc_key}.mp4"
    if vid_vault.exists() and vid_vault.stat().st_size > 1000:
        shutil.copy2(vid_vault, output_clip)
        print(f"      🌸 Presentadora: Escenario Cinemático [{esc_key}] cargado con éxito.")
        return True
        
    # Si existe la imagen nativa en scenarios, renderizar movimiento de cámara limpio
    img_native = scenarios_dir / f"{esc_key}.jpg"
    if not img_native.exists():
        img_native = scenarios_dir / "01_intro_greeting.jpg"
        
    if img_native.exists():
        frames = int(duracion_max * fps)
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_native.resolve()),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
                   f"zoompan=z='min(zoom+0.0015,1.12)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            "-t", f"{duracion_max:.2f}", "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(output_clip.resolve())
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_clip.exists() and output_clip.stat().st_size > 0
        
    return False
