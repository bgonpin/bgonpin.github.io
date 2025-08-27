import ollama
import base64
from PIL import Image
import io
import os

ruta = "./imagenes/"
modelo = "gemma3:12b"  # Modelo a elegir

def encode_image_to_base64(image_path):    
    """
    Codifica una imagen a formato base64 para enviarla a Ollama.
    
    Args:
        image_path (str): Ruta completa a la imagen que se desea codificar.
        
    Returns:
        str or None: Cadena codificada en base64 de la imagen, o None si ocurre un error.
        
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de imagen en la ruta especificada.
        Exception: Si ocurre algún otro error durante el procesamiento de la imagen.
    """
    try:
        with Image.open(image_path) as img:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")  # Puedes usar JPEG o PNG
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de imagen en la ruta: {image_path}")
        return None
    except Exception as e:
        print(f"Ocurrió un error al procesar la imagen: {e}")
        return None

def main():
    """
    Función principal que procesa todas las imágenes de la carpeta especificada.
    
    Esta función:
    - Verifica la existencia de la carpeta de imágenes
    - Recorre todas las imágenes en la carpeta (y subcarpetas)
    - Codifica cada imagen a base64
    - Envía las imágenes a Ollama para análisis
    - Guarda las descripciones generadas en un archivo de texto
    
    Returns:
        None
    """
    print("Iniciando el análisis de imágenes con Ollama...")
    
    # Verificar si la carpeta de imágenes existe
    if not os.path.exists(ruta):
        print(f"Error: No se encontró la carpeta: {ruta}")
        return
    
    for root, dirs, files in os.walk(ruta):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(root, file)
                print(f"Procesando imagen: {image_path}")

                # Prompt para el análisis de la imagen
                prompt = "Describe detalladamente la imagen. Limitate a describir la imagen. No hagas suposiciones."

                # Codifica la imagen y prepara los mensajes para Ollama
                encoded_image = encode_image_to_base64(image_path)

                if encoded_image:
                    messages = [
                        {
                            'role': 'user',
                            'content': prompt,
                            'images': [encoded_image]  # Aquí se pasa la imagen codificada
                        }
                    ]
                
                    print("Enviando la imagen a Ollama para su análisis...")
                    try:
                        response = ollama.chat(
                            model=modelo,  # Corregido: eliminada la asignación incorrecta
                            messages=messages
                        )

                        # Muestra la descripción generada
                        description = response['message']['content']
                        print("\nDescripción de la imagen:")
                        print("------------------------")
                        print(description)
                        
                        # Guarda la descripción en un archivo
                        with open("descripciones_ollama.txt", "a", encoding="utf-8") as f:
                            f.write(f"Imagen: {file}\nDescripción: {description}\n\n")
                        print("\nDescripción guardada en 'descripciones_ollama.txt'\n")

                    except Exception as e:
                        print(f"Ocurrió un error al comunicarse con Ollama: {e}")
                        print("Asegúrate de que el servidor de Ollama esté en ejecución y que el modelo 'llava' esté descargado.")
                else:
                    print(f"No se pudo procesar la imagen: {file}")

if __name__ == "__main__":
    main()
