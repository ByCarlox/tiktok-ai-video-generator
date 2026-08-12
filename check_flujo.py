# check_flujo.py - Auditoría completa del sistema
import importlib
import json
import shutil
import subprocess
from pathlib import Path

import requests
import yaml

def ok(msg): print(f"   ✅ {msg}")
def fail(msg): print(f"   ❌ {msg}")
def warn(msg): print(f"   ⚠️ {msg}")

print("🔍 AUDITORÍA DEL SISTEMA\n")

# 1) Dependencias
print("1) Dependencias Python:")
for mod in ["edge_tts", "faster_whisper", "feedparser", "requests", "yaml"]:
    try:
        importlib.import_module(mod)
        ok(mod)
    except Exception:
        fail(f"{mod} no instalado → pip install {mod}")

# 2) FFmpeg
print("2) FFmpeg:")
if shutil.which("ffmpeg"):
    ok("ffmpeg instalado")
else:
    fail("ffmpeg no está → brew install ffmpeg")

# 3) Ollama
print("3) IA local (Ollama):")
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=3)
    modelos = [m["name"] for m in r.json().get("models", [])]
    ok(f"Ollama corriendo. Modelos: {', '.join(modelos) or 'NINGUNO'}")
except Exception:
    fail("Ollama no responde → ejecuta 'ollama serve' en OTRA terminal")

# 4) Config
print("4) Configuración:")
try:
    config = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    ok(f"IA: {config['ia']['proveedor']} / {config['ia']['modelo']}")
    ok(f"Voz: {config['voz']}")
    ok(f"Videos por corrida: {config['numero_videos']}")
except Exception as e:
    fail(f"config.yaml inválido: {e}")
    config = {}

# 5) Tendencias
print("5) Tendencias:")
tf = Path("output/trends.json")
if tf.exists():
    data = json.load(open(tf, encoding="utf-8"))
    trends = data.get("tendencias", [])
    ok(f"{len(trends)} tendencias guardadas")
    # Verificar que el filtro de temas sensibles funcionó
    prohibidas = [p.lower() for p in config.get("filtro", {}).get("palabras_excluir", [])]
    sensibles = [t for t in trends if any(p in t.lower() for p in prohibidas)]
    if sensibles:
        warn(f"{len(sensibles)} tendencias sensibles detectadas → vuelve a correr 'python trends.py'")
        for t in sensibles[:3]:
            warn(f"   - {t[:60]}")
    else:
        ok("Sin temas sensibles (filtro funcionando)")
else:
    fail("No existe output/trends.json → corre 'python trends.py'")

# 6) Música
print("6) Música:")
mp3s = list(Path("assets/musica").glob("*.mp3")) if Path("assets/musica").exists() else []
if mp3s:
    ok(f"{len(mp3s)} tracks en caché")
else:
    warn("Sin música en caché (se descargará al generar)")

# 7) Videos
print("7) Videos generados:")
videos = list(Path("output/videos").glob("*.mp4")) if Path("output/videos").exists() else []
if videos:
    for v in videos[:5]:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(v)],
            capture_output=True, text=True)
        dur = float(p.stdout.strip() or 0)
        ok(f"{v.name} ({dur:.0f}s, {v.stat().st_size//1024} KB)")
else:
    warn("Aún no hay videos")

# 8) Obsidian
print("8) Obsidian:")
vault = Path(config.get("obsidian_vault", "TikTok-AI-Passive"))
if vault.exists():
    ok(f"Vault existe: {vault}")
    if (vault / "Dashboard.md").exists():
        ok("Dashboard.md dentro del vault")
    else:
        fail("Dashboard.md NO está en el vault")
    eps = list((vault / "03-Contenidos/Episodios").glob("*")) if (vault / "03-Contenidos/Episodios").exists() else []
    ok(f"{len(eps)} episodios registrados")
else:
    fail("Vault no encontrado")

# 9) Integraciones del pipeline
print("9) Pipeline (integraciones):")
txt = Path("pipeline.py").read_text(encoding="utf-8") if Path("pipeline.py").exists() else ""
if "from musica import" in txt:
    ok("Música automática integrada")
else:
    fail("pipeline.py NO importa musica.py → añade 'from musica import obtener_musica_para'")
if "revisar_guion" in txt:
    ok("Revisión de guiones integrada")
else:
    warn("Sin revisión de guiones (opcional pero recomendado)")
if "run_ffmpeg" in txt or "traceback" in txt:
    ok("Manejo de errores de FFmpeg presente")
else:
    warn("Pipeline sin logs de error detallados")

print("\n" + "="*50)
print("📋 Auditoría terminada. Si todo está ✅, sigue al Paso 2.")