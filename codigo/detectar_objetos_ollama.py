import ollama
import base64
import json
import re
from pathlib import Path
from typing import List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import signal
from contextlib import contextmanager

TAMAÑO_MAXIMO_IMAGEN_KB = 512  # 1 MB

@contextmanager
def timeout_context(seconds):
    """Context manager for timeout handling"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Tiempo de espera agotado después de {seconds} segundos")

    # Set the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Cancel the alarm
        signal.alarm(0)

class ObjectDetector:
    def __init__(self, model_name: str = "gemma3:4b"):
        """
        Inicializa el detector de objetos con Ollama
        
        Args:
            model_name: Nombre del modelo de Ollama a usar (por defecto: llava)
        """
        self.model_name = model_name
        self._verify_model()
    
    def _verify_model(self):
        """Verifica que el modelo esté disponible en Ollama"""
        try:
            models = ollama.list()
            available_models = []
            if 'models' in models:
                for model in models['models']:
                    if isinstance(model, dict) and 'name' in model:
                        available_models.append(model['name'])

            if self.model_name not in available_models:
                print(f"Advertencia: El modelo '{self.model_name}' no está instalado.")
                print(f"Para instalarlo, ejecuta: ollama pull {self.model_name}")
                print("Modelos disponibles:", available_models)

        except Exception as e:
            print(f"Error al verificar modelos: {e}")
    
    def _encode_image(self, image_path: str) -> str:
        """
        Codifica una imagen en base64
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            String con la imagen codificada en base64
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró la imagen: {image_path}")
        except Exception as e:
            raise Exception(f"Error al codificar la imagen: {e}")
    
    def _extract_objects_from_response(self, response_text: str) -> List[str]:
        """
        Extrae la lista de objetos de la respuesta del modelo

        Args:
            response_text: Texto de respuesta del modelo

        Returns:
            Lista de objetos detectados
        """
        # Método simple: dividir por comas y limpiar
        objects = [obj.strip(' .,;:!?-"\'()[]{}') for obj in response_text.split(',')]

        # Filtrar objetos válidos (más de 1 caracter, no vacíos)
        cleaned_objects = []
        seen = set()

        for obj in objects:
            obj = obj.lower()
            if obj and len(obj) > 1 and obj not in seen:
                cleaned_objects.append(obj)
                seen.add(obj)

        return cleaned_objects
    
    def detect_objects(self, image_path: str, prompt_language: str = "es") -> List[str]:
        """
        Detecta objetos en una imagen usando Ollama
        
        Args:
            image_path: Ruta a la imagen
            prompt_language: Idioma del prompt ("es" para español, "en" para inglés)
            
        Returns:
            Lista de objetos detectados en la imagen
        """
        # Verificar que existe la imagen
        if not Path(image_path).exists():
            raise FileNotFoundError(f"La imagen {image_path} no existe")
        
        # Codificar imagen
        try:
            image_base64 = self._encode_image(image_path)
        except Exception as e:
            raise Exception(f"Error al procesar la imagen: {e}")
        
        # Crear prompt según el idioma
        if prompt_language == "es":
            prompt = """Analiza esta imagen y proporciona una lista de todos los objetos que puedes identificar.
            IMPORTANTE: Responde ÚNICAMENTE con una lista de objetos en ESPAÑOL separados por comas, por ejemplo:
            mesa, silla, computadora, taza, libro

            No incluyas descripciones adicionales ni palabras en inglés, solo los nombres de los objetos en español."""
        else:
            prompt = """Analyze this image and provide a list of all objects you can identify.
            Respond ONLY with a comma-separated list of objects, for example:
            table, chair, computer, cup, book
            
            Do not include additional descriptions, just the object names."""
        
        try:
            # Llamar a Ollama
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                images=[image_base64]
            )

            response_text = response['response']

            # Extraer objetos de la respuesta
            objects = self._extract_objects_from_response(response_text)

            return objects

        except Exception as e:
            raise Exception(f"Error al procesar con Ollama: {e}")
    
    def detect_objects_detailed(self, image_path: str) -> dict:
        """
        Detecta objetos con información adicional
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Diccionario con objetos y respuesta completa
        """
        objects = self.detect_objects(image_path)
        
        return {
            "objects": objects,
            "total_objects": len(objects),
            "image_path": image_path
        }

def connect_to_mongodb():
    """Conecta a MongoDB"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        # Test the connection
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa")
        return client
    except ConnectionFailure:
        print("Error al conectar a MongoDB. Asegúrate de que MongoDB esté ejecutándose.")
        return None

def process_images_from_database():
    """Procesa imágenes desde la base de datos MongoDB"""

    # Conectar a MongoDB
    client = connect_to_mongodb()
    if not client:
        return

    # Acceder a la base de datos y colección
    db = client['album']
    collection = db['imagenes_2']

    # Inicializar detector
    detector = ObjectDetector()

    try:
        # Buscar imágenes no procesadas (objeto_procesado no existe o es false)
        query = {
            "$or": [
                {"objeto_procesado": {"$exists": False}},
                {"objeto_procesado": False}
            ]
        }

        images_to_process = collection.find(query)

        processed_count = 0

        for image_doc in images_to_process:
            image_path = image_doc.get('ruta')

            if not image_path:
                print(f"Documento sin campo 'ruta': {image_doc.get('_id')}")
                continue

            # Verificar tamaño de la imagen usando el campo 'peso' de la base de datos
            image_size_kb = image_doc.get('peso', 0)
            if image_size_kb > TAMAÑO_MAXIMO_IMAGEN_KB:
                print(f"Imagen demasiado grande ({image_size_kb:.1f} KB > {TAMAÑO_MAXIMO_IMAGEN_KB} KB): {image_path}")
                # Saltar por ahora, se procesará cuando se incremente el límite
                continue

            print(f"Procesando imagen: {image_path}")

            try:
                # Detectar objetos con timeout de 40 segundos
                with timeout_context(40):
                    objects = detector.detect_objects(image_path)

                # Actualizar documento en MongoDB
                update_data = {
                    "objetos": objects,
                    "objeto_procesado": True
                }

                collection.update_one(
                    {"_id": image_doc["_id"]},
                    {"$set": update_data}
                )

                print(f"Procesada: {image_path} - Objetos encontrados: {len(objects)}")
                processed_count += 1

            except FileNotFoundError:
                print(f"Imagen no encontrada: {image_path}")
                # Marcar como procesada aunque no se encontró la imagen
                collection.update_one(
                    {"_id": image_doc["_id"]},
                    {"$set": {"objeto_procesado": True}}
                )
            except TimeoutError as e:
                print(f"Timeout procesando {image_path}: {e}")
                # Marcar como procesada aunque excedió el tiempo límite
                collection.update_one(
                    {"_id": image_doc["_id"]},
                    {"$set": {"objeto_procesado": True}}
                )
            except Exception as e:
                print(f"Error procesando {image_path}: {e}")
                # Marcar como procesada aunque hubo error
                collection.update_one(
                    {"_id": image_doc["_id"]},
                    {"$set": {"objeto_procesado": True}}
                )

        print(f"\nProcesamiento completado. Imágenes procesadas: {processed_count}")

    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
    finally:
        client.close()

def main():
    """Función principal para procesar imágenes desde MongoDB"""

    process_images_from_database()

if __name__ == "__main__":
    main()
