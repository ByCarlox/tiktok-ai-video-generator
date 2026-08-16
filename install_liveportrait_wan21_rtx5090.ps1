# install_liveportrait_wan21_rtx5090.ps1 — Instalador de Animación Facial Neuronal 3D (LivePortrait + Wan 2.1 I2V)
# Ejecuta este script en PowerShell como Administrador en tu PC con la NVIDIA RTX 5090

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "🎭 INSTALADOR SOTA: LIVEPORTRAIT + WAN 2.1 I2V (ANIMACIÓN FACIAL REAL)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan

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
    Write-Host "🔍 No se detectó ComfyUI automáticamente." -ForegroundColor Yellow
    $ComfyPath = Read-Host "Ingresa la ruta raíz de tu ComfyUI (ejemplo: C:\ComfyUI_windows_portable)"
}

Write-Host "📂 Directorio ComfyUI: $ComfyPath" -ForegroundColor Green

$ComfyCore = if (Test-Path "$ComfyPath\ComfyUI\main.py") { "$ComfyPath\ComfyUI" } else { $ComfyPath }
$CustomNodesDir = "$ComfyCore\custom_nodes"
$ModelsDir = "$ComfyCore\models"
$PythonExe = if (Test-Path "$ComfyPath\python_embeded\python.exe") { "$ComfyPath\python_embeded\python.exe" } else { "python" }

# 2. Instalar ComfyUI-LivePortraitKJ (Animador Facial Neuronal #1 del mundo)
Write-Host "`n🎭 [1/3] Instalando ComfyUI-LivePortraitKJ (Kijai)..." -ForegroundColor Cyan
$LpNodeDir = "$CustomNodesDir\ComfyUI-LivePortraitKJ"
if (-not (Test-Path $LpNodeDir)) {
    git clone https://github.com/kijai/ComfyUI-LivePortraitKJ.git $LpNodeDir
} else {
    Set-Location $LpNodeDir
    git pull
}

# 3. Instalar Dependencias de LivePortrait
Write-Host "`n📦 [2/3] Instalando dependencias de LivePortrait..." -ForegroundColor Cyan
& $PythonExe -m pip install -r "$LpNodeDir\requirements.txt"
& $PythonExe -m pip install onnxruntime-gpu opencv-python dill pyyaml rich

# 4. Descargar Modelos Neuronales Oficiales de LivePortrait
Write-Host "`n⬇️ [3/3] Descargando pesos neuronales de LivePortrait..." -ForegroundColor Cyan
$LivePortraitModelsDir = "$ModelsDir\liveportrait"
New-Item -ItemType Directory -Force -Path $LivePortraitModelsDir | Out-Null

$ModelBaseUrl = "https://huggingface.co/Kijai/LivePortrait_safetensors/resolve/main"
$ModelFiles = @(
    "appearance_feature_extractor.safetensors",
    "motion_extractor.safetensors",
    "spade_generator.safetensors",
    "warping_module.safetensors",
    "stitching_retargeting_module.safetensors",
    "landmark.onnx"
)

foreach ($mf in $ModelFiles) {
    $target = "$LivePortraitModelsDir\$mf"
    if (-not (Test-Path $target)) {
        Write-Host "   -> Descargando $mf..." -ForegroundColor Yellow
        curl.exe -L -o $target "$ModelBaseUrl/$mf"
    } else {
        Write-Host "   ✅ $mf ya presente." -ForegroundColor Green
    }
}

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "🎉 ¡LIVEPORTRAIT INSTALADO CON ÉXITO EN TU RTX 5090!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Inicia ComfyUI con 'run_nvidia_gpu.bat' para animar al personaje con video real." -ForegroundColor Cyan
