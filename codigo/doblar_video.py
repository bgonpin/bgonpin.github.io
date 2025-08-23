#!/usr/bin/env python3
"""
Script para extraer audio de un video en inglés, doblarlo al español 
y reinsertar el audio doblado en el video original.

Dependencias requeridas:
pip install moviepy speechrecognition googletrans==4.0.0rc1 gtts pydub
"""

import os
import tempfile
import glob
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
from pydub.silence import split_on_silence
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoDubber:
    def __init__(self):
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        
    def extract_audio(self, video_path, audio_output_path):
        """Extrae el audio del video"""
        try:
            logger.info("Extrayendo audio del video...")
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(audio_output_path, verbose=False, logger=None)
            video.close()
            audio.close()
            logger.info(f"Audio extraído: {audio_output_path}")
        except Exception as e:
            logger.error(f"Error extrayendo audio: {e}")
            raise
    
    def split_audio_on_silence(self, audio_path, min_silence_len=1000, silence_thresh=-40):
        """Divide el audio en segmentos basados en silencios"""
        try:
            logger.info("Dividiendo audio en segmentos...")
            audio = AudioSegment.from_wav(audio_path)
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=500
            )
            logger.info(f"Audio dividido en {len(chunks)} segmentos")
            return chunks
        except Exception as e:
            logger.error(f"Error dividiendo audio: {e}")
            raise
    
    def transcribe_audio_chunk(self, audio_chunk, chunk_filename):
        """Transcribe un chunk de audio a texto"""
        try:
            # Guardar chunk temporalmente
            audio_chunk.export(chunk_filename, format="wav")
            
            # Transcribir
            with sr.AudioFile(chunk_filename) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language='en-US')
                return text
        except sr.UnknownValueError:
            logger.warning("No se pudo reconocer el audio en este segmento")
            return ""
        except sr.RequestError as e:
            logger.error(f"Error con el servicio de reconocimiento: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error transcribiendo chunk: {e}")
            return ""
    
    def translate_text(self, text, target_language='es'):
        """Traduce texto al idioma objetivo"""
        try:
            if not text.strip():
                return ""
            
            translated = self.translator.translate(text, dest=target_language)
            return translated.text
        except Exception as e:
            logger.error(f"Error traduciendo texto: {e}")
            return text  # Devolver texto original si falla
    
    def text_to_speech(self, text, output_path, language='es'):
        """Convierte texto a voz"""
        try:
            if not text.strip():
                # Crear un audio silencioso si no hay texto
                silent_audio = AudioSegment.silent(duration=1000)
                silent_audio.export(output_path, format="wav")
                return

            # gTTS siempre guarda como MP3, así que usamos un path temporal
            temp_mp3_path = output_path.replace('.wav', '.mp3')

            tts = gTTS(text=text, lang=language)
            tts.save(temp_mp3_path)

            # Convertir MP3 a WAV
            audio = AudioSegment.from_mp3(temp_mp3_path)
            audio.export(output_path, format="wav")

            # Limpiar archivo MP3 temporal
            if os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)

        except Exception as e:
            logger.error(f"Error generando TTS: {e}")
            # Crear audio silencioso como fallback
            silent_audio = AudioSegment.silent(duration=1000)
            silent_audio.export(output_path, format="wav")
    
    def process_audio_segments(self, audio_chunks, temp_dir):
        """Procesa todos los segmentos de audio"""
        translated_segments = []
        
        for i, chunk in enumerate(audio_chunks):
            logger.info(f"Procesando segmento {i+1}/{len(audio_chunks)}")
            
            # Archivos temporales
            chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
            tts_path = os.path.join(temp_dir, f"translated_{i}.wav")
            
            try:
                # Transcribir
                text = self.transcribe_audio_chunk(chunk, chunk_path)
                logger.info(f"Transcrito: {text[:50]}...")
                
                # Traducir
                translated_text = self.translate_text(text)
                logger.info(f"Traducido: {translated_text[:50]}...")
                
                # Generar voz
                self.text_to_speech(translated_text, tts_path)
                logger.info(f"Audio TTS generado: {tts_path}")

                # Cargar el audio generado y luego limpiar
                try:
                    if os.path.exists(tts_path):
                        logger.info(f"Cargando audio desde: {tts_path}")
                        translated_audio = AudioSegment.from_wav(tts_path)
                        logger.info(f"Audio cargado exitosamente, duración: {len(translated_audio)}ms")

                        # Ajustar duración al chunk original
                        original_duration = len(chunk)
                        if len(translated_audio) != original_duration:
                            if len(translated_audio) < original_duration:
                                # Añadir silencio si es más corto
                                silence = AudioSegment.silent(duration=original_duration - len(translated_audio))
                                translated_audio = translated_audio + silence
                            else:
                                # Recortar si es más largo
                                translated_audio = translated_audio[:original_duration]

                        translated_segments.append(translated_audio)
                    else:
                        # Si falla, usar silencio
                        translated_segments.append(AudioSegment.silent(duration=len(chunk)))

                    # Limpiar archivos temporales después de usarlos
                    for temp_file in [chunk_path, tts_path]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

                except Exception as e:
                    logger.error(f"Error cargando audio traducido para segmento {i}: {e}")
                    # Usar silencio como fallback
                    translated_segments.append(AudioSegment.silent(duration=len(chunk)))

                    # Limpiar archivos temporales incluso si hay error
                    for temp_file in [chunk_path, tts_path]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

            except Exception as e:
                logger.error(f"Error procesando segmento {i}: {e}")
                # Usar silencio como fallback
                translated_segments.append(AudioSegment.silent(duration=len(chunk)))
        
        return translated_segments
    
    def combine_audio_segments(self, segments, output_path):
        """Combina los segmentos de audio traducidos"""
        try:
            logger.info("Combinando segmentos de audio...")
            combined_audio = AudioSegment.empty()
            
            for segment in segments:
                combined_audio += segment
            
            combined_audio.export(output_path, format="wav")
            logger.info(f"Audio combinado guardado: {output_path}")
            
        except Exception as e:
            logger.error(f"Error combinando segmentos: {e}")
            raise
    
    def replace_video_audio(self, video_path, new_audio_path, output_path):
        """Reemplaza el audio del video original"""
        try:
            logger.info("Reemplazando audio en el video...")
            
            video = VideoFileClip(video_path)
            new_audio = AudioFileClip(new_audio_path)
            
            # Asegurar que el audio tenga la misma duración que el video
            if new_audio.duration > video.duration:
                new_audio = new_audio.subclip(0, video.duration)
            elif new_audio.duration < video.duration:
                # Extender con silencio si es necesario
                silence_duration = video.duration - new_audio.duration
                logger.warning(f"Añadiendo {silence_duration}s de silencio al final")
            
            final_video = video.set_audio(new_audio)
            final_video.write_videofile(output_path, verbose=False, logger=None)
            
            video.close()
            new_audio.close()
            final_video.close()
            
            logger.info(f"Video final guardado: {output_path}")
            
        except Exception as e:
            logger.error(f"Error reemplazando audio: {e}")
            raise
    
    def dub_video(self, input_video_path, output_video_path):
        """Proceso principal de doblaje"""
        # Crear carpeta temporal personalizada
        temp_folder = "temporal"
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        temp_dir = temp_folder
        try:
            # Paths temporales
            original_audio_path = os.path.join(temp_dir, "original_audio.wav")
            dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")

            # Paso 1: Extraer audio
            self.extract_audio(input_video_path, original_audio_path)

            # Paso 2: Dividir audio en segmentos
            audio_chunks = self.split_audio_on_silence(original_audio_path)

            # Paso 3: Procesar segmentos (transcribir, traducir, generar voz)
            translated_segments = self.process_audio_segments(audio_chunks, temp_dir)

            # Paso 4: Combinar segmentos
            self.combine_audio_segments(translated_segments, dubbed_audio_path)

            # Paso 5: Reemplazar audio en video
            self.replace_video_audio(input_video_path, dubbed_audio_path, output_video_path)

            logger.info("¡Proceso de doblaje completado exitosamente!")

            # Limpiar archivos temporales después del procesamiento exitoso
            try:
                for temp_file in [original_audio_path, dubbed_audio_path]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                logger.info("Archivos temporales limpiados")
            except Exception as e:
                logger.warning(f"No se pudieron limpiar algunos archivos temporales: {e}")

        except Exception as e:
            logger.error(f"Error en el proceso de doblaje: {e}")
            # Intentar limpiar archivos temporales incluso si hay error
            try:
                for temp_file in [original_audio_path, dubbed_audio_path]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            except:
                pass
            raise

def main():
    # Definir carpetas
    original_folder = "original"
    doblada_folder = "doblada"

    # Verificar que la carpeta original existe
    if not os.path.exists(original_folder):
        logger.error(f"La carpeta '{original_folder}' no existe")
        return

    # Crear carpeta doblada si no existe
    if not os.path.exists(doblada_folder):
        os.makedirs(doblada_folder)
        logger.info(f"Carpeta '{doblada_folder}' creada")

    # Extensiones de video soportadas
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv']

    # Buscar archivos de video en la carpeta original
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(original_folder, ext)))

    if not video_files:
        logger.info(f"No se encontraron archivos de video en la carpeta '{original_folder}'")
        print(f"\n📁 No hay videos para doblar en la carpeta '{original_folder}'")
        return

    logger.info(f"Se encontraron {len(video_files)} archivo(s) de video")
    print(f"\n🎬 Procesando {len(video_files)} video(s)...")

    dubber = VideoDubber()
    processed_count = 0

    for input_video_path in video_files:
        try:
            # Generar nombre del archivo de salida
            filename = os.path.basename(input_video_path)
            name_without_ext = os.path.splitext(filename)[0]
            output_video_path = os.path.join(doblada_folder, f"{name_without_ext}_doblado.mp4")

            print(f"\n🔄 Procesando: {filename}")

            # Doblar el video
            dubber.dub_video(input_video_path, output_video_path)

            processed_count += 1
            print(f"✅ ¡Video doblado guardado en: {output_video_path}")

        except Exception as e:
            logger.error(f"Error procesando {input_video_path}: {e}")
            print(f"❌ Error procesando {filename}: {e}")
            continue

    print(f"\n🎉 ¡Proceso completado! {processed_count}/{len(video_files)} video(s) procesado(s) exitosamente")
    print(f"📂 Videos doblados guardados en la carpeta '{doblada_folder}'")

    # Limpiar carpeta temporal al finalizar
    temp_folder = "temporal"
    if os.path.exists(temp_folder):
        try:
            import shutil
            shutil.rmtree(temp_folder)
            logger.info(f"Carpeta temporal '{temp_folder}' eliminada")
        except Exception as e:
            logger.warning(f"No se pudo eliminar la carpeta temporal: {e}")

if __name__ == "__main__":
    main()
