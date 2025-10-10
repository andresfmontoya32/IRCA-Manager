#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de rutas y parámetros del sistema IRCA
"""

import os
from pathlib import Path

class Settings:
    """Configuración centralizada del sistema"""
    
    def __init__(self):
        # Ruta base del proyecto
        self.BASE_DIR = Path(__file__).parent.parent.parent
        
        # Rutas de scripts existentes
        self.SCRIPTS_DIR = self.BASE_DIR / "Scripts"
        self.DATOS_DIR = self.BASE_DIR / "Datos"
        self.PLANTILLAS_DIR = self.BASE_DIR / "Plantillas"
        
        # Archivos específicos
        self.IRCA_FILE = self.DATOS_DIR / "IRCA(%).csv"
        
        # Rutas de origen para el generador base
        self.ORIGEN_DIR = Path(r"C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\2.Limpieza\Resultados_por_Aeropuerto")
        
        # Estados de los pasos del flujo
        self.ESTADOS_ARCHIVOS = {
            'paso1': self.DATOS_DIR / '.paso1_completed',
            'paso2': self.DATOS_DIR / '.paso2_completed', 
            'paso3': self.DATOS_DIR / '.paso3_completed'
        }
        
        # Configuración para mejoras nuevas
        self.SELECTED_MONTH = None
        self.SELECTED_YEAR = None
        self.OUTPUT_DIRECTORY = None
        
        # Archivo de configuración de sesión
        self.SESSION_CONFIG = self.DATOS_DIR / '.session_config.txt'
        
        # Configuración de la UI
        self.APP_TITLE = "🛩️ Sistema IRCA - Aerocivil"
        self.APP_ICON = "✈️"
        
        # Lista de aeropuertos/ciudades conocidas
        self.AEROPUERTOS = [
            "Aguachica", "Armenia", "Barranquilla", "Buenaventura", 
            "Guapi", "Ipiales", "Pasto", "Popayan", "Tolu", "Tumaco",
            "San Andres", "Providencia"
        ]
    
    def validar_rutas(self):
        """Valida que las rutas críticas existan"""
        errores = []
        
        if not self.SCRIPTS_DIR.exists():
            errores.append(f"Carpeta Scripts no encontrada: {self.SCRIPTS_DIR}")
        
        if not self.PLANTILLAS_DIR.exists():
            errores.append(f"Carpeta Plantillas no encontrada: {self.PLANTILLAS_DIR}")
            
        if not self.IRCA_FILE.exists():
            errores.append(f"Archivo IRCA no encontrado: {self.IRCA_FILE}")
            
        if not self.ORIGEN_DIR.exists():
            errores.append(f"Carpeta origen no encontrada: {self.ORIGEN_DIR}")
        
        return errores
    
    def get_paso_status(self, paso: str) -> bool:
        """Verifica si un paso del flujo está completado"""
        archivo_estado = self.ESTADOS_ARCHIVOS.get(paso)
        return archivo_estado.exists() if archivo_estado else False
    
    def marcar_paso_completado(self, paso: str, exito: bool = True):
        """Marca un paso como completado o fallido"""
        archivo_estado = self.ESTADOS_ARCHIVOS.get(paso)
        if archivo_estado:
            if exito:
                archivo_estado.touch()
            else:
                if archivo_estado.exists():
                    archivo_estado.unlink()
    
    def reset_estados(self):
        """Resetea todos los estados de pasos"""
        for archivo in self.ESTADOS_ARCHIVOS.values():
            if archivo.exists():
                archivo.unlink()
    
    def get_carpetas_datos(self):
        """Obtiene lista de carpetas de ciudades en Datos"""
        if not self.DATOS_DIR.exists():
            return []
        
        return [item.name for item in self.DATOS_DIR.iterdir() 
                if item.is_dir() and not item.name.startswith('.')]
    
    def get_available_months(self):
        """Obtiene lista de meses disponibles en el archivo CSV"""
        import pandas as pd
        
        try:
            if not self.IRCA_FILE.exists():
                return []
            
            # Leer CSV con separador punto y coma
            df = pd.read_csv(self.IRCA_FILE, sep=';')
            
            # Extraer años de la columna Fecha
            df['Fecha_parsed'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            df['Año'] = df['Fecha_parsed'].dt.year
            
            # Combinar Mes y Año únicos
            meses_años = df[['Mes', 'Año']].drop_duplicates().dropna()
            
            # Convertir a lista de diccionarios ordenada
            months_list = []
            for _, row in meses_años.iterrows():
                months_list.append({
                    'mes': row['Mes'],
                    'año': int(row['Año']),
                    'display': f"{row['Mes']} {int(row['Año'])}"
                })
            
            # Ordenar por año y mes
            months_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            def sort_key(item):
                mes_idx = months_order.index(item['mes']) if item['mes'] in months_order else 99
                return (item['año'], mes_idx)
            
            months_list.sort(key=sort_key, reverse=True)
            
            return months_list
            
        except Exception as e:
            print(f"Error obteniendo meses disponibles: {e}")
            return []
    
    def save_session_config(self, mes=None, año=None, output_dir=None):
        """Guarda configuración de sesión"""
        try:
            config_data = []
            if mes and año:
                config_data.append(f"SELECTED_MONTH={mes}")
                config_data.append(f"SELECTED_YEAR={año}")
                self.SELECTED_MONTH = mes
                self.SELECTED_YEAR = año
            
            if output_dir:
                config_data.append(f"OUTPUT_DIRECTORY={output_dir}")
                self.OUTPUT_DIRECTORY = output_dir
            
            with open(self.SESSION_CONFIG, 'w', encoding='utf-8') as f:
                f.write('\n'.join(config_data))
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def load_session_config(self):
        """Carga configuración de sesión"""
        try:
            if not self.SESSION_CONFIG.exists():
                return
            
            with open(self.SESSION_CONFIG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'SELECTED_MONTH':
                        self.SELECTED_MONTH = value
                    elif key == 'SELECTED_YEAR':
                        self.SELECTED_YEAR = int(value) if value.isdigit() else None
                    elif key == 'OUTPUT_DIRECTORY':
                        self.OUTPUT_DIRECTORY = value
        except Exception as e:
            print(f"Error cargando configuración: {e}")
    
    def reset_complete_workflow(self):
        """Reinicia completamente el flujo y configuración"""
        # Eliminar estados de pasos
        self.reset_estados()
        
        # Limpiar configuración de sesión
        self.SELECTED_MONTH = None
        self.SELECTED_YEAR = None
        self.OUTPUT_DIRECTORY = None
        
        if self.SESSION_CONFIG.exists():
            self.SESSION_CONFIG.unlink()
        
        # Limpiar carpetas de ciudades generadas
        for ciudad in self.get_carpetas_datos():
            ciudad_path = self.DATOS_DIR / ciudad
            if ciudad_path.exists() and ciudad_path.is_dir():
                import shutil
                try:
                    shutil.rmtree(ciudad_path)
                except Exception as e:
                    print(f"Error eliminando carpeta {ciudad}: {e}")
    
    def get_session_info(self):
        """Obtiene información actual de la sesión"""
        return {
            'selected_month': self.SELECTED_MONTH,
            'selected_year': self.SELECTED_YEAR,
            'output_directory': self.OUTPUT_DIRECTORY,
            'has_month_selected': bool(self.SELECTED_MONTH and self.SELECTED_YEAR),
            'has_output_dir': bool(self.OUTPUT_DIRECTORY)
        }

# Instancia global de configuración
settings = Settings()
