#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛩️ IRCA Manager - Aerocivil
Sistema de Automatización de Informes de Calidad del Agua

Punto de entrada principal para la aplicación Streamlit
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar la aplicación
from streamlit_app.views.streamlit_ui import run_app

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not (current_dir / "streamlit_app").exists():
        print("❌ Error: No se encuentra la carpeta streamlit_app")
        print(f"   Directorio actual: {current_dir}")
        print("   Asegúrese de ejecutar desde el directorio 3.correspondencia/")
        sys.exit(1)
    
    # Verificar que existen los scripts
    scripts_dir = current_dir / "Scripts"
    if not scripts_dir.exists():
        print("❌ Error: No se encuentra la carpeta Scripts")
        print("   Verifique la estructura de directorios")
        sys.exit(1)
    
    print("🛩️ Iniciando IRCA Manager - Aerocivil")
    print("=" * 50)
    print("📂 Directorio de trabajo:", current_dir)
    print("📁 Scripts encontrados en:", scripts_dir)
    print("🌐 Iniciando servidor Streamlit...")
    print("=" * 50)
    
    # Ejecutar la aplicación
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar la aplicación: {str(e)}")
        print("💡 Consejos de solución:")
        print("   1. Verifique que todas las dependencias están instaladas")
        print("   2. Ejecute: pip install -r requirements.txt")
        print("   3. Asegúrese de estar en el directorio correcto")
        sys.exit(1)
