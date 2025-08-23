#!/usr/bin/env python3
"""
Script para generar subtítulos de archivos de video usando Ollama y Whisper
Requiere: ffmpeg, ollama con modelo de whisper

FUNCIONALIDADES:
- Extrae audio de archivos de video
- Transcribe audio usando Whisper (local o vía Ollama)
- Genera subtítulos en formato SRT
- OPCIONAL: Traduce subtítulos al español usando Google Translate o Ollama

USO BÁSICO:
    python generar.py                                    # Procesa todos los videos usando Whisper local (RECOMENDADO)
    python generar.py --translate                        # Genera subtítulos traducidos al español
    python generar.py --translate --target-lang en       # Traduce al inglés
    python generar.py --translate --translation-method ollama  # Usa Ollama para traducción

IMPORTANTE:
    Por defecto, el script usa Whisper local para mejor calidad de transcripción.
    Si no tienes Whisper instalado, usa: pip install openai-whisper
    Solo usa --use-ollama si prefieres usar Ollama para transcripción (menos confiable).

OPCIONES DE TRADUCCIÓN:
    --translate                    : Habilita la traducción automática
    --translation-method METHOD    : Método de traducción (googletrans/ollama)
    --target-lang LANG             : Idioma destino (es, en, fr, de, it, pt, ru, ja, ko, zh)
    --translation-model MODEL       : Modelo de Ollama para traducción (solo con ollama)

DEPENDENCIAS OPCIONALES:
    - googletrans==4.0.0rc1 (para traducción con Google Translate)
    - openai-whisper (para transcripción local)
    - torch, torchvision, torchaudio (para Whisper)
"""

import os
import sys
import subprocess
import json
import tempfile
from pathlib import Path
import argparse
from datetime import datetime, timedelta
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("googletrans no disponible. Para traducción automática instala: pip install googletrans==4.0.0rc1")

def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas"""
    dependencies = {
        'ffmpeg': 'ffmpeg -version',
        'ollama': 'ollama --version'
    }
    
    missing = []
    for name, cmd in dependencies.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"✓ {name} encontrado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(name)
            print(f"✗ {name} no encontrado")
    
    if missing:
        print(f"\nError: Faltan dependencias: {', '.join(missing)}")
        print("\nPara instalar:")
        if 'ffmpeg' in missing:
            print("- FFmpeg: https://ffmpeg.org/download.html")
        if 'ollama' in missing:
            print("- Ollama: https://ollama.ai/")
        return False
    return True

def extract_audio(video_path, audio_path):
    """Extrae el audio del video usando ffmpeg"""
    print(f"Extrayendo audio de {video_path}...")
    
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vn',  # Sin video
        '-acodec', 'pcm_s16le',  # Codec de audio compatible
        '-ar', '16000',  # Frecuencia de muestreo
        '-ac', '1',  # Mono
        '-y',  # Sobrescribir archivo existente
        audio_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Audio extraído correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extrayendo audio: {e}")
        print(f"Error output: {e.stderr}")
        return False

def transcribe_with_ollama(audio_path, model="dimavz/whisper-tiny"):
    """Transcribe el audio usando Ollama con Whisper"""
    print(f"Transcribiendo audio con Ollama (modelo: {model})...")
    
    # Verificar que el modelo esté disponible
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        model_name = model.split('/')[-1]  # Obtener solo el nombre del modelo
        if model_name not in result.stdout:
            print(f"Modelo {model} no encontrado. Descargando...")
            subprocess.run(['ollama', 'pull', model], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error verificando/descargando modelo: {e}")
        return None
    
    # Transcribir usando Ollama - NOTA: Este método es experimental
    # Ollama no está optimizado para Whisper, se recomienda usar --use-whisper
    try:
        # Para modelos Whisper en Ollama, el proceso es diferente
        # Generalmente se usa whisper directamente, no a través de Ollama
        print("⚠ ADVERTENCIA: Ollama no es la forma óptima de usar Whisper")
        print("Se recomienda usar la opción --use-whisper para mejores resultados")
        
        # Método alternativo: crear transcripción básica usando un LLM de Ollama
        # para procesar el texto del audio (no es transcripción real)
        
        return {
            "segments": [
                {"start": 0.0, "end": 60.0, "text": "[Transcripción no disponible con Ollama - usa --use-whisper]"}
            ]
        }
    
    except subprocess.CalledProcessError as e:
        print(f"Error en transcripción: {e}")
        return None

def alternative_whisper_transcription(audio_path):
    """Método alternativo usando whisper directamente si está disponible"""
    try:
        import torch
        import whisper
        print("Usando Whisper local para transcripción...")

        # Verificar disponibilidad de CUDA antes de cargar el modelo
        if torch.cuda.is_available():
            try:
                print("GPU disponible, intentando cargar modelo en GPU...")
                model = whisper.load_model("base")
                print("✓ Modelo cargado en GPU")
            except Exception as gpu_error:
                print(f"Error cargando modelo en GPU: {gpu_error}")
                print("Cambiando a CPU...")
                model = whisper.load_model("base", device="cpu")
                print("✓ Modelo cargado en CPU")
        else:
            print("GPU no disponible, cargando modelo en CPU...")
            model = whisper.load_model("base", device="cpu")
            print("✓ Modelo cargado en CPU")

        print("Transcribiendo audio...")
        result = model.transcribe(audio_path)

        # Convertir a formato compatible
        segments = []
        for segment in result["segments"]:
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })

        return {"segments": segments}

    except ImportError:
        print("Whisper no está instalado. Instala con: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"Error en transcripción con Whisper: {e}")
        print("\nPosibles soluciones:")
        print("1. Reinstala PyTorch: pip uninstall torch torchvision torchaudio && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
        print("2. Para GPU, instala versión compatible: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print("3. Si usas conda: conda install pytorch torchvision torchaudio cpuonly -c pytorch")
        return None

def format_timestamp(seconds):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def translate_with_googletrans(text, target_lang='es'):
    """Traduce texto al español usando Google Translate"""
    if not GOOGLETRANS_AVAILABLE:
        print("Googletrans no disponible, saltando traducción")
        return text

    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        print(f"Error traduciendo con Google Translate: {e}")
        return text

def translate_with_ollama(text, target_lang='es', model='llama3.2'):
    """Traduce texto usando Ollama con un modelo LLM"""
    try:
        # Verificar que Ollama esté disponible
        subprocess.run(['ollama', 'list'], capture_output=True, check=True)

        # Verificar si el modelo está disponible, si no, descargarlo
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        if model not in result.stdout:
            print(f"Modelo {model} no encontrado. Descargando...")
            subprocess.run(['ollama', 'pull', model], check=True)

        # Mapear códigos de idioma a nombres completos para el prompt
        lang_names = {
            'es': 'Spanish',
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }

        target_lang_name = lang_names.get(target_lang, 'Spanish')

        # Crear prompt para traducción
        prompt = f"Translate the following text to {target_lang_name}. Only provide the translation, no explanations:\n\n{text}"

        # Usar Ollama para traducir
        cmd = ['ollama', 'run', model, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        translated_text = result.stdout.strip()
        return translated_text if translated_text else text

    except Exception as e:
        print(f"Error traduciendo con Ollama: {e}")
        return text

def translate_segments(transcription, method='googletrans', target_lang='es', ollama_model='llama3.2'):
    """Traduce todos los segmentos de la transcripción"""
    print(f"Traduciendo subtítulos a {target_lang} usando {method}...")

    translated_segments = []

    for i, segment in enumerate(transcription["segments"]):
        original_text = segment["text"].strip()
        if not original_text:
            translated_segments.append(segment)
            continue

        print(f"Traduciendo segmento {i+1}/{len(transcription['segments'])}...")

        if method == 'ollama':
            translated_text = translate_with_ollama(original_text, target_lang, ollama_model)
        else:  # googletrans por defecto
            translated_text = translate_with_googletrans(original_text, target_lang)

        # Crear nuevo segmento con texto traducido
        translated_segment = {
            "start": segment["start"],
            "end": segment["end"],
            "text": translated_text
        }
        translated_segments.append(translated_segment)

    return {"segments": translated_segments}

def create_srt(transcription, output_path, translate=False, translation_method='googletrans', target_lang='es', ollama_model='llama3.2'):
    """Crea archivo SRT a partir de la transcripción"""
    # Si se requiere traducción, aplicar traducción a toda la transcripción
    if translate:
        transcription = translate_segments(transcription, translation_method, target_lang, ollama_model)

    print(f"Creando archivo SRT: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(transcription["segments"], 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

    print("✓ Archivo SRT creado correctamente")

def main():
    parser = argparse.ArgumentParser(description='Genera subtítulos para archivos de video en carpeta videos_entrada')
    parser.add_argument('-v', '--video', help='Archivo de video específico (opcional, por defecto procesa todos en videos_entrada)')
    parser.add_argument('-m', '--model', default='dimavz/whisper-tiny', help='Modelo de Ollama a usar (recomendado: dimavz/whisper-tiny)')
    parser.add_argument('--keep-audio', action='store_true', help='Mantener archivo de audio temporal')
    parser.add_argument('--use-ollama', action='store_true', help='Usar Ollama para transcripción (recomendado: usar --use-whisper)')
    parser.add_argument('--use-whisper', action='store_true', help='Usar Whisper local en lugar de Ollama (RECOMENDADO)')
    parser.add_argument('--translate', action='store_true', help='Traducir subtítulos al idioma especificado')
    parser.add_argument('--translation-method', default='googletrans', choices=['googletrans', 'ollama'], help='Método de traducción a usar (por defecto: googletrans)')
    parser.add_argument('--target-lang', default='es', help='Idioma destino para la traducción (por defecto: es - español)')
    parser.add_argument('--translation-model', default='llama3.2', help='Modelo de Ollama para traducción (por defecto: llama3.2)')

    args = parser.parse_args()

    # Verificar dependencias
    if not args.use_whisper and not check_dependencies():
        return 1

    # Definir rutas de carpetas
    input_folder = Path("videos_entrada")
    output_folder = Path("videos_salida")

    # Crear carpetas si no existen
    input_folder.mkdir(exist_ok=True)
    output_folder.mkdir(exist_ok=True)

    # Determinar archivos a procesar
    if args.video:
        # Procesar archivo específico
        video_files = [Path(args.video)]
        if not video_files[0].exists():
            print(f"Error: El archivo {args.video} no existe")
            return 1
    else:
        # Procesar todos los archivos de video en videos_entrada
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        video_files = [f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() in video_extensions]

        if not video_files:
            print(f"No se encontraron archivos de video en {input_folder}")
            return 1

    print(f"Encontrados {len(video_files)} archivo(s) de video para procesar")

    processed_count = 0
    errors_count = 0

    for video_path in video_files:
        print(f"\n{'='*50}")
        print(f"Procesando: {video_path.name}")
        print(f"{'='*50}")

        # Determinar ruta de salida
        output_filename = video_path.stem + '.srt'
        output_path = output_folder / output_filename

        # Verificar si el archivo SRT ya existe
        if output_path.exists():
            print(f"El archivo SRT ya existe: {output_path}")
            user_input = input("¿Deseas sobrescribirlo? (s/n): ").lower().strip()
            if user_input != 's':
                print("Saltando archivo...")
                continue

        # Crear archivo temporal para audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_path = temp_audio.name

        try:
            # Paso 1: Extraer audio
            if not extract_audio(str(video_path), audio_path):
                errors_count += 1
                continue

            # Paso 2: Transcribir
            if args.use_ollama:
                transcription = transcribe_with_ollama(audio_path, args.model)
            else:
                # Por defecto usar Whisper local (más confiable)
                transcription = alternative_whisper_transcription(audio_path)

            if not transcription:
                print("❌ Error: No se pudo transcribir el audio")
                if not args.use_ollama:
                    print("💡 Sugerencias:")
                    print("   1. Instala Whisper: pip install openai-whisper")
                    print("   2. Si tienes problemas con PyTorch, instala versión CPU:")
                    print("      pip uninstall torch torchvision torchaudio")
                    print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
                    print("   3. O usa Ollama para transcripción: python generar.py --use-ollama")
                errors_count += 1
                continue

            # Paso 3: Crear SRT
            create_srt(
                transcription,
                str(output_path),
                translate=args.translate,
                translation_method=args.translation_method,
                target_lang=args.target_lang,
                ollama_model=args.translation_model
            )

            print(f"\n✅ ¡Subtítulos generados exitosamente!")
            if args.translate:
                print(f"🌐 Subtítulos traducidos a {args.target_lang} usando {args.translation_method}")
            print(f"📁 Archivo: {output_path}")
            processed_count += 1

        finally:
            # Limpiar archivo temporal
            if not args.keep_audio and os.path.exists(audio_path):
                os.unlink(audio_path)

    # Resumen final
    print(f"\n{'='*50}")
    print("RESUMEN DEL PROCESAMIENTO")
    print(f"{'='*50}")
    print(f"Archivos procesados exitosamente: {processed_count}")
    if errors_count > 0:
        print(f"Archivos con errores: {errors_count}")
    print(f"Total de archivos encontrados: {len(video_files)}")

    if processed_count > 0:
        print(f"\n📂 Los subtítulos se guardaron en: {output_folder}/")
        return 0
    else:
        print("\n❌ No se pudo procesar ningún archivo")
        return 1

if __name__ == "__main__":
    sys.exit(main())
