// Variable global para almacenar las obras
let obrasPorMes = {};

export function initOlmobras() {
  // Intentar obtener los datos desde el HTML (pasados desde Flask)
  const obrasDataElement = document.getElementById('obras-data');
  if (obrasDataElement) {
    try {
      obrasPorMes = JSON.parse(obrasDataElement.textContent);
    } catch (e) {
      console.error('Error al parsear datos de obras:', e);
      // Fallback a datos por defecto si hay error
      cargarObrasDesdeAPI();
    }
  } else {
    // Si no hay datos en el HTML, cargar desde API
    cargarObrasDesdeAPI();
  }

  inicializarInterfaz();
}

async function cargarObrasDesdeAPI() {
  try {
    const response = await fetch('/api/obras');
    if (response.ok) {
      obrasPorMes = await response.json();
      console.log('Obras cargadas desde API:', obrasPorMes);
    } else {
      console.error('Error al cargar obras desde API');
      // Usar datos por defecto como último recurso
    }
  } catch (error) {
    console.error('Error de red al cargar obras:', error);
  }
}

function inicializarInterfaz() {
  const mesSpan = document.getElementById("currentMonth");
  const obrasContainer = document.getElementById("obrasContainer");
  const btnAnterior = document.getElementById("btnAnterior");
  const btnSiguiente = document.getElementById("btnSiguiente");

  if (!mesSpan || !obrasContainer || !btnAnterior || !btnSiguiente) {
    console.error('Elementos de la interfaz no encontrados');
    return;
  }

  let meses = Object.keys(obrasPorMes);
  let indiceMes = 0;

  const modal = document.getElementById("obraModal");
  const modalBody = document.getElementById("modalBody");
  const cerrarModal = document.getElementById("cerrarModal");

function actualizarObras() {
  const mesActual = meses[indiceMes];
  mesSpan.textContent = mesActual;
  obrasContainer.innerHTML = "";

  const datosMes = obrasPorMes[mesActual];
  if (!datosMes) {
    console.error(`No hay datos para el mes: ${mesActual}`);
    return;
  }

  const hoy = new Date();
  let hayObraActiva = false;

  datosMes.obras.forEach((obra) => {
    const fechaActivacion = new Date(obra.activarDesde);
    if (hoy >= fechaActivacion) {
      hayObraActiva = true;
      const img = document.createElement("img");
      img.src = obra.imagen;
      img.alt = obra.titulo;
      img.classList.add("obra-img");
      img.style.cursor = "pointer";

      img.addEventListener("click", () => mostrarModal(obra));
      obrasContainer.appendChild(img);
    }
  });

  if (!hayObraActiva) {
    // Si no hay ninguna obra activa, mostrar cartel de "Próximamente"
    const proximoDiv = document.createElement("div");
    proximoDiv.className = "obra-proximamente";
    proximoDiv.textContent = "¡Próximamente!";
    obrasContainer.appendChild(proximoDiv);
  }
}

  function mostrarModal(obra) {
    // Cargar imagen y alt
    document.getElementById('modalObraImg').src = obra.imagen || '';
    document.getElementById('modalObraImg').alt = obra.titulo || 'Obra';

    // Actualizar texto
    document.getElementById('modalObraTitulo').textContent = obra.titulo || '';
    document.getElementById('modalObraDescripcion').textContent = obra.descripcion || '';

    // Manejar las fechas en formato grid
    const fechasGrid = document.getElementById('modalObraFechasGrid');
    fechasGrid.innerHTML = '';

    // Convertir las fechas de string a array si es necesario
    let fechasArray = [];
    if (typeof obra.fechas === 'string') {
      const fechaStr = obra.fechas;

      // Extraer el mes (asumiendo que todas las fechas son del mismo mes)
      const mesMatch = fechaStr.match(/de\s+(\w+)/i);
      const mes = mesMatch ? mesMatch[1] : '';

      // Extraer los días
      const diasMatch = fechaStr.match(/\d+/g);
      if (diasMatch) {
        fechasArray = diasMatch.map(dia => ({
          dia: dia,
          mes: mes
        }));
      }
    } else if (Array.isArray(obra.fechas)) {
      fechasArray = obra.fechas;
    }

    // Añadir la clase para el estilo basado en el número de fechas
    fechasGrid.className = `fechas-grid fechas-${fechasArray.length}`;

    // Crear los elementos de fecha
    fechasArray.forEach(fecha => {
      const fechaItem = document.createElement('div');
      fechaItem.className = 'fecha-item';

      const diaSpan = document.createElement('span');
      diaSpan.className = 'fecha-dia';
      diaSpan.textContent = fecha.dia;

      const mesSpan = document.createElement('span');
      mesSpan.className = 'fecha-mes';
      mesSpan.textContent = fecha.mes;

      fechaItem.appendChild(diaSpan);
      fechaItem.appendChild(mesSpan);

      // Evento click para abrir WhatsApp
      fechaItem.addEventListener('click', function () {
        const mensaje = `¡Hola! Me interesa asistir a la obra "${obra.titulo}" el día ${fecha.dia} de ${fecha.mes}. ¿Podría reservar?`;
        const whatsappURL = `https://wa.me/+51947919832?text=${encodeURIComponent(mensaje)}`;
        window.open(whatsappURL, '_blank');
      });

      fechasGrid.appendChild(fechaItem);
    });

    // Limpiar elenco y agregar nuevos círculos con fotos
    const elencoDiv = document.getElementById('modalObraElenco');
    elencoDiv.innerHTML = '';

    // Manejar tanto formato antiguo (array de strings) como nuevo (array de objetos)
    const elencoArray = Array.isArray(obra.elenco) ? obra.elenco : [];
    
    elencoArray.forEach(actor => {
      const actorDiv = document.createElement('div');
      actorDiv.classList.add('actor');

      const circleDiv = document.createElement('div');
      circleDiv.classList.add('actor-circle');

      let nombre = '';
      let fotoUrl = '';

      // Compatibilidad con formato antiguo y nuevo
      if (typeof actor === 'string') {
        nombre = actor;
        fotoUrl = ''; // Sin foto para formato antiguo
      } else if (typeof actor === 'object' && actor.nombre) {
        nombre = actor.nombre;
        fotoUrl = actor.foto || '';
      }

      // Si hay foto, agregar como background-image
      if (fotoUrl) {
        circleDiv.style.backgroundImage = `url(${fotoUrl})`;
        circleDiv.style.backgroundSize = 'cover';
        circleDiv.style.backgroundPosition = 'center';
        circleDiv.style.backgroundColor = '#f0f0f0';
      } else {
        // Si no hay foto, usar el círculo vacío tradicional
        circleDiv.style.backgroundColor = '#ddd';
      }

      const nameP = document.createElement('p');
      nameP.classList.add('actor-name');
      nameP.textContent = nombre;

      actorDiv.appendChild(circleDiv);
      actorDiv.appendChild(nameP);

      elencoDiv.appendChild(actorDiv);
    });

    // Mostrar modal
    document.getElementById('obraModal').classList.remove('hidden');

    // Evitar scroll en el body
    document.body.style.overflow = 'hidden';
  }

  // Cerrar modal con botón
  if (cerrarModal) {
    cerrarModal.onclick = function () {
      document.getElementById('obraModal').classList.add('hidden');
      document.body.style.overflow = 'auto';
    };
  }

  // Cerrar modal al hacer click fuera del contenido
  window.onclick = function (event) {
    const modal = document.getElementById('obraModal');
    if (event.target === modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = 'auto';
    }
  };

  btnAnterior.addEventListener("click", () => {
    indiceMes = (indiceMes - 1 + meses.length) % meses.length;
    actualizarObras();
  });

  btnSiguiente.addEventListener("click", () => {
    indiceMes = (indiceMes + 1) % meses.length;
    actualizarObras();
  });

  // Inicializar
  actualizarObras();
}

// Función para recargar obras (útil si se actualizan desde el admin)
export function recargarObras() {
  cargarObrasDesdeAPI().then(() => {
    inicializarInterfaz();
  });
}

let indiceActor = 1;

export function agregarActor() {
  const container = document.getElementById('elenco-container');
  if (!container) {
    console.warn('Contenedor de elenco no encontrado');
    return;
  }

  const currentIndex = indiceActor;
  const div = document.createElement('div');
  div.className = 'elenco-item';
  div.style.border = '1px solid #e0e0e0';
  div.style.padding = '15px';
  div.style.marginBottom = '15px';
  div.style.borderRadius = '8px';
  div.style.backgroundColor = '#f9f9f9';
  
  div.innerHTML = `
    <div class="actor-input-group" style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
      <input type="text" name="elenco[]" placeholder="Nombre del actor" required style="flex: 1;">
      <input type="file" name="foto_elenco_${currentIndex}" accept="image/*" 
             onchange="mostrarVistaPrevia(this, 'preview-actor-${currentIndex}')"
             id="foto-actor-${currentIndex}" style="flex: 1;">
      <button type="button" class="btn btn-danger btn-sm eliminar-actor" onclick="eliminarActor(this)" title="Eliminar actor">🗑️</button>
    </div>
    <div class="actor-preview-container" style="margin-top: 10px; text-align: center;">
      <img id="preview-actor-${currentIndex}" 
           style="display: none; width: 80px; height: 80px; border: 2px solid #ddd; border-radius: 50%; object-fit: cover; transition: all 0.3s ease;"
           alt="Vista previa foto actor">
    </div>
  `;
  container.appendChild(div);
  indiceActor++;
}

window.agregarActor = agregarActor;

window.eliminarActor = function (btn) {
  const container = document.getElementById('elenco-container');
  const items = container.querySelectorAll('.elenco-item');

  // No permitir eliminar si solo queda uno
  if (items.length <= 1) {
    alert("Debe haber al menos un actor.");
    return;
  }

  // Eliminar el bloque padre del botón
  btn.closest('.elenco-item').remove();
};

// Función para mostrar vista previa de imagen
function mostrarVistaPrevia(input, previewId) {
  const preview = document.getElementById(previewId);
  if (!preview) return;

  const file = input.files[0];
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = function(e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
      
      // Si es vista previa de imagen principal, mostrar también el texto
      if (previewId === 'imagen-preview') {
        const previewText = document.getElementById('imagen-preview-text');
        if (previewText) {
          previewText.style.display = 'block';
        }
      }
      
      // Si es vista previa de actor, mostrar texto correspondiente
      if (previewId.startsWith('preview-actor-')) {
        const actorIndex = previewId.replace('preview-actor-', '');
        const previewText = document.getElementById(`preview-text-${actorIndex}`);
        if (previewText) {
          previewText.style.display = 'block';
        }
      }
    };
    reader.readAsDataURL(file);
  } else {
    preview.style.display = 'none';
    
    // Ocultar texto si es imagen principal
    if (previewId === 'imagen-preview') {
      const previewText = document.getElementById('imagen-preview-text');
      if (previewText) {
        previewText.style.display = 'none';
      }
    }
    
    // Ocultar texto si es actor
    if (previewId.startsWith('preview-actor-')) {
      const actorIndex = previewId.replace('preview-actor-', '');
      const previewText = document.getElementById(`preview-text-${actorIndex}`);
      if (previewText) {
        previewText.style.display = 'none';
      }
    }
  }
}

window.mostrarVistaPrevia = mostrarVistaPrevia;

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const mesInput = document.getElementById("mes");
  const fechaInput = document.getElementById("activar_desde");
  const archivoInput = document.getElementById("imagen_archivo");

  if (!form || !mesInput || !fechaInput) return;

  // Configurar vista previa de imagen si existe el input
  if (archivoInput) {
    archivoInput.addEventListener("change", function () {
      if (archivoInput.files.length > 0) {
        archivoInput.title = "Archivo seleccionado: " + archivoInput.files[0].name;
        archivoInput.style.border = "2px solid green";
        
        // Mostrar vista previa
        mostrarVistaPrevia(archivoInput, 'imagen-preview');
      }
    });
  }

  // Validación al enviar - CORREGIDA
  form.addEventListener("submit", function (e) {
    const fechaStr = fechaInput.value;
    if (!fechaStr) {
      e.preventDefault();
      alert("Por favor, selecciona una fecha de activación.");
      return;
    }

    // Validar que se haya seleccionado una imagen (solo para nuevas obras)
    const isEditing = document.getElementById('obra_index');
    if (!isEditing && archivoInput && archivoInput.files.length === 0) {
      e.preventDefault();
      alert("Por favor, selecciona una imagen para la obra.");
      return;
    }
  });
});