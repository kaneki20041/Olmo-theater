export function initOlmobras() {
  const obrasPorMes = {
    "Julio": [
      {
        imagen: "/static/images/obra1.png",
        titulo: "LA PRINCESA Y EL DRAGÓN",
        descripcion: "Una escenografía centrada en las fiestas paganas del Dios Sol con juegos y más... APT",
          fechas: [
          { dia: "17", mes: "mayo" },
          { dia: "24", mes: "mayo" },
          { dia: "31", mes: "mayo" }
        ],
        elenco: ["Graysit Sarango", "Douglas Chotcón", "Jesús José Martín"]
      },
      {
        imagen: "/static/images/obra2.jpg",
        titulo: " Pink Floyd en movimiento",
        descripcion: "The Dark Side of the Moon de Pink Floyd es un viaje sonoro y existencial que abordó temas universales como el tiempo, la locura, la muerte y la alienación. Este espectáculo de danza contemporánea reinterpreta la esencia de ese universo. No es solo un tributo. Es una experiencia. Una invitación a sumergirse en el lado oscuro... y danzarlo",
        fechas: "16, 17, 23, 30 y 31 de mayo",
        elenco: ["Actor 1", "Actor 2"]
      }
    ],
    "Agosto": [
      {
        imagen: "/static/img/obra3.png",
        titulo: "Obra de Agosto",
        descripcion: "Obra especial del mes de agosto.",
        fechas: "5, 12, 19 de agosto",
        elenco: ["Actriz X", "Actor Y"]
      }
    ]
  };

  let meses = Object.keys(obrasPorMes);
  let indiceMes = 0;

  const mesSpan = document.getElementById("currentMonth");
  const obrasContainer = document.getElementById("obrasContainer");
  const btnAnterior = document.getElementById("btnAnterior");
  const btnSiguiente = document.getElementById("btnSiguiente");

  const modal = document.getElementById("obraModal");
  const modalBody = document.getElementById("modalBody");
  const cerrarModal = document.getElementById("cerrarModal");

  function actualizarObras() {
    const mesActual = meses[indiceMes];
    mesSpan.textContent = mesActual;
    obrasContainer.innerHTML = "";

    obrasPorMes[mesActual].forEach((obra, index) => {
      const img = document.createElement("img");
      img.src = obra.imagen;
      img.alt = obra.titulo;
      img.classList.add("obra-img");
      img.style.cursor = "pointer";

      img.addEventListener("click", () => mostrarModal(obra));

      obrasContainer.appendChild(img);
    });
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

  // Limpiar elenco y agregar nuevos círculos
  const elencoDiv = document.getElementById('modalObraElenco');
  elencoDiv.innerHTML = '';

  obra.elenco.forEach(nombre => {
    const actorDiv = document.createElement('div');
    actorDiv.classList.add('actor');

    const circleDiv = document.createElement('div');
    circleDiv.classList.add('actor-circle');

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
document.getElementById('cerrarModal').onclick = function () {
  document.getElementById('obraModal').classList.add('hidden');
  document.body.style.overflow = 'auto';
};

// Cerrar modal al hacer click fuera del contenido
window.onclick = function (event) {
  const modal = document.getElementById('obraModal');
  if (event.target === modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
  }
};


  cerrarModal.onclick = function () {
    modal.classList.add("hidden");
  };

  btnAnterior.addEventListener("click", () => {
    indiceMes = (indiceMes - 1 + meses.length) % meses.length;
    actualizarObras();
  });

  btnSiguiente.addEventListener("click", () => {
    indiceMes = (indiceMes + 1) % meses.length;
    actualizarObras();
  });

  actualizarObras();
}