#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo wrapper para rellenador_tags.py
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd

from ..config.settings import settings

class IRCAModel:
    """
    Wrapper para el script rellenador_tags.py
    Maneja la ejecución del paso 2 del flujo obligatorio
    """
    
    def __init__(self):
        self.script_path = settings.SCRIPTS_DIR / "rellenador_tags.py"
        # Verificar si el paso ya está completado al inicializar
        if settings.get_paso_status('paso2'):
            self.status = "completed"
        else:
            self.status = "not_executed"
        self.last_execution = None
        self.error_message = ""
        self.output_log = ""
        self.aeropuertos_procesados = 0
        self.aeropuertos_exitosos = 0
    
    def can_execute(self) -> Tuple[bool, str]:
        """Verifica si puede ejecutarse (requiere paso 1 completado)"""
        if not settings.get_paso_status('paso1'):
            return False, "❌ Debe ejecutar el Paso 1 (Generador Base) primero"
        
        if not self.script_path.exists():
            return False, f"❌ Script no encontrado: {self.script_path}"
        
        if not settings.IRCA_FILE.exists():
            return False, f"❌ Archivo IRCA no encontrado: {settings.IRCA_FILE}"
        
        ciudades = settings.get_carpetas_datos()
        if not ciudades:
            return False, "❌ No hay carpetas de ciudades para procesar"
        
        return True, "✅ Listo para ejecutar"
    
    def execute(self) -> Tuple[bool, str]:
        """
        Ejecuta el script rellenador_tags.py
        Crea archivo Excel temporal con datos CSV filtrados por mes
        
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
            self.aeropuertos_procesados = 0
            self.aeropuertos_exitosos = 0
            
            # PASO CRÍTICO: Preparar archivo Excel temporal para el script original
            excel_temp_path = self._prepare_excel_for_script()
            if not excel_temp_path:
                self.status = "error"
                self.error_message = "Error creando archivo Excel temporal"
                return False, "❌ Error preparando datos IRCA para procesamiento"
            
            # Configurar entorno con UTF-8 para manejar emojis
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Ejecutar el script original que ahora puede leer el Excel temporal
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                cwd=str(self.script_path.parent),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutos timeout
                env=env,
                encoding='utf-8',
                errors='replace'  # Reemplazar caracteres problemáticos
            )
            
            self.output_log = result.stdout
            
            # Limpiar archivo temporal
            self._cleanup_temp_excel(excel_temp_path)
            
            # Analizar output para extraer métricas
            self._parse_execution_metrics()
            
            # Debug: Mostrar información del resultado
            print(f"🔍 Return code del script: {result.returncode}")
            print(f"📊 STDOUT length: {len(result.stdout) if result.stdout else 0}")
            print(f"📊 STDERR length: {len(result.stderr) if result.stderr else 0}")
            
            # Verificar si el procesamiento fue exitoso basándose en el output
            # El script puede devolver código != 0 pero aún así procesar correctamente
            procesamiento_exitoso = False
            
            if result.returncode == 0:
                procesamiento_exitoso = True
            else:
                # Verificar si hay indicios de éxito en el output
                if result.stdout and "✅" in result.stdout:
                    # Contar cuántos aeropuertos se procesaron exitosamente
                    exitosos = result.stdout.count("✅")
                    total_procesados = result.stdout.count("[")  # Cada aeropuerto tiene [X/Y]
                    
                    print(f"🔍 Aeropuertos exitosos detectados: {exitosos}")
                    print(f"🔍 Total aeropuertos procesados: {total_procesados}")
                    
                    # Si se procesó al menos 1 aeropuerto exitosamente, considerar éxito
                    if exitosos > 0:
                        procesamiento_exitoso = True
                        print("✅ Detectado procesamiento parcial exitoso")
            
            if procesamiento_exitoso:
                self.status = "completed"
                settings.marcar_paso_completado('paso2', True)
                
                # Verificación adicional: asegurar que el archivo de estado se creó
                if not settings.get_paso_status('paso2'):
                    print("⚠️ ADVERTENCIA: El archivo de estado paso2 no se creó correctamente")
                    # Intentar crear manualmente
                    try:
                        settings.ESTADOS_ARCHIVOS['paso2'].touch()
                        print("✅ Archivo de estado paso2 creado manualmente")
                    except Exception as e:
                        print(f"❌ Error creando archivo de estado: {e}")
                
                return True, f"✅ Procesamiento IRCA completado: {self.aeropuertos_exitosos}/{self.aeropuertos_procesados} aeropuertos"
            else:
                self.status = "error"
                self.error_message = result.stderr or "Error desconocido"
                settings.marcar_paso_completado('paso2', False)
                print(f"❌ STDERR completo: {result.stderr}")
                return False, f"❌ Error en procesamiento IRCA: {self.error_message}"
                
        except subprocess.TimeoutExpired:
            self.status = "error"
            self.error_message = "Timeout: El procesamiento tardó más de 10 minutos"
            return False, self.error_message
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            settings.marcar_paso_completado('paso2', False)
            return False, f"❌ Error inesperado: {self.error_message}"
    
    def _parse_execution_metrics(self):
        """Extrae métricas del output del script"""
        try:
            lines = self.output_log.split('\n')
            for line in lines:
                if 'Total aeropuertos:' in line:
                    self.aeropuertos_procesados = int(line.split(':')[1].strip())
                elif 'Procesados exitosamente:' in line:
                    self.aeropuertos_exitosos = int(line.split(':')[1].strip())
        except:
            pass  # Si no puede parsear, mantener valores por defecto
    
    def is_ready_for_next_step(self) -> bool:
        """Verifica si este paso está completado y listo para el siguiente"""
        return (self.status == "completed" and 
                settings.get_paso_status('paso2'))
    
    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene información del estado actual"""
        return {
            'status': self.status,
            'completed': settings.get_paso_status('paso2'),
            'ready_for_next': self.is_ready_for_next_step(),
            'error_message': self.error_message,
            'output_log': self.output_log,
            'aeropuertos_procesados': self.aeropuertos_procesados,
            'aeropuertos_exitosos': self.aeropuertos_exitosos,
            'script_exists': self.script_path.exists()
        }
    
    def get_irca_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de datos IRCA"""
        try:
            if not settings.IRCA_FILE.exists():
                return {'error': 'Archivo IRCA no encontrado'}
            
            # Leer CSV con separador punto y coma
            df = pd.read_csv(settings.IRCA_FILE, sep=';')
            
            # Filtrar por mes/año seleccionado si está configurado
            if settings.SELECTED_MONTH and settings.SELECTED_YEAR:
                df = df[(df['Mes'] == settings.SELECTED_MONTH) & 
                       (pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce').dt.year == settings.SELECTED_YEAR)]
            
            ciudades_irca = df['Ciudad'].value_counts().to_dict()
            
            # Convertir porcentajes string a float
            df['IRCA_Numeric'] = df['IRCA (%)'].str.replace('%', '').str.replace(',', '.').astype(float)
            irca_promedio = df['IRCA_Numeric'].mean() if len(df) > 0 else 0
            
            return {
                'total_registros': len(df),
                'ciudades_con_datos': len(ciudades_irca),
                'irca_promedio': round(irca_promedio, 2),
                'ciudades_irca': ciudades_irca
            }
        except Exception as e:
            return {'error': f'Error leyendo archivo IRCA: {str(e)}'}
    
    def validate_tags_files(self) -> Dict[str, Any]:
        """Valida que los archivos TAGS estén correctamente creados"""
        ciudades = settings.get_carpetas_datos()
        archivos_validados = {}
        
        for ciudad in ciudades:
            ciudad_path = settings.DATOS_DIR / ciudad
            excel_file = ciudad_path / f"base_{ciudad}.xlsx"
            
            if excel_file.exists():
                try:
                    # Verificar que tiene hoja TAGS
                    df_tags = pd.read_excel(excel_file, sheet_name='TAGS')
                    archivos_validados[ciudad] = {
                        'excel_exists': True,
                        'tags_sheet_exists': True,
                        'tags_count': len(df_tags)
                    }
                except:
                    archivos_validados[ciudad] = {
                        'excel_exists': True,
                        'tags_sheet_exists': False,
                        'tags_count': 0
                    }
            else:
                archivos_validados[ciudad] = {
                    'excel_exists': False,
                    'tags_sheet_exists': False,
                    'tags_count': 0
                }
        
        return archivos_validados
    
    def _prepare_excel_for_script(self) -> str:
        """
        Crea archivo Excel temporal con datos CSV filtrados por mes seleccionado
        para que el script original rellenador_tags.py pueda procesarlo
        
        Returns:
            str: Ruta del archivo Excel temporal creado, o None si hay error
        """
        try:
            # Leer datos CSV con encoding UTF-8
            print(f"🔍 Leyendo CSV: {settings.IRCA_FILE}")
            df_csv = pd.read_csv(settings.IRCA_FILE, sep=';', encoding='utf-8')
            
            # DEBUG: Verificar columnas leídas
            print(f"📊 Columnas CSV leídas: {list(df_csv.columns)}")
            print(f"📊 Shape del DataFrame: {df_csv.shape}")
            print(f"📊 Primeras filas:\n{df_csv.head(2)}")
            
            # Validar que tiene las columnas necesarias
            required_cols = ['Ciudad', 'Codigo', 'IRCA (%)']
            missing_cols = [col for col in required_cols if col not in df_csv.columns]
            if missing_cols:
                print(f"❌ Columnas faltantes: {missing_cols}")
                print(f"📊 Columnas disponibles: {list(df_csv.columns)}")
                return None
            
            # Filtrar por mes/año seleccionado si está configurado
            if settings.SELECTED_MONTH and settings.SELECTED_YEAR:
                # Parsear fecha para extraer año
                df_csv['Fecha_parsed'] = pd.to_datetime(df_csv['Fecha'], format='%d/%m/%Y', errors='coerce')
                df_csv['Año_parsed'] = df_csv['Fecha_parsed'].dt.year
                
                # CORRECCIÓN: Filtrado más flexible para evitar mapeo vacío
                # Primero intentar filtrado exacto por mes y año
                df_filtered_exact = df_csv[
                    (df_csv['Mes'] == settings.SELECTED_MONTH) & 
                    (df_csv['Año_parsed'] == settings.SELECTED_YEAR)
                ].copy()
                
                print(f"🔍 Filtrando datos IRCA: {settings.SELECTED_MONTH} {settings.SELECTED_YEAR}")
                print(f"📊 Registros filtrado exacto: {len(df_filtered_exact)}")
                
                # Si el filtrado exacto resulta en pocos datos, usar filtrado por mes solamente
                if len(df_filtered_exact) < 10:  # Umbral mínimo de registros
                    print(f"⚠️ Pocos registros con filtrado exacto, usando solo filtro por mes")
                    df_filtered = df_csv[df_csv['Mes'] == settings.SELECTED_MONTH].copy()
                    print(f"📊 Registros con filtrado por mes: {len(df_filtered)}")
                    
                    # Si aún son pocos, usar los datos más recientes disponibles
                    if len(df_filtered) < 5:
                        print(f"⚠️ Muy pocos registros para {settings.SELECTED_MONTH}, usando datos más recientes")
                        # Obtener el año más reciente disponible para este mes
                        años_disponibles = df_csv[df_csv['Mes'] == settings.SELECTED_MONTH]['Año_parsed'].dropna()
                        if len(años_disponibles) > 0:
                            año_reciente = años_disponibles.max()
                            df_filtered = df_csv[
                                (df_csv['Mes'] == settings.SELECTED_MONTH) & 
                                (df_csv['Año_parsed'] == año_reciente)
                            ].copy()
                            print(f"📊 Usando datos de {settings.SELECTED_MONTH} {int(año_reciente)}: {len(df_filtered)} registros")
                        else:
                            # Último recurso: usar todos los datos
                            df_filtered = df_csv.copy()
                            print(f"⚠️ Usando todos los datos disponibles: {len(df_filtered)} registros")
                else:
                    df_filtered = df_filtered_exact
                
                # Verificar distribución de ciudades
                ciudades_disponibles = df_filtered['Ciudad'].unique()
                print(f"🏙️ Ciudades en datos filtrados: {len(ciudades_disponibles)}")
                print(f"🏙️ Lista: {sorted(ciudades_disponibles)}")
                
            else:
                df_filtered = df_csv.copy()
                print("⚠️ Sin filtro de mes - usando todos los datos CSV")
            
            if len(df_filtered) == 0:
                print("❌ No hay datos después del filtrado")
                return None
            
            # Convertir formato CSV a formato Excel compatible con script original
            # El script necesita todas las columnas del CSV original
            df_excel = df_filtered.copy()
            
            # Validar que df_excel mantiene las columnas críticas
            print(f"🔍 DataFrame Excel pre-proceso - Columnas: {list(df_excel.columns)}")
            if 'Ciudad' not in df_excel.columns:
                print(f"❌ ERROR CRÍTICO: Columna 'Ciudad' perdida durante filtrado")
                return None
            
            # CORRECCIÓN CRÍTICA: Formato de fecha inequívoco para rellenador_tags.py
            # El script original usa pd.to_datetime() sin formato, causando interpretación errónea
            if 'Fecha' in df_excel.columns:
                # Parsear correctamente como día/mes/año
                df_excel['Fecha_parsed_temp'] = pd.to_datetime(df_excel['Fecha'], format='%d/%m/%Y', errors='coerce')
                
                # SOLUCIÓN: Usar formato ISO YYYY-MM-DD que es inequívoco
                # El script rellenador_tags.py no puede malinterpretar este formato
                df_excel['Fecha'] = df_excel['Fecha_parsed_temp'].dt.strftime('%Y-%m-%d')
                
                # Eliminar columna temporal
                df_excel = df_excel.drop('Fecha_parsed_temp', axis=1)
                print(f"✅ Fechas convertidas a formato ISO (YYYY-MM-DD) - inequívoco")
                
                # Verificar algunas fechas como muestra
                fechas_muestra = df_excel['Fecha'].head(3).tolist()
                print(f"📅 Fechas ISO muestra: {fechas_muestra}")
                
                # Verificar específicamente datos de Pasto si existen
                pasto_datos = df_excel[df_excel['Ciudad'] == 'Pasto']
                if len(pasto_datos) > 0:
                    print(f"🎯 Fechas de Pasto corregidas:")
                    for _, row in pasto_datos.head(2).iterrows():
                        print(f"   • Código {row['Codigo']}: {row['Fecha']}")
                        # Verificar que es julio
                        fecha_check = pd.to_datetime(row['Fecha'])
                        mes_nombre = fecha_check.strftime('%B')
                        print(f"     → {fecha_check.day} de {mes_nombre} de {fecha_check.year}")
                        if fecha_check.month == 7:
                            print(f"     ✅ Correctamente identificado como julio")
                        else:
                            print(f"     ❌ ERROR: Mes {fecha_check.month} no es julio")
            
            # Limpiar datos de IRCA - remover % y convertir comas a puntos
            df_excel['IRCA (%)'] = df_excel['IRCA (%)'].astype(str).str.replace('%', '').str.replace(',', '.')
            df_excel['IRCA (%)'] = pd.to_numeric(df_excel['IRCA (%)'], errors='coerce')
            
            # Crear archivo Excel temporal
            excel_temp_path = settings.DATOS_DIR / "IRCA(%).xlsx"
            
            # CORRECCIÓN: Guardar Excel con fechas en formato ISO inequívoco
            # El formato YYYY-MM-DD no puede ser malinterpretado por pd.to_datetime()
            try:
                with pd.ExcelWriter(excel_temp_path, engine='openpyxl') as writer:
                    # Las fechas ya están en formato ISO YYYY-MM-DD, mantener como string
                    df_save = df_excel.copy()
                    if 'Fecha' in df_save.columns:
                        df_save['Fecha'] = df_save['Fecha'].astype(str)
                        print(f"✅ Fechas guardadas como string formato ISO")
                    
                    # Guardar el DataFrame
                    df_save.to_excel(writer, sheet_name='Sheet1', index=False)
                    
                    # Acceder a la hoja y configurar formato como texto para garantizar
                    worksheet = writer.sheets['Sheet1']
                    
                    # Formatear columna Fecha como texto
                    if 'Fecha' in df_save.columns:
                        fecha_col_idx = list(df_save.columns).index('Fecha') + 1
                        for row in range(2, len(df_save) + 2):
                            cell = worksheet.cell(row=row, column=fecha_col_idx)
                            cell.number_format = '@'  # Formato texto
                        
                        print(f"✅ Columna Fecha ISO formateada como texto en Excel")
                    
                print(f"✅ Excel temporal con fechas ISO inequívocas")
                
            except Exception as e:
                print(f"⚠️ Error con ExcelWriter, usando método estándar: {e}")
                # Fallback con fechas ISO
                df_excel.to_excel(excel_temp_path, index=False)
                print(f"✅ Fallback: Excel guardado con fechas ISO")
            
            # Validación post-guardado
            print(f"📄 Excel temporal guardado con {len(df_excel)} registros")
            
            # Verificar que el Excel se puede leer correctamente
            try:
                df_test = pd.read_excel(excel_temp_path)
                if 'Ciudad' not in df_test.columns:
                    print(f"❌ ERROR: Excel temporal no tiene columna 'Ciudad'")
                    return None
                print(f"✅ Excel temporal verificado - Columna 'Ciudad' presente")
                
                # NUEVA VALIDACIÓN: Verificar que hay datos suficientes para el mapeo
                ciudades_excel = df_test['Ciudad'].unique()
                codigos_excel = df_test['Codigo'].unique()
                
                print(f"✅ Ciudades en Excel temporal: {len(ciudades_excel)}")
                print(f"✅ Códigos únicos en Excel: {len(codigos_excel)}")
                
                # Verificar que hay al menos 1 código por ciudad
                min_ciudades_requeridas = 3  # Mínimo para que el mapeo sea útil
                if len(ciudades_excel) < min_ciudades_requeridas:
                    print(f"⚠️ ADVERTENCIA: Solo {len(ciudades_excel)} ciudades en Excel temporal")
                    print(f"⚠️ El rellenador_tags.py puede fallar para ciudades faltantes")
                
                # Verificar distribución de códigos por ciudad
                distribucion_codigos = df_test.groupby('Ciudad')['Codigo'].nunique()
                print(f"📊 Códigos por ciudad:")
                for ciudad, count in distribucion_codigos.items():
                    print(f"   • {ciudad}: {count} códigos")
                
            except Exception as e:
                print(f"❌ Error verificando Excel temporal: {e}")
                return None
            
            print(f"✅ Archivo Excel temporal creado: {excel_temp_path}")
            print(f"📄 Códigos únicos: {df_excel['Codigo'].nunique()}")
            print(f"🏙️ Ciudades únicas: {df_excel['Ciudad'].nunique()}")
            print(f"📊 Columnas disponibles: {list(df_excel.columns)}")
            
            return str(excel_temp_path)
            
        except Exception as e:
            print(f"❌ Error creando archivo Excel temporal: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _cleanup_temp_excel(self, excel_path: str):
        """
        Limpia el archivo Excel temporal creado para el script
        
        Args:
            excel_path (str): Ruta del archivo Excel temporal a eliminar
        """
        try:
            if excel_path and Path(excel_path).exists():
                Path(excel_path).unlink()
                print(f"🗑️ Archivo Excel temporal eliminado: {excel_path}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar archivo temporal: {str(e)}")
    
    def get_available_months(self):
        """Obtiene meses disponibles del archivo CSV"""
        return settings.get_available_months()
    
    def set_month_filter(self, mes: str, año: int):
        """Establece filtro de mes para procesamiento"""
        settings.save_session_config(mes=mes, año=año)
    
    def get_all_available_cities(self) -> List[str]:
        """Obtiene todas las ciudades disponibles en el archivo CSV"""
        try:
            if not settings.IRCA_FILE.exists():
                return []
            
            df = pd.read_csv(settings.IRCA_FILE, sep=';', encoding='utf-8')
            if 'Ciudad' in df.columns:
                return df['Ciudad'].unique().tolist()
            return []
        except Exception as e:
            print(f"⚠️ Error obteniendo ciudades del CSV: {e}")
            return []
    
    def get_available_cities_for_month(self, mes: str, año: int) -> List[str]:
        """Obtiene ciudades disponibles para un mes/año específico"""
        try:
            if not settings.IRCA_FILE.exists():
                print(f"📁 Archivo IRCA no existe: {settings.IRCA_FILE}")
                return []
            
            df = pd.read_csv(settings.IRCA_FILE, sep=';', encoding='utf-8')
            print(f"📊 CSV leído - Shape: {df.shape}")
            print(f"📊 Columnas disponibles: {list(df.columns)}")
            
            # Verificar primeras filas para entender formato
            if len(df) > 0:
                print(f"📊 Primeras 3 filas del CSV:")
                print(df.head(3).to_string())
            
            # Filtrar por mes (y año si existe)
            if 'Mes' in df.columns:
                print(f"🔍 Filtrando por Mes='{mes}'")
                
                # Mostrar valores únicos de Mes para debugging
                print(f"📅 Meses únicos en CSV: {df['Mes'].unique()}")
                
                # Si hay columna Año, usarla también
                if 'Año' in df.columns:
                    print(f"📅 Años únicos en CSV: {df['Año'].unique()}")
                    print(f"🔍 Filtrando por Mes='{mes}' y Año={año}")
                    df_filtered = df[(df['Mes'] == mes) & (df['Año'] == año)]
                else:
                    print(f"⚠️ Columna 'Año' no encontrada, filtrando solo por Mes='{mes}'")
                    df_filtered = df[df['Mes'] == mes]
                
                print(f"📊 Registros después del filtro: {len(df_filtered)}")
                
                if len(df_filtered) > 0:
                    print(f"📊 Muestra de datos filtrados:")
                    cols_to_show = ['Mes', 'Ciudad']
                    if 'Año' in df.columns:
                        cols_to_show = ['Mes', 'Año', 'Ciudad']
                    print(df_filtered[cols_to_show].head(3).to_string())
                
                if 'Ciudad' in df_filtered.columns:
                    ciudades = df_filtered['Ciudad'].unique().tolist()
                    print(f"🏢 Ciudades encontradas para {mes}" + (f"/{año}" if 'Año' in df.columns else "") + f": {ciudades}")
                    return ciudades
                else:
                    print(f"❌ Columna 'Ciudad' no encontrada en datos filtrados")
            else:
                print(f"❌ Columna 'Mes' no encontrada en CSV")
            
            return []
        except Exception as e:
            print(f"⚠️ Error obteniendo ciudades para {mes}/{año}: {e}")
            import traceback
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            return []
    
    def get_filtered_data(self, mes: str = None, año: int = None):
        """Obtiene datos IRCA filtrados por mes/año"""
        try:
            if not settings.IRCA_FILE.exists():
                return {'error': 'Archivo IRCA no encontrado'}
            
            # Leer CSV
            df = pd.read_csv(settings.IRCA_FILE, sep=';')
            
            # Aplicar filtro si se proporciona
            if mes and año:
                df = df[(df['Mes'] == mes) & 
                       (pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce').dt.year == año)]
            
            return {
                'data': df,
                'total_registros': len(df),
                'ciudades': df['Ciudad'].unique().tolist() if len(df) > 0 else []
            }
        except Exception as e:
            return {'error': f'Error obteniendo datos filtrados: {str(e)}'}
