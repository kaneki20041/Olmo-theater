from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
import uuid
import secrets
import re # Asegúrate de que 're' esté importado para 'valid_url'
import logging # Importar el módulo logging
from collections import OrderedDict

# Carga las variables de entorno desde .flaskenv o .env
load_dotenv()

app = Flask(__name__)
# Generar una clave secreta segura (guárdala en tu .env para producción)
app.secret_key = 'sk_teatro_2025_9f8e7d6c5b4a3e2f1d0c9b8a7f6e5d4c3b2a1f0e'

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/images/obras'
UPLOAD_FOLDER_ELENCO = 'static/images/elenco'
UPLOAD_FOLDER_SERVICIOS = 'static/images/servicios'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_ELENCO'] = UPLOAD_FOLDER_ELENCO
app.config['UPLOAD_FOLDER_SERVICIOS'] = UPLOAD_FOLDER_SERVICIOS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

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

# Las variables CATEGORIAS_SERVICIOS y NOMBRES_CATEGORIAS ya no son globales y estáticas
# Ahora se generarán dinámicamente dentro de cargar_servicios()

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    obras = cargar_obras()
    servicios_data, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios() 
    servicios_ordenados = ordenar_servicios(servicios_data)

    categorias_ordenadas = list(servicios_ordenados.keys())

    servicios_lista_ordenada = list(servicios_ordenados.items())

    return render_template('index.html', 
        obras_data=json.dumps(obras), 
        servicios_data=json.dumps(servicios_lista_ordenada),
        categorias=categorias_ordenadas,  # <- Usar categorías ordenadas aquí
        nombres_categorias=nombres_categorias_dinamicos)


@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

@app.route('/api/obras')
def api_obras():
    """API para obtener las obras actuales"""
    obras = cargar_obras()
    return jsonify(obras)

@app.route('/api/servicios')
def api_servicios():
    """API para obtener los servicios actuales"""
    servicios_data, _, _ = cargar_servicios() # Solo necesitamos los datos de servicios aquí
    return jsonify(servicios_data)

# ============= RUTAS DE ADMINISTRACIÓN DE OBRAS =============
@app.route('/admin-teatro-olmo-2025/obras')
def admin_obras():
    """Panel de administración de obras"""
    obras = cargar_obras()
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('admin_obras.html', obras=obras, meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/nueva')
def nueva_obra_sin_mes():
    """Formulario para crear nueva obra sin mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/nueva/<mes>')
def nueva_obra(mes):
    """Formulario para crear nueva obra en mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', mes=mes, meses_disponibles=meses_disponibles)

@app.route('/admin-teatro-olmo-2025/obra/editar/<mes>/<int:obra_index>')
def editar_obra(mes, obra_index):
    """Formulario para editar obra existente"""
    obras = cargar_obras()
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra = obras[mes]['obras'][obra_index]
        return render_template('editar_obra.html', mes=mes, obra=obra, obra_index=obra_index)
    else:
        flash('Obra no encontrada', 'error')
        return redirect(url_for('admin_obras'))

@app.route('/admin-teatro-olmo-2025/obra/guardar', methods=['POST'])
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
        flash('Formato de fecha "activarDesde" inválido. Debe serYYYY-MM-DD.', 'error')
        return redirect(request.referrer)
    
    imagen_url = None
    
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
            imagen_url = f"/static/images/obras/{unique_filename}"
    
    if not imagen_url:
        imagen_url = request.form.get('imagen_url', '').strip()
    
    if not imagen_url:
        flash('Debes proporcionar una imagen (archivo o URL)', 'error')
        return redirect(request.referrer)
    
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
    
    elenco_nombres = [nombre.strip() for nombre in request.form.getlist('elenco[]') if nombre.strip()]
    elenco = procesar_fotos_elenco(elenco_nombres, request.files)
    
    nueva_obra = {
        "activarDesde": activar_desde,
        "imagen": imagen_url,
        "titulo": titulo,
        "descripcion": descripcion,
        "fechas": fechas,
        "elenco": elenco
    }
    
    if mes not in obras:
        obras[mes] = {"obras": []}
    
    obra_index = request.form.get('obra_index')
    
    if obra_index is not None and obra_index.isdigit():
        obra_index = int(obra_index)
        if obra_index < 0 or obra_index >= len(obras[mes]['obras']):
            flash('Índice de obra inválido', 'error')
            return redirect(request.referrer)
        
        obra_anterior = obras[mes]['obras'][obra_index]
        
        if 'imagen_archivo' in request.files and request.files['imagen_archivo'].filename != '':
            if obra_anterior['imagen'].startswith('/static/images/obras/'):
                try:
                    os.remove(obra_anterior['imagen'][1:])
                except Exception as e:
                    app.logger.warning(f"No se pudo eliminar la imagen anterior: {e}")
        
        if 'elenco' in obra_anterior:
            for actor in obra_anterior['elenco']:
                if isinstance(actor, dict) and 'foto' in actor:
                    if actor['foto'].startswith('/static/images/elenco/'):
                        try:
                            os.remove(actor['foto'][1:])
                        except Exception as e:
                            app.logger.warning(f"No se pudo eliminar foto del elenco: {e}")
        
        obras[mes]['obras'][obra_index] = nueva_obra
        flash(f'Obra "{titulo}" actualizada exitosamente', 'success')
    else:
        obras[mes]['obras'].append(nueva_obra)
        flash(f'Obra "{titulo}" creada exitosamente en {mes}', 'success')

    obras = ordenar_obras_por_mes(obras)
    guardar_obras(obras)
    return redirect(url_for('admin_obras'))

@app.route('/admin-teatro-olmo-2025/obra/eliminar/<mes>/<int:obra_index>')
def eliminar_obra(mes, obra_index):
    """Elimina una obra"""
    obras = cargar_obras()
    
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra_eliminada = obras[mes]['obras'].pop(obra_index)
        
        if obra_eliminada['imagen'].startswith('/static/images/obras/'):
            try:
                os.remove(obra_eliminada['imagen'][1:])
            except Exception as e: # Captura la excepción para logging
                app.logger.warning(f"No se pudo eliminar la imagen: {e}")
        
        if 'elenco' in obra_eliminada and isinstance(obra_eliminada['elenco'], list):
            for actor in obra_eliminada['elenco']:
                if isinstance(actor, dict) and 'foto' in actor:
                    if actor['foto'].startswith('/static/images/elenco/'):
                        try:
                            os.remove(actor['foto'][1:])
                        except Exception as e: # Captura la excepción para logging
                            app.logger.warning(f"No se pudo eliminar foto del elenco: {e}")
        
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
def nuevo_servicio():
    """Formulario para crear nuevo servicio"""
    _, categorias_dinamicas, nombres_categorias_dinamicos = cargar_servicios() # Carga categorías dinámicas
    return render_template('nuevo_servicio.html', 
                           categorias=categorias_dinamicas,
                           nombres_categorias=nombres_categorias_dinamicos)

@app.route('/admin-teatro-olmo-2025/servicio/editar/<categoria>/<servicio_id>', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    # Asegúrate de crear las carpetas de subida si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_ELENCO'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_SERVICIOS'], exist_ok=True)
    app.run(debug=True)