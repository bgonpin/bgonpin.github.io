import os
import sys

def rename_files_in_data_folder():
    """
    Renombra todos los archivos en la carpeta 'data' 
    reemplazando espacios por guiones bajos (_)
    """
    # Definir la ruta de la carpeta data
    data_folder = "data"
    
    # Verificar si la carpeta existe
    if not os.path.exists(data_folder):
        print(f"Error: La carpeta '{data_folder}' no existe.")
        print("Asegúrate de que la carpeta 'data' esté en el mismo directorio que este script.")
        return
    
    if not os.path.isdir(data_folder):
        print(f"Error: '{data_folder}' no es una carpeta.")
        return
    
    # Obtener lista de archivos en la carpeta
    try:
        files = os.listdir(data_folder)
    except PermissionError:
        print(f"Error: No tienes permisos para acceder a la carpeta '{data_folder}'.")
        return
    
    # Filtrar solo archivos (no carpetas)
    files = [f for f in files if os.path.isfile(os.path.join(data_folder, f))]
    
    if not files:
        print(f"No se encontraron archivos en la carpeta '{data_folder}'.")
        return
    
    renamed_count = 0
    
    print(f"Procesando archivos en la carpeta '{data_folder}'...\n")
    
    for filename in files:
        # Verificar si el nombre contiene espacios
        if ' ' in filename:
            # Crear el nuevo nombre reemplazando espacios por guiones bajos
            new_filename = filename.replace(' ', '_')
            
            # Rutas completas
            old_path = os.path.join(data_folder, filename)
            new_path = os.path.join(data_folder, new_filename)
            
            # Verificar si ya existe un archivo con el nuevo nombre
            if os.path.exists(new_path):
                print(f"⚠️  Saltando '{filename}' -> ya existe '{new_filename}'")
                continue
            
            try:
                # Renombrar el archivo
                os.rename(old_path, new_path)
                print(f"✅ Renombrado: '{filename}' -> '{new_filename}'")
                renamed_count += 1
            except OSError as e:
                print(f"❌ Error al renombrar '{filename}': {e}")
        else:
            print(f"⏭️  Sin cambios: '{filename}' (no contiene espacios)")
    
    print(f"\n🎉 Proceso completado. Se renombraron {renamed_count} archivos.")

def main():
    """Función principal"""
    print("=" * 50)
    print("Script para renombrar archivos")
    print("Reemplaza espacios por guiones bajos (_)")
    print("=" * 50)
    
    # Mostrar directorio actual
    current_dir = os.getcwd()
    print(f"Directorio actual: {current_dir}")
    
    # Ejecutar la función de renombrado
    rename_files_in_data_folder()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()