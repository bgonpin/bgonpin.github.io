#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para traducir archivos VTT del inglés al castellano
Requiere: pip install googletrans==4.0.0rc1
"""

import os
import re
from pathlib import Path
from googletrans import Translator
import time

def parse_vtt_file(file_path):
    """
    Parsea un archivo VTT y extrae los segmentos de texto con sus timestamps
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    segments = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Buscar líneas de timestamp (formato: 00:00:01.000 --> 00:00:05.000)
        timestamp_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3}).*'
        match = re.match(timestamp_pattern, line)
        
        if match:
            start_time = match.group(1)
            end_time = match.group(2)
            
            # Extraer propiedades adicionales si existen (align, line, etc.)
            properties = line[len(f"{start_time} --> {end_time}"):].strip()
            
            # Buscar el texto del subtítulo en las siguientes líneas
            subtitle_text = []
            i += 1
            
            # Leer líneas hasta encontrar una línea vacía o otro timestamp
            while i < len(lines):
                current_line = lines[i].strip()
                
                # Si es línea vacía o encontramos otro timestamp, parar
                if not current_line or re.match(timestamp_pattern, current_line):
                    break
                
                # Si no es una línea de metadatos (como NOTE), agregar al texto
                if not current_line.startswith('NOTE') and not current_line.startswith('WEBVTT'):
                    subtitle_text.append(current_line)
                
                i += 1
            
            # Unir el texto del subtítulo
            full_text = ' '.join(subtitle_text).strip()
            
            # Solo agregar si hay texto real
            if full_text and full_text not in ['[MUSIC PLAYING]', '[SOUND EFFECTS]']:
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'text': full_text,
                    'properties': properties
                })
        else:
            i += 1
    
    return segments

def translate_text(text, translator, max_retries=3):
    """
    Traduce el texto con reintentos en caso de error
    """
    for attempt in range(max_retries):
        try:
            # Limpiar el texto de caracteres especiales que pueden causar problemas
            clean_text = re.sub(r'<[^>]+>', '', text)  # Remover tags HTML
            clean_text = clean_text.strip()
            
            if not clean_text:
                return text
            
            # No traducir elementos de sonido o música
            if clean_text.startswith('[') and clean_text.endswith(']'):
                return clean_text
            
            result = translator.translate(clean_text, src='en', dest='es')
            return result.text
        
        except Exception as e:
            print(f"Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Esperar antes del siguiente intento
            else:
                print(f"Error persistente traduciendo: {text}")
                return text  # Devolver texto original si falla

def create_vtt_content(segments, original_header="WEBVTT"):
    """
    Crea el contenido del archivo VTT traducido
    """
    content = original_header + "\n\n"
    
    for i, segment in enumerate(segments, 1):
        # Construir la línea de timestamp con propiedades si existen
        timestamp_line = f"{segment['start']} --> {segment['end']}"
        if segment.get('properties'):
            timestamp_line += f" {segment['properties']}"
        
        content += timestamp_line + "\n"
        content += f"{segment['text']}\n\n"
    
    return content

def translate_vtt_file(input_path, output_path):
    """
    Traduce un archivo VTT completo
    """
    print(f"Procesando: {input_path}")
    
    # Inicializar traductor
    translator = Translator()
    
    # Leer el archivo original para preservar el header
    with open(input_path, 'r', encoding='utf-8') as file:
        original_content = file.read()
    
    # Extraer header (primera línea)
    lines = original_content.split('\n')
    header = lines[0] if lines[0].startswith('WEBVTT') else 'WEBVTT'
    
    # Parsear segmentos
    segments = parse_vtt_file(input_path)
    
    if not segments:
        print(f"No se encontraron segmentos de subtítulos en {input_path}")
        return False
    
    # Traducir cada segmento
    translated_segments = []
    total_segments = len(segments)
    
    for i, segment in enumerate(segments, 1):
        print(f"Traduciendo segmento {i}/{total_segments}...", end='\r')
        
        translated_text = translate_text(segment['text'], translator)
        
        translated_segments.append({
            'start': segment['start'],
            'end': segment['end'],
            'text': translated_text,
            'properties': segment.get('properties', '')
        })
        
        # Pausa pequeña para evitar límites de rate limiting
        time.sleep(0.1)
    
    # Crear contenido del archivo traducido
    translated_content = create_vtt_content(translated_segments, header)
    
    # Guardar archivo traducido
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(translated_content)
    
    print(f"\nArchivo traducido guardado en: {output_path}")
    return True

def main():
    """
    Función principal que procesa todos los archivos VTT en la carpeta entrada
    """
    # Definir carpetas
    input_folder = Path("entrada")
    output_folder = Path("salida")
    
    # Verificar que existe la carpeta de entrada
    if not input_folder.exists():
        print(f"Error: La carpeta '{input_folder}' no existe.")
        print("Por favor, crea la carpeta 'entrada' y coloca los archivos VTT ahí.")
        return
    
    # Crear carpeta de salida si no existe
    output_folder.mkdir(exist_ok=True)
    
    # Buscar archivos VTT
    vtt_files = list(input_folder.glob("*.vtt"))
    
    if not vtt_files:
        print(f"No se encontraron archivos .vtt en la carpeta '{input_folder}'")
        return
    
    print(f"Encontrados {len(vtt_files)} archivos VTT para traducir\n")
    
    # Procesar cada archivo
    success_count = 0
    for vtt_file in vtt_files:
        try:
            # Crear ruta de salida con el mismo nombre que el original
            output_file = output_folder / vtt_file.name

            # Traducir archivo
            if translate_vtt_file(vtt_file, output_file):
                success_count += 1
            
            print("-" * 50)
        
        except Exception as e:
            print(f"Error procesando {vtt_file}: {e}")
    
    print(f"\nProceso completado: {success_count}/{len(vtt_files)} archivos traducidos exitosamente")

if __name__ == "__main__":
    main()
