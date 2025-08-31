# CONDA: album_mcp
"""
Script para alimentar una base de datos MongoDB con metadatos de imágenes.

Este módulo procesa imágenes de un directorio específico, extrae metadatos
como dimensiones, fecha de creación, coordenadas GPS y dirección geocodificada,
y los almacena en una colección de MongoDB usando el hash SHA512 del archivo
como identificador único.
"""

import os
import sys
import exifread
import requests
import pymongo
from datetime import datetime
import hashlib
from PIL import Image

# Constante para el directorio a escanear
DIRECTORY = '/mnt/local/datos/PROYCTO_ALBUM_SEMANTICO/IMAGENES'  # Cambia esta ruta por la deseada
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "album_2"
COLLECTION_NAME = "imagenes"

# Conexión a MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_file_hash(file_path):
    """
    Calcula el hash SHA512 del archivo para identificar duplicados.

    Args:
        file_path (str): Ruta completa al archivo de imagen.

    Returns:
        str or None: Hash SHA512 en formato hexadecimal, o None si ocurre un error.
    """
    hash_obj = hashlib.sha512()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None

def get_image_metadata(file_path):
    """
    Extrae metadatos básicos de la imagen usando PIL.

    Args:
        file_path (str): Ruta completa al archivo de imagen.

    Returns:
        dict or None: Diccionario con metadatos de la imagen incluyendo:
            - nombre_archivo: Nombre del archivo
            - ruta_completa: Ruta completa del archivo
            - ancho: Ancho de la imagen en píxeles
            - alto: Alto de la imagen en píxeles
            - fecha_creacion: Timestamp de modificación del archivo
            - coordenadas: None (se completa posteriormente con GPS)
            - direccion: None (se completa posteriormente con geocodificación)
            - fecha_procesamiento: Timestamp del momento del procesamiento
            Retorna None si ocurre un error al procesar la imagen.
    """
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            fecha_dt = datetime.fromtimestamp(os.path.getmtime(file_path))
            fecha_proc_dt = datetime.now()
            return {
                'nombre_archivo': os.path.basename(file_path),
                'ruta_completa': file_path,
                'ancho': width,
                'alto': height,
                'fecha_creacion_dia': fecha_dt.strftime('%d'),
                'fecha_creacion_mes': fecha_dt.strftime('%m'),
                'fecha_creacion_anio': fecha_dt.strftime('%Y'),
                'fecha_creacion_hora': fecha_dt.strftime('%H'),
                'fecha_creacion_minuto': fecha_dt.strftime('%M'),
                'coordenadas': None,
                'direccion': None,
                'fecha_procesamiento_dia': fecha_proc_dt.strftime('%d'),
                'fecha_procesamiento_mes': fecha_proc_dt.strftime('%m'),
                'fecha_procesamiento_anio': fecha_proc_dt.strftime('%Y'),
                'fecha_procesamiento_hora': fecha_proc_dt.strftime('%H'),
                'fecha_procesamiento_minuto': fecha_proc_dt.strftime('%M')
            }
    except Exception as e:
        print(f"Error extrayendo metadatos de {file_path}: {e}")
        return None

def dms_to_decimal(dms, ref):
    """
    Convierte coordenadas del formato DMS (grados, minutos, segundos) a formato decimal.

    Args:
        dms: Tupla con tres valores FRS (Fractional Rational String) representando
             grados, minutos y segundos de las coordenadas GPS.
        ref (str): Referencia de dirección ('N', 'S', 'E', 'W').

    Returns:
        float: Coordenadas en formato decimal. Negativas para 'S' y 'W'.
    """
    degrees = dms[0].num / dms[0].den
    minutes = dms[1].num / dms[1].den
    seconds = dms[2].num / dms[2].den
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def reverse_geocode(lat, lon):
    """
    Realiza geocodificación inversa usando la API de Nominatim (OpenStreetMap).

    Args:
        lat (float): Latitud en formato decimal.
        lon (float): Longitud en formato decimal.

    Returns:
        str or None: Dirección correspondiente a las coordenadas, o None si falla.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
    headers = {'User-Agent': 'image_gps_extractor'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('display_name')
    else:
        return None

def get_gps_location(file_path):
    """
    Procesa una imagen para extraer información GPS y actualizar la base de datos.

    Calcula el hash del archivo, verifica si ya existe en la base de datos,
    extrae coordenadas GPS de los metadatos EXIF, las geocodifica a direcciones,
    y actualiza el documento en MongoDB. Si el documento no existe, lo crea primero
    con metadatos básicos.

    Args:
        file_path (str): Ruta completa al archivo de imagen a procesar.

    Returns:
        None: No retorna valores, actualiza la base de datos directamente.

    Raises:
        Exception: Se maneja internamente imprimiendo mensajes de error.
    """
    try:
        hash_value = get_file_hash(file_path)
        if not hash_value:
            print(f"Error calculando hash para {file_path}")
            return

        # Buscar documento por hash
        document = collection.find_one({'_id': hash_value})
        if not document:
            # Insertar nuevo documento
            metadata = get_image_metadata(file_path)
            if metadata:
                metadata['_id'] = hash_value
                metadata['hash_sha512'] = hash_value
                try:
                    collection.insert_one(metadata)
                    document = metadata
                    print(f"Documento insertado: {file_path}")
                except Exception as e:
                    print(f"Error insertando documento: {e}")
                    return
            else:
                print(f"No se pudo obtener metadatos para insertar: {file_path}")
                return

        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        update_data = {}

        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            lat_tag = tags['GPS GPSLatitude']
            lon_tag = tags['GPS GPSLongitude']
            lat_ref = str(tags['GPS GPSLatitudeRef'])
            lon_ref = str(tags['GPS GPSLongitudeRef'])
            lat = dms_to_decimal(lat_tag.values, lat_ref)
            lon = dms_to_decimal(lon_tag.values, lon_ref)

            address = reverse_geocode(lat, lon)

            update_data['coordenadas'] = [lat, lon]
            if address:
                update_data['direccion_os'] = address
            else:
                update_data['direccion_os'] = None

            print(f"Actualizado {file_path} con GPS")
        else:
            print(f"Sin GPS: {file_path}")
            # Si no hay GPS, mantener campo null

        # Siempre actualizar fecha_procesamiento con campos separados
        now = datetime.now()
        update_data['fecha_procesamiento_dia'] = now.strftime('%d')
        update_data['fecha_procesamiento_mes'] = now.strftime('%m')
        update_data['fecha_procesamiento_anio'] = now.strftime('%Y')
        update_data['fecha_procesamiento_hora'] = now.strftime('%H')
        update_data['fecha_procesamiento_minuto'] = now.strftime('%M')

        collection.update_one({'_id': hash_value}, {'$set': update_data})

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")

def main():
    """
    Función principal que escanea el directorio definido y procesa todas las imágenes.

    Escanea recursivamente el directorio DIRECTORY en busca de archivos de imagen
    con extensiones válidas (jpg, jpeg, png, tiff, bmp), y para cada imagen encontrada
    ejecuta el procesamiento completo: extracción de metadatos, GPS y actualización
    en la base de datos MongoDB.

    Returns:
        None: No retorna valores, imprime información de progreso en consola.

    Raises:
        SystemExit: Si el directorio especificado en DIRECTORY no existe.
    """
    dir_path = DIRECTORY
    if not os.path.isdir(dir_path):
        print("El directorio no existe.")
        sys.exit(1)

    print(f"Procesando directorio: {dir_path}\n")

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            ext = file.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
                path = os.path.join(root, file)
                print(f"Procesando: {path}")
                get_gps_location(path)

if __name__ == "__main__":
    main()
