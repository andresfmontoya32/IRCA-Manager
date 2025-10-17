#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo wrapper para verificador_fotos.py
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, List

from ..config.settings import settings

class PhotoValidatorModel:
    """
    Wrapper para el script verificador_fotos.py
    Función opcional independiente del flujo principal
    """
    
    def __init__(self):
        self.script_path = settings.SCRIPTS_DIR / "verificador_fotos.py"
        self.status = "not_executed"
        self.last_execution = None
        self.error_message = ""
        self.output_log = ""
        self.fotos_encontradas = 0
        self.fotos_no_encontradas = 0
        self.ciudades_problemas = []
    
    def can_execute(self) -> Tuple[bool, str]:
        """Verifica si puede ejecutarse (función independiente)"""
        if not self.script_path.exists():
            return False, f"❌ Script no encontrado: {self.script_path}"
        
        return True, "✅ Listo para verificar fotos"
    
    def execute(self, ciudad_especifica: str = None) -> Tuple[bool, str]:
        """
        Ejecuta el script verificador_fotos.py
        
        Args:
            ciudad_especifica: Si se especifica, verifica solo esa ciudad
            
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
            self.fotos_encontradas = 0
            self.fotos_no_encontradas = 0
            self.ciudades_problemas = []
            
            # Preparar comando
            cmd = [sys.executable, str(self.script_path)]
            if ciudad_especifica:
                cmd.append(ciudad_especifica)
            
            # Configurar entorno con UTF-8 para manejar emojis
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Ejecutar el script
            result = subprocess.run(
                cmd,
                cwd=str(self.script_path.parent),
                capture_output=True,
                text=True,
                timeout=60,  # 1 minuto timeout
                env=env,
                encoding='utf-8',
                errors='replace'  # Reemplazar caracteres problemáticos
            )
            
            self.output_log = result.stdout
            
            # Analizar output para extraer métricas
            self._parse_execution_metrics()
            
            if result.returncode == 0:
                self.status = "completed"
                todas_encontradas = self.fotos_no_encontradas == 0
                if todas_encontradas:
                    return True, f"✅ Verificación completada: {self.fotos_encontradas} fotos encontradas"
                else:
                    return True, f"⚠️ Verificación completada: {self.fotos_encontradas} encontradas, {self.fotos_no_encontradas} faltantes"
            else:
                self.status = "error"
                self.error_message = result.stderr or "Error desconocido"
                return False, f"❌ Error en verificación: {self.error_message}"
                
        except subprocess.TimeoutExpired:
            self.status = "error"
            self.error_message = "Timeout: La verificación tardó más de 1 minuto"
            return False, self.error_message
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            return False, f"❌ Error inesperado: {self.error_message}"
    
    def _parse_execution_metrics(self):
        """Extrae métricas del output del script"""
        try:
            lines = self.output_log.split('\n')
            for line in lines:
                if 'Fotos encontradas:' in line:
                    self.fotos_encontradas = int(line.split(':')[1].strip())
                elif 'Fotos NO encontradas:' in line:
                    self.fotos_no_encontradas = int(line.split(':')[1].strip())
                elif line.strip().startswith('• ') and 'Ciudades con problemas' in self.output_log:
                    ciudad = line.strip()[2:]  # Remover '• '
                    if ciudad not in self.ciudades_problemas:
                        self.ciudades_problemas.append(ciudad)
        except:
            pass  # Si no puede parsear, mantener valores por defecto
    
    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene información del estado actual"""
        return {
            'status': self.status,
            'error_message': self.error_message,
            'output_log': self.output_log,
            'fotos_encontradas': self.fotos_encontradas,
            'fotos_no_encontradas': self.fotos_no_encontradas,
            'ciudades_problemas': self.ciudades_problemas,
            'script_exists': self.script_path.exists(),
            'success_rate': (self.fotos_encontradas / max(1, self.fotos_encontradas + self.fotos_no_encontradas)) * 100
        }
    
    def get_available_cities(self) -> List[str]:
        """Obtiene lista de ciudades disponibles para verificar"""
        return settings.AEROPUERTOS
    
    def quick_check_city(self, ciudad: str) -> Dict[str, Any]:
        """Hace una verificación rápida de una ciudad específica sin ejecutar el script"""
        # Este es un diccionario simplificado basado en el script original
        fotos_por_ciudad = {
            "Aguachica": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Armenia": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Barranquilla": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Buenaventura": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Guapi": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Ipiales": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Pasto": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Popayan": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Tolu": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Tumaco": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "San Andres": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"],
            "Providencia": ["FOTO1", "FOTO2", "FOTO3", "FOTO4"]
        }
        
        if ciudad not in fotos_por_ciudad:
            return {'error': f'Ciudad {ciudad} no encontrada en configuración'}
        
        return {
            'ciudad': ciudad,
            'fotos_configuradas': len(fotos_por_ciudad[ciudad]),
            'fotos_esperadas': fotos_por_ciudad[ciudad]
        }
