#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Automatización IRCA - Calidad del Agua por Aeropuerto
================================================================

Automatiza la actualización de datos técnicos de calidad del agua usando
el índice IRCA (Índice de Riesgo de la Calidad del Agua) para múltiples aeropuertos.

Autor: andres montoya el practicante
Versión: 2.0 Simplificada
"""

import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import calendar

class IRCAAutomationSystem:
    """
    Sistema simplificado de automatización para actualización de datos IRCA
    """
    
    def __init__(self, base_path: str, irca_file: str):
        self.base_path = Path(base_path)
        self.irca_file = Path(irca_file)
        self.irca_data = None
        self.irca_dict = {}
        
        # Etiquetas válidas según especificaciones (nro como primera, clasificaciones agregadas)
        self.etiquetas_validas = {
            'nro', 'periodo', 'mes', 'año', 'pto_1', 'pto_2', 'pto_3', 'pto_4', 
            'fecha_mu', 'dia_mu', 'cod_1', 'cod_2', 'cod_3', 'cod_4',
            'irca_pto_1', 'irca_pto_2', 'irca_pto_3', 'irca_pto_4',
            'clasificacion_riesgo_1', 'clasificacion_riesgo_2', 'clasificacion_riesgo_3', 'clasificacion_riesgo_4'
        }
        
        # Orden específico para las etiquetas (nro primero, clasificaciones después de sus IRCAs)
        self.orden_etiquetas = [
            'nro', 'periodo', 'mes', 'año', 'pto_1', 'pto_2', 'pto_3', 'pto_4', 
            'fecha_mu', 'dia_mu', 'cod_1', 'cod_2', 'cod_3', 'cod_4',
            'irca_pto_1', 'clasificacion_riesgo_1',
            'irca_pto_2', 'clasificacion_riesgo_2',
            'irca_pto_3', 'clasificacion_riesgo_3',
            'irca_pto_4', 'clasificacion_riesgo_4'
        ]

    def clasificar_irca(self, irca: float) -> dict:
        """
        Retorna la clasificación de riesgo y su descripción según el valor de IRCA.

        Clasificación:
        - 1: Sin Riesgo (0 - 5)
        - 2: Bajo (5.1 - 14)
        - 3: Medio (14.1 - 35)
        - 4: Alto (35.1 - 80)
        - 5: Inviable Sanitamente (80.1 - 100)

        Parámetros:
            irca (float): Valor numérico del IRCA (%)

        Retorna:
            dict: {"clasificacion": int, "nivel": str}
        """
        if irca < 0 or irca > 100:
            return {"clasificacion": 0, "nivel": "Valor Inválido"}

        if 0 <= irca <= 5:
            return {"clasificacion": 1, "nivel": "Sin Riesgo"}
        elif 5 < irca <= 14:
            return {"clasificacion": 2, "nivel": "Bajo"}
        elif 14 < irca <= 35:
            return {"clasificacion": 3, "nivel": "Medio"}
        elif 35 < irca <= 80:
            return {"clasificacion": 4, "nivel": "Alto"}
        else:  # 80 < irca <= 100
            return {"clasificacion": 5, "nivel": "Inviable Sanitamente"}

    def obtener_nro(self, ciudad: str, mes: str) -> int:
        """
        Calcula el valor de 'nro' a partir de la ciudad y el mes dado.

        Junio es el mes base:
        - Barranquilla tiene un valor base de 10 en junio.
        - Las demás ciudades tienen un valor base de 25 en junio.

        Parámetros:
            ciudad (str): Nombre de la ciudad, e.g. "Barranquilla", "Popayán"
            mes (str): Nombre del mes en minúscula, e.g. "junio", "agosto"

        Retorna:
            int: valor entero correspondiente a 'nro' para la ciudad y mes indicados.
        """
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        if mes.lower() not in meses:
            # Si el mes no está en la lista, devolver valor por defecto
            mes = "junio"
        
        indice_junio = meses.index("junio")
        indice_mes = meses.index(mes.lower())
        diferencia = indice_mes - indice_junio

        # Normalizar nombre de ciudad para comparación
        ciudad_normalizada = self.normalizar_nombre_ciudad(ciudad)
        base = 10 if "barranquilla" in ciudad_normalizada.lower() else 25
        return base + diferencia

    def cargar_datos_irca(self) -> bool:
        """Carga los datos del archivo IRCA(%).xlsx"""
        try:
            self.irca_data = pd.read_excel(self.irca_file)
            # Crear diccionario para búsqueda rápida
            self.irca_dict = dict(zip(
                self.irca_data['Codigo'].astype(str),
                self.irca_data['IRCA (%)']
            ))
            return True
        except Exception as e:
            print(f"Error cargando datos IRCA: {str(e)}")
            return False

    def obtener_carpetas_ciudades(self) -> List[Path]:
        """Obtiene lista de carpetas que corresponden a ciudades"""
        return [item for item in self.base_path.iterdir() if item.is_dir()]

    def encontrar_archivo_base(self, carpeta_ciudad: Path) -> Optional[Path]:
        """Encuentra el archivo Base_ciudad.xlsx en la carpeta especificada"""
        patron = re.compile(r'^Base_.*\.xlsx$', re.IGNORECASE)
        
        for archivo in carpeta_ciudad.iterdir():
            if archivo.is_file() and patron.match(archivo.name):
                return archivo
        return None

    def buscar_irca_por_codigo(self, codigo: str) -> Optional[float]:
        """Busca el valor IRCA para un código específico"""
        valor_bruto = self.irca_dict.get(str(codigo))
        if valor_bruto is not None:
            return self.convertir_a_porcentaje(valor_bruto)
        return None

    def obtener_datos_ciudad_desde_irca(self, nombre_ciudad: str) -> Dict:
        """Obtiene los datos específicos de una ciudad desde el archivo IRCA, mapeando por número de punto."""
        datos_ciudad = {
            'codigos_encontrados': [],
            'puntos_muestreo': [],
            'valores_irca': [],
            'mes': '',
            'año': '',
            'fecha_mu': '',
            'dia_mu': '',
            'puntos_dict': {}  # Nuevo: mapeo por número de punto
        }
        
        # Normalizar nombre de ciudad para búsqueda
        nombre_normalizado = self.normalizar_nombre_ciudad(nombre_ciudad)
        
        # Filtrar datos por ciudad
        mask_ciudad = self.irca_data['Ciudad'].str.upper().str.contains(
            nombre_normalizado.upper(), na=False, regex=False
        )
        datos_ciudad_irca = self.irca_data[mask_ciudad]
        
        if not datos_ciudad_irca.empty:
            # Tomar el registro más reciente
            datos_recientes = datos_ciudad_irca.sort_values('Fecha', ascending=False).iloc[0]
            
            # Extraer información temporal
            if pd.notna(datos_recientes['Fecha']):
                fecha = pd.to_datetime(datos_recientes['Fecha'])
                datos_ciudad['fecha_mu'] = fecha.strftime('%Y-%m-%d')
                # Convertir mes a nombre textual
                meses = {
                    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
                }
                datos_ciudad['mes'] = meses[fecha.month]
                datos_ciudad['año'] = fecha.strftime('%Y')
                datos_ciudad['dia_mu'] = self.formatear_fecha_textual(fecha)
            
            # Obtener todos los puntos de muestreo para esta ciudad
            for _, row in datos_ciudad_irca.iterrows():
                if pd.notna(row['Codigo']) and pd.notna(row['Punto de Muestreo']):
                    codigo = str(row['Codigo'])
                    punto = str(row['Punto de Muestreo'])
                    valor_irca = self.convertir_a_porcentaje(row['IRCA (%)'])
                    datos_ciudad['codigos_encontrados'].append(codigo)
                    datos_ciudad['puntos_muestreo'].append(punto)
                    datos_ciudad['valores_irca'].append(valor_irca)
                    # Detectar número de punto (p1, p2, p3, p4, 01, 02, etc.)
                    match = re.search(r'(?:^|[^a-zA-Z])p(?:to)?[_\- ]?([1-4]|0[1-4])', punto, re.IGNORECASE)
                    if match:
                        num = match.group(1)
                        # Normalizar a 1-4
                        num_norm = str(int(num))
                        datos_ciudad['puntos_dict'][num_norm] = {
                            'codigo': codigo,
                            'punto': punto,
                            'irca': valor_irca
                        }
        return datos_ciudad

    def formatear_fecha_textual(self, fecha: pd.Timestamp) -> str:
        """Convierte una fecha a formato textual en español"""
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        
        dia = fecha.day
        mes = meses[fecha.month]
        año = fecha.year
        
        return f"{dia} de {mes} de {año}"

    def convertir_a_porcentaje(self, valor_irca) -> float:
        """Convierte el valor IRCA al formato de porcentaje correcto"""
        if pd.isna(valor_irca):
            return 0.0
        
        valor = float(valor_irca)
        
        # Si el valor está entre 0 y 1, probablemente es decimal (0.48)
        if 0 <= valor <= 1:
            return valor * 100
        
        return valor

    def normalizar_nombre_ciudad(self, nombre: str) -> str:
        """Normaliza el nombre de la ciudad para búsquedas más flexibles"""
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        
        nombre_normalizado = nombre.lower()
        for original, reemplazo in reemplazos.items():
            nombre_normalizado = nombre_normalizado.replace(original, reemplazo)
        
        return nombre_normalizado

    def calcular_periodo_mes(self, mes: str, año: str) -> str:
        """Calcula el periodo de días para el mes y año dados"""
        meses = {
            '01': 'enero', '1': 'enero', 'enero': 'enero',
            '02': 'febrero', '2': 'febrero', 'febrero': 'febrero',
            '03': 'marzo', '3': 'marzo', 'marzo': 'marzo',
            '04': 'abril', '4': 'abril', 'abril': 'abril',
            '05': 'mayo', '5': 'mayo', 'mayo': 'mayo',
            '06': 'junio', '6': 'junio', 'junio': 'junio',
            '07': 'julio', '7': 'julio', 'julio': 'julio',
            '08': 'agosto', '8': 'agosto', 'agosto': 'agosto',
            '09': 'septiembre', '9': 'septiembre', 'septiembre': 'septiembre',
            '10': 'octubre', 'octubre': 'octubre',
            '11': 'noviembre', 'noviembre': 'noviembre',
            '12': 'diciembre', 'diciembre': 'diciembre'
        }
        
        mes_num = mes
        if mes not in meses:
            try:
                mes_num = str(int(mes)).zfill(2)
            except:
                mes_num = mes
        nombre_mes = meses.get(mes, meses.get(mes_num, mes))
        try:
            ultimo_dia = calendar.monthrange(int(año), int(mes_num))[1]
        except:
            ultimo_dia = 30
        return f"1 de {nombre_mes} al {ultimo_dia} de {nombre_mes} de {año}"

    def validar_y_actualizar_tags(self, df_tags: pd.DataFrame, ciudad: str) -> pd.DataFrame:
        """Valida y actualiza la hoja TAGS con los valores IRCA, mapeando por número de punto."""
        
        # Asegurar que el DataFrame tenga las columnas necesarias
        if 'ETIQUETA' not in df_tags.columns or 'VALOR' not in df_tags.columns:
            df_tags = pd.DataFrame(columns=['ETIQUETA', 'VALOR'])
        
        # Crear un diccionario para manejo más fácil
        tags_dict = dict(zip(df_tags['ETIQUETA'], df_tags['VALOR']))
        
        # Obtener datos específicos de la ciudad desde IRCA
        datos_ciudad = self.obtener_datos_ciudad_desde_irca(ciudad)
        
        # Aplicar datos automáticos basados en la ciudad
        if datos_ciudad['mes']:
            tags_dict['mes'] = datos_ciudad['mes']
            # Calcular nro automáticamente usando la ciudad y el mes
            tags_dict['nro'] = self.obtener_nro(ciudad, datos_ciudad['mes'])
        
        if datos_ciudad['año']:
            tags_dict['año'] = datos_ciudad['año']
        
        if datos_ciudad['fecha_mu']:
            tags_dict['fecha_mu'] = datos_ciudad['fecha_mu']
            
        if 'dia_mu' in datos_ciudad and datos_ciudad['dia_mu']:
            tags_dict['dia_mu'] = datos_ciudad['dia_mu']

        # Calcular y asignar periodo si mes y año están presentes
        if 'mes' in tags_dict and 'año' in tags_dict and tags_dict['mes'] and tags_dict['año']:
            tags_dict['periodo'] = self.calcular_periodo_mes(tags_dict['mes'], tags_dict['año']).upper()

        # Asignar automáticamente códigos y puntos de muestreo encontrados usando el mapeo por número
        for i in range(1, 5):
            num_str = str(i)
            cod_key = f'cod_{i}'
            pto_key = f'pto_{i}'
            irca_key = f'irca_pto_{i}'
            punto_info = datos_ciudad.get('puntos_dict', {}).get(num_str)
            if punto_info:
                tags_dict[cod_key] = punto_info['codigo']
                tags_dict[pto_key] = punto_info['punto']
                tags_dict[irca_key] = punto_info['irca']
        
        # Procesar códigos restantes (si existen códigos manuales en los TAGS)
        for i in range(1, 5):
            cod_key = f'cod_{i}'
            irca_key = f'irca_pto_{i}'
            if cod_key in tags_dict and pd.notna(tags_dict[cod_key]) and tags_dict[cod_key] != '':
                codigo = str(tags_dict[cod_key])
                # Solo buscar si no está ya en puntos_dict
                if not any(p['codigo'] == codigo for p in datos_ciudad.get('puntos_dict', {}).values()):
                    valor_irca = self.buscar_irca_por_codigo(codigo)
                    if valor_irca is not None:
                        tags_dict[irca_key] = valor_irca
        
        # 🔧 NUEVO: Calcular clasificaciones de riesgo automáticamente
        for i in range(1, 5):
            irca_key = f'irca_pto_{i}'
            clasificacion_key = f'clasificacion_riesgo_{i}'
            
            # Si existe el valor IRCA y no está vacío
            if irca_key in tags_dict and tags_dict[irca_key] != '' and pd.notna(tags_dict[irca_key]):
                try:
                    valor_irca = float(tags_dict[irca_key])
                    clasificacion = self.clasificar_irca(valor_irca)
                    # Usar el nombre textual de la clasificación ("Sin Riesgo", "Bajo", etc.)
                    tags_dict[clasificacion_key] = clasificacion['nivel']
                except (ValueError, TypeError):
                    # Si hay error en la conversión, dejar vacío
                    tags_dict[clasificacion_key] = ''
            else:
                # Si no hay valor IRCA, dejar clasificación vacía
                tags_dict[clasificacion_key] = ''
        
        # Asegurar que todas las etiquetas válidas existan
        for etiqueta in self.etiquetas_validas:
            if etiqueta not in tags_dict:
                tags_dict[etiqueta] = ''
        
        # Convertir de vuelta a DataFrame con orden específico (nro primero)
        datos_ordenados = []
        for etiqueta in self.orden_etiquetas:
            if etiqueta in tags_dict:
                datos_ordenados.append({'ETIQUETA': etiqueta, 'VALOR': tags_dict[etiqueta]})
        
        # Agregar cualquier etiqueta adicional que no esté en el orden predefinido
        for etiqueta, valor in tags_dict.items():
            if etiqueta not in self.orden_etiquetas:
                datos_ordenados.append({'ETIQUETA': etiqueta, 'VALOR': valor})
        
        df_resultado = pd.DataFrame(datos_ordenados)
        
        return df_resultado

    def procesar_aeropuerto(self, carpeta_ciudad: Path) -> bool:
        """Procesa un aeropuerto específico"""
        ciudad = carpeta_ciudad.name
        
        # Encontrar archivo Base_ciudad.xlsx
        archivo_base = self.encontrar_archivo_base(carpeta_ciudad)
        if not archivo_base:
            print(f"❌ {ciudad}: Archivo Base_ciudad.xlsx no encontrado")
            return False
        
        # Leer hoja TAGS
        try:
            df_tags = pd.read_excel(archivo_base, sheet_name='TAGS')
        except Exception as e:
            print(f"❌ {ciudad}: Error leyendo hoja TAGS: {str(e)}")
            return False
        
        # Validar y actualizar TAGS
        df_actualizado = self.validar_y_actualizar_tags(df_tags, ciudad)
        
        # Guardar archivo actualizado usando método más robusto
        try:
            # Leer todas las hojas existentes primero
            hojas_existentes = {}
            try:
                xl_file = pd.ExcelFile(archivo_base)
                for sheet_name in xl_file.sheet_names:
                    if sheet_name != 'TAGS':  # No leer TAGS, la vamos a reemplazar
                        hojas_existentes[sheet_name] = pd.read_excel(archivo_base, sheet_name=sheet_name)
            except Exception as e:
                print(f"⚠️ {ciudad}: Advertencia leyendo hojas existentes: {str(e)}")
            
            # Escribir todas las hojas (incluyendo TAGS actualizada)
            with pd.ExcelWriter(archivo_base, engine='openpyxl') as writer:
                # Escribir hoja TAGS actualizada
                df_actualizado.to_excel(writer, sheet_name='TAGS', index=False)
                
                # Escribir hojas existentes
                for sheet_name, df_sheet in hojas_existentes.items():
                    df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"✅ {ciudad}: Procesado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ {ciudad}: Error guardando archivo: {str(e)}")
            import traceback
            print(f"   Detalle del error: {traceback.format_exc()}")
            return False

    def ejecutar_procesamiento(self) -> bool:
        """Ejecuta el procesamiento completo de todos los aeropuertos"""
        print("=== INICIANDO PROCESAMIENTO IRCA ===")
        
        # Cargar datos IRCA
        if not self.cargar_datos_irca():
            print("❌ No se pudieron cargar los datos IRCA")
            return False
        
        # Obtener carpetas de ciudades
        carpetas_ciudades = self.obtener_carpetas_ciudades()
        if not carpetas_ciudades:
            print("❌ No se encontraron carpetas de ciudades")
            return False
        
        # Procesar cada aeropuerto
        total_aeropuertos = len(carpetas_ciudades)
        aeropuertos_exitosos = 0
        
        print(f"📁 Procesando {total_aeropuertos} aeropuertos...")
        
        for i, carpeta in enumerate(carpetas_ciudades, 1):
            print(f"\n[{i}/{total_aeropuertos}] {carpeta.name}")
            
            if self.procesar_aeropuerto(carpeta):
                aeropuertos_exitosos += 1
        
        # Resumen final
        print(f"\n=== RESUMEN FINAL ===")
        print(f"Total aeropuertos: {total_aeropuertos}")
        print(f"Procesados exitosamente: {aeropuertos_exitosos}")
        print(f"Con errores: {total_aeropuertos - aeropuertos_exitosos}")
        
        return aeropuertos_exitosos > 0

def main():
    """Función principal del script"""
    
    # Configuración de rutas
    BASE_PATH = r"C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\3.correspondencia\Datos"
    IRCA_FILE = r"C:\Users\PAEROCIVIL\Desktop\Automatizacion\AUTOMATIZACION\3.correspondencia\Datos\IRCA(%).xlsx"
    
    print("Sistema de Automatización IRCA - Versión Simplificada")
    print("=" * 55)
    
    # Validar rutas antes de iniciar
    if not Path(BASE_PATH).exists():
        print(f"❌ Ruta base no existe: {BASE_PATH}")
        return False
    
    if not Path(IRCA_FILE).exists():
        print(f"❌ Archivo IRCA no existe: {IRCA_FILE}")
        return False
    
    # Inicializar y ejecutar sistema
    sistema = IRCAAutomationSystem(BASE_PATH, IRCA_FILE)
    exito = sistema.ejecutar_procesamiento()
    
    if exito:
        print("\n✅ Procesamiento completado exitosamente")
    else:
        print("\n❌ Procesamiento completado con errores")
    
    return exito

if __name__ == "__main__":
    main()
