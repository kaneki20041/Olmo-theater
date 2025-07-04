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

  const div = document.createElement('div');
  div.className = 'elenco-item';
  div.innerHTML = `
    <input type="text" name="elenco[]" placeholder="Nombre del actor" required>
    <input type="file" name="foto_elenco_${indiceActor}" accept="image/*">
    <button type="button" class="btn btn-danger btn-sm eliminar-actor" onclick="eliminarActor(this)" title="Eliminar actor">🗑️</button>
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

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const mesInput = document.getElementById("mes");
  const fechaInput = document.getElementById("activar_desde");
  const archivoInput = document.getElementById("imagen_archivo");
  const urlInput = document.getElementById("imagen_url");

  if (!form || !mesInput || !fechaInput) return;

  // Validación al enviar
  form.addEventListener("submit", function (e) {
    const fechaStr = fechaInput.value;
    if (!fechaStr) return;

    const archivoSeleccionado = archivoInput && archivoInput.files.length > 0;
    const urlEscrita = urlInput && urlInput.value.trim() !== "";

    if (archivoSeleccionado && urlEscrita) {
      e.preventDefault();
      alert("Por favor, selecciona solo una imagen o coloca una URL, no ambas.");
    }
  });

  // Desactivar uno si se usa el otro
  if (archivoInput && urlInput) {
    archivoInput.addEventListener("change", function () {
      if (archivoInput.files.length > 0) {
        urlInput.disabled = true;
        archivoInput.title = "Archivo seleccionado: " + archivoInput.files[0].name;
        archivoInput.style.border = "2px solid green";
      } else {
        urlInput.disabled = false;
        archivoInput.style.border = "";
      }
    });

    urlInput.addEventListener("input", function () {
      if (urlInput.value.trim() !== "") {
        archivoInput.disabled = true;
      } else {
        archivoInput.disabled = false;
      }
    });
  }
});
