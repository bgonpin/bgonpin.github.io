"""
Script para redimensionar imágenes de una carpeta ORIGINALES
y guardarlas optimizadas en la carpeta MODIFICADAS

Este script procesa automáticamente todas las imágenes en formato JPG, JPEG, PNG, BMP,
TIFF, TIF y WEBP de la carpeta ORIGINALES, las redimensiona a 1024px de ancho
manteniendo la proporción original, y las guarda en la carpeta MODIFICADAS con
optimización para web.

Características principales:
- Redimensionado proporcional con ancho fijo de 1024px
- Optimización automática para web (calidad 85%, JPEG progresivo)
- Conversión a RGB para compatibilidad
- Informe detallado del procesamiento con estadísticas de reducción
- Manejo de errores robusto con mensajes descriptivos

Autor: Benito González Piñeiro
Fecha de creación: Agosto 2025
Versión: 1.0
"""

import os
from PIL import Image
import sys

def crear_carpeta_modificadas():
    """
    Crea la carpeta MODIFICADAS si no existe.

    Esta función verifica si existe la carpeta 'MODIFICADAS' en el directorio
    actual. Si no existe, la crea automáticamente y muestra un mensaje de
    confirmación.

    Returns:
        None

    Side effects:
        - Crea la carpeta 'MODIFICADAS' si no existe
        - Imprime mensaje en consola si se crea la carpeta
    """
    if not os.path.exists("MODIFICADAS"):
        os.makedirs("MODIFICADAS")
        print("Carpeta MODIFICADAS creada")

def es_imagen(archivo):
    """
    Verifica si el archivo es una imagen con extensión soportada.

    Esta función evalúa la extensión del archivo para determinar si es un
    tipo de imagen compatible con el script. Las extensiones válidas incluyen
    formatos comunes de imagen digital.

    Args:
        archivo (str): Nombre del archivo a verificar (con extensión)

    Returns:
        bool: True si el archivo tiene una extensión de imagen soportada,
              False en caso contrario

    Extensiones soportadas:
        - .jpg, .jpeg: JPEG/JFIF
        - .png: Portable Network Graphics
        - .bmp: Bitmap
        - .tiff, .tif: Tagged Image File Format
        - .webp: WebP
    """
    extensiones_validas = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    return archivo.lower().endswith(extensiones_validas)

def redimensionar_imagen(ruta_origen, nombre_archivo):
    """
    Redimensiona una imagen manteniendo la proporción original.

    Esta función toma una imagen de la ruta especificada, la redimensiona a un
    ancho fijo de 1024 píxeles manteniendo la proporción original, la optimiza
    para web y la guarda en la carpeta MODIFICADAS. También muestra estadísticas
    detalladas del procesamiento.

    Args:
        ruta_origen (str): Ruta completa del archivo de imagen original
        nombre_archivo (str): Nombre del archivo de imagen (sin ruta)

    Returns:
        None

    Características del procesamiento:
        - Ancho fijo: 1024 píxeles
        - Alto proporcional calculado automáticamente
        - Conversión a RGB si es necesario
        - Algoritmo de remuestreo: LANCZOS (alta calidad)
        - Formato de salida: JPEG optimizado
        - Calidad: 85% (balance entre tamaño y calidad)
        - Optimización: activada
        - JPEG progresivo: activado

    Side effects:
        - Crea archivo en la carpeta MODIFICADAS
        - Imprime información del procesamiento en consola
        - Maneja errores y muestra mensajes descriptivos

    Raises:
        Exception: Si ocurre un error durante el procesamiento de la imagen
    """
    try:
        # Abrir la imagen original
        with Image.open(ruta_origen) as img:
            # Convertir a RGB si es necesario (para PNG con transparencia, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Obtener dimensiones originales
            ancho_original, alto_original = img.size
            
            # Calcular nuevo alto manteniendo la proporción
            ancho_nuevo = 1024
            alto_nuevo = int((alto_original * ancho_nuevo) / ancho_original)
            
            # Redimensionar la imagen
            img_redimensionada = img.resize((ancho_nuevo, alto_nuevo), Image.Resampling.LANCZOS)
            
            # Crear nombre del archivo de salida
            nombre_base = os.path.splitext(nombre_archivo)[0]
            nombre_salida = f"{nombre_base}_1024.jpg"
            ruta_salida = os.path.join("MODIFICADAS", nombre_salida)
            
            # Guardar la imagen con calidad reducida para web
            img_redimensionada.save(
                ruta_salida,
                "JPEG",
                quality=85,  # Calidad del 85% - buena para web
                optimize=True,  # Optimiza el archivo
                progressive=True  # JPEG progresivo para carga web
            )
            
            # Mostrar información del procesamiento
            tamaño_original = os.path.getsize(ruta_origen)
            tamaño_nuevo = os.path.getsize(ruta_salida)
            reduccion = ((tamaño_original - tamaño_nuevo) / tamaño_original) * 100
            
            print(f"✓ {nombre_archivo} -> {nombre_salida}")
            print(f"  Dimensiones: {ancho_original}x{alto_original} -> {ancho_nuevo}x{alto_nuevo}")
            print(f"  Tamaño: {tamaño_original/1024:.1f}KB -> {tamaño_nuevo/1024:.1f}KB ({reduccion:.1f}% reducción)")
            print()
            
    except Exception as e:
        print(f"❌ Error procesando {nombre_archivo}: {str(e)}")

def procesar_imagenes():
    """
    Función principal que coordina el procesamiento completo de imágenes.

    Esta función orquesta todo el proceso de redimensionado de imágenes:
    1. Verifica la existencia de la carpeta ORIGINALES
    2. Crea la carpeta MODIFICADAS si no existe
    3. Busca y filtra archivos de imagen válidos
    4. Procesa cada imagen individualmente
    5. Muestra estadísticas del procesamiento completo

    Returns:
        bool: True si el procesamiento se completó exitosamente,
              False si ocurrió algún error o no se encontraron imágenes

    Estructura del proceso:
        - Verificación de carpetas
        - Filtrado de archivos por extensión
        - Procesamiento individual de cada imagen
        - Reporte de estadísticas finales

    Side effects:
        - Imprime mensajes informativos en consola
        - Crea la carpeta MODIFICADAS si no existe
        - Procesa y guarda imágenes redimensionadas
        - Muestra estadísticas de procesamiento
    """
    # Verificar que existe la carpeta ORIGINALES
    if not os.path.exists("ORIGINALES"):
        print("❌ Error: No se encontró la carpeta 'ORIGINALES'")
        print("Asegúrate de que la carpeta existe y contiene imágenes")
        return False
    
    # Crear carpeta de destino
    crear_carpeta_modificadas()
    
    # Obtener lista de archivos en ORIGINALES
    archivos = os.listdir("ORIGINALES")
    imagenes = [archivo for archivo in archivos if es_imagen(archivo)]
    
    if not imagenes:
        print("❌ No se encontraron imágenes en la carpeta ORIGINALES")
        print("Formatos soportados: JPG, JPEG, PNG, BMP, TIFF, WEBP")
        return False
    
    print(f"📁 Encontradas {len(imagenes)} imágenes para procesar")
    print("=" * 60)
    
    # Procesar cada imagen
    imagenes_procesadas = 0
    for imagen in imagenes:
        ruta_origen = os.path.join("ORIGINALES", imagen)
        redimensionar_imagen(ruta_origen, imagen)
        imagenes_procesadas += 1
    
    print("=" * 60)
    print(f"✅ Procesamiento completado: {imagenes_procesadas} imágenes redimensionadas")
    print(f"📂 Imágenes guardadas en la carpeta 'MODIFICADAS'")
    
    return True

if __name__ == "__main__":
    print("🖼️  Script de Redimensionado de Imágenes")
    print("Redimensiona imágenes a 1024px de ancho manteniendo proporción")
    print()
    
    # Verificar que PIL está instalado
    try:
        from PIL import Image
    except ImportError:
        print("❌ Error: La librería Pillow no está instalada")
        print("Instálala con: pip install Pillow")
        sys.exit(1)
    
    # Ejecutar el procesamiento
    if procesar_imagenes():
        print("🎉 ¡Proceso completado con éxito!")
    else:
        print("❌ El proceso terminó con errores")
        sys.exit(1)
