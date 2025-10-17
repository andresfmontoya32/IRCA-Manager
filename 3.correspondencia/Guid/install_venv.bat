@echo off
echo.
echo ======================================================
echo 🛩️ Sistema IRCA - Aerocivil - Instalacion con venv
echo ======================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo.
    echo 💡 Instale Python 3.8 o superior desde:
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

echo.
echo 📦 Creando entorno virtual en .venv...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

echo.
echo 📦 Activando entorno virtual e instalando dependencias...
call .venv\Scripts\activate.bat && pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Error al instalar dependencias
    echo.
    echo 💡 Intente manualmente:
    echo    .venv\Scripts\activate.bat
    echo    pip install streamlit pandas openpyxl python-docx plotly tqdm
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas correctamente en .venv
echo.
echo 🎉 Instalación completada exitosamente
echo.
echo 💡 Para ejecutar la aplicación use: run_venv.bat
echo.
pause
