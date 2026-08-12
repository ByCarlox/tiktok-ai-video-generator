#!/usr/bin/env python3
# test_musica.py - Prueba manual del sistema de música
from musica import obtener_musica_para
from pathlib import Path

print("🎵 Probando descarga de música...\n")

# Probar con un tema simple
resultado = obtener_musica_para("tecnologia futurista", 0)

if resultado:
    print(f"\n✅ ÉXITO: Música en {resultado}")
    print(f"   Tamaño: {resultado.stat().st_size / 1024:.1f} KB")
else:
    print("\n❌ FALLÓ: No se pudo obtener música")
    print("   Revisa:")
    print("   1. Tu API key de Pixabay en config.yaml")
    print("   2. Conexión a internet")
    print("   3. Que FFmpeg esté instalado (brew install ffmpeg)")
