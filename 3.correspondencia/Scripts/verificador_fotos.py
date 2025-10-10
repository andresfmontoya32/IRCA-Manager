#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# Script de verificación de existencia de fotos
# ============================================================

from pathlib import Path
import os

# Diccionario de fotos por ciudad (corregido)
fotos_por_ciudad_septiembre = {
    "Aguachica": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Aguachica\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Aguachica\202509_AP\Reg Foto\Muestras-P2.jpg",
    },
    "Armenia": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Armenia\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Armenia\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Armenia\202509_AP\Reg Foto\Muestras-P3.jpg",
        "FOTO4": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Armenia\202509_AP\Reg Foto\Muestras-P4.jpg",
    },
    "Barranquilla": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\14.Calidad agua_ACTA 2_Consorcio\202509\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\14.Calidad agua_ACTA 2_Consorcio\202509\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\14.Calidad agua_ACTA 2_Consorcio\202509\202509_AP\Reg Foto\Muestras-P3.jpg",
        "FOTO4": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\14.Calidad agua_ACTA 2_Consorcio\202509\202509_AP\Reg Foto\Muestras-P4.jpg",
    },
    "Buenaventura": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Buenaventura\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Buenaventura\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Buenaventura\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Guapi": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Guapi\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Guapi\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Guapi\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Ipiales": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Ipiales\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Ipiales\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Ipiales\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Pasto": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Pasto\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Pasto\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Pasto\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Popayan": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Popayan\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Popayan\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Popayan\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Tolu": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Tolu\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Tolu\202509_AP\Reg Foto\Muestras-P2.jpg",
    },
    "Tumaco": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Tumaco\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Tumaco\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Tumaco\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "San Andres": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\SAI\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\SAI\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\SAI\202509_AP\Reg Foto\Muestras-P3.jpg",
    },
    "Providencia": {
        "FOTO1": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Providencia\202509_AP\Reg Foto\Muestras-P1.jpg",
        "FOTO2": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Providencia\202509_AP\Reg Foto\Muestras-P2.jpg",
        "FOTO3": r"C:\Users\PAEROCIVIL\CONHYDRA SA ESP\Aerocivil - General\2. PIE\2. Hacer\12.Calidad Agua_ACTA 11\Providencia\202509_AP\Reg Foto\Muestras-P3.jpg",
    }
}

def verificar_fotos():
    """
    Verifica la existencia de todas las fotos en el diccionario
    """
    print("🔍 VERIFICACIÓN DE EXISTENCIA DE FOTOS")
    print("=" * 60)
    
    total_fotos = 0
    fotos_encontradas = 0
    fotos_no_encontradas = 0
    ciudades_problemas = []
    
    for ciudad, fotos in fotos_por_ciudad_septiembre.items():
        print(f"\n📍 Verificando {ciudad}:")
        ciudad_tiene_problemas = False
        
        for foto_tag, ruta_foto in fotos.items():
            total_fotos += 1
            img_path = Path(ruta_foto)
            
            if img_path.exists():
                print(f"   ✅ {foto_tag}: ENCONTRADA")
                fotos_encontradas += 1
            else:
                print(f"   ❌ {foto_tag}: NO ENCONTRADA")
                print(f"      Ruta: {ruta_foto}")
                fotos_no_encontradas += 1
                ciudad_tiene_problemas = True
        
        if ciudad_tiene_problemas:
            ciudades_problemas.append(ciudad)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print(f"   Total de fotos configuradas: {total_fotos}")
    print(f"   Fotos encontradas: {fotos_encontradas}")
    print(f"   Fotos NO encontradas: {fotos_no_encontradas}")
    print(f"   Porcentaje de éxito: {(fotos_encontradas/total_fotos)*100:.1f}%")
    
    if ciudades_problemas:
        print(f"\n⚠️  Ciudades con problemas:")
        for ciudad in ciudades_problemas:
            print(f"   • {ciudad}")
    else:
        print("\n🎉 ¡Todas las fotos fueron encontradas!")
    
    return fotos_encontradas == total_fotos

def verificar_ciudad_especifica(nombre_ciudad):
    """
    Verifica las fotos de una ciudad específica
    """
    if nombre_ciudad not in fotos_por_ciudad_septiembre:
        print(f"❌ La ciudad '{nombre_ciudad}' no está configurada en el diccionario.")
        return False
    
    print(f"🔍 Verificando fotos para: {nombre_ciudad}")
    print("-" * 40)
    
    fotos = fotos_por_ciudad_septiembre[nombre_ciudad]
    todas_encontradas = True
    
    for foto_tag, ruta_foto in fotos.items():
        img_path = Path(ruta_foto)
        
        if img_path.exists():
            file_size = img_path.stat().st_size
            print(f"✅ {foto_tag}: ENCONTRADA ({file_size:,} bytes)")
        else:
            print(f"❌ {foto_tag}: NO ENCONTRADA")
            print(f"   Ruta: {ruta_foto}")
            todas_encontradas = False
    
    return todas_encontradas

if __name__ == "__main__":
    print("🚀 Iniciando verificación de fotos...")
    
    # Verificar todas las ciudades
    todas_ok = verificar_fotos()
    
    if not todas_ok:
        print("\n" + "⚠️ " * 20)
        print("RECOMENDACIONES:")
        print("1. Verifica que las rutas en el diccionario sean correctas")
        print("2. Verifica que los nombres de archivos coincidan exactamente")
        print("3. Verifica que las carpetas existan")
        print("4. Ejecuta este script con una ciudad específica para más detalles")
        print("\nEjemplo: python verificar_fotos.py Armenia")
    
    # Si se pasa un argumento, verificar solo esa ciudad
    import sys
    if len(sys.argv) > 1:
        ciudad_especifica = sys.argv[1]
        print(f"\n\n🎯 VERIFICACIÓN ESPECÍFICA:")
        verificar_ciudad_especifica(ciudad_especifica) 