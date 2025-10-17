#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador del flujo secuencial obligatorio del sistema IRCA
"""

from typing import Tuple, Dict, Any, List
import streamlit as st
from datetime import datetime

from ..models.base_generator_model import BaseGeneratorModel
from ..models.irca_model import IRCAModel
from ..models.report_model import ReportModel
from ..config.settings import settings

class WorkflowController:
    """
    Controlador principal del flujo secuencial obligatorio:
    Paso 1 → Paso 2 → Paso 3
    """
    
    def __init__(self):
        self.base_generator = BaseGeneratorModel()
        self.irca_processor = IRCAModel()
        self.report_generator = ReportModel()
        self._initialize_session_state()
        # Cargar configuración de sesión persistente
        settings.load_session_config()
    
    def _initialize_session_state(self):
        """Inicializa variables de estado de Streamlit"""
        if 'workflow_state' not in st.session_state:
            st.session_state.workflow_state = {
                'last_refresh': datetime.now(),
                'execution_history': [],
                'current_step': None
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del flujo de trabajo"""
        paso1_status = self.base_generator.get_status_info()
        paso2_status = self.irca_processor.get_status_info()
        paso3_status = self.report_generator.get_status_info()
        
        # Determinar estado general
        if paso3_status['completed']:
            estado_general = "✅ Completado"
        elif paso2_status['completed']:
            estado_general = "🔄 En Paso 3"
        elif paso1_status['completed']:
            estado_general = "🔄 En Paso 2"
        else:
            estado_general = "⚪ Pendiente"
        
        return {
            'estado_general': estado_general,
            'paso1': paso1_status,
            'paso2': paso2_status,
            'paso3': paso3_status,
            'flujo_completo': paso3_status['workflow_complete'],
            'siguiente_paso': self._get_next_step()
        }
    
    def _get_next_step(self) -> str:
        """Determina cuál es el siguiente paso a ejecutar"""
        if not settings.get_paso_status('paso1'):
            return "paso1"
        elif not settings.get_paso_status('paso2'):
            return "paso2"
        elif not settings.get_paso_status('paso3'):
            return "paso3"
        else:
            return "completado"
    
    def can_execute_step(self, paso: str) -> Tuple[bool, str]:
        """Verifica si un paso específico puede ejecutarse"""
        # Validar requisitos de mes para todos los pasos
        month_valid, month_msg = self.validate_month_requirements(paso)
        if not month_valid:
            return False, month_msg
        
        if paso == "paso1":
            workflow_valid, workflow_msg = self.can_execute_workflow()
            if not workflow_valid:
                return False, workflow_msg
            return self.base_generator.is_ready_to_execute(), "Paso 1 disponible"
        
        elif paso == "paso2":
            if not settings.get_paso_status('paso1'):
                return False, "❌ Debe completar Paso 1 primero"
            return self.irca_processor.can_execute()
        
        elif paso == "paso3":
            if not settings.get_paso_status('paso1'):
                return False, "❌ Debe completar Paso 1 primero"
            if not settings.get_paso_status('paso2'):
                return False, "❌ Debe completar Paso 2 primero"
            return self.report_generator.can_execute()
        
        else:
            return False, "❌ Paso no reconocido"
    
    def execute_step(self, paso: str) -> Tuple[bool, str]:
        """Ejecuta un paso específico del flujo"""
        can_execute, message = self.can_execute_step(paso)
        if not can_execute:
            return False, message
        
        # Registrar inicio de ejecución
        st.session_state.workflow_state['current_step'] = paso
        execution_start = datetime.now()
        
        try:
            if paso == "paso1":
                success, msg = self.base_generator.execute()
            elif paso == "paso2":
                success, msg = self.irca_processor.execute()
            elif paso == "paso3":
                success, msg = self.report_generator.execute()
            else:
                return False, "❌ Paso no reconocido"
            
            # Registrar resultado
            execution_end = datetime.now()
            duration = (execution_end - execution_start).total_seconds()
            
            st.session_state.workflow_state['execution_history'].append({
                'step': paso,
                'success': success,
                'message': msg,
                'timestamp': execution_end,
                'duration': duration
            })
            
            st.session_state.workflow_state['current_step'] = None
            return success, msg
            
        except Exception as e:
            st.session_state.workflow_state['current_step'] = None
            return False, f"❌ Error inesperado: {str(e)}"
    
    def execute_complete_workflow(self) -> Tuple[bool, str]:
        """Ejecuta el flujo completo secuencialmente"""
        resultados = []
        
        # Ejecutar Paso 1
        if not settings.get_paso_status('paso1'):
            success, msg = self.execute_step('paso1')
            resultados.append(f"Paso 1: {msg}")
            if not success:
                return False, "\n".join(resultados)
        
        # Ejecutar Paso 2
        if not settings.get_paso_status('paso2'):
            success, msg = self.execute_step('paso2')
            resultados.append(f"Paso 2: {msg}")
            if not success:
                return False, "\n".join(resultados)
        
        # Ejecutar Paso 3
        if not settings.get_paso_status('paso3'):
            success, msg = self.execute_step('paso3')
            resultados.append(f"Paso 3: {msg}")
            if not success:
                return False, "\n".join(resultados)
        
        if not resultados:
            return True, "✅ Flujo ya estaba completado"
        
        return True, "✅ Flujo completo ejecutado:\n" + "\n".join(resultados)
    
    def reset_workflow(self) -> bool:
        """Resetea todo el flujo de trabajo"""
        try:
            settings.reset_estados()
            
            # Resetear modelos
            self.base_generator.status = "not_executed"
            self.irca_processor.status = "not_executed"
            self.report_generator.status = "not_executed"
            
            # Limpiar historial
            st.session_state.workflow_state['execution_history'] = []
            
            return True
        except Exception as e:
            return False
    
    def get_step_button_config(self, paso: str) -> Dict[str, Any]:
        """Obtiene configuración para botones de UI"""
        can_execute, message = self.can_execute_step(paso)
        
        if paso == "paso1":
            title = "🚀 PASO 1: Generador Base"
            description = "Crea estructura de carpetas y archivos base"
        elif paso == "paso2":
            title = "📊 PASO 2: Procesamiento IRCA"
            description = "Procesa datos IRCA y rellena hojas TAGS"
        elif paso == "paso3":
            title = "📄 PASO 3: Generación Reportes"
            description = "Genera informes Word finales con fotos"
        else:
            title = "❓ Paso Desconocido"
            description = ""
        
        # Determinar estado visual
        is_completed = settings.get_paso_status(paso)
        is_executing = st.session_state.workflow_state.get('current_step') == paso
        
        if is_executing:
            status_icon = "🔄"
            status_text = "Ejecutando..."
        elif is_completed:
            status_icon = "✅"
            status_text = "Completado"
        elif can_execute:
            status_icon = "⚪"
            status_text = "Listo"
        else:
            status_icon = "🔒"
            status_text = "Bloqueado"
        
        return {
            'title': title,
            'description': description,
            'can_execute': can_execute and not is_executing,
            'is_completed': is_completed,
            'is_executing': is_executing,
            'status_icon': status_icon,
            'status_text': status_text,
            'message': message
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas para el dashboard"""
        ciudades = settings.get_carpetas_datos()
        irca_summary = self.irca_processor.get_irca_summary()
        
        # Nota: Métrica "Reportes Generados" eliminada por solicitud del usuario
        
        # Calcular ciudades pendientes
        # Ciudades que NO están en IRCA(%).csv para el mes seleccionado
        ciudades_pendientes = 0
        
        try:
            # Obtener todas las ciudades de aeropuertos definidas (AEROPUERTOS es una lista)
            todas_ciudades = set(settings.AEROPUERTOS)
            
            # Obtener ciudades que SÍ están en IRCA(%).csv
            if settings.SELECTED_MONTH and settings.SELECTED_YEAR:
                print(f"🔍 Buscando ciudades para {settings.SELECTED_MONTH}/{settings.SELECTED_YEAR}")
                ciudades_en_csv = set(self.irca_processor.get_available_cities_for_month(
                    settings.SELECTED_MONTH, 
                    settings.SELECTED_YEAR
                ) or [])
                print(f"📊 Ciudades en CSV para {settings.SELECTED_MONTH}: {ciudades_en_csv}")
            else:
                # Si no hay mes seleccionado, obtener todas las ciudades del CSV
                ciudades_en_csv = set(self.irca_processor.get_all_available_cities() or [])
                print(f"📊 Todas las ciudades en CSV: {ciudades_en_csv}")
            
            # Ciudades pendientes = Ciudades totales - Ciudades en CSV
            ciudades_faltantes = todas_ciudades - ciudades_en_csv
            ciudades_pendientes = len(ciudades_faltantes)
            
            print(f"🏢 Total aeropuertos definidos: {len(todas_ciudades)}")
            print(f"🏢 Lista aeropuertos: {list(todas_ciudades)}")
            print(f"✅ Ciudades en CSV: {len(ciudades_en_csv)}")
            print(f"✅ Lista ciudades CSV: {list(ciudades_en_csv)}")
            print(f"❌ Ciudades faltantes: {ciudades_pendientes}")
            print(f"📋 Lista ciudades faltantes: {list(ciudades_faltantes)}")
            
        except Exception as e:
            print(f"⚠️ Error calculando ciudades pendientes: {e}")
            ciudades_pendientes = 0
        
        return {
            'total_aeropuertos': len(settings.AEROPUERTOS),
            'carpetas_creadas': len(ciudades),
            'ciudades_pendientes': ciudades_pendientes,
            'irca_promedio': irca_summary.get('irca_promedio', 0),
            'ultimo_proceso': max(
                [h['timestamp'] for h in st.session_state.workflow_state['execution_history']]
                + [datetime.min]
            ).strftime('%d/%m/%Y %H:%M') if st.session_state.workflow_state['execution_history'] else "Nunca"
        }
    
    # ======================== NUEVAS FUNCIONALIDADES ========================
    
    def get_available_months(self) -> List[Dict[str, Any]]:
        """Obtiene lista de meses disponibles para procesamiento"""
        return self.irca_processor.get_available_months()
    
    def set_selected_month(self, mes: str, año: int) -> bool:
        """Establece el mes seleccionado para procesamiento"""
        try:
            settings.save_session_config(mes=mes, año=año)
            # Resetear flujo si ya había uno en progreso
            if any([settings.get_paso_status(f'paso{i}') for i in range(1, 4)]):
                self.reset_workflow()
            return True
        except Exception as e:
            return False
    
    def set_output_directory(self, directory_path: str) -> bool:
        """Establece la carpeta de destino para los reportes"""
        try:
            from pathlib import Path
            path = Path(directory_path)
            if path.exists() and path.is_dir():
                settings.save_session_config(output_dir=directory_path)
                return True
            return False
        except Exception:
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Obtiene información de la sesión actual"""
        session_info = settings.get_session_info()
        workflow_status = self.get_workflow_status()
        
        # Verificar si hay reportes válidos para descarga
        reports_status = self.get_reports_status()
        
        # Simplificar lógica: can_download se basa en que los 3 pasos estén completados
        steps_completed = (
            settings.get_paso_status('paso1') and 
            settings.get_paso_status('paso2') and 
            settings.get_paso_status('paso3')
        )
        
        return {
            **session_info,
            'workflow_complete': steps_completed,
            'can_download': steps_completed,  # Habilitar descarga tan pronto se completen los 3 pasos
            'month_display': f"{session_info['selected_month']} {session_info['selected_year']}" 
                           if session_info['has_month_selected'] else None,
            'reports_ready': reports_status['ready_for_download'],
            'valid_reports_count': reports_status['reportes_validos']
        }
    
    def can_execute_workflow(self) -> Tuple[bool, str]:
        """Verifica si el flujo puede ejecutarse con la configuración actual"""
        session_info = settings.get_session_info()
        
        if not session_info['has_month_selected']:
            return False, "❌ Debe seleccionar un mes para procesar"
        
        # Verificar que hay datos para el mes seleccionado
        filtered_data = self.irca_processor.get_filtered_data(
            session_info['selected_month'], 
            session_info['selected_year']
        )
        
        if 'error' in filtered_data:
            return False, f"❌ Error obteniendo datos: {filtered_data['error']}"
        
        if filtered_data['total_registros'] == 0:
            return False, f"❌ No hay datos para {session_info['selected_month']} {session_info['selected_year']}"
        
        return True, f"✅ Listo para procesar {filtered_data['total_registros']} registros"
    
    def reset_complete_workflow(self) -> Tuple[bool, str]:
        """Reinicia completamente el flujo incluyendo configuración"""
        try:
            # Resetear configuración en settings
            settings.reset_complete_workflow()
            
            # Resetear modelos
            self.base_generator.status = "not_executed"
            self.irca_processor.status = "not_executed"
            self.report_generator.status = "not_executed"
            
            # Limpiar historial de Streamlit
            st.session_state.workflow_state = {
                'last_refresh': datetime.now(),
                'execution_history': [],
                'current_step': None
            }
            
            return True, "✅ Flujo reiniciado completamente"
        except Exception as e:
            return False, f"❌ Error en reinicio: {str(e)}"
    
    def prepare_download_zip(self) -> bytes:
        """Prepara ZIP en memoria con los reportes Word generados para Streamlit Cloud"""
        import zipfile
        import io
        from datetime import datetime
        
        # Crear buffer en memoria para el ZIP
        zip_buffer = io.BytesIO()
        
        # Obtener info de sesión
        session_info = settings.get_session_info()
        
        # Buscar reportes Word generados
        ciudades = settings.get_carpetas_datos()
        reportes_agregados = 0
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Agregar cada reporte Word al ZIP
            for ciudad in ciudades:
                ciudad_path = settings.DATOS_DIR / ciudad
                if ciudad_path.exists():
                    reporte_file = ciudad_path / f"reporte_{ciudad}.docx"
                    
                    # Verificar que el reporte existe y tiene contenido válido
                    if reporte_file.exists() and reporte_file.stat().st_size > 1024:  # Mínimo 1KB
                        # Nombre descriptivo para el archivo en el ZIP
                        if session_info['has_month_selected']:
                            nombre_en_zip = f"Reporte_IRCA_{ciudad}_{session_info['selected_month']}_{session_info['selected_year']}.docx"
                        else:
                            nombre_en_zip = f"Reporte_IRCA_{ciudad}.docx"
                        
                        # Agregar archivo al ZIP
                        zip_file.write(reporte_file, arcname=nombre_en_zip)
                        reportes_agregados += 1
                        print(f"✅ Agregado al ZIP: {nombre_en_zip}")
            
            # Agregar archivo de resumen
            resumen_content = f"""DESCARGA DE REPORTES IRCA
{'='*50}

Período: {session_info.get('month_display', 'No especificado')}
Fecha descarga: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Total reportes: {reportes_agregados}

Ciudades incluidas:
"""
            for ciudad in ciudades:
                ciudad_path = settings.DATOS_DIR / ciudad
                reporte_file = ciudad_path / f"reporte_{ciudad}.docx"
                if reporte_file.exists() and reporte_file.stat().st_size > 1024:
                    resumen_content += f"  ✅ {ciudad}\n"
            
            # Agregar resumen al ZIP
            zip_file.writestr("RESUMEN_DESCARGA.txt", resumen_content.encode('utf-8'))
        
        # Retornar bytes del ZIP
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def validate_month_requirements(self, paso: str) -> Tuple[bool, str]:
        """Valida que se cumplen los requisitos de mes para ejecutar un paso"""
        session_info = settings.get_session_info()
        
        if not session_info['has_month_selected']:
            return False, "❌ Debe seleccionar un mes antes de ejecutar el flujo"
        
        return True, "✅ Configuración válida"
    
    def get_reports_status(self) -> Dict[str, Any]:
        """Obtiene estado detallado de los reportes generados"""
        ciudades = settings.get_carpetas_datos()
        reportes_info = []
        total_reportes = 0
        reportes_validos = 0
        
        for ciudad in ciudades:
            ciudad_path = settings.DATOS_DIR / ciudad
            reporte_file = ciudad_path / f"reporte_{ciudad}.docx"
            
            if reporte_file.exists():
                size = reporte_file.stat().st_size
                total_reportes += 1
                if size > 1024:  # Mayor a 1KB considerado válido
                    reportes_validos += 1
                    
                reportes_info.append({
                    'ciudad': ciudad,
                    'existe': True,
                    'size': size,
                    'size_mb': round(size / 1024 / 1024, 2),
                    'valido': size > 1024,
                    'path': str(reporte_file)
                })
            else:
                reportes_info.append({
                    'ciudad': ciudad,
                    'existe': False,
                    'size': 0,
                    'size_mb': 0,
                    'valido': False,
                    'path': str(reporte_file)
                })
        
        return {
            'total_ciudades': len(ciudades),
            'reportes_encontrados': total_reportes,
            'reportes_validos': reportes_validos,
            'reportes_info': reportes_info,
            'ready_for_download': reportes_validos > 0
        }
