"""
Sistema de Consulta de Imágenes con IA

Aplicación que permite realizar consultas en lenguaje natural sobre una base de datos
MongoDB de imágenes procesadas. Utiliza un modelo de lenguaje (Gemma 3:4b) para convertir
consultas en texto plano a pipelines de agregación MongoDB.

Características principales:
- Consultas en lenguaje natural sobre metadatos de imágenes
- Detección automática del tipo de consulta (conteo, lista, búsqueda específica)
- Formateo inteligente de respuestas según contexto
- Interfaz gráfica basada en PyQt6
- Sistema de logging automático con archivos de texto
- Funciones avanzadas de limpieza de JSON generado por LLM

Autor: Sistema de Consultas de Imágenes
Versión: 2.0
"""

from pymongo import MongoClient
try:
    from langchain_ollama import ChatOllama
except ImportError:
    try:
        from langchain_community.llms import ChatOllama
    except ImportError:
        print("No se pudo importar ChatOllama. Instalando langchain...")
        import subprocess
        # Instalar los paquetes necesarios uno por uno
        subprocess.check_call(["pip", "install", "langchain"])
        subprocess.check_call(["pip", "install", "langchain-community"])
        subprocess.check_call(["pip", "install", "langchain-ollama"])
        from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
import json
import re
import warnings
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QFrame, QSplitter, QMessageBox, QMenu,
                             QStatusBar, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction

# Suprimir warnings de deprecación para una mejor experiencia de usuario
warnings.filterwarnings("ignore", category=DeprecationWarning)

# =========================
# 1. Conexión a MongoDB
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["album_2"]

# =========================
# 2. LLM con Ollama
# =========================
llm = ChatOllama(model="gemma3:4b_40K", temperature=0)

# =========================
# 3. Funciones para limpiar/reparar JSON
# =========================
def limpiar_json_response(response_text):
    """
    Extrae el JSON de la respuesta, removiendo bloques de código markdown y texto extra.
    """
    # Primero limpiamos texto inicial no-JSON
    response_text = response_text.strip()

    # Remover bloques de código markdown
    if '```' in response_text:
        # Extraer contenido entre ``` o ```json
        lines = response_text.split('\n')
        json_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    # Si es ```json, comenzamos a capturar
                    if 'json' in line.lower():
                        continue
                else:
                    # Fin del bloque
                    in_code_block = False
                    break
            elif in_code_block:
                json_lines.append(line)

        if json_lines:
            return '\n'.join(json_lines).strip()

    # Si no es markdown, intentar encontrar JSON directo
    # Buscar arrays JSON
    import re
    json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()

    return response_text.strip()

def reparar_json(pipeline_str: str, verbose: bool = False) -> str:
    """
    Repara JSON malformado con enfoque híbrido:
    - Conserva estructura original (no escapa newlines)
    - Maneja balanceo de llaves correcto
    - Agrega comillas faltantes en claves
    - Función mejorada que combina lo mejor del simple y avanzado
    """
    import re

    if not pipeline_str:
        return pipeline_str

    pipeline_str = pipeline_str.strip()

    # Usamos un patrón más simple y robusto
    def agregar_comillas_match(match):
        try:
            clave = match.group(1).strip()
            resto = match.group(2)

            # Determinar si ya tiene comillas o no las necesita
            if clave.startswith('"') and clave.endswith('"'):
                # Ya está quotizado correctamente
                return f"{clave}:{resto}"
            elif clave.startswith('$') or re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', clave):
                # Es un operador MongoDB o nombre válido sin quotes
                if verbose:
                    print(f"Adding quotes to: '{clave}'")
                return f'"{clave}":{resto}'
            else:
                # Mantener como está (casos que no calzan en el patrón)
                return f"{clave}:{resto}"
        except (IndexError, AttributeError) as e:
            # Si hay algún problema con el match, devolver el match original
            if verbose:
                print(f"Error processing match: {e}, returning original")
            return match.group(0)

    # Patrón más simple y robusto: clave sin quotes seguida de ':'
    # Captura: cualquier palabra (letras, números, guión bajo, dólar) seguida de ':' y cualquier cosa después
    patron = r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(.*?)(?=\,|{|}|\[|\]|$)'

    # Hacer el reemplazo con cuidado, procesando todas las coincidencias
    try:
        # Primero, reemplazar patrones que no tienen quotes alrededor de operadores $
        pipeline_str = re.sub(r'(\$[a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', pipeline_str)
        # Luego, reemplazar otros nombres de propiedades sin quotes
        pipeline_str = re.sub(patron, agregar_comillas_match, pipeline_str, flags=re.MULTILINE | re.DOTALL)
    except Exception as e:
        if verbose:
            print(f"Regex error in reparar_json: {e}")
        # Si hay algún error con regex, intentar continuar sin reparar

    # Balanceo simple de llaves para casos básicos
    aperturas = pipeline_str.count('{') + pipeline_str.count('[')
    cierres = pipeline_str.count('}') + pipeline_str.count(']')

    if aperturas > cierres:
        missing = aperturas - cierres
        pipeline_str += '}' * missing
    elif cierres > aperturas:
        # Si hay cierres extra, intentar identificar y remover
        pipeline_str = pipeline_str.rstrip('}')

    return pipeline_str

# Mantenemos la función simple como alias para compatibilidad, pero usando la versión avanzada
def reparar_json_simple(pipeline_str: str) -> str:
    """
    Alias para reparar_json - usa la versión avanzada mejorada.
    """
    return reparar_json(pipeline_str)

# =========================
# 7. Funciones para formatear respuestas
# =========================
def crear_directorio_logs():
    """
    Crea el directorio de logs si no existe.
    """
    log_dir = "consultas_imagenes"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"📁 Directorio creado: {log_dir}")
    return log_dir

def generar_nombre_archivo():
    """
    Genera un nombre único para el archivo de logs basado en la fecha y hora.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"consulta_{timestamp}.txt"

def guardar_consulta(pregunta: str, respuesta: str, pipeline: dict = None, num_resultados: int = 0):
    """
    Guarda la consulta y respuesta en un archivo de texto.
    """
    try:
        log_dir = crear_directorio_logs()
        nombre_archivo = generar_nombre_archivo()
        ruta_archivo = os.path.join(log_dir, nombre_archivo)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        contenido = f"""{'='*60}
CONSULTA A BASE DE DATOS DE IMÁGENES
{'='*60}
Fecha y hora: {timestamp}
Pregunta del usuario: {pregunta}

Pipeline MongoDB generado:
{json.dumps(pipeline, indent=2, ensure_ascii=False) if pipeline else "No disponible"}

Número de resultados encontrados: {num_resultados}

RESPUESTA:
{respuesta}

{'='*60}
"""

        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)

        return ruta_archivo

    except Exception as e:
        print(f"⚠️ Error al guardar archivo: {e}")
        return None

def guardar_sesion_completa(historial_consultas: list):
    """
    Guarda todas las consultas de la sesión en un archivo resumen.
    """
    try:
        log_dir = crear_directorio_logs()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"sesion_completa_{timestamp}.txt"
        ruta_archivo = os.path.join(log_dir, nombre_archivo)

        contenido = f"""{'='*80}
SESIÓN COMPLETA DE CONSULTAS - BASE DE DATOS DE IMÁGENES
{'='*80}
Fecha de inicio: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total de consultas: {len(historial_consultas)}

"""

        for i, consulta in enumerate(historial_consultas, 1):
            contenido += f"""
{'─'*40} CONSULTA {i} {'─'*40}
Pregunta: {consulta['pregunta']}
Hora: {consulta['timestamp']}
Resultados: {consulta['num_resultados']}

Respuesta:
{consulta['respuesta']}

"""

        contenido += f"{'='*80}\n"

        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)

        return ruta_archivo

    except Exception as e:
        print(f"⚠️ Error al guardar sesión completa: {e}")
        return None

def detectar_tipo_consulta(pregunta: str, results: list) -> str:
    """
    Detecta si la consulta es de conteo, listado, o búsqueda específica.
    """
    pregunta_lower = pregunta.lower()

    # Palabras clave que indican conteo
    palabras_conteo = ['cuántas', 'cuantas', 'cantidad', 'número', 'total', 'contar', 'count']

    # Verificar si es una consulta de conteo por palabras clave
    if any(palabra in pregunta_lower for palabra in palabras_conteo):
        return 'conteo'

    # Verificar si el resultado tiene estructura de conteo MongoDB
    if len(results) == 1 and len(results[0]) == 1:
        keys = list(results[0].keys())
        if keys[0] in ['count', 'total', 'cantidad', '_id'] or keys[0].startswith('count'):
            return 'conteo'

    # Si pide una lista o mostrar - incluir más variaciones
    palabras_lista = ['lista', 'listado', 'muestra', 'mostrar', 'listar', 'enumera', 'dime', 'cuáles', 'cuales']
    if any(palabra in pregunta_lower for palabra in palabras_lista):
        return 'lista'

    return 'busqueda'

# =========================
# 5. Función para formatear respuestas
# =========================
def formatear_respuesta_conteo(results: list, pregunta: str) -> str:
    """
    Formatea respuestas de conteo de manera concisa.
    """
    if len(results) == 1 and len(results[0]) == 1:
        valor = list(results[0].values())[0]
        return str(valor)
    elif len(results) == 1 and 'count' in str(results[0]).lower():
        # Buscar el valor numérico en el resultado
        for key, value in results[0].items():
            if isinstance(value, (int, float)):
                return str(value)

    return str(len(results))

def formatear_respuesta_lista(results: list, pregunta: str, limite: int = None) -> str:
    """
    Formatea respuestas de lista de manera concisa pero informativa.
    """
    if not results:
        return "No se encontraron resultados."

    total = len(results)
    respuesta = f"Se encontraron {total} imagen(es):\n\n"

    # Determinar qué resultados mostrar
    if limite is not None and total > limite:
        resultados_mostrar = results[:limite]
        respuesta = f"Se encontraron {total} imágenes. Mostrando las primeras {limite}:\n\n"
    else:
        resultados_mostrar = results

    for i, img in enumerate(resultados_mostrar, 1):
        # Priorizar ruta_completa si está disponible, sino usar nombre_archivo
        display_name = None
        if 'ruta_completa' in img:
            display_name = img['ruta_completa']
        elif 'nombre_archivo' in img:
            display_name = img['nombre_archivo']
        else:
            # Fall back to _id or a generic name
            display_name = img.get('_id', f'Imagen_{i}')

        respuesta += f"{i}. {display_name}"

        # Agregar información relevante según el contexto de la pregunta
        pregunta_lower = pregunta.lower()

        if 'tamaño' in pregunta_lower or 'ancho' in pregunta_lower or 'alto' in pregunta_lower:
            if 'ancho' in img and 'alto' in img:
                respuesta += f" ({img['ancho']}x{img['alto']}px)"

        if 'fecha' in pregunta_lower:
            if all(k in img for k in ['fecha_creacion_dia', 'fecha_creacion_mes', 'fecha_creacion_anio']):
                fecha = f"{img['fecha_creacion_dia']}/{img['fecha_creacion_mes']}/{img['fecha_creacion_anio']}"
                respuesta += f" (Creada: {fecha})"

        if 'persona' in pregunta_lower or 'objeto' in pregunta_lower:
            objetos = img.get('objetos_detectados', [])
            if objetos:
                objetos_str = ", ".join([obj['objeto_detectado'] for obj in objetos])
                respuesta += f" (Objetos: {objetos_str})"

        respuesta += "\n"

    if limite is not None and total > limite:
        restantes = total - limite
        respuesta += f"\n... y {restantes} imagen(es) más con las mismas características."

    return respuesta

def formatear_respuesta_busqueda(results: list, pregunta: str) -> str:
    """
    Formatea respuestas de búsqueda específica.
    """
    if not results:
        return "No se encontraron resultados para la búsqueda."

    if len(results) == 1:
        img = results[0]
        # Get display name with better fallback
        display_name = img.get('ruta_completa') or img.get('nombre_archivo') or img.get('_id', 'Imagen_1')
        respuesta = f"Imagen encontrada: {display_name}\n"
        respuesta += f"Tamaño: {img.get('ancho', '--')}x{img.get('alto', '--')}px\n"

        fecha_creacion = f"{img.get('fecha_creacion_dia', '--')}/{img.get('fecha_creacion_mes', '--')}/{img.get('fecha_creacion_anio', '----')}"
        respuesta += f"Fecha de creación: {fecha_creacion}\n"

        if img.get('descripcion'):
            respuesta += f"Descripción: {img.get('descripcion')}\n"

        objetos = img.get('objetos_detectados', [])
        if objetos:
            objetos_str = ", ".join([f"{obj['objeto_detectado']} ({obj['porcentaje']:.1f}%)" for obj in objetos])
            respuesta += f"Objetos detectados: {objetos_str}\n"

        return respuesta
    else:
        return formatear_respuesta_lista(results, pregunta)

# =========================
# 8. Función principal para consultas (con guardado)
# =========================
def ejecutar_query(pregunta: str, guardar_archivo: bool = True):
    """
    Usa el LLM para generar un pipeline de agregación MongoDB
    para la colección de imágenes y formatea la respuesta apropiadamente.
    Opcionalmente guarda la consulta y respuesta en un archivo.
    """
    prompt = PromptTemplate(
        input_variables=["pregunta"],
        template="""
Eres un experto en MongoDB. Convierte la siguiente pregunta en un pipeline de agregación MongoDB en formato JSON válido.

IMPORTANTE:
- Si la pregunta es sobre contar/cantidad, usa $count o $group con $sum para obtener un número.
- Para consultas de listado, usa $match y opcionalmente $limit si hay muchos resultados. Incluye un $project para seleccionar campos útiles como nombre_archivo, ruta_completa, ancho, alto, fecha_creacion_dia, fecha_creacion_mes, fecha_creacion_anio, objetos_detectados.
- Para búsquedas específicas, usa $match con los criterios apropiados.

Esquema de la colección imagenes:
{{
  _id: String,  // Identificador único autogenerado por MongoDB para cada imagen
  nombre_archivo: String,  // Nombre del archivo de la imagen (ej: "foto001.jpg")
  ruta_completa: String,  // Ruta completa del archivo en el sistema de archivos
  ancho: Int32,  // Ancho de la imagen en píxeles (ej: 1920)
  alto: Int32,  // Alto de la imagen en píxeles (ej: 1080)
  fecha_creacion_dia: String (formato: "01", "02", etc.),  // Día de creación de la imagen (con cero a la izquierda)
  fecha_creacion_mes: String (formato: "01", "02", etc.),  // Mes de creación de la imagen (con cero a la izquierda)
  fecha_creacion_anio: String (formato: "2024"),  // Año de creación de la imagen
  fecha_creacion_hora: String (formato: "14", "09", etc.),  // Hora de creación de la imagen (formato 24h)
  fecha_creacion_minuto: String (formato: "30", "05", etc.),  // Minuto de creación de la imagen
  coordenadas: Null,  // Coordenadas GPS de la imagen (por implementar o no disponibles)
  direccion: Null,  // Dirección geográfica asociada a la imagen (por implementar o no disponible)
  fecha_procesamiento_dia: String,  // Día en que la imagen fue procesada por el sistema
  fecha_procesamiento_mes: String,  // Mes en que la imagen fue procesada
  fecha_procesamiento_anio: String,  // Año en que la imagen fue procesada
  fecha_procesamiento_hora: String,  // Hora en que la imagen fue procesada
  fecha_procesamiento_minuto: String,  // Minuto en que la imagen fue procesada
  hash_sha512: String,  // Hash SHA-512 del archivo para detección de duplicados y verificación de integridad
  objetos_detectados: Array [
    {{
      objeto_detectado: String (ej: "person", "car", "dog"),  // Nombre del objeto identificado en la imagen
      porcentaje: Double (0-100),  // Porcentaje de confianza en la detección del objeto
      coordenadas: Array de 4 Int32 [x1, y1, x2, y2]  // Coordenadas del bounding box del objeto en la imagen
    }}
  ],  // Array de objetos detectados mediante IA en la imagen
  visto: Boolean,  // Indica si el usuario ha visto la imagen (true/false)
  descripcion: String,  // Descripción textual de la imagen generada por IA
  descrito: Boolean  // Indica si la imagen ya tiene una descripción generada (true/false)
}}

Pregunta: {pregunta}

Responde ÚNICAMENTE con el pipeline JSON que empiece con [ y termine con ].
NO incluyas explicaciones ni bloques de código markdown.
"""
    )

    pipeline_str = llm.invoke(prompt.format(pregunta=pregunta)).content

    # Log the raw LLM response for debugging
    print(f"🔍 Respuesta LLM cruda: {repr(pipeline_str[:200])}...")

    pipeline_str_limpio = reparar_json_simple(limpiar_json_response(pipeline_str))

    # Log the cleaned response for debugging
    print(f"🧹 Respuesta limpiada: {repr(pipeline_str_limpio[:200])}...")

    try:
        pipeline = json.loads(pipeline_str_limpio)
        print(f"📋 Pipeline: {json.dumps(pipeline, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON: {e}")
        print(f"❌ Pipeline problemático: {repr(pipeline_str_limpio)}")

        # Try alternative parsing approaches
        error_msg = f"Error al interpretar el pipeline: {e}"

        # Fallback 1: Try without repair
        try:
            pipeline_fallback = json.loads(limpiar_json_response(pipeline_str))
            print("✅ Fallback exitoso: JSON parsed without repair")
            pipeline = pipeline_fallback
        except:
            # Fallback 2: Try extracting just the array by removing markdown completely
            try:
                import re
                json_match = re.search(r'\[.*\]', pipeline_str, re.DOTALL)
                if json_match:
                    pipeline_alt = json.loads(json_match.group(0))
                    print("✅ Fallback exitoso: Array extracted from raw response")
                    pipeline = pipeline_alt
                else:
                    if guardar_archivo:
                        guardar_consulta(pregunta, error_msg)
                    return error_msg
            except Exception as e2:
                print(f"❌ Todos los fallbacks fallaron: {e2}")
                if guardar_archivo:
                    guardar_consulta(pregunta, f"{error_msg}. Fallback también falló: {e2}")
                return error_msg

    try:
        results = list(db["imagenes"].aggregate(pipeline))
        num_resultados = len(results)
        print(f"✅ Encontrados {num_resultados} resultados.")
    except Exception as e:
        error_msg = f"Error al ejecutar consulta: {e}"
        if guardar_archivo:
            guardar_consulta(pregunta, error_msg, pipeline)
        return error_msg

    # Detectar tipo de consulta y formatear respuesta apropiadamente
    tipo_consulta = detectar_tipo_consulta(pregunta, results)

    if tipo_consulta == 'conteo':
        respuesta = formatear_respuesta_conteo(results, pregunta)
    elif tipo_consulta == 'lista':
        respuesta = formatear_respuesta_lista(results, pregunta)
    else:
        respuesta = formatear_respuesta_busqueda(results, pregunta)

    # Guardar la consulta y respuesta en archivo si está habilitado
    if guardar_archivo:
        archivo_guardado = guardar_consulta(pregunta, respuesta, pipeline, num_resultados)
        if archivo_guardado:
            print(f"💾 Consulta guardada en: {archivo_guardado}")

    return respuesta

# =========================
# Función principal para consultas directas
# =========================
def procesar_consulta_directa(pregunta: str):
    """
    Procesa la consulta directamente usando el LLM para generar pipelines MongoDB.
    """
    try:
        resultado = ejecutar_query(pregunta)
        return resultado
    except Exception as e:
        return f"Error al procesar la consulta: {e}"

# =========================
# GUI Application
# =========================
class ImageSearchGUI(QMainWindow):
    """
    Interfaz gráfica principal para el asistente de consultas de imágenes.

    Esta clase implementa una aplicación PyQt6 que permite a los usuarios realizar
    consultas en lenguaje natural sobre una base de datos de imágenes MongoDB,
    utilizando un modelo de lenguaje para generar pipelines de agregación.

    Características principales:
    - Campo de entrada de texto para consultas en lenguaje natural
    - Área de resultados con opciones de contexto personalizadas
    - Gestión automática de historial y guardado de consultas
    - Funciones avanzadas de limpieza y filtrado de resultados
    - Atajos de teclado para operaciones comunes
    - Menús contextuales para manipulación de texto
    """
    def __init__(self):
        """
        Inicializa la interfaz gráfica del asistente de consultas de imágenes.

        Configura la ventana principal, variables de instancia, widgets de la interfaz,
        atajos de teclado y muestra el mensaje de bienvenida inicial.
        """
        super().__init__()
        self.setWindowTitle("🖼️ Asistente de Consultas de Imágenes")
        self.resize(1000, 700)

        # Variables
        self.historial_consultas = []
        self.guardar_automatico = True

        # Crear widgets
        self.create_widgets()

        # Estado inicial
        self.update_guardar_status()

        # Inicializar variables para context menu
        self.context_menu = QMenu(self)

        # Configurar atajos de teclado
        self.setup_shortcuts()

        # Mostrar mensaje inicial
        self.limpiar_output()

    def create_widgets(self):
        """
        Crea y configura todos los widgets de la interfaz gráfica principal.

        Esta función inicializa y configura todos los componentes visuales de la aplicación,
        incluyendo el layout principal, campos de entrada, botones, área de resultados
        y barra de estado. Establece las conexiones de señales y establece las propiedades
        visuales básicas de cada componente.
        """
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Título
        title_label = QLabel("Asistente de Consultas de Imágenes")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Frame para entrada
        input_group = QFrame()
        input_group.setFrameStyle(QFrame.Shape.Box)
        input_layout = QVBoxLayout(input_group)

        input_title = QLabel("Consulta")
        input_title_font = QFont("Arial", 12, QFont.Weight.Bold)
        input_title.setFont(input_title_font)
        input_layout.addWidget(input_title)

        # Campo de entrada
        self.query_entry = QLineEdit()
        self.query_entry.setFont(QFont("Arial", 12))
        self.query_entry.returnPressed.connect(self.procesar_consulta)
        input_layout.addWidget(self.query_entry)

        # Botones
        button_layout = QHBoxLayout()

        self.buscar_btn = QPushButton("🔍 Buscar")
        self.buscar_btn.clicked.connect(self.procesar_consulta)
        button_layout.addWidget(self.buscar_btn)

        self.guardar_toggle_btn = QPushButton("💾 Auto-guardar: ON")
        self.guardar_toggle_btn.clicked.connect(self.toggle_guardar)
        button_layout.addWidget(self.guardar_toggle_btn)

        self.historial_btn = QPushButton("📂 Ver Historial")
        self.historial_btn.clicked.connect(self.ver_historial)
        button_layout.addWidget(self.historial_btn)

        self.clear_btn = QPushButton("🗑️ Limpiar")
        self.clear_btn.clicked.connect(self.limpiar_output)
        button_layout.addWidget(self.clear_btn)

        # Botón de opciones avanzadas
        self.clear_options_btn = QPushButton("🔧 Opciones")
        self.create_options_menu()
        button_layout.addWidget(self.clear_options_btn)

        input_layout.addLayout(button_layout)
        main_layout.addWidget(input_group)

        # Área de salida
        output_group = QFrame()
        output_group.setFrameStyle(QFrame.Shape.Box)
        output_layout = QVBoxLayout(output_group)

        output_title = QLabel("Resultados")
        output_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        output_layout.addWidget(output_title)

        # Scrollable text area
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.output_text.customContextMenuRequested.connect(self.show_context_menu)
        output_layout.addWidget(self.output_text)

        main_layout.addWidget(output_group, 1)  # stretch factor

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Listo - Ingrese una consulta...")

    def create_options_menu(self):
        """Crea el menú de opciones avanzadas"""
        self.options_menu = QMenu(self)

        # Añadir acciones al menú
        self.clear_all_action = self.options_menu.addAction("🗑️ Limpiar Todo (Completo)")
        self.clear_all_action.triggered.connect(self.limpiar_completo)

        self.clear_last_action = self.options_menu.addAction("📝 Limpiar Última Consulta")
        self.clear_last_action.triggered.connect(self.limpiar_ultima_consulta)

        self.clear_keep_header_action = self.options_menu.addAction("🧹 Limpiar Salida Manteniendo Header")
        self.clear_keep_header_action.triggered.connect(self.limpiar_output_con_header)

        self.options_menu.addSeparator()

        self.save_and_clear_action = self.options_menu.addAction("💾 Guardar y Limpiar")
        self.save_and_clear_action.triggered.connect(self.guardar_y_limpiar)

        self.clear_options_btn.setMenu(self.options_menu)

    def procesar_consulta(self):
        pregunta = self.query_entry.text().strip()

        if not pregunta:
            self.mostrar_mensaje("Por favor ingrese una consulta.", "error")
            return

        # Comandos especiales
        if pregunta.lower() in ['exit', 'quit', 'salir']:
            self.close()
            return

        self.status_bar.showMessage("Procesando consulta...")
        current_text = self.output_text.toPlainText()
        self.output_text.setPlainText(current_text + f"\n👉 Usuario: {pregunta}\n")
        QApplication.processEvents()  # Actualizar la interfaz

        timestamp_consulta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            resultado = procesar_consulta_directa(pregunta)

            # Mostrar resultado
            current_text = self.output_text.toPlainText()
            self.output_text.setPlainText(current_text + f"🤖 Respuesta:\n{resultado}\n")
            self.output_text.setPlainText(self.output_text.toPlainText() + "="*50 + "\n")

            # Agregar al historial
            if self.guardar_automatico:
                # Extraer número de resultados
                num_resultados = 'N/A'
                match = re.search(r'Encontrados (\d+) imagen', resultado)
                if match:
                    num_resultados = match.group(1)

                self.historial_consultas.append({
                    'timestamp': timestamp_consulta,
                    'pregunta': pregunta,
                    'respuesta': resultado,
                    'num_resultados': num_resultados
                })

            self.status_bar.showMessage("Consulta procesada exitosamente.")

        except Exception as e:
            error_msg = f"❌ Error: {e}"
            current_text = self.output_text.toPlainText()
            self.output_text.setPlainText(current_text + error_msg + "\n")
            if self.guardar_automatico:
                self.historial_consultas.append({
                    'timestamp': timestamp_consulta,
                    'pregunta': pregunta,
                    'respuesta': error_msg,
                    'num_resultados': 0
                })
            self.status_bar.showMessage("Error en la consulta.")

        # Scroll al final
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

        self.query_entry.clear()

    def toggle_guardar(self):
        self.guardar_automatico = not self.guardar_automatico
        self.update_guardar_status()

    def update_guardar_status(self):
        status = "ON" if self.guardar_automatico else "OFF"
        self.guardar_toggle_btn.setText(f"💾 Auto-guardar: {status}")

    def ver_historial(self):
        log_dir = "consultas_imagenes"
        if os.path.exists(log_dir):
            archivos = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
            if archivos:
                # Mostrar los 10 más recientes
                recientes = sorted(archivos)[-10:]
                current_text = self.output_text.toPlainText()
                self.output_text.setPlainText(current_text + "\n📂 Últimos 10 archivos guardados:\n")
                for archivo in recientes:
                    current_text = self.output_text.toPlainText()
                    self.output_text.setPlainText(current_text + f"   - {archivo}\n")
                current_text = self.output_text.toPlainText()
                self.output_text.setPlainText(current_text + "="*50 + "\n")
            else:
                self.mostrar_mensaje("No hay archivos guardados aún.", "info")
        else:
            self.mostrar_mensaje("No existe el directorio de logs.", "error")

        # Scroll al final
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def limpiar_output(self):
        self.output_text.clear()
        welcome_message = ("Bienvenido al Asistente de Consultas de Imágenes\n"
                          "Ejemplo: '¿Cuántas imágenes tienen un ancho mayor a 1000 píxeles?'\n"
                          "Las consultas se guardarán automáticamente si está activado.\n" +
                          "="*60)
        self.output_text.setPlainText(welcome_message)

    def mostrar_mensaje(self, mensaje, tag="info"):
        current_text = self.output_text.toPlainText()
        self.output_text.setPlainText(current_text + f"{mensaje}\n")

    # ===================== FUNCIONES DE MENÚ CONTEXTUAL =====================

    def show_context_menu(self, position):
        """Muestra el menú contextual personalizado en el área de texto."""
        # Limpiar menú anterior
        self.context_menu.clear()

        # Añadir acciones
        copy_action = self.context_menu.addAction("📋 Copiar")
        copy_action.triggered.connect(self.copiar_seleccion)

        clear_selection_action = self.context_menu.addAction("🗑️ Limpiar Selección")
        clear_selection_action.triggered.connect(self.limpiar_seleccion)

        self.context_menu.addSeparator()

        show_responses_action = self.context_menu.addAction("🗣️ Mostrar Solo Resultados")
        show_responses_action.triggered.connect(self.mostrar_solo_resultados)

        show_queries_action = self.context_menu.addAction("📝 Mostrar Solo Consultas")
        show_queries_action.triggered.connect(self.mostrar_solo_consultas)

        # Mostrar menú en la posición del cursor
        self.context_menu.exec(self.output_text.mapToGlobal(position))

    def copiar_seleccion(self):
        """Copia el texto seleccionado al portapapeles."""
        seleccionado = self.output_text.textCursor().selectedText()
        if seleccionado:
            clipboard = QApplication.clipboard()
            clipboard.setText(seleccionado)
            self.status_bar.showMessage("Texto copiado al portapapeles.")
        else:
            QMessageBox.information(self, "Info", "No hay texto seleccionado.")

    def limpiar_seleccion(self):
        """Elimina el texto seleccionado."""
        cursor = self.output_text.textCursor()
        if cursor.hasSelection():
            pregunta = "¿Quieres eliminar el texto seleccionado?\n\n"
            seleccionado = cursor.selectedText()

            if len(seleccionado) > 50:
                pregunta += f"'{seleccionado[:50]}...'"
            else:
                pregunta += f"'{seleccionado}'"

            respuesta = QMessageBox.question(self, "Confirmar", pregunta,
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if respuesta == QMessageBox.StandardButton.Yes:
                cursor.removeSelectedText()
                self.status_bar.showMessage("Texto seleccionado eliminado.")
        else:
            QMessageBox.information(self, "Info", "No hay texto seleccionado.")

    def mostrar_solo_resultados(self):
        """Filtra el contenido para mostrar solo las respuestas del asistente."""
        contenido = self.output_text.toPlainText()
        lines = contenido.split('\n')

        resultados = []
        in_respuesta = False

        for line in lines:
            if line.startswith("🤖 Respuesta:"):
                in_respuesta = True
                resultados.append(line)
            elif in_respuesta and line.startswith("="*50):
                in_respuesta = False
                resultados.append(line)
            elif in_respuesta:
                resultados.append(line)

        if resultados:
            self.output_text.clear()
            self.output_text.setPlainText('\n'.join(resultados))
            self.status_bar.showMessage("Mostrando solo respuestas.")
        else:
            QMessageBox.information(self, "Info", "No se encontraron respuestas para mostrar.")

    def mostrar_solo_consultas(self):
        """Filtra el contenido para mostrar solo las consultas del usuario."""
        contenido = self.output_text.toPlainText()
        lines = contenido.split('\n')

        consultas = []
        for line in lines:
            if line.startswith("👉 Usuario:"):
                consultas.append(line)

        if consultas:
            self.output_text.clear()
            self.output_text.setPlainText('\n'.join(consultas))
            self.status_bar.showMessage("Mostrando solo consultas.")
        else:
            QMessageBox.information(self, "Info", "No se encontraron consultas para mostrar.")

    def closeEvent(self, event):
        """Maneja el evento de cierre de la aplicación."""
        # Guardar sesión completa si hay historial
        if self.historial_consultas and self.guardar_automatico:
            archivo_sesion = guardar_sesion_completa(self.historial_consultas)
            if archivo_sesion:
                QMessageBox.information(self, "Sesión Guardada",
                                      f"Sesión completa guardada en: {archivo_sesion}")
        event.accept()

    # ===================== NUEVAS FUNCIONES DE LIMPIEZA =====================

    def limpiar_completo(self):
        """Limpia completamente el área de salida."""
        respuesta = QMessageBox.question(self, "Confirmar",
                                       "¿Estás seguro de que quieres limpiar completamente?\n\n"
                                       "Esto eliminará TODOS los resultados y consultas de la pantalla.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if respuesta == QMessageBox.StandardButton.Yes:
            self.output_text.clear()
            self.output_text.setPlainText("Área de resultados completamente limpia.\nPuedes comenzar nuevas consultas.")

    def limpiar_ultima_consulta(self):
        """Limpia solo la última consulta y su respuesta."""
        contenido = self.output_text.toPlainText().strip()
        if not contenido:
            return

        # Buscar el último separador (====) para encontrar la última consulta
        lines = contenido.split('\n')

        # Buscar la última consulta
        last_separator = -1
        for i in range(len(lines) - 1, -1, -1):
            if '=' * 50 in lines[i]:
                last_separator = i
                break

        if last_separator > 0:
            # Buscar la consulta anterior
            consulta_start = -1
            for i in range(last_separator - 1, -1, -1):
                if "👉 Usuario:" in lines[i]:
                    consulta_start = i
                    break

            if consulta_start >= 0:
                # Mantener solo el contenido antes de la consulta
                new_content = '\n'.join(lines[:consulta_start])
                self.output_text.setPlainText(new_content + "\n\n🗑️ Última consulta eliminada.")
                self.status_bar.showMessage("Última consulta eliminada.")
            else:
                QMessageBox.information(self, "Info", "No se encontró una consulta específica para eliminar.")
        else:
            QMessageBox.information(self, "Info", "No hay consultas para eliminar.")

    def limpiar_output_con_header(self):
        """Limpia los resultados pero mantiene el header de bienvenida."""
        contenido = self.output_text.toPlainText().strip()
        if not contenido:
            return

        # Buscar líneas del header
        lines = contenido.split('\n')
        header_line = None

        for line in lines:
            if "Bienvenido al Asistente de Consultas" in line:
                header_line = line
                break

        # Recargar el output
        self.output_text.clear()
        if header_line:
            self.output_text.setPlainText(header_line)
        else:
            self.output_text.setPlainText("Resultados limpios. Header restablecido.")

    def guardar_y_limpiar(self):
        """Guarda la sesión actual y limpia completamente."""
        if not self.historial_consultas:
            QMessageBox.information(self, "Info", "No hay consultas para guardar.")
            return

        # Guardar sesión completa
        archivo_sesion = guardar_sesion_completa(self.historial_consultas)
        if archivo_sesion:
            QMessageBox.information(self, "Sesión Guardada", f"Sesión guardada en:\n{archivo_sesion}")

        # Limpiar contenido
        self.limpiar_completo()
        self.historial_consultas = []  # Limpiar historial en memoria

# =========================
# Shortcuts (Funcionalidad adicional)
# =========================
    def setup_shortcuts(self):
        """Configura atajos de teclado usando Qt shortcuts."""
        from PyQt6.QtGui import QShortcut, QKeySequence

        # Ctrl+L para limpiar
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.limpiar_output)

        # Ctrl+H para historial
        history_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        history_shortcut.activated.connect(self.ver_historial)

        # Ctrl+S para toggle guardar
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.toggle_guardar)

        # Ctrl+Q para salir
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

# =========================
# Main
# =========================
if __name__ == "__main__":
    import sys

    # Crear aplicación Qt
    app = QApplication(sys.argv)

    # Crear ventana principal
    window = ImageSearchGUI()
    window.show()

    # Ejecutar el bucle de eventos de la aplicación
    sys.exit(app.exec())
