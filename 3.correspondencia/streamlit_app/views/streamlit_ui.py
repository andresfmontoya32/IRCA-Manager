#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz de usuario principal en Streamlit para el Sistema IRCA
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, Any
import threading
from pathlib import Path

from ..controllers.workflow_controller import WorkflowController
from ..controllers.optional_controller import OptionalController
from ..config.settings import settings

class StreamlitUI:
    """
    Interfaz de usuario principal del Sistema IRCA
    """
    
    def __init__(self):
        self.workflow_controller = WorkflowController()
        self.optional_controller = OptionalController()
        self._configure_page()
    
    def _configure_page(self):
        """Configura la página de Streamlit"""
        st.set_page_config(
            page_title="🛩️ IRCA Manager - Aerocivil",
            page_icon="🛩️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def _render_header_with_logos(self):
        """Renderiza header profesional con logos institucionales"""
        # CSS para el header profesional
        st.markdown(
            """
            <style>
            .header-container {
                background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .title-text {
                color: #1f4e79;
                font-weight: 700;
                margin-bottom: 5px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }
            .subtitle-text {
                color: #6c757d;
                font-style: italic;
                font-size: 16px;
            }
            .logo-container {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Contenedor principal del header
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        # Crear columnas para layout del header
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            # Logo Conhydra (izquierda)
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            try:
                st.image(
                    "streamlit_app/assets/Conhydra.png",
                    width=300  # CAMBIAR AQUÍ EL TAMAÑO DEL LOGO CONHYDRA
                )
                st.markdown(
                    '<p style="text-align: center; font-size: 12px; color: #666; margin-top: 5px;">Empresa</p>',
                    unsafe_allow_html=True
                )
            except Exception:
                st.markdown(
                    """
                    <div style="text-align: center;">
                        <strong>CONHYDRA</strong><br>
                        <small style="color: #666;">.</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Título centrado con estilo profesional
            st.markdown(
                """
                <div style="text-align: center; padding-top: 15px;">
                    <h1 class="title-text">
                        IRCA MANAGER - AEROCIVIL
                    </h1>
                    <p class="subtitle-text">
                        Sistema de Automatización de Informes de Calidad del Agua
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            # Logo Aerocivil (derecha)
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            try:
                st.image(
                    "streamlit_app/assets/aerocivil.png",
                    width=150  # CAMBIAR AQUÍ EL TAMAÑO DEL LOGO AEROCIVIL
                )
                st.markdown(
                    '<p style="text-align: center; font-size: 12px; color: #666; margin-top: 5px;">Cliente</p>',
                    unsafe_allow_html=True
                )
            except Exception:
                st.markdown(
                    """
                    <div style="text-align: center;">
                        <strong>AEROCIVIL</strong><br>
                        <small style="color: #666;">Cliente</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cerrar contenedor del header
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render(self):
        """Renderiza la interfaz principal"""
        # Header profesional con logos institucionales
        self._render_header_with_logos()
        st.markdown("---")
        
        # Sidebar para navegación
        with st.sidebar:
            self._render_sidebar()
        
        # Contenido principal basado en navegación
        page = st.session_state.get('current_page', 'dashboard')
        
        if page == 'dashboard':
            self._render_dashboard()
        elif page == 'workflow':
            self._render_workflow()
        elif page == 'optional':
            self._render_optional_functions()
        elif page == 'config':
            self._render_configuration()
        elif page == 'logs':
            self._render_logs()
    
    def _render_sidebar(self):
        """Renderiza la barra lateral de navegación"""
        # Logo en sidebar
        try:
            st.image(
                "streamlit_app/assets/IRCA Manager.png",
                width=150
            )
        except Exception:
            # Fallback si no se encuentra la imagen
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 20px;">
                    <h3 style="color: #1f4e79;">🛩️ IRCA Manager</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.header("🧭 Navegación")
        
        # Obtener estado del sistema
        workflow_status = self.workflow_controller.get_workflow_status()
        
        # Indicador de estado general
        st.info(f"Estado: {workflow_status['estado_general']}")
        
        # Botones de navegación
        pages = {
            'dashboard': '📊 Dashboard',
            'workflow': '🔄 Flujo Principal',
            'optional': '🔧 Funciones Opcionales',
            'config': '⚙️ Configuración',
            'logs': '📋 Logs'
        }
        
        for key, label in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Acciones Rápidas")
        
        if st.button("🔄 Refrescar", use_container_width=True):
            st.rerun()
        
        if st.button("🔄 Reiniciar Flujo", use_container_width=True):
            with st.spinner("🧹 Limpiando outputs y reiniciando..."):
                # Usar reset_complete_workflow que elimina todos los outputs
                success, message = self.workflow_controller.reset_complete_workflow()
                
                # Limpiar también estados de descarga en Streamlit
                if 'selected_download_folder' in st.session_state:
                    del st.session_state['selected_download_folder']
                if 'last_successful_download' in st.session_state:
                    del st.session_state['last_successful_download']
                    
            if success:
                st.success("✅ " + message + " - Todos los outputs eliminados")
                st.rerun()
            else:
                st.error("❌ " + message)
    
    def _render_dashboard(self):
        """Renderiza el dashboard principal"""
        st.header("📊 Dashboard")
        
        # Información de sesión actual
        session_info = self.workflow_controller.get_session_info()
        
        if session_info['has_month_selected']:
            st.info(f"📅 **Configuración Actual:** {session_info['month_display']} | 📁 {session_info.get('output_directory', 'Sin configurar')}")
        else:
            st.warning("⚠️ **Configure mes y carpeta destino en la sección 'Flujo Principal'**")
        
        # Métricas principales
        metrics = self.workflow_controller.get_dashboard_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Aeropuertos",
                value=metrics['total_aeropuertos']
            )
        
        with col2:
            st.metric(
                label="Carpetas Creadas",
                value=metrics['carpetas_creadas']
            )
        
        with col3:
            # Métrica: Ciudades Faltantes en IRCA
            pendientes = metrics.get('ciudades_pendientes', 0)
            delta_text = "✅ Todas en IRCA" if pendientes == 0 else f"❌ {pendientes} faltantes"
            st.metric(
                label="Ciudades Faltantes",
                value=pendientes,
                delta=delta_text
            )
        
        with col4:
            available_months = self.workflow_controller.get_available_months()
            st.metric(
                label="Meses Disponibles",
                value=len(available_months)
            )
        
        # Estado del flujo
        st.markdown("---")
        workflow_status = self.workflow_controller.get_workflow_status()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🔄 Estado del Flujo")
            
            # Indicadores de pasos
            steps_info = [
                ("Paso 1: Generador Base", workflow_status['paso1']),
                ("Paso 2: Procesamiento IRCA", workflow_status['paso2']),
                ("Paso 3: Generación Reportes", workflow_status['paso3'])
            ]
            
            for step_name, step_info in steps_info:
                status_icon = "✅" if step_info['completed'] else "⚪"
                st.write(f"{status_icon} {step_name}")
        
        with col2:
            st.subheader("📈 Progreso")
            
            # Calcular progreso
            completed_steps = sum([
                workflow_status['paso1']['completed'],
                workflow_status['paso2']['completed'],
                workflow_status['paso3']['completed']
            ])
            
            progress = completed_steps / 3
            st.progress(progress)
            st.write(f"Completado: {completed_steps}/3 pasos")
        
        # Dashboard Power BI
        self._render_power_bi_dashboard()
        
        # Información del sistema
        st.markdown("---")
        self._render_system_health()
    
    def _render_workflow(self):
        """Renderiza la página del flujo principal"""
        st.header("🔄 Flujo Principal Obligatorio")
        
        # ==================== CONFIGURACIÓN DEL PROCESO ====================
        st.subheader("⚙️ Configuración del Proceso")
        
        # Obtener información de sesión
        session_info = self.workflow_controller.get_session_info()
        
        # Selector de mes
        st.write("**📅 Mes a procesar:**")
        available_months = self.workflow_controller.get_available_months()
        
        if available_months:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Encontrar índice del mes seleccionado
                selected_index = 0
                if session_info['has_month_selected']:
                    for i, month in enumerate(available_months):
                        if (month['mes'] == session_info['selected_month'] and 
                            month['año'] == session_info['selected_year']):
                            selected_index = i
                            break
                
                selected_month_obj = st.selectbox(
                    "Seleccione el mes:",
                    available_months,
                    index=selected_index,
                    format_func=lambda x: x['display'],
                    key="month_selector"
                )
                
                # Actualizar configuración si cambió
                if (selected_month_obj['mes'] != session_info.get('selected_month') or 
                    selected_month_obj['año'] != session_info.get('selected_year')):
                    if self.workflow_controller.set_selected_month(
                        selected_month_obj['mes'], 
                        selected_month_obj['año']
                    ):
                        st.rerun()
            
            with col2:
                # Mostrar información del mes seleccionado
                filtered_data = self.workflow_controller.irca_processor.get_filtered_data(
                    selected_month_obj['mes'], selected_month_obj['año']
                )
                if 'error' not in filtered_data:
                    st.metric(
                        "Registros Disponibles", 
                        filtered_data['total_registros'],
                        help=f"Datos para {selected_month_obj['display']}"
                    )
                    if filtered_data['ciudades']:
                        st.write(f"🏢 **Ciudades en IRCA:** {', '.join(filtered_data['ciudades'])}")
                        
                        # Mostrar ciudades faltantes
                        metrics = self.workflow_controller.get_dashboard_metrics()
                        ciudades_faltantes = metrics.get('ciudades_pendientes', 0)
                        if ciudades_faltantes > 0:
                            st.warning(f"❌ **{ciudades_faltantes} ciudades faltantes** en IRCA(%) para este mes")
                        else:
                            st.success("✅ **Todas las ciudades** están en IRCA(%) para este mes")
                else:
                    st.error(filtered_data['error'])
        else:
            st.error("❌ No se encontraron datos en el archivo IRCA CSV")
        
        st.markdown("---")
        
        # ==================== ESTADO Y CONTROLES PRINCIPALES ====================
        workflow_status = self.workflow_controller.get_workflow_status()
        
        # Estado general
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if session_info['has_month_selected']:
                st.success(f"📅 **Procesando:** {session_info['month_display']}")
            else:
                st.warning("⚠️ Seleccione un mes para continuar")
        
        with col2:
            # Reinicio completo con confirmación
            if st.button("🔄 REINICIAR COMPLETO", type="secondary", use_container_width=True):
                if 'confirm_reset' not in st.session_state:
                    st.session_state.confirm_reset = False
                st.session_state.confirm_reset = not st.session_state.confirm_reset
        
        with col3:
            # Flujo completo
            can_execute_workflow, workflow_msg = self.workflow_controller.can_execute_workflow()
            if st.button(
                "⚡ FLUJO COMPLETO", 
                type="primary", 
                disabled=not can_execute_workflow,
                use_container_width=True
            ):
                with st.spinner("Ejecutando flujo completo..."):
                    success, message = self.workflow_controller.execute_complete_workflow()
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                st.rerun()
        
        # Confirmación de reinicio
        if st.session_state.get('confirm_reset', False):
            st.warning("⚠️ ¿Está seguro de reiniciar completamente? Se perderá todo el progreso actual.")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ SÍ, REINICIAR", type="primary"):
                    success, msg = self.workflow_controller.reset_complete_workflow()
                    if success:
                        # Limpiar también los estados de descarga persistentes
                        if 'selected_download_folder' in st.session_state:
                            del st.session_state['selected_download_folder']
                        if 'last_successful_download' in st.session_state:
                            del st.session_state['last_successful_download']
                        st.success(msg + " - Estados de descarga también reiniciados")
                    else:
                        st.error(msg)
                    st.session_state.confirm_reset = False
                    st.rerun()
            with col2:
                if st.button("❌ CANCELAR"):
                    st.session_state.confirm_reset = False
                    st.rerun()
        
        # Mostrar mensaje de validación si hay problemas
        if not can_execute_workflow:
            st.error(workflow_msg)
        
        st.markdown("---")
        
        # ==================== PASOS INDIVIDUALES ====================
        st.subheader("🔧 Ejecución Individual de Pasos")
        
        for paso in ['paso1', 'paso2', 'paso3']:
            self._render_step_section(paso)
            st.markdown("---")
        
        # Nota: Sección "Estado de Reportes Generados" eliminada por solicitud del usuario
        
        # ==================== SECCIÓN DE DESCARGA SIEMPRE VISIBLE ====================
        st.markdown("---")
        st.subheader("📥 Descarga de Reportes")
        
        # Verificar estado actual de reportes y workflow
        workflow_status = self.workflow_controller.get_workflow_status()
        reports_status = self.workflow_controller.get_reports_status()
        can_download = session_info['can_download']
        
        # Mostrar estado del workflow
        completed_steps = sum([
            workflow_status['paso1']['completed'],
            workflow_status['paso2']['completed'],
            workflow_status['paso3']['completed']
        ])
        
        if completed_steps == 3:
            if reports_status['ready_for_download']:
                st.success("🎉 ¡Flujo completado! Reportes listos para descarga")
            else:
                st.warning("⚠️ Flujo completado - Verificando reportes...")
        else:
            st.info(f"📊 Progreso del flujo: {completed_steps}/3 pasos completados")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if can_download:
                # Estado cuando puede descargar - verificar si hay reportes
                if reports_status['ready_for_download'] and reports_status['reportes_validos'] > 0:
                    st.success(f"✅ **{reports_status['reportes_validos']} reportes Word disponibles**")
                    if session_info['month_display']:
                        st.write(f"📅 **Período:** {session_info['month_display']}")
                    st.info("💡 Los reportes se descargarán en una carpeta en tu Escritorio")
                    
                    # Mostrar lista de reportes disponibles
                    if reports_status['reportes_info']:
                        valid_cities = [info['ciudad'] for info in reports_status['reportes_info'] if info['valido']]
                        if valid_cities:
                            st.write(f"🏢 **Ciudades incluidas:** {', '.join(valid_cities)}")
                else:
                    # Flujo completado pero sin reportes válidos
                    st.warning("⚠️ **Flujo completado pero sin reportes válidos**")
                    if session_info['month_display']:
                        st.write(f"📅 **Período:** {session_info['month_display']}")
                    st.write("• Los archivos pueden estar vacíos o corruptos")
                    st.write("• Intente ejecutar el flujo nuevamente")
                    st.write("• Verifique que los scripts originales funcionan correctamente")
            else:
                # Estado cuando no puede descargar
                if workflow_status['flujo_completo']:
                    st.warning("❌ **No hay reportes válidos para descargar**")
                    st.write("• Los archivos pueden estar vacíos o corruptos")
                    st.write("• Verifique que el Paso 3 se ejecutó correctamente")
                else:
                    steps_needed = []
                    if not workflow_status['paso1']['completed']:
                        steps_needed.append("Paso 1")
                    if not workflow_status['paso2']['completed']:
                        steps_needed.append("Paso 2")
                    if not workflow_status['paso3']['completed']:
                        steps_needed.append("Paso 3")
                    
                    st.warning(f"🔒 **Complete el flujo para descargar reportes**")
                    st.write(f"• Pasos pendientes: {', '.join(steps_needed)}")
                    if session_info['month_display']:
                        st.write(f"📅 Mes configurado: {session_info['month_display']}")
                    else:
                        st.write("📅 Seleccione un mes en la configuración")
        
        with col2:
            # Información sobre el estado de los reportes
            if can_download:
                st.info("📁 Seleccione una carpeta para descargar los reportes")
            else:
                st.warning("🔒 Complete el flujo para habilitar la descarga")
            
            # Folder picker nativo como única opción de descarga
            if can_download:
                col_picker, col_path = st.columns([1, 2])
                
                with col_picker:
                    if st.button("📁 Seleccionar Carpeta", use_container_width=True, 
                               help="Abrir diálogo nativo para seleccionar carpeta de destino"):
                        # Usar folder picker nativo
                        selected_folder = self._show_folder_picker()
                        
                        if selected_folder:
                            # Guardar en session_state
                            st.session_state['selected_download_folder'] = selected_folder
                            st.rerun()  # Refrescar para mostrar la ruta
                        else:
                            st.warning("⚠️ No se seleccionó ninguna carpeta")
                
                with col_path:
                    # Mostrar carpeta seleccionada
                    if 'selected_download_folder' in st.session_state:
                        selected_folder = st.session_state['selected_download_folder']
                        st.text_input(
                            "Carpeta seleccionada:",
                            value=selected_folder,
                            disabled=True,
                            key="display_selected_folder"
                        )
                    else:
                        st.text_input(
                            "Carpeta seleccionada:",
                            value="",
                            placeholder="Use el botón para seleccionar una carpeta",
                            disabled=True,
                            key="display_placeholder_folder"
                        )
                
                # Botón de descarga principal
                if 'selected_download_folder' in st.session_state:
                    custom_folder = st.session_state['selected_download_folder']
                    
                    # Validar que la carpeta existe y es escribible
                    folder_path = Path(custom_folder)
                    if not folder_path.exists():
                        st.error(f"❌ La carpeta no existe: {custom_folder}")
                    elif not folder_path.is_dir():
                        st.error(f"❌ La ruta no es una carpeta: {custom_folder}")
                    else:
                        # Verificar permisos de escritura
                        try:
                            test_file = folder_path / ".test_write_permission"
                            test_file.touch()
                            test_file.unlink()
                            can_write = True
                        except:
                            can_write = False
                        
                        if not can_write:
                            st.error(f"❌ Sin permisos de escritura en: {custom_folder}")
                        else:
                            # Todo OK, mostrar botón de descarga
                            st.success(f"✅ Carpeta válida: {custom_folder}")
                            
                            if st.button("📥 Descargar Reportes", 
                                       type="primary", 
                                       use_container_width=True):
                                with st.spinner("📥 Descargando reportes..."):
                                    success, message, download_path = self.workflow_controller.prepare_download_package(custom_folder)
                                
                                if success:
                                    st.success("🎉 " + message)
                                    st.balloons()
                                    
                                    if download_path:
                                        st.success(f"📂 **Reportes guardados en:**")
                                        st.code(download_path, language=None)
                                        
                                        # Botones persistentes para abrir y copiar
                                        # Guardar el último path de descarga exitosa
                                        st.session_state['last_successful_download'] = download_path
                
                # Mostrar botones persistentes después de descarga exitosa
                if 'last_successful_download' in st.session_state:
                    st.divider()
                    st.subheader("🛠️ Acciones de Descarga")
                    
                    last_download_path = st.session_state['last_successful_download']
                    st.success(f"📂 **Última descarga exitosa:** `{last_download_path}`")
                    
                    # Botones persistentes que no desaparecen
                    col_open, col_copy, col_clear = st.columns(3)
                    
                    with col_open:
                        if st.button("📂 Abrir Carpeta", key="persistent_open", use_container_width=True):
                            # Método más robusto para abrir carpeta
                            import os
                            import platform
                            import subprocess
                            
                            try:
                                if platform.system() == "Windows":
                                    # Usar os.startfile() que es más confiable en Windows
                                    os.startfile(last_download_path)
                                    st.success("📂 Carpeta abierta en el explorador")
                                else:
                                    # Para otros OS (Linux/Mac)
                                    if platform.system() == "Darwin":  # macOS
                                        subprocess.run(["open", last_download_path])
                                    else:  # Linux
                                        subprocess.run(["xdg-open", last_download_path])
                                    st.success("📂 Carpeta abierta")
                            except Exception as e:
                                st.error(f"❌ No se pudo abrir la carpeta: {str(e)}")
                                # Fallback: intentar con explorer
                                try:
                                    subprocess.run(f'explorer "{last_download_path}"', shell=True, check=True)
                                    st.success("📂 Carpeta abierta (método alternativo)")
                                except Exception as e2:
                                    st.error(f"❌ Error en método alternativo: {str(e2)}")
                    
                    with col_copy:
                        if st.button("📋 Copiar Ruta", key="persistent_copy", use_container_width=True):
                            components.html(f"""
                            <script>
                                navigator.clipboard.writeText('{last_download_path}').then(function() {{
                                    console.log('Ruta copiada al portapapeles');
                                }});
                            </script>
                            """, height=0)
                            st.success("📋 Ruta copiada al portapapeles")
                    
                    with col_clear:
                        if st.button("🗑️ Nueva Carpeta", key="persistent_clear", use_container_width=True):
                            # Solo limpiar la carpeta seleccionada, no el historial de descarga
                            if 'selected_download_folder' in st.session_state:
                                del st.session_state['selected_download_folder']
                            st.info("🗑️ Carpeta limpiada. Seleccione una nueva carpeta.")
                            st.rerun()
                else:
                    st.error("❌ " + message)
                    
                    # Mostrar información de debug
                    with st.expander("🔍 Ver detalles del error"):
                        reports_status = self.workflow_controller.get_reports_status()
                        for info in reports_status['reportes_info']:
                            icon = "✅" if info['valido'] else ("⚠️" if info['existe'] else "❌")
                            st.write(f"{icon} **{info['ciudad']}**: {info['size']} bytes")
            else:
                # Mostrar botón deshabilitado
                st.button("📁 Seleccionar Carpeta", 
                         disabled=True,
                         use_container_width=True, 
                         help="Complete el flujo para habilitar la descarga")
    
    def _render_step_section(self, paso: str):
        """Renderiza sección de un paso específico"""
        config = self.workflow_controller.get_step_button_config(paso)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"### {config['title']}")
            st.write(config['description'])
            st.write(f"Estado: {config['status_icon']} {config['status_text']}")
        
        with col2:
            button_disabled = not config['can_execute']
            button_key = f"execute_{paso}"
            
            if st.button(
                f"Ejecutar {paso.upper()}",
                disabled=button_disabled,
                key=button_key,
                use_container_width=True
            ):
                with st.spinner(f"Ejecutando {paso}..."):
                    success, message = self.workflow_controller.execute_step(paso)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                st.rerun()
        
        with col3:
            if config['is_completed']:
                st.success("✅ Completado")
            elif config['is_executing']:
                st.warning("🔄 Ejecutando...")
            elif not config['can_execute']:
                st.warning("🔒 Bloqueado")
            else:
                st.info("⚪ Listo")
        
        # Mostrar mensaje si hay
        if config['message'] and not config['can_execute']:
            st.warning(config['message'])
    
    def _render_optional_functions(self):
        """Renderiza la página de funciones opcionales"""
        st.header("🔧 Funciones Opcionales")
        
        # Validación de fotos
        st.subheader("📷 Verificación de Fotos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Selector de ciudad
            cities = self.optional_controller.photo_validator.get_available_cities()
            selected_city = st.selectbox(
                "Seleccionar ciudad (opcional):",
                ["Todas las ciudades"] + cities,
                key="photo_city_selector"
            )
            
            city_param = None if selected_city == "Todas las ciudades" else selected_city
            
            if st.button("🔍 Verificar Fotos", use_container_width=True):
                with st.spinner("Verificando fotos..."):
                    success, message = self.optional_controller.validate_photos(city_param)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                
                # Mostrar detalles
                photo_status = self.optional_controller.get_photo_validation_status()
                if photo_status['last_validation']:
                    details = photo_status['last_validation']['details']
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Fotos Encontradas", details['fotos_encontradas'])
                    with col_b:
                        st.metric("Fotos Faltantes", details['fotos_no_encontradas'])
                    with col_c:
                        st.metric("Tasa de Éxito", f"{details['success_rate']:.1f}%")
        
        with col2:
            # Estado de la última validación
            photo_status = self.optional_controller.get_photo_validation_status()
            if photo_status['last_validation']:
                last = photo_status['last_validation']
                st.info(f"Última validación: {last['timestamp'].strftime('%H:%M:%S')}")
                
                if last['details']['ciudades_problemas']:
                    st.warning(f"Ciudades con problemas: {', '.join(last['details']['ciudades_problemas'])}")
    
    def _render_configuration(self):
        """Renderiza la página de configuración"""
        st.header("⚙️ Configuración del Sistema")
        
        config = self.optional_controller.get_system_configuration()
        
        # Estado de validación
        if config['rutas_validas']:
            st.success("✅ Todas las rutas están configuradas correctamente")
        else:
            st.error("❌ Problemas encontrados en la configuración:")
            for error in config['errores_validacion']:
                st.error(f"• {error}")
        
        # Rutas configuradas
        st.subheader("📁 Rutas Configuradas")
        
        rutas_df = pd.DataFrame([
            {"Componente": "Scripts", "Ruta": config['rutas_configuradas']['scripts_dir']},
            {"Componente": "Datos", "Ruta": config['rutas_configuradas']['datos_dir']},
            {"Componente": "Plantillas", "Ruta": config['rutas_configuradas']['plantillas_dir']},
            {"Componente": "Archivo IRCA", "Ruta": config['rutas_configuradas']['irca_file']},
            {"Componente": "Origen", "Ruta": config['rutas_configuradas']['origen_dir']}
        ])
        
        st.dataframe(rutas_df, use_container_width=True, hide_index=True)
        
        # Estados de pasos
        st.subheader("📊 Estado de Pasos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = "✅" if config['estados_pasos']['paso1'] else "⚪"
            st.write(f"{status} Paso 1: Generador Base")
        
        with col2:
            status = "✅" if config['estados_pasos']['paso2'] else "⚪"
            st.write(f"{status} Paso 2: Procesamiento IRCA")
        
        with col3:
            status = "✅" if config['estados_pasos']['paso3'] else "⚪"
            st.write(f"{status} Paso 3: Generación Reportes")
        
        # Salud del sistema
        st.markdown("---")
        self._render_system_health_detailed()
    
    def _render_logs(self):
        """Renderiza la página de logs"""
        st.header("📋 Logs del Sistema")
        
        logs_data = self.optional_controller.get_logs_summary()
        
        # Resumen de logs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Logs", logs_data['total_logs'])
        
        with col2:
            st.metric("Validaciones Fotos", logs_data['photo_validations'])
        
        with col3:
            st.metric("Ejecuciones Flujo", logs_data['workflow_executions'])
        
        with col4:
            st.write("**Última Actividad:**")
            st.write(logs_data['last_activity'])
        
        # Tabla de logs recientes
        if logs_data['recent_logs']:
            st.subheader("📜 Logs Recientes")
            
            logs_df = pd.DataFrame(logs_data['recent_logs'])
            st.dataframe(logs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay logs disponibles")
        
        # Acciones de logs
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpiar Logs de Fotos"):
                if self.optional_controller.reset_photo_validations():
                    st.success("Logs de validación de fotos limpiados")
                    st.rerun()
                else:
                    st.error("Error al limpiar logs")
        
        with col2:
            if st.button("💾 Exportar Configuración"):
                config_export = self.optional_controller.export_configuration()
                st.json(config_export)
    
    def _render_power_bi_dashboard(self):
        """Renderiza el dashboard de Power BI embebido"""
        st.markdown("---")
        st.subheader("📊 Dashboard IRCA - Power BI")
        
        # Iframe de Power BI
        power_bi_iframe = """
        <iframe 
            title="DASHBOARD IRCA AEROCIVIL" 
            width="100%" 
            height="600" 
            src="https://app.powerbi.com/view?r=eyJrIjoiMzE3NDAzYTgtYmIwYi00NGM1LTg1MDgtMDc3MmQ3M2NlYTI1IiwidCI6ImE1YjMzYzBiLTA2NTItNDU2MC1iOTcyLTRiZDAyMTcyZDY1NSJ9" 
            frameborder="0" 
            allowFullScreen="true">
        </iframe>
        """
        
        # Renderizar el iframe
        components.html(power_bi_iframe, height=620)
        
        # Información adicional
        st.info("💡 Dashboard personalizado de Power BI con análisis avanzado de datos IRCA")
        
        # Botón para abrir en nueva pestaña
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.link_button(
                "🔗 Abrir Dashboard en Nueva Pestaña",
                "https://app.powerbi.com/view?r=eyJrIjoiMzE3NDAzYTgtYmIwYi00NGM1LTg1MDgtMDc3MmQ3M2NlYTI1IiwidCI6ImE1YjMzYzBiLTA2NTItNDU2MC1iOTcyLTRiZDAyMTcyZDY1NSJ9",
                use_container_width=True
            )
    
    def _render_system_health(self):
        """Renderiza resumen de salud del sistema"""
        st.subheader("🏥 Salud del Sistema")
        
        health = self.optional_controller.validate_system_health()
        
        if health['overall_healthy']:
            st.success(health['status'])
        else:
            st.error(health['status'])
            
            # Mostrar issues
            st.write("**Problemas detectados:**")
            for issue in health['issues']:
                st.write(f"• {issue}")
    
    def _render_system_health_detailed(self):
        """Renderiza salud del sistema detallada"""
        st.subheader("🔍 Verificación Detallada del Sistema")
        
        health = self.optional_controller.validate_system_health()
        
        # Checks individuales
        checks_df = pd.DataFrame([
            {"Verificación": "Rutas Críticas", "Estado": "✅ OK" if health['checks']['rutas_criticas'] else "❌ Error"},
            {"Verificación": "Scripts Disponibles", "Estado": "✅ OK" if health['checks']['scripts_disponibles'] else "❌ Error"},
            {"Verificación": "Datos Accesibles", "Estado": "✅ OK" if health['checks']['datos_accesibles'] else "❌ Error"},
            {"Verificación": "Permisos Escritura", "Estado": "✅ OK" if health['checks']['permisos_escritura'] else "❌ Error"}
        ])
        
        st.dataframe(checks_df, use_container_width=True, hide_index=True)
        
        # Recomendaciones
        if health['recommendations']:
            st.subheader("💡 Recomendaciones")
            for rec in health['recommendations']:
                st.info(f"• {rec}")
    
    def _show_folder_picker(self) -> str:
        """
        Muestra un folder picker nativo del sistema operativo
        
        Returns:
            str: Ruta de la carpeta seleccionada, o None si se cancela
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Crear ventana raíz de tkinter (oculta)
            root = tk.Tk()
            root.withdraw()  # Ocultar la ventana principal
            root.wm_attributes('-topmost', 1)  # Poner el diálogo al frente
            
            # Mostrar diálogo de selección de carpeta
            folder_path = filedialog.askdirectory(
                title="📁 Seleccionar Carpeta para Reportes IRCA",
                initialdir=str(Path.home() / "Desktop")  # Empezar en el escritorio
            )
            
            # Limpiar ventana tkinter
            root.destroy()
            
            return folder_path if folder_path else None
            
        except ImportError:
            st.error("❌ Tkinter no está disponible. Use el input de texto manual.")
            return None
        except Exception as e:
            st.error(f"❌ Error abriendo folder picker: {str(e)}")
            return None

# Función principal para ejecutar la aplicación
def run_app():
    """Función principal para ejecutar la aplicación Streamlit"""
    ui = StreamlitUI()
    ui.render()
