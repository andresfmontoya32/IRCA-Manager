@echo off
echo.
echo ======================================================
echo 🛩️ Sistema IRCA - Aerocivil (con entorno virtual)
echo ======================================================
echo.

REM Verificar que existe el entorno virtual
if not exist ".venv" (
    echo ❌ Error: No se encuentra el entorno virtual .venv
    echo.
    echo 💡 Ejecute primero: install_venv.bat
    echo.
    pause
    exit /b 1
)

REM Verificar que existe streamlit_app
if not exist "streamlit_app" (
    echo ❌ Error: No se encuentra la carpeta streamlit_app
    echo.
    echo 💡 Asegúrese de ejecutar desde el directorio correcto:
    echo    3.correspondencia\
    echo.
    pause
    exit /b 1
)

REM Verificar que existe la carpeta Scripts
if not exist "Scripts" (
    echo ❌ Error: No se encuentra la carpeta Scripts
    echo.
    echo 💡 Verifique la estructura de directorios
    echo.
    pause
    exit /b 1
)

echo ✅ Estructura de directorios verificada
echo ✅ Entorno virtual encontrado
echo.
echo 🚀 Activando entorno virtual e iniciando Sistema IRCA...
echo.
echo 💡 La aplicación se abrirá en: http://localhost:8501
echo ⚠️  Para detener: Ctrl + C en esta ventana
echo.

call .venv\Scripts\activate.bat && streamlit run main.py

echo.
echo 👋 Aplicación cerrada
pause
