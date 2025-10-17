# 🚀 INSTRUCCIONES DE USO - Sistema IRCA

## ⚡ Inicio Rápido (3 pasos)

### 1. 📦 Instalación
```bash
# Opción A: Instalación automática (recomendado)
doble clic en → install.bat

# Opción B: Instalación manual
pip install -r requirements.txt
```

### 2. 🚀 Ejecutar Aplicación
```bash
# Opción A: Ejecución automática (recomendado)
doble clic en → run.bat

# Opción B: Ejecución manual
streamlit run main.py
```

### 3. 🌐 Acceder a la Aplicación
- Se abrirá automáticamente en el navegador
- URL: `http://localhost:8501`

---

## 🔄 Flujo de Trabajo Completo

### 📊 Dashboard (Primera Vista)
Al iniciar, verás:
- **Métricas**: Total aeropuertos, carpetas creadas, reportes generados
- **Estado del Flujo**: Progreso visual de los 3 pasos
- **Gráficos IRCA**: Distribución de datos por ciudad
- **Salud del Sistema**: Verificación automática

### 🔄 Flujo Principal (Secuencial Obligatorio)

#### Opción 1: Ejecución Automática Completa
1. Ir a **"🔄 Flujo Principal"** en la barra lateral
2. Hacer clic en **"⚡ EJECUTAR FLUJO COMPLETO"**
3. Esperar a que se completen los 3 pasos automáticamente

#### Opción 2: Ejecución Paso a Paso
1. **PASO 1: Generador Base** 
   - Clic en **"Ejecutar PASO1"**
   - Esperar confirmación ✅
   
2. **PASO 2: Procesamiento IRCA** (solo después de Paso 1)
   - Clic en **"Ejecutar PASO2"**  
   - Esperar confirmación ✅
   
3. **PASO 3: Generación Reportes** (solo después de Paso 2)
   - Clic en **"Ejecutar PASO3"**
   - Esperar confirmación ✅

### 🔧 Funciones Opcionales
1. Ir a **"🔧 Funciones Opcionales"**
2. **Verificar Fotos**:
   - Seleccionar ciudad específica o "Todas"
   - Clic en **"🔍 Verificar Fotos"**

### ⚙️ Configuración y Monitoreo
- **"⚙️ Configuración"**: Ver rutas y estado del sistema
- **"📋 Logs"**: Historial de ejecuciones y validaciones

---

## 🎯 Casos de Uso Típicos

### 🆕 Primera Vez (Setup Inicial)
```
1. Ejecutar install.bat
2. Ejecutar run.bat  
3. Dashboard → verificar métricas
4. Flujo Principal → "⚡ EJECUTAR FLUJO COMPLETO"
5. Verificar que se generaron todos los reportes
```

### 🔄 Uso Regular (Mes a Mes)
```
1. Actualizar archivo IRCA(%).xlsx con nuevos datos
2. Ejecutar run.bat
3. Flujo Principal → "⚡ EJECUTAR FLUJO COMPLETO"
4. Opcional: Verificar fotos si hay nuevas rutas
```

### 🔧 Mantenimiento
```
1. Configuración → verificar salud del sistema
2. Logs → revisar ejecuciones anteriores
3. Funciones Opcionales → validar fotos periódicamente
```

### 🛠️ Resolución de Problemas
```
1. Dashboard → revisar métricas del sistema
2. Configuración → verificar rutas y estados
3. Logs → identificar errores en historial
4. Flujo Principal → "🔄 Reiniciar Flujo" si es necesario
```

---

## 🚨 Validaciones Automáticas

### ✅ Antes de Ejecutar Cada Paso
- Verificación de archivos requeridos
- Validación de pasos anteriores completados
- Comprobación de permisos de escritura

### 🔒 Flujo Secuencial Obligatorio
- **Paso 2** solo se puede ejecutar si **Paso 1** está completo
- **Paso 3** solo se puede ejecutar si **Pasos 1 y 2** están completos
- Los botones se bloquean automáticamente si no se cumplen prerequisitos

### 📊 Monitoreo en Tiempo Real
- Estado visual de cada paso (⚪ Pendiente, 🔄 Ejecutando, ✅ Completado, ❌ Error)
- Progreso en tiempo real durante ejecución
- Logs automáticos de todas las operaciones

---

## 💡 Consejos y Mejores Prácticas

### ⚡ Para Máxima Eficiencia
1. **Usar "Flujo Completo"** para procesamientos regulares
2. **Verificar Dashboard** antes de iniciar procesos
3. **Revisar Logs** después de cada ejecución importante

### 🛡️ Para Evitar Problemas
1. **No cerrar** la ventana de terminal mientras se ejecuta
2. **No modificar** archivos mientras el sistema está procesando
3. **Verificar espacio en disco** antes de procesos grandes

### 📈 Para Presentaciones/Demos
1. **Dashboard** muestra métricas impresionantes
2. **Flujo Principal** demuestra automatización completa
3. **Configuración** muestra robustez del sistema

---

## 🆘 Resolución de Problemas Comunes

### ❌ "Carpeta Scripts no encontrada"
**Solución**: Ejecutar desde el directorio correcto
```bash
cd "C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\3.correspondencia"
```

### ❌ "Archivo IRCA no encontrado"  
**Solución**: Verificar que `Datos/IRCA(%).xlsx` existe

### ❌ "Botones bloqueados"
**Solución**: Ejecutar pasos en orden secuencial (1→2→3)

### ❌ "Sin permisos de escritura"
**Solución**: Ejecutar `run.bat` como administrador

### ❌ "Error de dependencias"
**Solución**: Ejecutar `install.bat` nuevamente

---

## 🎉 ¡Listo para Producción!

Una vez instalado y configurado, el sistema está listo para:
- ✅ **Automatización completa** del flujo IRCA
- ✅ **Monitoreo profesional** con dashboard
- ✅ **Validaciones robustas** para evitar errores  
- ✅ **Interfaz moderna** para presentar al gerente
- ✅ **Mantenimiento fácil** sin tocar scripts originales

**¡El sistema mantiene intacta toda la lógica de negocio existente mientras proporciona una experiencia de usuario profesional!**
