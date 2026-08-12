#!/bin/bash
source .venv/bin/activate
echo "🔍 Paso 1: Buscando tendencias..."
python trends.py
echo ""
echo "🎬 Paso 2: Generando videos..."
python pipeline.py
echo ""
echo "🎉 Todo listo. Revisa output/videos/"