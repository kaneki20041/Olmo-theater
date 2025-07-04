from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
import uuid

# Carga las variables de entorno desde .flaskenv o .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave más segura

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/images/obras'
UPLOAD_FOLDER_ELENCO = 'static/images/elenco'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_ELENCO'] = UPLOAD_FOLDER_ELENCO
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Crear carpetas de uploads si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_ELENCO, exist_ok=True)

ORDEN_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"
]

# Archivo donde se guardarán las obras
OBRAS_FILE = 'obras.json'

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
        # Datos iniciales si no existe el archivo
        return {}

def guardar_obras(obras):
    """Guarda las obras en el archivo JSON"""
    with open(OBRAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(obras, f, ensure_ascii=False, indent=2)

def procesar_fotos_elenco(elenco_nombres, archivos_fotos):
    """Procesa las fotos del elenco y devuelve la estructura de datos"""
    elenco_procesado = []
    
    for i, nombre in enumerate(elenco_nombres):
        if not nombre.strip():
            continue
            
        foto_url = ""
        campo_foto = f"foto_elenco_{i}"
        
        # Verificar si se subió una foto para este actor
        if campo_foto in archivos_fotos:
            file = archivos_fotos[campo_foto]
            if file and file.filename != '' and allowed_file(file.filename):
                # Generar nombre único para el archivo
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"elenco_{uuid.uuid4().hex[:8]}{ext}"
                
                # Guardar archivo
                file_path = os.path.join(app.config['UPLOAD_FOLDER_ELENCO'], unique_filename)
                file.save(file_path)
                
                # URL relativa para la foto
                foto_url = f"/static/images/elenco/{unique_filename}"
        
        # Si no se subió foto, usar URL proporcionada
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
    return render_template('index.html', obras_data=json.dumps(obras))

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

@app.route('/api/obras')
def api_obras():
    """API para obtener las obras actuales"""
    obras = cargar_obras()
    return jsonify(obras)

# URL secreta para gestionar obras - cambia 'admin-secreto-2025' por algo más seguro
@app.route('/admin-secreto-2025/obras')
def admin_obras():
    """Panel de administración de obras"""
    obras = cargar_obras()
    # Lista de meses disponibles para agregar nuevos
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('admin_obras.html', obras=obras, meses_disponibles=meses_disponibles)

@app.route('/admin-secreto-2025/obra/nueva')
def nueva_obra_sin_mes():
    """Formulario para crear nueva obra sin mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', meses_disponibles=meses_disponibles)

@app.route('/admin-secreto-2025/obra/nueva/<mes>')
def nueva_obra(mes):
    """Formulario para crear nueva obra en mes específico"""
    meses_disponibles = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return render_template('nueva_obra.html', mes=mes, meses_disponibles=meses_disponibles)

@app.route('/admin-secreto-2025/obra/editar/<mes>/<int:obra_index>')
def editar_obra(mes, obra_index):
    """Formulario para editar obra existente"""
    obras = cargar_obras()
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra = obras[mes]['obras'][obra_index]
        return render_template('editar_obra.html', mes=mes, obra=obra, obra_index=obra_index)
    else:
        flash('Obra no encontrada', 'error')
        return redirect(url_for('admin_obras'))

@app.route('/admin-secreto-2025/obra/guardar', methods=['POST'])
def guardar_obra():
    """Guarda una nueva obra o actualiza una existente"""
    obras = cargar_obras()
    
    # Validar campos obligatorios
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
    
    imagen_url = None
    
    # Manejar archivo subido
    if 'imagen_archivo' in request.files:
        file = request.files['imagen_archivo']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            imagen_url = f"/static/images/obras/{unique_filename}"
    
    # Si no hay archivo, usar URL del formulario
    if not imagen_url:
        imagen_url = request.form.get('imagen_url', '').strip()
    
    if not imagen_url:
        flash('Debes proporcionar una imagen (archivo o URL)', 'error')
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
    
    # Procesar elenco con fotos (asegúrate que procesar_fotos_elenco sea robusto)
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
        
        # Eliminar imágenes solo si se subió nueva imagen localmente
        if 'imagen_archivo' in request.files and request.files['imagen_archivo'].filename != '':
            if obra_anterior['imagen'].startswith('/static/images/obras/'):
                try:
                    os.remove(obra_anterior['imagen'][1:])
                except Exception as e:
                    app.logger.warning(f"No se pudo eliminar la imagen anterior: {e}")
        
        # Eliminar fotos del elenco anteriores solo si se subieron nuevas
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

def ordenar_obras_por_mes(obras):
    """
    Ordena el diccionario obras por mes (orden alfabético)
    y dentro de cada mes ordena la lista de obras por 'activarDesde' (fecha ascendente).
    """
    # Primero, ordenar las obras dentro de cada mes por activarDesde
    for mes in obras:
        obras[mes]['obras'].sort(key=lambda obra: obra.get('activarDesde', ''))
    
    obras_ordenadas = dict(
        sorted(
            obras.items(),
            key=lambda item: ORDEN_MESES.index(item[0]) if item[0] in ORDEN_MESES else 99
        )
    )

    
    return obras_ordenadas

@app.route('/admin-secreto-2025/obra/eliminar/<mes>/<int:obra_index>')
def eliminar_obra(mes, obra_index):
    """Elimina una obra"""
    obras = cargar_obras()
    
    if mes in obras and obra_index < len(obras[mes]['obras']):
        obra_eliminada = obras[mes]['obras'].pop(obra_index)
        
        # Eliminar archivo de imagen principal si es local
        if obra_eliminada['imagen'].startswith('/static/images/obras/'):
            try:
                os.remove(obra_eliminada['imagen'][1:])  # Remover '/' inicial
            except:
                pass  # Ignorar si no se puede eliminar
        
        # Eliminar fotos del elenco si son locales
        if 'elenco' in obra_eliminada and isinstance(obra_eliminada['elenco'], list):
            for actor in obra_eliminada['elenco']:
                if isinstance(actor, dict) and 'foto' in actor:
                    if actor['foto'].startswith('/static/images/elenco/'):
                        try:
                            os.remove(actor['foto'][1:])  # Remover '/' inicial
                        except:
                            pass  # Ignorar si no se puede eliminar
        
        # Si no quedan obras en el mes, eliminar el mes completo
        if len(obras[mes]['obras']) == 0:
            del obras[mes]
            flash(f'Obra "{obra_eliminada["titulo"]}" eliminada y mes {mes} removido', 'success')
        else:
            flash(f'Obra "{obra_eliminada["titulo"]}" eliminada exitosamente', 'success')
        
        guardar_obras(obras)
    else:
        flash('Obra no encontrada', 'error')
    
    return redirect(url_for('admin_obras'))

if __name__ == '__main__':
    app.run(debug=True)