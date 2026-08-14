# install_wan21_rtx5090.ps1 — Instalador Automático de Wan 2.1 para ComfyUI en Windows (RTX 5090)
# Ejecuta este script en PowerShell como Administrador o dentro de tu carpeta de ComfyUI.

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 INSTALADOR AUTOMÁTICO WAN 2.1 (SOTA 14B) PARA COMFYUI (RTX 5090)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Detectar o pedir la ruta de ComfyUI
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
    Write-Host "🔍 No se detectó ComfyUI en rutas automáticas." -ForegroundColor Yellow
    $ComfyPath = Read-Host "Por favor ingresa la ruta raíz de tu ComfyUI (ejemplo: C:\ComfyUI_windows_portable)"
}

Write-Host "📂 Directorio de ComfyUI seleccionado: $ComfyPath" -ForegroundColor Green

# Ajustar rutas internas
$ComfyCore = if (Test-Path "$ComfyPath\ComfyUI\main.py") { "$ComfyPath\ComfyUI" } else { $ComfyPath }
$CustomNodesDir = "$ComfyCore\custom_nodes"
$ModelsDir = "$ComfyCore\models"
$PythonExe = if (Test-Path "$ComfyPath\python_embeded\python.exe") { "$ComfyPath\python_embeded\python.exe" } else { "python" }

# 2. Instalar el Custom Node ComfyUI-WanVideoWrapper
Write-Host "`n📦 [1/4] Clonando ComfyUI-WanVideoWrapper (kijai)..." -ForegroundColor Cyan
$WanNodeDir = "$CustomNodesDir\ComfyUI-WanVideoWrapper"
if (-not (Test-Path $WanNodeDir)) {
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git $WanNodeDir
} else {
    Write-Host "   El nodo ya existe. Actualizando..." -ForegroundColor Yellow
    Set-Location $WanNodeDir
    git pull
}

# 3. Instalar Dependencias de Python
Write-Host "`n📦 [2/4] Instalando dependencias de Python (FlashAttention, diffusers, etc.)..." -ForegroundColor Cyan
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r "$WanNodeDir\requirements.txt"
& $PythonExe -m pip install torch torchvision torchaudio --upgrade
& $PythonExe -m pip install accelerate einops diffusers sentencepiece ftfy

# 4. Crear carpetas de modelos
$DiffusionDir = "$ModelsDir\diffusion_models"
$TextEncDir = "$ModelsDir\text_encoders"
$VaeDir = "$ModelsDir\vae"

New-Item -ItemType Directory -Force -Path $DiffusionDir | Out-Null
New-Item -ItemType Directory -Force -Path $TextEncDir | Out-Null
New-Item -ItemType Directory -Force -Path $VaeDir | Out-Null

# 5. Descargar Modelos Oficiales de Alta Velocidad (FP8 optimizados para RTX 5090)
Write-Host "`n⬇️ [3/4] Descargando modelos oficiales de Wan 2.1 (Hugging Face)..." -ForegroundColor Cyan

# VAE
$VaeFile = "$VaeDir\wan_2.1_vae.safetensors"
if (-not (Test-Path $VaeFile)) {
    Write-Host "   Descargando Wan 2.1 VAE..." -ForegroundColor Yellow
    curl.exe -L -o $VaeFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors"
} else {
    Write-Host "   ✅ VAE ya presente." -ForegroundColor Green
}

# Text Encoder (UMT5 XXL FP8)
$TEncFile = "$TextEncDir\umt5_xxl_fp8_e4m3fn.safetensors"
if (-not (Test-Path $TEncFile)) {
    Write-Host "   Descargando Text Encoder UMT5-XXL FP8..." -ForegroundColor Yellow
    curl.exe -L -o $TEncFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/umt5_xxl_fp8_e4m3fn.safetensors"
} else {
    Write-Host "   ✅ Text Encoder ya presente." -ForegroundColor Green
}

# Wan 2.1 14B Text-to-Video (T2V) FP8 para 720P Ultra Calidad
$Wan14BFile = "$DiffusionDir\Wan2_1_T2V_14B_fp8_e4m3fn.safetensors"
if (-not (Test-Path $Wan14BFile)) {
    Write-Host "   Descargando Wan 2.1 14B T2V (FP8 para RTX 5090 ~14GB)..." -ForegroundColor Yellow
    curl.exe -L -o $Wan14BFile "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_T2V_14B_fp8_e4m3fn.safetensors"
} else {
    Write-Host "   ✅ Modelo Wan 2.1 14B T2V ya presente." -ForegroundColor Green
}

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "🎉 ¡INSTALACIÓN DE WAN 2.1 COMPLETADA CON ÉXITO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "Inicia ComfyUI con 'run_nvidia_gpu.bat' y tu Mac se conectará automáticamente por Tailscale." -ForegroundColor Cyan
