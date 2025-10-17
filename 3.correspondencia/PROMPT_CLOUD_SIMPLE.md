# 🚀 PROMPT: Adaptar IRCA Manager para Streamlit Cloud

## OBJETIVO
Tengo una aplicación Streamlit que genera reportes Word. Funciona local pero necesito desplegarla en Streamlit Cloud. Solo necesito arreglar 3 cosas:
1. **Paso 1:** Cambiar path absoluto que busca archivos fuera de la app
2. Eliminar el folder picker nativo (usa tkinter que no funciona en cloud)
3. Permitir descargar los reportes como archivo ZIP

## PROBLEMA ACTUAL

Mi app tiene un folder picker que NO funciona en cloud:
```python
# streamlit_app/views/streamlit_ui.py (líneas 965-997)
def _show_folder_picker(self):
    import tkinter as tk  # ❌ No funciona en Streamlit Cloud
    from tkinter import filedialog
    folder_path = filedialog.askdirectory()
```

Y después copia archivos a carpeta local del usuario:
```python
# workflow_controller.py
def prepare_download_package(self, custom_folder):
    shutil.copytree(source, destination)  # ❌ No funciona en cloud
```

## ESTRUCTURA DEL PROYECTO

```
3.correspondencia/
├── main.py                      # Punto de entrada Streamlit
├── requirements.txt             # Dependencias (streamlit, pandas, python-docx)
├── streamlit_app/
│   ├── views/streamlit_ui.py   # UI principal - MODIFICAR AQUÍ
│   ├── controllers/workflow_controller.py  # Lógica - MODIFICAR AQUÍ
│   ├── models/report_model.py  # Genera reportes Word
│   └── config/settings.py      # Paths - MODIFICAR path absoluto
├── Datos/
│   ├── IRCA(%).csv                      # ✅ YA ESTÁ EN REPO
│   ├── Resultados_por_Aeropuerto/       # ✅ YA ESTÁ EN REPO (datos origen Paso 1)
│   └── [Ciudades]/                      # Carpetas que genera el flujo
├── Plantillas/
│   └── *.docx                 # ✅ YA ESTÁN EN REPO (no subir)
└── Scripts/
    └── *.py                   # Scripts de procesamiento
```

## LO QUE NECESITO

### 1. ARREGLAR PASO 1 - Cambiar path absoluto en settings.py (línea 26):

**PROBLEMA:** El Paso 1 busca archivos fuera de la app
```python
# ❌ ACTUAL: Busca en otra carpeta del sistema
self.ORIGEN_DIR = Path(r"C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\2.Limpieza\Resultados_por_Aeropuerto")
```

**SOLUCIÓN:** Ya subí esos datos al repo en `Datos/Resultados_por_Aeropuerto/`
```python
# ✅ CAMBIAR A: Path relativo dentro de la app
self.ORIGEN_DIR = self.BASE_DIR / "Datos" / "Resultados_por_Aeropuerto"
```

Los archivos que el Paso 1 necesita YA ESTÁN en el repo:
```
Datos/
  └── Resultados_por_Aeropuerto/  ← Nueva carpeta con datos de origen
      ├── Aguachica/
      ├── Armenia/
      ├── Barranquilla/
      └── ... (datos Excel por aeropuerto)
```

### 2. Reemplazar sección de descarga en `streamlit_ui.py` (líneas 473-701):

**ACTUAL (NO FUNCIONA EN CLOUD):**
- Botón "Seleccionar Carpeta" con tkinter
- Copia archivos a PC del usuario
- Botón "Abrir Carpeta" con os.startfile()

**NECESITO (FUNCIONA EN CLOUD):**
- Generar ZIP con todos los reportes Word
- Botón `st.download_button()` para descargar el ZIP
- Simple y directo

### 3. Modificar función en `workflow_controller.py`:

**ACTUAL:**
```python
def prepare_download_package(self, custom_folder):
    # Copia archivos a carpeta local
    shutil.copytree(datos_path, destino_path)
```

**NECESITO:**
```python
def prepare_download_zip(self) -> bytes:
    # Crear ZIP en memoria con reportes Word
    # Retornar bytes del ZIP
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Agregar archivos reporte_*.docx
    
    return zip_buffer.getvalue()
```

## ARCHIVOS A MODIFICAR

Solo necesito modificar estos 3 archivos:

1. **`streamlit_app/config/settings.py`**
   - Cambiar `ORIGEN_DIR` de path absoluto a relativo (línea 26)
   - De: `Path(r"C:\Users\...\2.Limpieza\Resultados_por_Aeropuerto")`
   - A: `self.BASE_DIR / "Datos" / "Resultados_por_Aeropuerto"`

2. **`streamlit_app/controllers/workflow_controller.py`**
   - Cambiar `prepare_download_package()` a `prepare_download_zip()`
   - Retornar bytes del ZIP en lugar de copiar archivos

3. **`streamlit_app/views/streamlit_ui.py`**
   - Eliminar función `_show_folder_picker()` (líneas 965-997)
   - Reemplazar sección "Descarga de Reportes" (líneas 473-701) con:
     ```python
     if st.button("📥 Descargar Reportes", type="primary"):
         zip_bytes = self.workflow_controller.prepare_download_zip()
         
         st.download_button(
             label="💾 Descargar ZIP con Reportes",
             data=zip_bytes,
             file_name=f"reportes_irca_{mes}_{año}.zip",
             mime="application/zip"
         )
     ```

## DEPENDENCIAS (YA INSTALADAS)
```
streamlit==1.49.1
pandas==2.3.2
python-docx==1.2.0
openpyxl==3.1.5
```

## LO QUE NO NECESITO CAMBIAR
- ✅ Plantillas y CSV ya están en el repo
- ✅ El flujo de 3 pasos funciona bien
- ✅ La UI y navegación está bien
- ✅ Los scripts de procesamiento funcionan
- ✅ Solo arreglar la descarga

## ENTREGABLES

Dame el código modificado de estos 3 archivos:
1. `settings.py` - cambiar ORIGEN_DIR a path relativo (línea 26)
2. `workflow_controller.py` - función para generar ZIP en memoria
3. `streamlit_ui.py` - nueva sección de descarga con st.download_button()

---

**RESUMEN:** 
- Arreglar Paso 1: path absoluto → path relativo (`Datos/Resultados_por_Aeropuerto`)
- Arreglar descarga: copiar a carpeta local → descargar ZIP directo

