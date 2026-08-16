# install_wan21_comfyui_weights.ps1 — Descarga de Pesos Oficiales Wan 2.1 I2V 14B para ComfyUI (RTX 5090)
# Ejecuta en PowerShell en tu PC con Windows y la RTX 5090

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "🚀 DESCARGADOR DE MODELOS WAN 2.1 (IMAGE-TO-VIDEO 14B) PARA COMFYUI" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Detectar ComfyUI
$Rutas = @("C:\ComfyUI_windows_portable", "C:\ComfyUI", "D:\ComfyUI_windows_portable", "D:\ComfyUI", "E:\ComfyUI_windows_portable", "$PWD")
$Comfy = ""
foreach ($r in $Rutas) {
    if (Test-Path "$r\ComfyUI\main.py" -or Test-Path "$r\main.py") {
        $Comfy = $r
        break
    }
}

if ($Comfy -eq "") {
    $Comfy = Read-Host "Ingresa la ruta de ComfyUI (ej: C:\ComfyUI_windows_portable)"
}

$ComfyCore = if (Test-Path "$Comfy\ComfyUI\main.py") { "$Comfy\ComfyUI" } else { $Comfy }
$DiffDir = "$ComfyCore\models\diffusion_models"
$VaeDir = "$ComfyCore\models\vae"
$ClipDir = "$ComfyCore\models\text_encoders"
$ClipVisionDir = "$ComfyCore\models\clip_vision"

New-Item -ItemType Directory -Force -Path $DiffDir | Out-Null
New-Item -ItemType Directory -Force -Path $VaeDir | Out-Null
New-Item -ItemType Directory -Force -Path $ClipDir | Out-Null
New-Item -ItemType Directory -Force -Path $ClipVisionDir | Out-Null

Write-Host "📂 Directorio de Modelos ComfyUI: $ComfyCore\models" -ForegroundColor Green

# 2. Descargar Wan 2.1 VAE
$VaeFile = "$VaeDir\wan_2.1_vae.safetensors"
if (-not (Test-Path $VaeFile)) {
    Write-Host "`n📦 [1/4] Descargando Wan 2.1 VAE (wan_2.1_vae.safetensors)..." -ForegroundColor Yellow
    curl.exe -L -C - -o $VaeFile "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"
} else {
    Write-Host "✅ Wan 2.1 VAE ya presente." -ForegroundColor Green
}

# 3. Descargar Wan 2.1 UMT5-XXL Text Encoder (FP8)
$ClipFile = "$ClipDir\umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if (-not (Test-Path $ClipFile)) {
    Write-Host "`n📦 [2/4] Descargando Text Encoder UMT5-XXL (umt5_xxl_fp8_e4m3fn_scaled.safetensors)..." -ForegroundColor Yellow
    curl.exe -L -C - -o $ClipFile "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
} else {
    Write-Host "✅ Text Encoder UMT5-XXL ya presente." -ForegroundColor Green
}

# 4. Descargar CLIP Vision (para Image-to-Video)
$VisionFile = "$ClipVisionDir\clip_vision_h.safetensors"
if (-not (Test-Path $VisionFile)) {
    Write-Host "`n📦 [3/4] Descargando CLIP Vision (clip_vision_h.safetensors)..." -ForegroundColor Yellow
    curl.exe -L -C - -o $VisionFile "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"
} else {
    Write-Host "✅ CLIP Vision ya presente." -ForegroundColor Green
}

# 5. Descargar Wan 2.1 I2V 14B High Quality Diffusion Model (FP8 para máxima velocidad y fidelidad en 5090)
$WanModel = "$DiffDir\wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors"
if (-not (Test-Path $WanModel)) {
    Write-Host "`n📦 [4/4] Descargando Wan 2.1 Image-to-Video 14B (wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors ~14GB)..." -ForegroundColor Yellow
    curl.exe -L -C - -o $WanModel "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors"
} else {
    Write-Host "✅ Wan 2.1 I2V 14B ya presente." -ForegroundColor Green
}

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "🎉 ¡TODOS LOS PESOS DE WAN 2.1 INSTALADOS CON ÉXITO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Reinicia ComfyUI ('run_nvidia_gpu.bat') para cargar los modelos en la RTX 5090." -ForegroundColor Cyan
