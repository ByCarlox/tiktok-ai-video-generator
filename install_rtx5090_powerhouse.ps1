# install_rtx5090_powerhouse.ps1 — Setup Completo de Máxima Calidad para PC con NVIDIA RTX 5090 (32GB VRAM)
# Instala Ollama LLMs Top-Tier + ComfyUI Wan 2.1 (14B SOTA T2V & I2V) + Reglas de Red

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "👑 SETUP POWERHOUSE RTX 5090: MÁXIMA CALIDAD AUDIOVISUAL & IA (32GB VRAM)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan

# ---------------------------------------------------------
# 1. INSTALACIÓN Y ACTUALIZACIÓN DE MODELOS OLLAMA LLM
# ---------------------------------------------------------
Write-Host "`n🧠 [1/3] Configurando Cerebro LLM en Ollama..." -ForegroundColor Cyan

# Habilitar acceso en red para Tailscale / Mac
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')
$env:OLLAMA_HOST = "0.0.0.0:11434"

# Iniciar servidor si no está corriendo
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

Write-Host "⬇️ Descargando Modelos LLM Top-Tier para la RTX 5090..." -ForegroundColor Yellow

# Qwen 2.5 32B (Modelo estrella de razonamiento profundo y redacción de guiones cinematográficos)
Write-Host "   -> Descargando Qwen 2.5 32B (Calidad SOTA)..." -ForegroundColor White
ollama pull qwen2.5:32b

# Qwen 2.5 72B Quantizado (Máxima capacidad posible que cabe en 32GB VRAM + RAM)
Write-Host "   -> Descargando Qwen 2.5 72B (Versión ultra pesada)..." -ForegroundColor White
ollama pull qwen2.5:72b-instruct-q4_K_M

# DeepSeek R1 32B (Razonamiento lógico paso a paso)
Write-Host "   -> Descargando DeepSeek R1 32B..." -ForegroundColor White
ollama pull deepseek-r1:32b

Write-Host "✅ Modelos Ollama listos." -ForegroundColor Green


# ---------------------------------------------------------
# 2. CONFIGURACIÓN DE COMFYUI Y NODOS SOTA WAN 2.1 (14B)
# ---------------------------------------------------------
Write-Host "`n🎬 [2/3] Configurando Motor de Video Wan 2.1 14B en ComfyUI..." -ForegroundColor Cyan

# Detectar ruta de ComfyUI
$RutasComunes = @(
    "C:\ComfyUI_windows_portable",
    "C:\ComfyUI",
    "D:\ComfyUI_windows_portable",
    "D:\ComfyUI",
    "E:\ComfyUI_windows_portable",
    "E:\ComfyUI",
    "$PWD"
)

$ComfyPath = ""
foreach ($r in $RutasComunes) {
    if (Test-Path "$r\ComfyUI\main.py" -or Test-Path "$r\main.py") {
        $ComfyPath = $r
        break
    }
}

if ($ComfyPath -eq "") {
    Write-Host "🔍 No se detectó ComfyUI automáticamente." -ForegroundColor Yellow
    $ComfyPath = Read-Host "Ingresa la ruta raíz de ComfyUI (ejemplo: C:\ComfyUI_windows_portable)"
}

Write-Host "📂 Directorio ComfyUI: $ComfyPath" -ForegroundColor Green

$ComfyCore = if (Test-Path "$ComfyPath\ComfyUI\main.py") { "$ComfyPath\ComfyUI" } else { $ComfyPath }
$CustomNodesDir = "$ComfyCore\custom_nodes"
$ModelsDir = "$ComfyCore\models"
$PythonExe = if (Test-Path "$ComfyPath\python_embeded\python.exe") { "$ComfyPath\python_embeded\python.exe" } else { "python" }

# Instalar Nodos de Video de Máxima Calidad
$WanNodeDir = "$CustomNodesDir\ComfyUI-WanVideoWrapper"
if (-not (Test-Path $WanNodeDir)) {
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git $WanNodeDir
} else {
    Set-Location $WanNodeDir
    git pull
}

# Video Helper Suite (para exportar a ProRes / H264 sin compresión)
$VhsDir = "$CustomNodesDir\ComfyUI-VideoHelperSuite"
if (-not (Test-Path $VhsDir)) {
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git $VhsDir
}

# Instalar dependencias
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r "$WanNodeDir\requirements.txt"
& $PythonExe -m pip install accelerate einops diffusers sentencepiece ftfy torchvision torchaudio

# Crear carpetas de modelos
$DiffusionDir = "$ModelsDir\diffusion_models"
$TextEncDir = "$ModelsDir\text_encoders"
$VaeDir = "$ModelsDir\vae"

New-Item -ItemType Directory -Force -Path $DiffusionDir | Out-Null
New-Item -ItemType Directory -Force -Path $TextEncDir | Out-Null
New-Item -ItemType Directory -Force -Path $VaeDir | Out-Null

# Descargar VAE Oficial Wan 2.1
$VaeFile = "$VaeDir\wan_2.1_vae.safetensors"
if (-not (Test-Path $VaeFile)) {
    Write-Host "⬇️ Descargando Wan 2.1 VAE..." -ForegroundColor Yellow
    curl.exe -L -o $VaeFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors"
}

# Descargar Text Encoder UMT5-XXL FP8
$TEncFile = "$TextEncDir\umt5_xxl_fp8_e4m3fn.safetensors"
if (-not (Test-Path $TEncFile)) {
    Write-Host "⬇️ Descargando Text Encoder UMT5-XXL FP8..." -ForegroundColor Yellow
    curl.exe -L -o $TEncFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/umt5_xxl_fp8_e4m3fn.safetensors"
}

# 1. Wan 2.1 14B Text-to-Video (T2V) — Máxima calidad de generación desde texto
$WanT2VFile = "$DiffusionDir\Wan2_1_T2V_14B_fp8_e4m3fn.safetensors"
if (-not (Test-Path $WanT2VFile)) {
    Write-Host "⬇️ Descargando Wan 2.1 14B Text-to-Video (FP8 ~14 GB)..." -ForegroundColor Yellow
    curl.exe -L -o $WanT2VFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_T2V_14B_fp8_e4m3fn.safetensors"
}

# 2. Wan 2.1 14B Image-to-Video 720P (I2V) — Para animar al personaje y fotos con movimiento 3D real
$WanI2VFile = "$DiffusionDir\Wan2_1_I2V_14B_720P_fp8_e4m3fn.safetensors"
if (-not (Test-Path $WanI2VFile)) {
    Write-Host "⬇️ Descargando Wan 2.1 14B Image-to-Video 720P (FP8 ~14 GB)..." -ForegroundColor Yellow
    curl.exe -L -o $WanI2VFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_I2V_14B_720P_fp8_e4m3fn.safetensors"
}

Write-Host "✅ Modelos Wan 2.1 listos en ComfyUI." -ForegroundColor Green


# ---------------------------------------------------------
# 3. REGLAS DE FIREWALL PARA ACCESO DESDE TU MAC (TAILSCALE)
# ---------------------------------------------------------
Write-Host "`n🛡️ [3/3] Abriendo puertos en Firewall de Windows..." -ForegroundColor Cyan
netsh advfirewall firewall add rule name="Ollama API 11434" dir=in action=allow protocol=TCP localport=11434 | Out-Null
netsh advfirewall firewall add rule name="ComfyUI API 8188" dir=in action=allow protocol=TCP localport=8188 | Out-Null

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "🎉 ¡INSTALACIÓN POWERHOUSE DE MÁXIMA CALIDAD COMPLETADA!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "1. En ComfyUI: Ejecuta 'run_nvidia_gpu.bat' (con --listen 0.0.0.0 --port 8188 --highvram)" -ForegroundColor Cyan
Write-Host "2. En Ollama: Ya está configurado con Qwen 2.5 32B / 72B en el puerto 11434." -ForegroundColor Cyan
