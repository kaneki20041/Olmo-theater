from flask import Flask, render_template, request, redirect, url_for, jsonify, flash,session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
import uuid
import pandas as pd
import secrets
import re # Asegúrate de que 're' esté importado para 'valid_url'
import logging # Importar el módulo logging
from collections import OrderedDict
from functools import wraps
import math
from PIL import Image

# Carga las variables de entorno desde .flaskenv o .env
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
USERNAME = os.environ.get("ADMIN_USERNAME")
PASSWORD = os.environ.get("ADMIN_PASSWORD")
print("SECRET_KEY:", os.environ.get("SECRET_KEY"))
print("USERNAME:", os.environ.get("ADMIN_USERNAME"))
print("PASSWORD:", os.environ.get("ADMIN_PASSWORD"))




# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/images/obras'
UPLOAD_FOLDER_OBRAS = 'static/images/obras'
UPLOAD_FOLDER_ELENCO = 'static/images/elenco'
UPLOAD_FOLDER_SERVICIOS = 'static/images/servicios'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_ELENCO'] = UPLOAD_FOLDER_ELENCO
app.config['UPLOAD_FOLDER_SERVICIOS'] = UPLOAD_FOLDER_SERVICIOS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Variable global para almacenar clientes (en producción usa base de datos)
clients_storage = []


for folder in [UPLOAD_FOLDER, UPLOAD_FOLDER_ELENCO, UPLOAD_FOLDER_SERVICIOS]:
    os.makedirs(folder, exist_ok=True)
    
# Configuración del logger para app.logger.warning
logging.basicConfig(level=logging.INFO)


ORDEN_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"
]

ORDEN_FILTROS = ['talleres-ninos', 'talleres-adultos', 'servicios-pre-funcion', 'contratos']

# Archivos donde se guardarán los datos
OBRAS_FILE = 'obras.json'
SERVICIOS_FILE = 'servicios.json'
DATA_FILE = 'teatro_faq.json'
JSON_FILE = 'obras_historicas.json'
# Las variables CATEGORIAS_SERVICIOS y NOMBRES_CATEGORIAS ya no son globales y estáticas
# Ahora se generarán dinámicamente dentro de cargar_servicios()

def init_json_data():
    initial_data = {
        "categorias": [
            {"id": 1, "nombre": "Todas", "slug": "all", "creado_en": datetime.now().isoformat()},
            {"id": 2, "nombre": "Reservas", "slug": "reservas", "creado_en": datetime.now().isoformat()},
            {"id": 3, "nombre": "Espectáculos", "slug": "espectaculos", "creado_en": datetime.now().isoformat()},
            {"id": 4, "nombre": "Precios", "slug": "precios", "creado_en": datetime.now().isoformat()},
            {"id": 5, "nombre": "Ubicación", "slug": "ubicacion", "creado_en": datetime.now().isoformat()}
        ],
        "preguntas": [
            {
                "id": 1,
                "pregunta": "¿Cómo puedo reservar entradas para un espectáculo?",
                "respuesta": "Puedes reservar tus entradas de varias formas: a través de nuestro sitio web, llamando directamente al teatro, o visitando nuestra taquilla. Recomendamos reservar con anticipación, especialmente para espectáculos populares, ya que las entradas suelen agotarse rápidamente.",
                "categoria_id": 2,
                "activa": True,
                "orden": 0,
                "creado_en": datetime.now().isoformat()
            },
            {
                "id": 2,
                "pregunta": "¿Puedo cancelar o cambiar mi reserva?",
                "respuesta": "Sí, puedes cancelar o modificar tu reserva hasta 24 horas antes del espectáculo. Para cambios realizados con menos de 24 horas de anticipación, se aplicará una tarifa administrativa. Las cancelaciones realizadas el mismo día del evento no son reembolsables.",
                "categoria_id": 2,
                "activa": True,
                "orden": 1,
                "creado_en": datetime.now().isoformat()
            },
            {
                "id": 3,
                "pregunta": "¿Ofrecen descuentos para estudiantes o grupos?",
                "respuesta": "¡Por supuesto! Ofrecemos descuentos del 20% para estudiantes con identificación válida, 15% para grupos de 10 o más personas, y descuentos especiales para adultos mayores. También tenemos promociones especiales durante ciertas fechas del año.",
                "categoria_id": 4,
                "activa": True,
                "orden": 0,
                "creado_en": datetime.now().isoformat()
            },
            {
                "id": 4,
                "pregunta": "¿Cuánto tiempo duran los espectáculos?",
                "respuesta": "La duración varía según el espectáculo. Generalmente, nuestras obras duran entre 90 y 120 minutos, incluyendo un intermedio de 15 minutos. La información específica sobre la duración se incluye en cada descripción del espectáculo y en tu boleto.",
                "categoria_id": 3,
                "activa": True,
                "orden": 0,
                "creado_en": datetime.now().isoformat()
            }
        ],
        "next_categoria_id": 6,
        "next_pregunta_id": 5
    }
    return initial_data

# Funciones auxiliares para manejar el JSON
def load_data():
    """Cargar datos desde el archivo JSON"""
    if not os.path.exists(DATA_FILE):
        data = init_json_data()
        save_data(data)
        return data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Si hay error, crear archivo nuevo con datos iniciales
        data = init_json_data()
        save_data(data)
        return data
def get_default_data():
    """Datos por defecto si no existe el archivo JSON"""
    return {
        "trayectoria": [
            {
                "id": 1,
                "title": "Ilusión",
                "year": 2018,
                "description": "Inspirado en la emoción que mantiene nuestros sueños y nos impulsa a alcanzarlos, Ilusión narra las peripecias que vive Max, un niño de 7 años...",
                "image": "/static/images/obras/ilusion.jpg"
            },
            {
                "id": 2,
                "title": "Bandurria",
                "year": 2017,
                "description": "Con Bandurria, La Tarumba volvió a poner al Perú en escena para celebrarlo. Una fusión de circo, fantasía del Perú y la magia del Circo en una creación...",
                "image": "/static/images/obras/bandurria.jpg"
            },
            # Agregar más datos según tu JS original...
        ],
        "proyectos": [
            {
                "id": 19,
                "title": "Teatro en las Escuelas",
                "year": 2020,
                "description": "Proyecto educativo que lleva el teatro a instituciones educativas de Trujillo, fomentando la creatividad en niños y jóvenes...",
                "image": "/static/images/proyectos/teatro-escuelas.jpg"
            },
            # Agregar más datos según tu JS original...
        ]
    }

def get_next_id(data):
    """Obtener el siguiente ID disponible"""
    max_id = 0
    for categoria in data.values():
        for obra in categoria:
            if obra['id'] > max_id:
                max_id = obra['id']
    return max_id + 1
def save_data(data):
    """Guardar datos en el archivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_categoria_by_id(categoria_id, data):
    """Obtener categoría por ID"""
    for categoria in data['categorias']:
        if categoria['id'] == categoria_id:
            return categoria
    return None
def load_obras_data():
    """Cargar datos del archivo JSON"""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return get_default_data()
    else:
        return get_default_data()

def save_uploaded_file(file):
    """Guarda el archivo subido y devuelve la ruta relativa"""
    if file and allowed_file(file.filename):
        # Crear directorio si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        try:
            # Guardar archivo
            file.save(file_path)
            
            # Optimizar imagen
            optimize_image(file_path)
            
            # Retornar ruta relativa para usar en templates
            return f"/static/images/obras/{unique_filename}"
            
        except Exception as e:
            print(f"Error guardando archivo: {e}")
            # Limpiar archivo si hubo error
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    return None

def save_obras_data(data):
    """Guardar datos en el archivo JSON"""
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
def get_pregunta_by_id(pregunta_id, data):
    """Obtener pregunta por ID"""
    for pregunta in data['preguntas']:
        if pregunta['id'] == pregunta_id:
            return pregunta
    return None

# Inicializar datos al cargar la aplicación
load_data()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Debes iniciar sesión para acceder a esta sección.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_image(image_path, max_width=1200, max_height=800, quality=85):
    """Optimiza la imagen redimensionándola y comprimiéndola"""
    try:
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar manteniendo proporción
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Guardar con compresión
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error optimizando imagen: {e}")
        return False
    
def cargar_obras():
    """Carga las obras desde el archivo JSON"""
    if os.path.exists(OBRAS_FILE):
        with open(OBRAS_FILE, 'r', encoding='utf-8') as f:
            obras = json.load(f)
            return ordenar_obras_por_mes(obras)
    else:
        return {}

def guardar_obras(obras):
    """Guarda las obras en el archivo JSON"""
    with open(OBRAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(obras, f, ensure_ascii=False, indent=2)

def cargar_servicios():
    """
    Carga los servicios desde el archivo JSON.
    Genera y devuelve las categorías y sus nombres de forma dinámica.
    """
    servicios_data = {}
    if os.path.exists(SERVICIOS_FILE):
        with open(SERVICIOS_FILE, 'r', encoding='utf-8') as f:
            servicios_data = json.load(f)
    else:
        # Si el archivo no existe, inicializa con datos de ejemplo
        servicios_data = {
            'talleres-ninos': [
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres-ninos-1.jpg',
                    'alt': 'Talleres de Verano Niños',
                    'titulo': 'Talleres de Verano Niños',
                    'descripcion': 'Talleres creativos para niños durante las vacaciones',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres-ninos-2.jpg',
                    'alt': 'Talleres Teatro Musical',
                    'titulo': 'Talleres Teatro Musical',
                    'descripcion': 'Aprendizaje de teatro musical para niños',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/TALLERES_INVIERNO_2025_7.png',
                    'alt': 'Talleres Teatro Musical',
                    'titulo': 'Talleres de Invierno 2025',
                    'descripcion': 'Talleres especiales de invierno para niños',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres-ninos-4.jpg',
                    'alt': 'Talleres Teatro Musical',
                    'titulo': 'Talleres Teatro Musical Avanzado',
                    'descripcion': 'Talleres avanzados de teatro musical',
                    'activo': True
                }
            ],
            'talleres-adultos': [
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/TALLERES_INVIERNO_6.png',
                    'alt': 'Talleres Adultos 1',
                    'titulo': 'Talleres de Invierno Adultos',
                    'descripcion': 'Talleres especializados para adultos',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres.png',
                    'alt': 'Talleres Adultos 2',
                    'titulo': 'Talleres Generales',
                    'descripcion': 'Talleres generales para adultos',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres-adultos-3.jpg',
                    'alt': 'Talleres Adultos 2',
                    'titulo': 'Talleres Especializados',
                    'descripcion': 'Talleres especializados para adultos',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/talleres-adultos-4.jpg',
                    'alt': 'Talleres Adultos 2',
                    'titulo': 'Talleres Avanzados',
                    'descripcion': 'Talleres avanzados para adultos',
                    'activo': True
                }
            ],
            'contratos': [
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/obras-beneficas.jpg',
                    'alt': 'Contratos 1',
                    'titulo': 'Obras Benéficas',
                    'descripcion': 'Presentaciones para eventos benéficos',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/eventos-especiales.jpg',
                    'alt': 'Contratos 2',
                    'titulo': 'Eventos Especiales',
                    'descripcion': 'Contratación para eventos especiales',
                    'activo': True
                }
            ],
            'servicios-pre-funcion': [
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/olmo-kiosko.jpg',
                    'alt': 'Servicios Pre-función 1',
                    'titulo': 'Olmo Kiosko',
                    'descripcion': 'Servicios de kiosko antes de la función',
                    'activo': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'imagen': '/static/images/dinamicas-infantiles.jpg',
                    'alt': 'Servicios Pre-función 2',
                    'titulo': 'Dinámicas Infantiles',
                    'descripcion': 'Actividades para niños antes de la función',
                    'activo': True
                }
            ]
        }
        guardar_servicios(servicios_data) # Guarda los datos iniciales si no existían

    # Generar categorías y nombres de categorías dinámicamente
    # Las categorías serán las claves del diccionario servicios_data
    dynamic_categorias = sorted(servicios_data.keys()) # Ordenar alfabéticamente para consistencia
    dynamic_nombres_categorias = {key: key.replace('-', ' ').title() for key in dynamic_categorias}

    return servicios_data, dynamic_categorias, dynamic_nombres_categorias

def guardar_servicios(servicios):
    """Guarda los servicios en el archivo JSON"""
    with open(SERVICIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(servicios, f, ensure_ascii=False, indent=2)

def procesar_fotos_elenco(elenco_nombres, archivos_fotos):
    """Procesa las fotos del elenco y devuelve la estructura de datos"""
    elenco_procesado = []
    
    for i, nombre in enumerate(elenco_nombres):
        if not nombre.strip():
            continue
            
        foto_url = ""
        campo_foto = f"foto_elenco_{i}"
        
        if campo_foto in archivos_fotos:
            file = archivos_fotos[campo_foto]
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"elenco_{uuid.uuid4().hex[:8]}{ext}"
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER_ELENCO'], unique_filename)
                file.save(file_path)
                
                foto_url = f"/static/images/elenco/{unique_filename}"
        
        if not foto_url:
            foto_url = request.form.get(f'foto_url_{i}', '')
        
        elenco_procesado.append({
            "nombre": nombre.strip(),
            "foto": foto_url
        })
    
    return elenco_procesado

@app.route('/')
def home():
    # Cargar datos de obras (dos fuentes distintas)
    obras = cargar_obras()
    obras_data = load_obras_data()

    # Cargar y ordenar servicios
    servicios_data, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios()
    servicios_ordenados = ordenar_servicios(servicios_data)
    categorias_ordenadas = list(servicios_ordenados.keys())
    servicios_lista_ordenada = list(servicios_ordenados.items())

    # Renderizar la plantilla con todos los datos necesarios
    return render_template(
        'index.html',
        obras_data=json.dumps(obras),               # Datos de cargar_obras()
        obras_data1=json.dumps(obras_data),         # Datos de load_obras_data()
        servicios_data=json.dumps(servicios_lista_ordenada),
        categorias=categorias_ordenadas,
        nombres_categorias=nombres_categorias_dinamicos
    )


@app.route('/olmo-mesagges')
@login_required
def whatsapp_sender():
    """Página principal con el enviador de WhatsApp"""
    return render_template('whatsapp_sender.html')

@app.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    """Obtener lista de clientes"""
    return jsonify({
        'success': True,
        'clients': clients_storage,
        'total': len(clients_storage)
    })

@app.route('/api/clients', methods=['POST'])
@login_required
def add_client():
    """Agregar cliente individual"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        if not name or not phone:
            return jsonify({
                'success': False,
                'message': 'Nombre y teléfono son requeridos'
            }), 400
        
        # Formatear teléfono
        formatted_phone = format_phone_number(phone)
        
        # Verificar duplicados
        if any(client['phone'] == formatted_phone for client in clients_storage):
            return jsonify({
                'success': False,
                'message': 'Este número ya existe en la lista'
            }), 400
        
        # Agregar cliente
        client = {
            'id': len(clients_storage) + 1,
            'name': name,
            'phone': formatted_phone
        }
        
        clients_storage.append(client)
        
        return jsonify({
            'success': True,
            'message': 'Cliente agregado correctamente',
            'client': client
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al agregar cliente: {str(e)}'
        }), 500

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@login_required
def delete_client(client_id):
    """Eliminar cliente por ID"""
    global clients_storage
    
    clients_storage = [c for c in clients_storage if c['id'] != client_id]
    
    return jsonify({
        'success': True,
        'message': 'Cliente eliminado correctamente'
    })

@app.route('/api/clients/clear', methods=['DELETE'])
@login_required
def clear_clients():
    """Limpiar todos los clientes"""
    global clients_storage
    clients_storage = []
    
    return jsonify({
        'success': True,
        'message': 'Todos los clientes han sido eliminados'
    })

@app.route('/api/upload-excel', methods=['POST'])
@login_required
def upload_excel():
    """Subir y procesar archivo Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ningún archivo'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ningún archivo'
            }), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'message': 'Solo se permiten archivos Excel (.xlsx, .xls)'
            }), 400
        
        # Leer Excel
        df = pd.read_excel(file)
        
        # Procesar datos
        imported, skipped = process_excel_data(df)
        
        message = f'Se importaron {imported} clientes correctamente'
        if skipped > 0:
            message += f'. {skipped} registros fueron omitidos'
        
        return jsonify({
            'success': True,
            'message': message,
            'imported': imported,
            'skipped': skipped,
            'total_clients': len(clients_storage)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al procesar archivo: {str(e)}'
        }), 500

@app.route('/api/export-excel', methods=['GET'])
@login_required
def export_excel():
    """Exportar clientes a Excel"""
    try:
        if not clients_storage:
            return jsonify({
                'success': False,
                'message': 'No hay clientes para exportar'
            }), 400
        
        # Crear DataFrame
        df = pd.DataFrame(clients_storage)
        
        # Guardar archivo
        filename = 'clientes_whatsapp.xlsx'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df.to_excel(filepath, index=False)
        
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al exportar: {str(e)}'
        }), 500

@app.route('/api/generate-whatsapp-urls', methods=['POST'])
@login_required
def generate_whatsapp_urls():
    """Generar URLs de WhatsApp para todos los clientes"""
    try:
        data = request.get_json()
        message_template = data.get('message', '').strip()
        
        if not message_template:
            return jsonify({
                'success': False,
                'message': 'El mensaje es requerido'
            }), 400
        
        if not clients_storage:
            return jsonify({
                'success': False,
                'message': 'No hay clientes para enviar mensajes'
            }), 400
        
        # Generar URLs
        whatsapp_urls = []
        for client in clients_storage:
            personalized_message = message_template.replace('{nombre}', client['name'])
            clean_phone = ''.join(filter(str.isdigit, client['phone']))
            
            url = f"https://wa.me/{clean_phone}?text={personalized_message}"
            
            whatsapp_urls.append({
                'client': client,
                'url': url,
                'message': personalized_message
            })
        
        return jsonify({
            'success': True,
            'urls': whatsapp_urls,
            'total': len(whatsapp_urls)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar URLs: {str(e)}'
        }), 500

def format_phone_number(phone):
    """Formatear número de teléfono"""
    # Remover caracteres no numéricos excepto +
    cleaned = ''.join(char for char in phone if char.isdigit() or char == '+')
    
    # Agregar código de país si no existe
    if not cleaned.startswith('+'):
        if cleaned.startswith('51'):
            cleaned = '+' + cleaned
        elif cleaned.startswith('9'):
            cleaned = '+51' + cleaned
        else:
            cleaned = '+51' + cleaned
    
    return cleaned

def process_excel_data(df):
    """Procesar datos del Excel"""
    imported = 0
    skipped = 0
    
    # Buscar columnas relevantes
    name_columns = [col for col in df.columns if any(name in col.lower() for name in ['nombre', 'name', 'cliente', 'client'])]
    phone_columns = [col for col in df.columns if any(phone in col.lower() for phone in ['telefono', 'phone', 'celular', 'movil', 'whatsapp', 'tel'])]
    
    name_col = name_columns[0] if name_columns else None
    phone_col = phone_columns[0] if phone_columns else None
    
    if not name_col or not phone_col:
        raise ValueError("No se encontraron columnas de nombre o teléfono válidas")
    
    for index, row in df.iterrows():
        try:
            name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
            phone = str(row[phone_col]).strip() if pd.notna(row[phone_col]) else ''
            
            if name and phone and len(phone.replace('+', '').replace(' ', '')) >= 10:
                formatted_phone = format_phone_number(phone)
                
                # Evitar duplicados
                if not any(client['phone'] == formatted_phone for client in clients_storage):
                    client = {
                        'id': len(clients_storage) + 1,
                        'name': name,
                        'phone': formatted_phone
                    }
                    clients_storage.append(client)
                    imported += 1
                else:
                    skipped += 1
            else:
                skipped += 1
                
        except Exception:
            skipped += 1
    
    return imported, skipped

@app.route('/contactanos')
def contactanos():
    """Vista pública de consultas frecuentes - ahora desde JSON"""
    data = load_data()
    
    # Obtener preguntas activas con sus categorías
    preguntas_con_categoria = []
    for pregunta in data['preguntas']:
        if pregunta['activa']:
            categoria = get_categoria_by_id(pregunta['categoria_id'], data)
            if categoria and categoria['slug'] != 'all':
                pregunta_data = (
                    pregunta['id'],
                    pregunta['pregunta'],
                    pregunta['respuesta'],
                    categoria['nombre'],
                    categoria['slug']
                )
                preguntas_con_categoria.append(pregunta_data)
    
    # Ordenar por categoría y orden
    preguntas_con_categoria.sort(key=lambda x: (x[3], 
                                  next((p['orden'] for p in data['preguntas'] if p['id'] == x[0]), 0), 
                                  x[0]))
    
    # Obtener categorías que tienen preguntas activas
    categorias_con_preguntas = set()
    for pregunta in data['preguntas']:
        if pregunta['activa']:
            categoria = get_categoria_by_id(pregunta['categoria_id'], data)
            if categoria and categoria['slug'] != 'all':
                categorias_con_preguntas.add((categoria['id'], categoria['nombre'], categoria['slug']))
    
    categorias_activas = list(categorias_con_preguntas)
    categorias_activas.sort(key=lambda x: x[1])
    
    return render_template('contactanos.html', 
                         preguntas=preguntas_con_categoria, 
                         categorias=categorias_activas)

@app.route('/api/obras')
@login_required
def api_obras():
    """API para obtener las obras actuales"""
    obras = cargar_obras()
    return jsonify(obras)

@app.route('/api/servicios')
@login_required
def api_servicios():
    """API para obtener los servicios actuales"""
    servicios_data, _, _ = cargar_servicios() # Solo necesitamos los datos de servicios aquí
    return jsonify(servicios_data)

# ============= RUTAS DE ADMINISTRACIÓN DE OBRAS =============
@app.route('/admin-teatro-olmo-2025/obras')
@login_required
def admin_obras():
    """Panel de administración de obras"""
    obras = cargar_obras()
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('admin_obras.html', obras=obras, meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/nueva')
@login_required
def nueva_obra_sin_mes():
    """Formulario para crear nueva obra sin mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/nueva/<mes>')
@login_required
def nueva_obra(mes):
    """Formulario para crear nueva obra en mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', mes=mes, meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/editar/<mes>/<int:obra_index>')
@login_required
def editar_obra(mes, obra_index):
    """Formulario para editar obra existente"""
    obras = cargar_obras()
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra = obras[mes]['obras'][obra_index]
        meses_disponibles = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        return render_template('editar_obra.html', mes=mes, obra=obra, obra_index=obra_index, meses_disponibles=meses_disponibles)
    else:
        flash('Obra no encontrada', 'error')
        return redirect(url_for('admin_obras'))

@app.route('/admin-teatro-olmo-2025/obra/guardar', methods=['POST'])
@login_required
def guardar_obra():
    """Guarda una nueva obra o actualiza una existente"""
    obras = cargar_obras()
    
    mes = request.form.get('mes', '').strip()
    titulo = request.form.get('titulo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    activar_desde = request.form.get('activar_desde', '').strip()
    
    if not mes or not titulo or not descripcion or not activar_desde:
        flash('Todos los campos son obligatorios', 'error')
        return redirect(request.referrer)
    
    try:
        fecha_activar = datetime.strptime(activar_desde, "%Y-%m-%d")
    except ValueError:
        flash('Formato de fecha "activarDesde" inválido. Debe ser YYYY-MM-DD.', 'error')
        return redirect(request.referrer)
    
    obra_index = request.form.get('obra_index')
    is_editing = obra_index is not None and obra_index.isdigit()
    
    # Manejar la imagen
    imagen_url = None
    
    # Si estamos editando, obtener la imagen actual como fallback
    if is_editing:
        obra_index_int = int(obra_index)
        if mes in obras and obra_index_int < len(obras[mes]['obras']):
            imagen_url = obras[mes]['obras'][obra_index_int]['imagen']  # Imagen actual como fallback
    
    # Verificar si se subió una nueva imagen
    if 'imagen_archivo' in request.files:
        file = request.files['imagen_archivo']
        print(f"Archivo de imagen recibido: {file.filename}")
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(f"Archivo seguro: {filename}")
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Si estamos editando y había una imagen anterior, eliminarla
            if is_editing and imagen_url and imagen_url.startswith('/static/images/obras/'):
                try:
                    os.remove(imagen_url[1:])  # Quitar el '/' inicial
                    print(f"Imagen anterior eliminada: {imagen_url}")
                except Exception as e:
                    app.logger.warning(f"No se pudo eliminar la imagen anterior: {e}")
            
            # Actualizar con la nueva imagen
            imagen_url = f"/static/images/obras/{unique_filename}"
    
    # Validar que tengamos una imagen
    if not imagen_url:
        if is_editing:
            flash('Error al procesar la imagen', 'error')
        else:
            flash('Debes proporcionar una imagen para la obra', 'error')
        return redirect(request.referrer)
    
    # Procesar fechas
    fechas_input = request.form.get('fechas', '').strip()
    fechas = []
    for fecha_str in fechas_input.split(','):
        fecha_str = fecha_str.strip()
        if fecha_str:
            partes = fecha_str.split()
            if len(partes) == 2:
                fechas.append({"dia": partes[0], "mes": partes[1].lower()})
            else:
                fechas.append({"dia": partes[0], "mes": mes.lower()})
    
    # Procesar elenco
    elenco_nombres = [nombre.strip() for nombre in request.form.getlist('elenco[]') if nombre.strip()]
    elenco = procesar_fotos_elenco(elenco_nombres, request.files)
    
    # Crear objeto obra
    nueva_obra = {
        "activarDesde": activar_desde,
        "imagen": imagen_url,
        "titulo": titulo,
        "descripcion": descripcion,
        "fechas": fechas,
        "elenco": elenco
    }
    
    # Asegurar que el mes existe
    if mes not in obras:
        obras[mes] = {"obras": []}
    
    # Guardar o actualizar la obra
    if is_editing:
        obra_index_int = int(obra_index)
        if obra_index_int < 0 or obra_index_int >= len(obras[mes]['obras']):
            flash('Índice de obra inválido', 'error')
            return redirect(request.referrer)
        
        # Al editar, si no se cambió la imagen, mantener las fotos del elenco anterior
        obra_anterior = obras[mes]['obras'][obra_index_int]
        
        # Solo eliminar fotos del elenco si se está actualizando con nuevas fotos
        if 'elenco' in obra_anterior:
            for actor in obra_anterior['elenco']:
                if isinstance(actor, dict) and 'foto' in actor:
                    if actor['foto'].startswith('/static/images/elenco/'):
                        try:
                            os.remove(actor['foto'][1:])
                        except Exception as e:
                            app.logger.warning(f"No se pudo eliminar foto del elenco: {e}")
        
        obras[mes]['obras'][obra_index_int] = nueva_obra
        flash(f'Obra "{titulo}" actualizada exitosamente', 'success')
    else:
        # Nueva obra
        obras[mes]['obras'].append(nueva_obra)
        flash(f'Obra "{titulo}" creada exitosamente en {mes}', 'success')

    # Ordenar y guardar
    obras = ordenar_obras_por_mes(obras)
    guardar_obras(obras)
    return redirect(url_for('admin_obras'))

@app.route('/admin-teatro-olmo-2025/obra/eliminar/<mes>/<int:obra_index>')
@login_required
def eliminar_obra(mes, obra_index):
    """Elimina una obra"""
    obras = cargar_obras()
    
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra_eliminada = obras[mes]['obras'].pop(obra_index)
        
        # Eliminar imagen de la obra si es un archivo local
        if obra_eliminada['imagen'].startswith('/static/images/obras/'):
            try:
                os.remove(obra_eliminada['imagen'][1:])
                print(f"Imagen eliminada: {obra_eliminada['imagen']}")
            except Exception as e:
                app.logger.warning(f"No se pudo eliminar la imagen: {e}")
        
        # Eliminar fotos del elenco si son archivos locales
        if 'elenco' in obra_eliminada and isinstance(obra_eliminada['elenco'], list):
            for actor in obra_eliminada['elenco']:
                if isinstance(actor, dict) and 'foto' in actor:
                    if actor['foto'].startswith('/static/images/elenco/'):
                        try:
                            os.remove(actor['foto'][1:])
                            print(f"Foto del elenco eliminada: {actor['foto']}")
                        except Exception as e:
                            app.logger.warning(f"No se pudo eliminar foto del elenco: {e}")
        
        # Si no quedan más obras en el mes, eliminar el mes completo
        if len(obras[mes]['obras']) == 0:
            del obras[mes]
            flash(f'Obra "{obra_eliminada["titulo"]}" eliminada y mes {mes} removido', 'success')
        else:
            flash(f'Obra "{obra_eliminada["titulo"]}" eliminada exitosamente', 'success')
        
        guardar_obras(obras)
    else:
        flash('Obra no encontrada', 'error')
    
    return redirect(url_for('admin_obras'))

# ============= RUTAS DE ADMINISTRACIÓN DE SERVICIOS (MODIFICADAS) =============
@app.route('/admin-teatro-olmo-2025/servicios')
@login_required
def admin_servicios():
    """
    Panel de administración de servicios con filtros por estado y categoría.
    Permite filtrar los servicios mostrados en la tabla.
    """
    servicios_data, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios() # Carga todos los servicios y categorías dinámicas
    servicios_filtrados = {}

    # Obtener parámetros de filtro de la URL
    filtro_activo_str = request.args.get('filtro_activo') # 'true', 'false', o None
    filtro_categoria = request.args.get('filtro_categoria') # 'teatro', 'musica', 'todos', o None

    # Convertir el string 'filtro_activo' a booleano o None
    filtro_activo = None
    if filtro_activo_str == 'true':
        filtro_activo = True
    elif filtro_activo_str == 'false':
        filtro_activo = False

    # Aplicar filtros
    for categoria_key, lista_servicios in servicios_data.items(): # Iterar sobre servicios_data
        # Filtrar por categoría
        if filtro_categoria and filtro_categoria != 'todos' and categoria_key != filtro_categoria:
            continue # Saltar esta categoría si no coincide con el filtro

        servicios_en_categoria_filtrados = []
        for servicio in lista_servicios:
            # Filtrar por estado 'activo'
            if filtro_activo is not None:
                if servicio.get('activo', True) == filtro_activo:
                    servicios_en_categoria_filtrados.append(servicio)
            else:
                # Si no hay filtro de activo, añadir todos los servicios de la categoría
                servicios_en_categoria_filtrados.append(servicio)
        
        # Si quedan servicios después de filtrar, añadirlos al resultado final
        if servicios_en_categoria_filtrados:
            servicios_filtrados[categoria_key] = servicios_en_categoria_filtrados

    print(servicios_filtrados) # Verifica qué datos estás obteniendo después del filtro
    servicios_ordenados = ordenar_servicios(servicios_filtrados)
    return render_template('admin_servicios.html', 
                           servicios=servicios_ordenados, # Pasa los servicios filtrados
                           categorias=categorias_dinamicas, # Pasa las categorías dinámicas
                           nombres_categorias=nombres_categorias_dinamicos, # Pasa los nombres de categorías dinámicos
                           filtro_activo_seleccionado=filtro_activo_str, # Para mantener el estado del filtro en el HTML
                           filtro_categoria_seleccionada=filtro_categoria) # Para mantener el estado del filtro en el HTML

@app.route('/admin-teatro-olmo-2025/servicio/nuevo')
@login_required
def nuevo_servicio():
    """Formulario para crear nuevo servicio"""
    _, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios() # Carga categorías dinámicas
    return render_template('nuevo_servicio.html', 
                           categorias=categorias_dinamicas,
                           nombres_categorias=nombres_categorias_dinamicos)

@app.route('/admin-teatro-olmo-2025/servicio/editar/<categoria>/<servicio_id>', methods=['GET', 'POST'])
@login_required
def editar_servicio(categoria, servicio_id):
    """Formulario para editar servicio existente"""
    
    servicios_data, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios() # Función para cargar los servicios y categorías dinámicas
    
    # Verificar si la categoría existe en los servicios cargados
    if categoria not in servicios_data:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('admin_servicios')) 
    
    # Buscar el servicio en la categoría especificada
    servicio = None
    for s in servicios_data[categoria]:
        if s['id'] == servicio_id:
            servicio = s
            break
    
    # Verificar si el servicio existe
    if not servicio:
        flash('Servicio no encontrado', 'error')
        return redirect(url_for('admin_servicios')) 
    
    # Si la solicitud es POST (cuando el formulario se envía)
    if request.method == 'POST':
        # Procesar los datos del formulario y guardar
        return guardar_servicio() 
    
    # Si la solicitud es GET (cuando se carga el formulario)
    return render_template('editar_servicio.html', 
                           servicio=servicio, 
                           categoria=categoria,
                           categorias=categorias_dinamicas, # Pasa las categorías dinámicas
                           nombres_categorias=nombres_categorias_dinamicos) # Pasa los nombres de categorías dinámicos


@app.route('/admin-teatro-olmo-2025/servicio/guardar', methods=['POST'])
@login_required
def guardar_servicio():
    """Guarda un nuevo servicio o actualiza uno existente"""
    servicios_data, _, _ = cargar_servicios() # Carga solo los datos de servicios
    
    # Obtener datos del formulario
    categoria = request.form.get('categoria', '').strip()
    titulo = request.form.get('titulo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    alt = request.form.get('alt', '').strip()
    activo = request.form.get('activo') == 'on'
    
    # Verifica que los campos de título, descripción y categoría no estén vacíos
    print(f"Categoria: {categoria}")
    print(f"Título: {titulo}")
    print(f"Descripción: {descripcion}")
    print(f"Activo: {activo}")
    print(f"Alt: {alt}")
    
    # Validaciones de campos obligatorios
    if not categoria or not titulo or not descripcion:
        flash('Categoría, título y descripción son obligatorios', 'error')
        return redirect(request.referrer)
    
    # Ya no necesitamos validar 'categoria not in CATEGORIAS_SERVICIOS' aquí
    # porque las categorías pueden ser nuevas y se añadirán si no existen en 'servicios_data'

    # Procesar imagen
    imagen_url = None
    
    # Verificar si se sube un archivo de imagen
    if 'imagen_archivo' in request.files:
        file = request.files['imagen_archivo']
        print(f"Imagen archivo recibido: {file}")
        
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"servicio_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER_SERVICIOS'], unique_filename)
            file.save(file_path)
            imagen_url = f"/static/images/servicios/{unique_filename}"
            print(f"Imagen guardada en: {imagen_url}")
        elif file and file.filename != '':
            flash("El archivo seleccionado no es una imagen válida.", "error")
            return redirect(request.referrer)
    
    # Si no se sube un archivo, utilizar la URL proporcionada
    if not imagen_url:
        imagen_url = request.form.get('imagen_url', '').strip()
        print(f"Imagen URL proporcionada: {imagen_url}")
        if imagen_url and not valid_url(imagen_url):
            flash("La URL de la imagen no es válida.", "error")
            return redirect(request.referrer)
    
    # Obtener el ID de servicio si se está editando un servicio existente
    servicio_id = request.form.get('servicio_id')
    
    if servicio_id:  # Editando servicio existente
        print(f"Editando servicio con ID: {servicio_id}")
        servicio_encontrado = False
        # Asegurarse de que la categoría existe en 'servicios_data' antes de intentar iterar
        if categoria in servicios_data:
            for i, servicio in enumerate(servicios_data.get(categoria, [])):
                if servicio['id'] == servicio_id:
                    servicio_anterior = servicios_data[categoria][i].copy()
                    
                    # Eliminar imagen anterior si se subió una nueva
                    if 'imagen_archivo' in request.files and request.files['imagen_archivo'].filename != '':
                        if servicio_anterior['imagen'].startswith('/static/images/servicios/'):
                            try:
                                os.remove(servicio_anterior['imagen'][1:])
                            except Exception as e:
                                app.logger.warning(f"No se pudo eliminar la imagen anterior: {e}")
                    
                    # Actualizar servicio
                    servicios_data[categoria][i] = {
                        'id': servicio_id,
                        'titulo': titulo,
                        'descripcion': descripcion,
                        'imagen': imagen_url or servicio_anterior['imagen'],
                        'alt': alt or titulo,
                        'activo': activo
                    }
                    
                    servicio_encontrado = True
                    flash(f'Servicio "{titulo}" actualizado exitosamente', 'success')
                    break
        
        if not servicio_encontrado:
            flash('Servicio no encontrado', 'error')
            return redirect(request.referrer)
    
    else:  # Creando nuevo servicio
        print(f"Creando nuevo servicio: {titulo}")
        
        # Si la categoría no existe en el diccionario de servicios, la crea
        if categoria not in servicios_data:
            servicios_data[categoria] = []
        
        nuevo_servicio = {
            'id': str(uuid.uuid4()),
            'titulo': titulo,
            'descripcion': descripcion,
            'imagen': imagen_url,
            'alt': alt or titulo,
            'activo': activo
        }
        
        servicios_data[categoria].append(nuevo_servicio)
        flash(f'Servicio "{titulo}" creado exitosamente', 'success')
    
    # Guardar los cambios
    guardar_servicios(servicios_data)
    return redirect(url_for('admin_servicios'))


def valid_url(url):
    """Valida si la URL proporcionada es válida y apunta a una imagen."""
    regex = r'^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}(/[\w-]*)*(\.(jpg|jpeg|png|gif|bmp))$'
    return bool(re.match(regex, url))

@app.route('/admin-teatro-olmo-2025/servicio/eliminar/<categoria>/<servicio_id>')
@login_required
def eliminar_servicio(categoria, servicio_id):
    """Elimina un servicio"""
    servicios_data, _, _ = cargar_servicios() # Carga solo los datos de servicios
    
    if categoria not in servicios_data:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('admin_servicios'))
    
    servicio_eliminado = None
    for i, servicio in enumerate(servicios_data[categoria]):
        if servicio['id'] == servicio_id:
            servicio_eliminado = servicios_data[categoria].pop(i)
            break
    
    if servicio_eliminado:
        # Eliminar imagen si es local
        if servicio_eliminado['imagen'].startswith('/static/images/servicios/'):
            try:
                os.remove(servicio_eliminado['imagen'][1:])
            except Exception as e:
                app.logger.warning(f"No se pudo eliminar la imagen: {e}")
        
        # Si no quedan servicios en la categoría, eliminar la categoría del diccionario
        if len(servicios_data[categoria]) == 0:
            del servicios_data[categoria]
        
        guardar_servicios(servicios_data)
        flash(f'Servicio "{servicio_eliminado["titulo"]}" eliminado exitosamente', 'success')
    else:
        flash('Servicio no encontrado', 'error')
    
    return redirect(url_for('admin_servicios'))


@app.route('/admin-teatro-olmo-2025/servicio/toggle/<categoria>/<servicio_id>')
@login_required
def toggle_servicio(categoria, servicio_id):
    """Activa/desactiva un servicio"""
    servicios_data, _, _ = cargar_servicios() # Carga solo los datos de servicios
    
    if categoria not in servicios_data:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('admin_servicios'))
    
    for servicio in servicios_data[categoria]:
        if servicio['id'] == servicio_id:
            servicio['activo'] = not servicio.get('activo', True)
            guardar_servicios(servicios_data)
            estado = 'activado' if servicio['activo'] else 'desactivado'
            flash(f'Servicio "{servicio["titulo"]}" {estado}', 'success')
            break
    else:
        flash('Servicio no encontrado', 'error')
    
    return redirect(url_for('admin_servicios'))

def ordenar_obras_por_mes(obras):
    """Ordena el diccionario obras por mes y dentro de cada mes por activarDesde"""
    for mes in obras:
        # Asegúrate de que 'obras' dentro de cada mes sea una lista antes de intentar ordenar
        if 'obras' in obras[mes] and isinstance(obras[mes]['obras'], list):
            obras[mes]['obras'].sort(key=lambda obra: obra.get('activarDesde', ''))
    
    obras_ordenadas = dict(
        sorted(
            obras.items(),
            key=lambda item: ORDEN_MESES.index(item[0]) if item[0] in ORDEN_MESES else 99
        )
    )
    
    return obras_ordenadas

def ordenar_servicios(servicios):
    servicios_ordenados = OrderedDict()

    for clave in ORDEN_FILTROS:
        if clave in servicios:
            servicios_ordenados[clave] = servicios[clave]

    # Agrega las categorías que no están en ORDEN_FILTROS al final
    for clave in servicios:
        if clave not in ORDEN_FILTROS:
            servicios_ordenados[clave] = servicios[clave]

    return servicios_ordenados

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('admin_servicios'))  # Evita repetir login

    if request.method == 'POST':
        usuario = request.form['username']
        clave = request.form['password']
        if usuario == USERNAME and clave == PASSWORD:
            session['logged_in'] = True
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('admin_servicios'))
        else:
            flash('Credenciales incorrectas', 'error')

    return render_template('login.html')

@app.route('/admin/consultas')
@login_required
def admin_consultas():
    """Vista principal de administración de consultas frecuentes"""
    data = load_data()
    
    # Preparar datos para el template (similar a como venían de SQLite)
    preguntas_con_categoria = []
    for pregunta in data['preguntas']:
        categoria = get_categoria_by_id(pregunta['categoria_id'], data)
        if categoria and categoria['slug'] != 'all':
            pregunta_data = (
                pregunta['id'],
                pregunta['pregunta'],
                pregunta['respuesta'],
                pregunta['activa'],
                pregunta['orden'],
                categoria['nombre'],
                categoria['slug']
            )
            preguntas_con_categoria.append(pregunta_data)
    
    # Ordenar por categoría y orden
    preguntas_con_categoria.sort(key=lambda x: (x[5], x[4], x[0]))
    
    # Obtener categorías (excepto "Todas")
    categorias = [(cat['id'], cat['nombre'], cat['slug']) 
                  for cat in data['categorias'] if cat['slug'] != 'all']
    categorias.sort(key=lambda x: x[1])
    
    return render_template('admin_consultas.html', 
                         preguntas=preguntas_con_categoria, 
                         categorias=categorias)

@app.route('/admin/consultas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_consulta():
    """Crear nueva consulta frecuente"""
    data = load_data()
    
    if request.method == 'POST':
        pregunta = request.form['pregunta'].strip()
        respuesta = request.form['respuesta'].strip()
        categoria_id = int(request.form['categoria_id'])
        orden = int(request.form.get('orden', 0))
        
        # Crear nueva pregunta
        nueva_pregunta = {
            "id": data['next_pregunta_id'],
            "pregunta": pregunta,
            "respuesta": respuesta,
            "categoria_id": categoria_id,
            "activa": True,
            "orden": orden,
            "creado_en": datetime.now().isoformat()
        }
        
        data['preguntas'].append(nueva_pregunta)
        data['next_pregunta_id'] += 1
        
        save_data(data)
        flash('Consulta creada exitosamente', 'success')
        return redirect(url_for('admin_consultas'))
    
    # GET - Mostrar formulario
    categorias = [(cat['id'], cat['nombre']) 
                  for cat in data['categorias'] if cat['slug'] != 'all']
    categorias.sort(key=lambda x: x[1])
    
    return render_template('admin_consultas.html', categorias=categorias, modo='crear')

@app.route('/admin/consultas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_consulta(id):
    """Editar consulta frecuente existente"""
    data = load_data()
    pregunta_actual = get_pregunta_by_id(id, data)
    
    if not pregunta_actual:
        flash('Consulta no encontrada', 'error')
        return redirect(url_for('admin_consultas'))
    
    if request.method == 'POST':
        pregunta_actual['pregunta'] = request.form['pregunta'].strip()
        pregunta_actual['respuesta'] = request.form['respuesta'].strip()
        pregunta_actual['categoria_id'] = int(request.form['categoria_id'])
        pregunta_actual['orden'] = int(request.form.get('orden', 0))
        pregunta_actual['activa'] = 'activa' in request.form
        
        save_data(data)
        flash('Consulta actualizada exitosamente', 'success')
        return redirect(url_for('admin_consultas'))
    
    # GET - Mostrar formulario con datos existentes
    categorias = [(cat['id'], cat['nombre']) 
                  for cat in data['categorias'] if cat['slug'] != 'all']
    categorias.sort(key=lambda x: x[1])
    
    # Convertir a tupla para compatibilidad con template
    pregunta_tuple = (
        pregunta_actual['id'],
        pregunta_actual['pregunta'],
        pregunta_actual['respuesta'],
        pregunta_actual['categoria_id'],
        pregunta_actual['orden'],
        pregunta_actual['activa']
    )
    
    return render_template('admin_consultas.html', 
                         pregunta_actual=pregunta_tuple,
                         categorias=categorias, 
                         modo='editar')

@app.route('/admin/consultas/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_consulta(id):
    """Eliminar consulta frecuente"""
    data = load_data()
    
    # Buscar y eliminar la pregunta
    data['preguntas'] = [p for p in data['preguntas'] if p['id'] != id]
    
    save_data(data)
    flash('Consulta eliminada exitosamente', 'success')
    return redirect(url_for('admin_consultas'))

@app.route('/admin/consultas/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_consulta(id):
    """Activar/Desactivar consulta frecuente"""
    data = load_data()
    pregunta = get_pregunta_by_id(id, data)
    
    if pregunta:
        pregunta['activa'] = not pregunta['activa']
        save_data(data)
        return jsonify({'success': True})
    
    return jsonify({'success': False})

# RUTAS PARA GESTIÓN DE CATEGORÍAS

@app.route('/admin/categorias/nueva', methods=['POST'])
@login_required
def nueva_categoria():
    """Crear nueva categoría"""
    data = load_data()
    nombre = request.form['nombre'].strip()
    
    # Crear slug from nombre
    slug = nombre.lower().replace(' ', '_')
    # Reemplazar caracteres especiales
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    
    # Verificar que no exista una categoría con el mismo nombre o slug
    for categoria in data['categorias']:
        if categoria['nombre'].lower() == nombre.lower() or categoria['slug'] == slug:
            flash('Ya existe una categoría con ese nombre', 'error')
            return redirect(url_for('admin_consultas'))
    
    # Crear nueva categoría
    nueva_categoria = {
        "id": data['next_categoria_id'],
        "nombre": nombre,
        "slug": slug,
        "creado_en": datetime.now().isoformat()
    }
    
    data['categorias'].append(nueva_categoria)
    data['next_categoria_id'] += 1
    
    save_data(data)
    flash('Categoría creada exitosamente', 'success')
    return redirect(url_for('admin_consultas'))

# Rutas CRUD para administración
@app.route('/admin_obras_historicas')
@login_required
def admin_obras_historicas():
    """Panel de administración de obras históricas"""
    obras_data = load_obras_data()
    
    # Calcular estadísticas para mostrar
    total_trayectoria = len(obras_data.get('trayectoria', []))
    total_proyectos = len(obras_data.get('proyectos', []))
    
    # Calcular páginas
    items_per_page = 9
    paginas_trayectoria = math.ceil(total_trayectoria / items_per_page)
    paginas_proyectos = math.ceil(total_proyectos / items_per_page)
    
    stats = {
        'total_trayectoria': total_trayectoria,
        'total_proyectos': total_proyectos,
        'paginas_trayectoria': paginas_trayectoria,
        'paginas_proyectos': paginas_proyectos
    }
    
    return render_template('admin_obras_historicas.html', 
                         obras_data=obras_data, 
                         stats=stats)

@app.route('/obras_historicas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_obra_historica():
    """Crear nueva obra"""
    if request.method == 'POST':
        obras_data = load_obras_data()
        
        # Obtener datos del formulario
        categoria = request.form.get('categoria')
        title = request.form.get('title')
        year_str = request.form.get('year')
        description = request.form.get('description')
        
        # Validar año
        try:
            year = int(year_str) if year_str else None
        except ValueError:
            year = None
        
        # Validaciones básicas
        if not all([categoria, title, year, description]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('nueva_obra_historica.html')
        
        if categoria not in ['trayectoria', 'proyectos']:
            flash('Categoría no válida', 'error')
            return render_template('nueva_obra_historica.html')
        
        # Procesar imagen
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Verificar tamaño del archivo
                if request.content_length > MAX_FILE_SIZE:
                    flash('El archivo es demasiado grande. Máximo 16MB permitido.', 'error')
                    return render_template('nueva_obra_historica.html')
                
                image_path = save_uploaded_file(file)
                if not image_path:
                    flash('Error al procesar la imagen. Verifica el formato (PNG, JPG, JPEG, GIF, WEBP).', 'error')
                    return render_template('nueva_obra_historica.html')
        
        if not image_path:
            flash('Debe seleccionar una imagen', 'error')
            return render_template('nueva_obra_historica.html')
        
        # Crear nueva obra
        nueva_obra = {
            'id': get_next_id(obras_data),
            'title': title,
            'year': year,
            'description': description,
            'image': image_path
        }
        
        # Agregar a la categoría correspondiente
        if categoria not in obras_data:
            obras_data[categoria] = []
        
        obras_data[categoria].append(nueva_obra)
        
        # Guardar datos
        if save_obras_data(obras_data):
            flash(f'Obra "{title}" agregada exitosamente a {categoria}', 'success')
            return redirect(url_for('admin_obras_historicas'))
        else:
            flash('Error al guardar la obra', 'error')
    
    return render_template('nueva_obra_historica.html')

@app.route('/obras_historicas/editar/<int:obra_id>', methods=['GET', 'POST'])
@login_required
def editar_obra_historica(obra_id):
    """Editar obra existente"""
    obras_data = load_obras_data()
    
    # Buscar la obra
    obra = None
    categoria_actual = None
    
    for cat_name, obras in obras_data.items():
        for o in obras:
            if o['id'] == obra_id:
                obra = o
                categoria_actual = cat_name
                break
        if obra:
            break
    
    if not obra:
        flash('Obra no encontrada', 'error')
        return redirect(url_for('admin_obras_historicas'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nueva_categoria = request.form.get('categoria')
        title = request.form.get('title')
        year_str = request.form.get('year')
        description = request.form.get('description')
        
        # Validar año
        try:
            year = int(year_str) if year_str else None
        except ValueError:
            year = None
        
        # Validaciones
        if not all([nueva_categoria, title, year, description]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('editar_obra_historica.html', obra=obra, categoria_actual=categoria_actual)
        
        if nueva_categoria not in ['trayectoria', 'proyectos']:
            flash('Categoría no válida', 'error')
            return render_template('editar_obra_historica.html', obra=obra, categoria_actual=categoria_actual)
        
        # Procesar nueva imagen si se subió
        image_path = obra['image']  # Mantener imagen actual por defecto
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Verificar tamaño del archivo
                if request.content_length > MAX_FILE_SIZE:
                    flash('El archivo es demasiado grande. Máximo 16MB permitido.', 'error')
                    return render_template('editar_obra_historica.html', obra=obra, categoria_actual=categoria_actual)
                
                new_image_path = save_uploaded_file(file)
                if new_image_path:
                    # Eliminar imagen anterior si existe y no es la imagen por defecto
                    old_image_path = obra['image']
                    if old_image_path and old_image_path.startswith('/static/images/obras/'):
                        old_file_path = old_image_path[1:]  # Remover '/' inicial
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except Exception as e:
                                print(f"Error eliminando imagen anterior: {e}")
                    
                    image_path = new_image_path
                else:
                    flash('Error al procesar la nueva imagen. Se mantuvo la imagen actual.', 'error')
        
        # Si cambió de categoría, mover la obra
        if nueva_categoria != categoria_actual:
            # Remover de categoría actual
            obras_data[categoria_actual] = [o for o in obras_data[categoria_actual] if o['id'] != obra_id]
            
            # Agregar a nueva categoría
            if nueva_categoria not in obras_data:
                obras_data[nueva_categoria] = []
        
        # Actualizar datos de la obra
        obra_actualizada = {
            'id': obra_id,
            'title': title,
            'year': year,
            'description': description,
            'image': image_path
        }
        
        # Encontrar y actualizar la obra en la nueva categoría
        if nueva_categoria != categoria_actual:
            obras_data[nueva_categoria].append(obra_actualizada)
        else:
            for i, o in enumerate(obras_data[categoria_actual]):
                if o['id'] == obra_id:
                    obras_data[categoria_actual][i] = obra_actualizada
                    break
        
        # Guardar datos
        if save_obras_data(obras_data):
            flash(f'Obra "{title}" actualizada exitosamente', 'success')
            return redirect(url_for('admin_obras_historicas'))
        else:
            flash('Error al actualizar la obra', 'error')
    
    return render_template('editar_obra_historica.html', obra=obra, categoria_actual=categoria_actual)

@app.route('/obras_historicas/eliminar/<int:obra_id>', methods=['POST'])
@login_required
def eliminar_obra_historica(obra_id):
    """Eliminar obra"""
    obras_data = load_obras_data()
    
    # Buscar y eliminar la obra
    obra_eliminada = False
    obra_title = ""
    
    for cat_name, obras in obras_data.items():
        for i, obra in enumerate(obras):
            if obra['id'] == obra_id:
                obra_title = obra['title']
                del obras_data[cat_name][i]
                obra_eliminada = True
                break
        if obra_eliminada:
            break
    
    if obra_eliminada:
        if save_obras_data(obras_data):
            flash(f'Obra "{obra_title}" eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la obra', 'error')
    else:
        flash('Obra no encontrada', 'error')
    
    return redirect(url_for('admin_obras_historicas'))

# API endpoint para obtener datos (para tu JavaScript)
@app.route('/api/obras_historicas')
@login_required
def api_obras_historicas():
    """API para obtener datos de obras históricas"""
    obras_data = load_obras_data()
    return jsonify(obras_data)
# Logout

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Sesión cerrada', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Asegúrate de crear las carpetas de subida si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_ELENCO'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_SERVICIOS'], exist_ok=True)
    app.run(debug=True)