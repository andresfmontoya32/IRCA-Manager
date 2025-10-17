#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador para funciones opcionales del sistema IRCA
"""

from typing import Tuple, Dict, Any, List
import streamlit as st
from datetime import datetime

from ..models.photo_validator_model import PhotoValidatorModel
from ..config.settings import settings

class OptionalController:
    """
    Controlador para funciones opcionales independientes del flujo principal
    """
    
    def __init__(self):
        self.photo_validator = PhotoValidatorModel()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Inicializa variables de estado de Streamlit para funciones opcionales"""
        if 'optional_state' not in st.session_state:
            st.session_state.optional_state = {
                'photo_validations': [],
                'last_validation': None,
                'config_changes': []
            }
    
    def validate_photos(self, ciudad_especifica: str = None) -> Tuple[bool, str]:
        """
        Valida existencia de fotos
        
        Args:
            ciudad_especifica: Si se especifica, valida solo esa ciudad
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            success, message = self.photo_validator.execute(ciudad_especifica)
            
            # Registrar validación
            validation_record = {
                'timestamp': datetime.now(),
                'ciudad': ciudad_especifica or "Todas",
                'success': success,
                'message': message,
                'details': self.photo_validator.get_status_info()
            }
            
            st.session_state.optional_state['photo_validations'].append(validation_record)
            st.session_state.optional_state['last_validation'] = validation_record
            
            return success, message
            
        except Exception as e:
            return False, f"❌ Error en validación de fotos: {str(e)}"
    
    def get_photo_validation_status(self) -> Dict[str, Any]:
        """Obtiene estado de la validación de fotos"""
        status_info = self.photo_validator.get_status_info()
        last_validation = st.session_state.optional_state.get('last_validation')
        
        return {
            'status': status_info,
            'last_validation': last_validation,
            'validation_history': st.session_state.optional_state['photo_validations'],
            'available_cities': self.photo_validator.get_available_cities()
        }
    
    def get_system_configuration(self) -> Dict[str, Any]:
        """Obtiene información de configuración del sistema"""
        errores_validacion = settings.validar_rutas()
        
        return {
            'rutas_validas': len(errores_validacion) == 0,
            'errores_validacion': errores_validacion,
            'rutas_configuradas': {
                'scripts_dir': str(settings.SCRIPTS_DIR),
                'datos_dir': str(settings.DATOS_DIR),
                'plantillas_dir': str(settings.PLANTILLAS_DIR),
                'irca_file': str(settings.IRCA_FILE),
                'origen_dir': str(settings.ORIGEN_DIR)
            },
            'estados_pasos': {
                'paso1': settings.get_paso_status('paso1'),
                'paso2': settings.get_paso_status('paso2'),
                'paso3': settings.get_paso_status('paso3')
            },
            'aeropuertos_configurados': settings.AEROPUERTOS,
            'carpetas_datos': settings.get_carpetas_datos()
        }
    
    def get_logs_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de logs del sistema"""
        # Obtener logs de validación de fotos
        photo_logs = []
        for validation in st.session_state.optional_state['photo_validations']:
            photo_logs.append({
                'timestamp': validation['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'action': f"Validación fotos - {validation['ciudad']}",
                'status': "✅ Éxito" if validation['success'] else "❌ Error",
                'details': validation['message']
            })
        
        # Obtener logs del workflow si existe
        workflow_logs = []
        if 'workflow_state' in st.session_state:
            for execution in st.session_state.workflow_state.get('execution_history', []):
                workflow_logs.append({
                    'timestamp': execution['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'action': f"Ejecución {execution['step']}",
                    'status': "✅ Éxito" if execution['success'] else "❌ Error",
                    'details': execution['message'],
                    'duration': f"{execution['duration']:.1f}s"
                })
        
        # Combinar y ordenar logs
        all_logs = photo_logs + workflow_logs
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'total_logs': len(all_logs),
            'photo_validations': len(photo_logs),
            'workflow_executions': len(workflow_logs),
            'recent_logs': all_logs[:50],  # Últimos 50 logs
            'last_activity': all_logs[0]['timestamp'] if all_logs else "Sin actividad"
        }
    
    def reset_photo_validations(self) -> bool:
        """Resetea historial de validaciones de fotos"""
        try:
            st.session_state.optional_state['photo_validations'] = []
            st.session_state.optional_state['last_validation'] = None
            self.photo_validator.status = "not_executed"
            return True
        except Exception:
            return False
    
    def export_configuration(self) -> Dict[str, Any]:
        """Exporta configuración actual del sistema"""
        config = self.get_system_configuration()
        photo_status = self.get_photo_validation_status()
        logs = self.get_logs_summary()
        
        return {
            'exported_at': datetime.now().isoformat(),
            'system_config': config,
            'photo_validation_status': photo_status,
            'logs_summary': logs,
            'version': "1.0"
        }
    
    def validate_system_health(self) -> Dict[str, Any]:
        """Realiza verificación completa de salud del sistema"""
        health_checks = {
            'rutas_criticas': True,
            'scripts_disponibles': True,
            'datos_accesibles': True,
            'permisos_escritura': True
        }
        
        issues = []
        
        # Verificar rutas críticas
        errores_rutas = settings.validar_rutas()
        if errores_rutas:
            health_checks['rutas_criticas'] = False
            issues.extend(errores_rutas)
        
        # Verificar scripts
        scripts_requeridos = [
            'generador_base_script.py',
            'rellenador_tags.py',
            'Correspondencia.py',
            'verificador_fotos.py'
        ]
        
        for script in scripts_requeridos:
            script_path = settings.SCRIPTS_DIR / script
            if not script_path.exists():
                health_checks['scripts_disponibles'] = False
                issues.append(f"Script faltante: {script}")
        
        # Verificar acceso a datos
        try:
            if settings.IRCA_FILE.exists():
                import pandas as pd
                df = pd.read_csv(settings.IRCA_FILE, sep=';')
                if len(df) == 0:
                    health_checks['datos_accesibles'] = False
                    issues.append("Archivo IRCA está vacío")
            else:
                health_checks['datos_accesibles'] = False
                issues.append("Archivo IRCA no accesible")
        except Exception as e:
            health_checks['datos_accesibles'] = False
            issues.append(f"Error leyendo IRCA: {str(e)}")
        
        # Verificar permisos de escritura
        try:
            test_file = settings.DATOS_DIR / '.write_test'
            test_file.touch()
            test_file.unlink()
        except Exception:
            health_checks['permisos_escritura'] = False
            issues.append("Sin permisos de escritura en carpeta Datos")
        
        overall_health = all(health_checks.values())
        
        return {
            'overall_healthy': overall_health,
            'status': "🟢 Sistema Saludable" if overall_health else "🔴 Problemas Detectados",
            'checks': health_checks,
            'issues': issues,
            'recommendations': self._get_health_recommendations(issues)
        }
    
    def _get_health_recommendations(self, issues: List[str]) -> List[str]:
        """Genera recomendaciones basadas en problemas encontrados"""
        recommendations = []
        
        for issue in issues:
            if "Script faltante" in issue:
                recommendations.append("Verificar que todos los scripts estén en la carpeta Scripts/")
            elif "IRCA" in issue:
                recommendations.append("Verificar archivo IRCA(%).csv en carpeta Datos/")
            elif "permisos" in issue:
                recommendations.append("Ejecutar como administrador o verificar permisos de carpeta")
            elif "ruta" in issue.lower():
                recommendations.append("Verificar configuración de rutas en settings.py")
        
        if not recommendations:
            recommendations.append("Sistema funcionando correctamente")
        
        return list(set(recommendations))  # Remover duplicados
