#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo wrapper para generador_base_script.py
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any
import streamlit as st

from ..config.settings import settings

class BaseGeneratorModel:
    """
    Wrapper para el script generador_base_script.py
    Maneja la ejecución del paso 1 del flujo obligatorio
    """
    
    def __init__(self):
        self.script_path = settings.SCRIPTS_DIR / "generador_base_script.py"
        # Verificar si el paso ya está completado al inicializar
        if settings.get_paso_status('paso1'):
            self.status = "completed"
        else:
            self.status = "not_executed"
        self.last_execution = None
        self.error_message = ""
        self.output_log = ""
    
    def is_ready_to_execute(self) -> bool:
        """Verifica si el script está listo para ejecutarse"""
        if not self.script_path.exists():
            self.error_message = f"Script no encontrado: {self.script_path}"
            return False
        
        errores = settings.validar_rutas()
        if errores:
            self.error_message = f"Errores de configuración: {'; '.join(errores)}"
            return False
        
        return True
    
    def execute(self) -> Tuple[bool, str]:
        """
        Ejecuta el script generador_base_script.py
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.is_ready_to_execute():
            return False, self.error_message
        
        try:
            # Resetear estado previo
            self.status = "executing"
            self.output_log = ""
            self.error_message = ""
            
            # Contar carpetas antes de la ejecución
            carpetas_antes = len(settings.get_carpetas_datos())
            
            # Configurar entorno con UTF-8 para manejar emojis
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Ejecutar el script como subprocess para capturar salida
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                cwd=str(self.script_path.parent),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
                env=env,
                encoding='utf-8',
                errors='replace'  # Reemplazar caracteres problemáticos
            )
            
            self.output_log = result.stdout
            
            # Verificar si el proceso fue exitoso
            carpetas_despues = len(settings.get_carpetas_datos())
            proceso_exitoso = (result.returncode == 0 and carpetas_despues > carpetas_antes)
            
            # Parsear el output para obtener número de ciudades procesadas
            ciudades_procesadas = 0
            if "Ciudades procesadas:" in self.output_log:
                try:
                    linea = [l for l in self.output_log.split('\n') if "Ciudades procesadas:" in l][0]
                    ciudades_procesadas = int(linea.split(':')[1].strip())
                except:
                    pass
            
            # También verificar por el mensaje final
            if "Proceso terminado" in self.output_log and "Ciudades procesadas:" not in self.output_log:
                # Buscar patrón "Proceso terminado. Ciudades procesadas: X"
                try:
                    lineas = self.output_log.split('\n')
                    for linea in lineas:
                        if "Proceso terminado" in linea and "procesadas:" in linea:
                            ciudades_procesadas = int(linea.split(':')[1].strip())
                            break
                except:
                    pass
            
            if proceso_exitoso or ciudades_procesadas > 0:
                self.status = "completed"
                settings.marcar_paso_completado('paso1', True)
                mensaje = f"✅ Generador base ejecutado exitosamente"
                if ciudades_procesadas > 0:
                    mensaje += f" - {ciudades_procesadas} ciudades procesadas"
                if carpetas_despues > carpetas_antes:
                    mensaje += f" - {carpetas_despues - carpetas_antes} carpetas creadas"
                return True, mensaje
            else:
                self.status = "error"
                self.error_message = result.stderr or "No se crearon carpetas de ciudades"
                settings.marcar_paso_completado('paso1', False)
                return False, f"❌ Error en ejecución: {self.error_message}"
                
        except subprocess.TimeoutExpired:
            self.status = "error"
            self.error_message = "Timeout: El script tardó más de 5 minutos"
            settings.marcar_paso_completado('paso1', False)
            return False, self.error_message
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            settings.marcar_paso_completado('paso1', False)
            return False, f"❌ Error inesperado: {self.error_message}"
    
    def is_ready_for_next_step(self) -> bool:
        """Verifica si este paso está completado y listo para el siguiente"""
        # Verificar si hay carpetas de ciudades ya creadas
        carpetas_existentes = len(settings.get_carpetas_datos())
        
        # Si hay carpetas y archivos de estado válidos, considerar completado
        if carpetas_existentes > 0:
            # Verificar que las carpetas tienen archivos Excel válidos
            for ciudad in settings.get_carpetas_datos():
                excel_file = settings.DATOS_DIR / ciudad / f"base_{ciudad}.xlsx"
                if excel_file.exists():
                    # Si encontramos al menos un archivo Excel válido, marcar como completado
                    settings.marcar_paso_completado('paso1', True)
                    self.status = "completed"
                    break
        
        return (self.status == "completed" and 
                settings.get_paso_status('paso1'))
    
    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene información del estado actual"""
        # Verificar automáticamente si debería estar completado
        self.is_ready_for_next_step()
        
        return {
            'status': self.status,
            'completed': settings.get_paso_status('paso1'),
            'ready_for_next': self.is_ready_for_next_step(),
            'error_message': self.error_message,
            'output_log': self.output_log,
            'script_exists': self.script_path.exists()
        }
    
    def get_validation_info(self) -> Dict[str, Any]:
        """Obtiene información de validación para mostrar en UI"""
        ciudades_creadas = settings.get_carpetas_datos()
        
        return {
            'carpetas_datos_creadas': len(ciudades_creadas),
            'ciudades_encontradas': ciudades_creadas,
            'origen_exists': settings.ORIGEN_DIR.exists(),
            'plantillas_exists': settings.PLANTILLAS_DIR.exists()
        }
