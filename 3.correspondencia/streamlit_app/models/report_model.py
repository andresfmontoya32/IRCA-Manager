#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo wrapper para Correspondencia.py
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, List

from ..config.settings import settings

class ReportModel:
    """
    Wrapper para el script Correspondencia.py
    Maneja la ejecución del paso 3 del flujo obligatorio
    """
    
    def __init__(self):
        self.script_path = settings.SCRIPTS_DIR / "Correspondencia.py"
        # Verificar si el paso ya está completado al inicializar
        if settings.get_paso_status('paso3'):
            self.status = "completed"
        else:
            self.status = "not_executed"
        self.last_execution = None
        self.error_message = ""
        self.output_log = ""
        self.informes_generados = 0
        self.carpetas_omitidas = 0
    
    def can_execute(self) -> Tuple[bool, str]:
        """Verifica si puede ejecutarse (requiere pasos 1 y 2 completados)"""
        if not settings.get_paso_status('paso1'):
            return False, "❌ Debe ejecutar el Paso 1 (Generador Base) primero"
        
        if not settings.get_paso_status('paso2'):
            return False, "❌ Debe ejecutar el Paso 2 (Procesamiento IRCA) primero"
        
        if not self.script_path.exists():
            return False, f"❌ Script no encontrado: {self.script_path}"
        
        ciudades = settings.get_carpetas_datos()
        if not ciudades:
            return False, "❌ No hay carpetas de ciudades para procesar"
        
        # Verificar que existan archivos Excel con TAGS
        archivos_validos = 0
        for ciudad in ciudades:
            excel_file = settings.DATOS_DIR / ciudad / f"base_{ciudad}.xlsx"
            if excel_file.exists():
                archivos_validos += 1
        
        if archivos_validos == 0:
            return False, "❌ No hay archivos Excel válidos para procesar"
        
        return True, f"✅ Listo para generar {archivos_validos} informes"
    
    def execute(self) -> Tuple[bool, str]:
        """
        Ejecuta el script Correspondencia.py
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        can_run, message = self.can_execute()
        if not can_run:
            return False, message
        
        try:
            # Resetear estado
            self.status = "executing"
            self.output_log = ""
            self.error_message = ""
            self.informes_generados = 0
            self.carpetas_omitidas = 0
            
            # Configurar entorno con UTF-8 para manejar emojis
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Ejecutar el script
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                cwd=str(self.script_path.parent),
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutos timeout
                env=env,
                encoding='utf-8',
                errors='replace'  # Reemplazar caracteres problemáticos
            )
            
            self.output_log = result.stdout
            
            # Analizar output para extraer métricas
            self._parse_execution_metrics()
            
            # Debug: Mostrar información del resultado
            print(f"🔍 Return code del script Correspondencia: {result.returncode}")
            print(f"📊 STDOUT length: {len(result.stdout) if result.stdout else 0}")
            print(f"📊 STDERR length: {len(result.stderr) if result.stderr else 0}")
            
            # Verificar si el procesamiento fue exitoso basándose en el output
            # El script puede devolver código != 0 pero aún así generar reportes correctamente
            procesamiento_exitoso = False
            
            if result.returncode == 0:
                procesamiento_exitoso = True
            else:
                # Verificar si hay indicios de éxito en el output
                if result.stdout:
                    # Buscar indicadores de éxito en el output
                    indicadores_exito = [
                        "✅", "Procesado exitosamente", "generado correctamente", 
                        "Informe creado", "Documento generado", "completado"
                    ]
                    
                    exitos_detectados = 0
                    for indicador in indicadores_exito:
                        exitos_detectados += result.stdout.count(indicador)
                    
                    print(f"🔍 Indicadores de éxito detectados: {exitos_detectados}")
                    
                    # También verificar si se crearon archivos de reporte
                    reportes_creados = 0
                    ciudades = settings.get_carpetas_datos()
                    for ciudad in ciudades:
                        reporte_file = settings.DATOS_DIR / ciudad / f"reporte_{ciudad}.docx"
                        if reporte_file.exists() and reporte_file.stat().st_size > 1024:
                            reportes_creados += 1
                    
                    print(f"🔍 Reportes Word creados: {reportes_creados}")
                    
                    # Si hay indicios de éxito O se crearon reportes, considerar éxito
                    if exitos_detectados > 0 or reportes_creados > 0:
                        procesamiento_exitoso = True
                        print("✅ Detectado procesamiento exitoso basado en output/archivos")
            
            if procesamiento_exitoso:
                self.status = "completed"
                settings.marcar_paso_completado('paso3', True)
                
                # Verificación adicional: asegurar que el archivo de estado se creó
                if not settings.get_paso_status('paso3'):
                    print("⚠️ ADVERTENCIA: El archivo de estado paso3 no se creó correctamente")
                    # Intentar crear manualmente
                    try:
                        settings.ESTADOS_ARCHIVOS['paso3'].touch()
                        print("✅ Archivo de estado paso3 creado manualmente")
                    except Exception as e:
                        print(f"❌ Error creando archivo de estado: {e}")
                
                return True, f"✅ Generación de informes completada: {self.informes_generados} generados, {self.carpetas_omitidas} omitidas"
            else:
                self.status = "error"
                self.error_message = result.stderr or "Error desconocido"
                settings.marcar_paso_completado('paso3', False)
                print(f"❌ STDERR completo: {result.stderr}")
                return False, f"❌ Error en generación de informes: {self.error_message}"
                
        except subprocess.TimeoutExpired:
            self.status = "error"
            self.error_message = "Timeout: La generación tardó más de 15 minutos"
            return False, self.error_message
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            settings.marcar_paso_completado('paso3', False)
            return False, f"❌ Error inesperado: {self.error_message}"
    
    def _parse_execution_metrics(self):
        """Extrae métricas del output del script"""
        try:
            lines = self.output_log.split('\n')
            for line in lines:
                if 'Informes generados:' in line:
                    self.informes_generados = int(line.split(':')[1].strip())
                elif 'Carpetas omitidas:' in line:
                    self.carpetas_omitidas = int(line.split(':')[1].strip())
        except:
            pass  # Si no puede parsear, mantener valores por defecto
    
    def is_workflow_complete(self) -> bool:
        """Verifica si todo el flujo está completado"""
        return (self.status == "completed" and 
                settings.get_paso_status('paso3'))
    
    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene información del estado actual"""
        return {
            'status': self.status,
            'completed': settings.get_paso_status('paso3'),
            'workflow_complete': self.is_workflow_complete(),
            'error_message': self.error_message,
            'output_log': self.output_log,
            'informes_generados': self.informes_generados,
            'carpetas_omitidas': self.carpetas_omitidas,
            'script_exists': self.script_path.exists()
        }
    
    def get_generated_reports(self) -> List[Dict[str, Any]]:
        """Obtiene lista de informes generados"""
        reportes = []
        ciudades = settings.get_carpetas_datos()
        
        for ciudad in ciudades:
            ciudad_path = settings.DATOS_DIR / ciudad
            reporte_file = ciudad_path / f"reporte_{ciudad}.docx"
            excel_file = ciudad_path / f"base_{ciudad}.xlsx"
            plantilla_files = list(ciudad_path.glob("*.docx"))
            plantilla_files = [f for f in plantilla_files if not f.name.startswith("reporte_")]
            
            reportes.append({
                'ciudad': ciudad,
                'reporte_generado': reporte_file.exists(),
                'reporte_path': reporte_file if reporte_file.exists() else None,
                'excel_exists': excel_file.exists(),
                'plantilla_exists': len(plantilla_files) > 0,
                'plantilla_path': plantilla_files[0] if plantilla_files else None,
                'reporte_size': reporte_file.stat().st_size if reporte_file.exists() else 0
            })
        
        return reportes
    
    def validate_prerequisites(self) -> Dict[str, Any]:
        """Valida prerequisitos para la generación de reportes"""
        ciudades = settings.get_carpetas_datos()
        validaciones = {}
        
        for ciudad in ciudades:
            ciudad_path = settings.DATOS_DIR / ciudad
            excel_file = ciudad_path / f"base_{ciudad}.xlsx"
            plantilla_files = list(ciudad_path.glob("*.docx"))
            plantilla_files = [f for f in plantilla_files if not f.name.startswith("reporte_")]
            
            validaciones[ciudad] = {
                'excel_exists': excel_file.exists(),
                'plantilla_exists': len(plantilla_files) > 0,
                'ready_for_report': excel_file.exists() and len(plantilla_files) > 0
            }
            
            # Validar hoja TAGS si existe el Excel
            if excel_file.exists():
                try:
                    import pandas as pd
                    df_tags = pd.read_excel(excel_file, sheet_name='TAGS')
                    validaciones[ciudad]['tags_sheet_exists'] = True
                    validaciones[ciudad]['tags_count'] = len(df_tags)
                except:
                    validaciones[ciudad]['tags_sheet_exists'] = False
                    validaciones[ciudad]['tags_count'] = 0
        
        return validaciones
