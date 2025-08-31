# CONDA: ia_p7
from imageai.Detection import ObjectDetection
import os
import pymongo
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

MONGO_URI = "mongodb://localhost:27017" # URI de conexión a MongoDB
DB_NAME = "album_2"  # Nombre de la base de datos
COLLECTION_NAME = "imagenes"  # Nombre de la colección

# Enable GPU usage if available (requires PyTorch with CUDA support)
USE_GPU = True

def create_detector():
    """Create a new detector instance for process safety"""
    det = ObjectDetection()
    det.setModelTypeAsYOLOv3()
    det.setModelPath("/home/nito/Documentos/desarrollo/python/modelos/yolov3.pt")
    det.loadModel()
    return det

print("Modelo YOLOv3 preparado para carga en procesos (GPU habilitado si PyTorch tiene soporte CUDA).")


def insertar_en_mongodb(_id, datos):
    """
    Inserta o actualiza datos en la colección 'imagenes' de la base de datos de MongoDB, marcando como visto=True.

    Args:
        _id (str): ID del documento en MongoDB
        datos (list): Lista de objetos detectados a insertar/actualizar
    """
    client = None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]  # Usar la colección 'imagenes'

        # Obtener fecha de procesamiento en campos separados
        now = datetime.now()
        update_data = {
            "$set": {
                "objetos_detectados": datos,
                "visto": True,
                "fecha_procesamiento_dia": now.strftime('%d'),
                "fecha_procesamiento_mes": now.strftime('%m'),
                "fecha_procesamiento_anio": now.strftime('%Y'),
                "fecha_procesamiento_hora": now.strftime('%H'),
                "fecha_procesamiento_minuto": now.strftime('%M')
            }
        }

        result = collection.update_one(
            {"_id": _id},
            update_data,
            upsert=True
        )

        if result.upserted_id is not None:
            print(f"Datos de objetos detectados añadidos al documento en MongoDB para ID: {_id}")
        elif result.modified_count > 0:
            print(f"Datos de objetos detectados actualizados en documento para ID: {_id}")
        else:
            print(f"Documento para ID {_id} ya contenía esta información.")

    except pymongo.errors.ConnectionFailure as e:
        print(f"Error de conexión a MongoDB en insertar_en_mongodb para ID {_id}: {e}")
    except Exception as e:
        print(f"Error inesperado al insertar/actualizar en MongoDB para ID {_id}: {e}")
    finally:
        if client:
            client.close()


def verificar_imagen_procesada(_id):
    """
    Verifica si la imagen ya ha sido procesada (campo 'visto' es True).

    Args:
        _id (str): ID del documento en MongoDB

    Returns:
        bool: True si ya está procesada (visto = True), False en caso contrario
    """
    client = None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        doc = collection.find_one({"_id": _id})
        if doc and doc.get("visto") == True:
            return True
        return False

    except pymongo.errors.ConnectionFailure as e:
        print(f"Error de conexión a MongoDB en verificar_imagen_procesada para ID {_id}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al verificar imagen procesada para ID {_id}: {e}")
        return False
    finally:
        if client:
            client.close()




def detectar_objetos(ruta_imagen):
    objetos = []
    """
    Detecta objetos en una imagen utilizando ImageAI.
    Args:
        ruta_imagen (str): Ruta de la imagen a procesar
    """
    det = create_detector()  # Create detector instance per process

    try:
        detections = det.detectObjectsFromImage(
            input_image=ruta_imagen,
            minimum_percentage_probability=30
        )

    except FileNotFoundError:
        print(f"Error en detectar_objetos: Archivo no encontrado - {ruta_imagen}")
        return []
    except Exception as e:
        print(f"Error inesperado durante la detección de objetos para {ruta_imagen}: {e}")
        return None  # Indicate detection error

    if detections is None:
        return None # Indicate detection error

    for eachObject in detections:
        # print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] ) # Reduce verbosity
        print("--------------------------------")
        objeto_detectado = eachObject["name"]
        porcentaje = eachObject["percentage_probability"]
        coordenadas = eachObject["box_points"]
        datos_a_insertar = {
            "objeto_detectado": objeto_detectado,
            "porcentaje": porcentaje,
            "coordenadas": coordenadas
        }
        objetos.append(datos_a_insertar)
    return objetos


def actualizar_campo_visto_mongodb(_id):
    """
    Actualiza el documento en la colección 'imagenes' marcando 'visto' como True.
    Se usa cuando la detección de objetos falla o no encuentra objetos.

    Args:
        _id (str): ID del documento en MongoDB
    """
    client = None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]  # Usar la colección 'imagenes'

        # Obtener fecha de procesamiento en campos separados
        now = datetime.now()
        update_data = {
            "$set": {
                "visto": True,
                "fecha_procesamiento_dia": now.strftime('%d'),
                "fecha_procesamiento_mes": now.strftime('%m'),
                "fecha_procesamiento_anio": now.strftime('%Y'),
                "fecha_procesamiento_hora": now.strftime('%H'),
                "fecha_procesamiento_minuto": now.strftime('%M')
            },
            "$setOnInsert": {
                "objetos_detectados": []  # Añadir lista vacía si es un nuevo documento
            }
        }

        result = collection.update_one(
            {"_id": _id},
            update_data,
            upsert=True
        )

        if result.upserted_id is not None:
             print(f"Documento creado y marcado como 'visto'=True en MongoDB para ID: {_id}")
        elif result.modified_count > 0:
             print(f"Documento marcado como 'visto'=True en MongoDB para ID: {_id}")
        else:
             print(f"Documento para ID {_id} ya estaba marcado como 'visto'=True.")

    except pymongo.errors.ConnectionFailure as e:
        print(f"Error de conexión a MongoDB en actualizar_campo_visto_mongodb para ID {_id}: {e}")
    except Exception as e:
        print(f"Error inesperado al actualizar documento en MongoDB para ID {_id}: {e}")
    finally:
        if client:
            client.close()

def obtener_ruta_imagenes_mongodb():
    listado_archivos = []
    """
    Conecta a MongoDB y obtiene la lista de archivos en la colección.
    
    Returns:
        list: Lista de archivos en la colección
    """
    listado_archivos = [] # Initialize the list here
    client = None # Initialize client to None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Obtener solo los documentos que NO han sido procesados (visto != True)
        archivos = list(collection.find({"visto": {"$ne": True}}))

        for archivo in archivos:
            listado_archivos.append(archivo)
            # Convertir ObjectId a string para evitar problemas de serialización
        return listado_archivos # Return inside the try block after successful fetch

    except pymongo.errors.ConnectionFailure as e:
        print(f"Error de conexión a MongoDB en obtener_ruta_imagenes_mongodb: {e}")
        return [] # Return empty list on connection error
    except Exception as e:
        print(f"Error inesperado al obtener rutas de MongoDB: {e}")
        return [] # Return empty list on other errors
    finally:
        if client:
            client.close() # Ensure client is closed


def procesar_archivo(archivo, processed_count, error_count, skipped_count):
    """
    Worker function to process a single file using multiprocessing.
    Returns (result): 'success' or 'error' or 'skipped'
    """
    try:
        # Verificar si las claves existen antes de acceder
        if 'ruta_completa' not in archivo or '_id' not in archivo:
            print(f"Advertencia: Documento incompleto encontrado, saltando: {archivo}")
            return 'error'

        ruta_imagen = archivo["ruta_completa"]
        _id = archivo["_id"]
        if ruta_imagen.upper().endswith((".JPG", ".JPEG", ".PNG", ".GIF", ".BMP", ".TIFF", ".WEBP")):
            # Comprobar si el archivo de imagen existe físicamente
            if not os.path.exists(ruta_imagen):
                print(f"Error: El archivo de imagen no existe en la ruta: {ruta_imagen} (ID: {_id}). Saltando.")
                return 'error'

            # Note: Using ruta_completa from new database structure
            # Verificar si la imagen ya ha sido procesada
            if verificar_imagen_procesada(_id):
                print(f"Imagen ya procesada (visto = True), saltando: {ruta_imagen} (ID: {_id})")
                return 'skipped'

            print(f"Procesando imagen: {ruta_imagen} (ID: {_id})")
            # Procesar objeto de detección y guardar en colección 'imagenes'
            objetos_detectados = detectar_objetos(ruta_imagen)

            if objetos_detectados is not None:  # Detection successful (objects or no objects)
                if objetos_detectados:
                    print(f"Detectados {len(objetos_detectados)} objetos para ID: {_id}")
                    insertar_en_mongodb(_id, objetos_detectados)
                    return 'success'
                else:
                    print(f"No se detectaron objetos (o hubo un error en detección) para: {ruta_imagen} (ID: {_id})")
                    actualizar_campo_visto_mongodb(_id) # Mark as visto
                    return 'error'
            else:
                print(f"Error en la detección de objetos para: {ruta_imagen} (ID: {_id})")
                actualizar_campo_visto_mongodb(_id) # Mark as visto even on detection error
                return 'error'
    except KeyError as e:
        print(f"Error: Clave faltante en el documento de MongoDB: {e}. Documento: {archivo}")
        return 'error'
    except Exception as e:
        print(f"Error inesperado procesando el archivo {archivo.get('ruta_completa', 'N/A')} (ID: {archivo.get('_id', 'N/A')}): {e}")
        return 'error'


if __name__ == "__main__":
    try:
        print("Iniciando proceso de detección de objetos...")
        listado_archivos = obtener_ruta_imagenes_mongodb()

        if not listado_archivos:
            print("No se encontraron archivos en MongoDB para procesar o hubo un error al obtenerlos.")
        else:
            print(f"Se encontraron {len(listado_archivos)} archivos para procesar.")
            processed_count = 0
            error_count = 0
            skipped_count = 0

            # Usar ProcessPoolExecutor para procesamiento paralelo con 3 procesos simultáneos
            with ProcessPoolExecutor(max_workers=3) as executor:
                # Enviar tareas al executor
                future_to_archivo = {executor.submit(procesar_archivo, archivo, processed_count, error_count, skipped_count): archivo for archivo in listado_archivos}

                # Procesar resultados
                for future in as_completed(future_to_archivo):
                    try:
                        result = future.result()
                        if result == 'success':
                            processed_count += 1
                        elif result == 'error':
                            error_count += 1
                        elif result == 'skipped':
                            skipped_count += 1
                    except Exception as e:
                        print(f"Error en el procesamiento paralelo: {e}")
                        error_count += 1

            print("\n--- Resumen del Proceso ---")
            print(f"Imágenes procesadas (con objetos detectados e insertados): {processed_count}")
            print(f"Errores encontrados (archivo no existe, documento incompleto, error detección/inserción): {error_count}")
            print(f"Imágenes saltadas (visto = True, ya procesadas): {skipped_count}")

    except Exception as e:
        print(f"Error general en la ejecución principal: {e}")

    print("\nProceso completado.")
