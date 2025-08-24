import os
import requests

# Configuración
carpeta_entrada = "entrada"
carpeta_salida = "salida"
modelo = "llama3.2:latest"   # Cambia por el modelo que prefieras en Ollama (ej: llama2, gemma, mixtral, etc.)
os.makedirs(carpeta_salida, exist_ok=True)

def traducir_texto(texto: str) -> str:
    """Traduce texto del inglés al castellano usando Ollama en local."""
    if not texto.strip():
        return texto

    prompt = f"Traduce al castellano de forma natural y concisa. Mantén el sentido original y usa un lenguaje natural, No hagas comentario ni des opciones, limitate a traducir:\n\n{texto}"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": modelo,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"⚠️ Error con Ollama: {response.status_code} - {response.text}")
            return texto  # Si falla, deja el texto original

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error de conexión con Ollama: {e}")
        return texto

def es_linea_traducible(linea: str) -> bool:
    """Determina si una línea debe ser traducida."""
    linea = linea.strip()
    # No traducir: números de secuencia, timestamps, líneas vacías
    return not (linea.isdigit() or "-->" in linea or linea == "")

def procesar_srt(ruta_entrada, ruta_salida):
    """Traduce línea por línea de un archivo SRT y guarda el resultado manteniendo la estructura."""
    try:
        # Intentar diferentes codificaciones
        for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
            try:
                with open(ruta_entrada, "r", encoding=encoding) as f:
                    lineas = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"⚠️ No se pudo decodificar {ruta_entrada}")
            return

        resultado = []

        for linea in lineas:
            linea_original = linea.rstrip('\n\r')  # Preservar la línea original sin modificar

            if es_linea_traducible(linea_original):
                # Traducir solo el contenido, preservar la indentación
                texto_traducido = traducir_texto(linea_original)
                resultado.append(texto_traducido)
            else:
                # Mantener líneas no traduccibles exactamente como están
                resultado.append(linea_original)

        # Guardar archivo traducido
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write("\n".join(resultado))

    except Exception as e:
        print(f"⚠️ Error procesando {ruta_entrada}: {e}")

# Procesar todos los archivos .srt en la carpeta de entrada
if __name__ == "__main__":
    archivos_srt = [f for f in os.listdir(carpeta_entrada) if f.endswith(".srt")]

    if not archivos_srt:
        print("⚠️ No se encontraron archivos .srt en la carpeta de entrada")
    else:
        print(f"🔍 Encontrados {len(archivos_srt)} archivos SRT para traducir")

        for archivo in archivos_srt:
            ruta_in = os.path.join(carpeta_entrada, archivo)
            ruta_out = os.path.join(carpeta_salida, archivo)
            print(f"🌐 Traduciendo '{archivo}' con {modelo} en Ollama...")
            procesar_srt(ruta_in, ruta_out)
            print(f"✅ Traducción completada: {ruta_out}")
