# 🛩️ Sistema IRCA - Aerocivil

Aplicación web local desarrollada con **Streamlit** para automatizar la generación de informes técnicos de calidad del agua (IRCA) para aeropuertos.

## 📋 Descripción

Esta aplicación envuelve el sistema existente de scripts Python en una **arquitectura MVC** profesional, proporcionando una interfaz web intuitiva para el proceso de generación de informes IRCA manteniendo toda la lógica de negocio existente intacta.

## 🏗️ Arquitectura

### Estructura del Proyecto
```
3.correspondencia/
├── 📂 Scripts/                       # Scripts originales (NO TOCAR)
│   ├── generador_base_script.py      # Paso 1: Generador Base
│   ├── rellenador_tags.py            # Paso 2: Procesamiento IRCA
│   ├── Correspondencia.py            # Paso 3: Generación Reportes
│   └── verificador_fotos.py          # Función opcional
├── 📂 Datos/                         # Datos y archivos generados
├── 📂 Plantillas/                    # Plantillas Word por aeropuerto
├── 📂 streamlit_app/                 # Nueva capa MVC
│   ├── 📂 models/                    # Wrappers de scripts
│   ├── 📂 controllers/               # Lógica de control
│   ├── 📂 views/                     # Interfaz Streamlit
│   └── 📂 config/                    # Configuración
├── main.py                           # Punto de entrada
├── requirements.txt                  # Dependencias
└── README.md                         # Este archivo
```

### Flujo Obligatorio Secuencial
1. **Paso 1: Generador Base** → Crea estructura de carpetas y archivos
2. **Paso 2: Procesamiento IRCA** → Rellena hojas Excel con datos validados  
3. **Paso 3: Generación Reportes** → Genera informes Word finales

⚠️ **IMPORTANTE**: Los pasos deben ejecutarse en orden. No es posible saltarse pasos.

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- Acceso a las carpetas de datos y plantillas existentes

### Instalación
```bash
# 1. Navegar al directorio del proyecto
cd "C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\3.correspondencia"

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run main.py
```

### Acceso a la Aplicación
- La aplicación se abrirá automáticamente en el navegador
- URL local: `http://localhost:8501`
- Para detener: `Ctrl + C` en la terminal

## 📊 Funcionalidades

### Dashboard Principal
- **Métricas del Sistema**: Total aeropuertos, carpetas creadas, reportes generados
- **Estado del Flujo**: Progreso visual de los 3 pasos obligatorios
- **Gráficos IRCA**: Visualización de datos de calidad del agua
- **Salud del Sistema**: Verificación automática de configuración

### Flujo Principal
- **Ejecución Individual**: Ejecutar pasos uno por uno con validaciones
- **Flujo Completo**: Ejecutar los 3 pasos automáticamente
- **Validaciones**: Imposible ejecutar pasos fuera de orden
- **Monitoreo**: Estado en tiempo real de cada proceso

### Funciones Opcionales
- **Verificación de Fotos**: Validar existencia de imágenes por ciudad
- **Configuración**: Ver y validar rutas del sistema
- **Logs**: Historial de ejecuciones y validaciones

## 🔧 Configuración

### Rutas del Sistema
El sistema utiliza estas rutas configuradas automáticamente:

- **Scripts**: `./Scripts/` (scripts originales)
- **Datos**: `./Datos/` (archivos Excel y carpetas por ciudad)
- **Plantillas**: `./Plantillas/` (plantillas Word por aeropuerto)
- **IRCA**: `./Datos/IRCA(%).xlsx` (archivo principal de datos)
- **Origen**: `../../2.Limpieza/Resultados_por_Aeropuerto/` (fuente de datos)

### Estados de Pasos
El sistema mantiene automáticamente el estado de cada paso usando archivos de control:
- `.paso1_completed` - Paso 1 ejecutado exitosamente
- `.paso2_completed` - Paso 2 ejecutado exitosamente  
- `.paso3_completed` - Paso 3 ejecutado exitosamente

## 🎯 Características Principales

### ✅ Ventajas del Sistema MVC
- **Separación de Responsabilidades**: Modelos, Controladores y Vistas independientes
- **Mantenibilidad**: Fácil modificación sin afectar scripts originales
- **Escalabilidad**: Posible agregar nuevas funcionalidades
- **Profesionalismo**: Interfaz web moderna para demostrar al gerente

### 🔒 Validaciones de Seguridad
- **Flujo Secuencial Obligatorio**: Imposible ejecutar pasos fuera de orden
- **Validaciones de Prerequisitos**: Verificación automática antes de ejecutar
- **Manejo de Errores**: Captura y muestra errores de forma comprensible
- **Timeouts**: Prevención de procesos colgados

### 📈 Monitoreo y Logs
- **Estado en Tiempo Real**: Actualización automática del progreso
- **Historial de Ejecuciones**: Registro completo de todas las operaciones
- **Métricas de Rendimiento**: Tiempo de ejecución y tasa de éxito
- **Salud del Sistema**: Verificación automática de configuración

## 🛠️ Solución de Problemas

### Problemas Comunes

#### Error: "Carpeta Scripts no encontrada"
- **Causa**: Ejecutando desde directorio incorrecto
- **Solución**: Navegar a `3.correspondencia/` antes de ejecutar

#### Error: "Archivo IRCA no encontrado"
- **Causa**: Falta el archivo `IRCA(%).xlsx` en `Datos/`
- **Solución**: Verificar que el archivo existe y es accesible

#### Error: "Sin permisos de escritura"
- **Causa**: Permisos insuficientes en carpeta `Datos/`
- **Solución**: Ejecutar como administrador o cambiar permisos

#### Los botones aparecen bloqueados
- **Causa**: Pasos anteriores no completados
- **Solución**: Ejecutar pasos en orden secuencial obligatorio

### Comandos de Depuración
```bash
# Verificar instalación de dependencias
pip list | grep streamlit

# Ejecutar con información de depuración
streamlit run main.py --logger.level=debug

# Limpiar cache de Streamlit
streamlit cache clear
```

## 📞 Soporte

### Verificación de Sistema
La aplicación incluye verificación automática de:
- ✅ Existencia de rutas críticas
- ✅ Disponibilidad de scripts
- ✅ Acceso a archivos de datos
- ✅ Permisos de escritura

### Logs del Sistema
- Acceder a **"📋 Logs"** en la barra lateral
- Ver historial completo de ejecuciones
- Exportar configuración del sistema
- Limpiar logs cuando sea necesario

## 🔄 Actualizaciones

### Agregar Nuevos Aeropuertos
1. Agregar ciudad a `settings.AEROPUERTOS`
2. Crear plantilla Word correspondiente
3. Actualizar diccionario de fotos si es necesario

### Modificar Scripts Originales
⚠️ **NO RECOMENDADO**: Los scripts en `Scripts/` son código de producción.

Si es absolutamente necesario:
1. Hacer backup completo
2. Probar cambios en ambiente de desarrollo
3. Actualizar wrappers en `models/` si cambian interfaces

## 📄 Licencia

Sistema interno de Aerocivil para automatización de informes IRCA.

---
**Desarrollado con ❤️ para mejorar la eficiencia del proceso de informes técnicos de calidad del agua en aeropuertos.**
