# test_comfy.py - Script de verificación y test de renderizado en RTX 5090
import requests
import json
import time

host = "http://100.95.107.65:8188"
print(f"🔍 Conectando con ComfyUI en {host}...")

try:
    r = requests.get(f"{host}/object_info/CheckpointLoaderSimple", timeout=5)
    if r.status_code == 200:
        ckpts = r.json().get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
        print(f"📦 Checkpoints detectados en la RTX 5090: {ckpts}")
        if not ckpts:
            print("⏳ Aún no hay modelos .safetensors en la carpeta ComfyUI/models/checkpoints/")
            exit(0)
        ckpt_target = ckpts[0]
    else:
        print(f"⚠️ Error consultando checkpoints: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

print(f"🚀 Enviando renderizado de prueba a la GPU RTX 5090 con el modelo [{ckpt_target}]...")
workflow = {
    "prompt": {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7.0, "denoise": 1.0, "latent_image": ["5", 0], "model": ["4", 0],
                "positive": ["6", 0], "negative": ["7", 0], "sampler_name": "euler", "scheduler": "normal", "seed": 12345, "steps": 20
            }
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_target}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 1024, "width": 576}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "cinematic 4k vertical tech scene, glowing futuristic quantum supercomputer, hyperrealistic, neon cyan and gold lights, 8k resolution"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry, low quality, distortion, text, watermark"}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "TikTokAI_Test", "images": ["8", 0]}}
    }
}

t0 = time.time()
res = requests.post(f"{host}/prompt", json=workflow, timeout=10)
if res.status_code == 200:
    prompt_id = res.json().get("prompt_id")
    print(f"🎉 ¡PETICIÓN ACEPTADA POR LA GPU! ID: {prompt_id}")
    print("⏳ Monitoreando generación en los núcleos CUDA de la RTX 5090...")
    for _ in range(30):
        time.sleep(1)
        hist = requests.get(f"{host}/history/{prompt_id}", timeout=5).json()
        if prompt_id in hist:
            elapsed = time.time() - t0
            print(f"🔥 ¡RENDER COMPLETADO EN {elapsed:.2f}s EN LA RTX 5090!")
            print("   Output generado:", hist[prompt_id].get("outputs", {}))
            break
        else:
            print("   ... Procesando en GPU ...")
else:
    print("Error:", res.text)
