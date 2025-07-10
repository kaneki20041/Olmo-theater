// servicios.js
export function initServicios() {

    // Acceder a los datos pasados desde Flask a través de window
// Convertir lista de pares a objeto para facilitar acceso por categoría
    const serviciosData = Object.fromEntries(window.serviciosData);
    const nombresCategorias = window.nombresCategorias; // Acceder a los nombres de categorías

    // Verificar que window.serviciosData existe y no está vacío
    if (!serviciosData || Object.keys(serviciosData).length === 0) {
        document.getElementById('servicesGrid').innerHTML = `
            <div class="no-services-message">
                <i class="fas fa-inbox fa-3x" style="margin-bottom: 20px; opacity: 0.5;"></i>
                <p>No hay servicios disponibles para cargar.</p>
            </div>
        `;
        return;
    }

    const filterOptions = document.querySelectorAll('.filter-option');
    const servicesGrid = document.getElementById('servicesGrid'); // ID corregido

    // Limpiar el grid antes de cargar los servicios
    servicesGrid.innerHTML = '';

    // Función para mostrar los servicios en el grid (todos los servicios activos inicialmente)
    function displayAllActiveServices() {
        let totalServiciosRendered = 0;

        // Iterar sobre todas las categorías y sus servicios
        Object.entries(serviciosData).forEach(([categoria, servicios]) => {
            servicios.forEach(servicio => {
                if (servicio.activo) { // Solo renderizar servicios activos
                    const serviceCard = document.createElement('div');
                    serviceCard.className = 'service-card';
                    serviceCard.setAttribute('data-category', categoria); // Añadir atributo de categoría

                    serviceCard.innerHTML = `
                        <img src="${servicio.imagen}" alt="${servicio.alt || servicio.titulo}" class="service-image">
                        <div class="service-info">
                        </div>
                    `;
                    
                    const imgElement = serviceCard.querySelector('.service-image');
                    imgElement.onerror = function() {
                        // Opcional: mostrar imagen placeholder si la original falla
                        this.src = 'https://placehold.co/300x200/cccccc/333333?text=Imagen+no+disponible'; 
                    };

                    servicesGrid.appendChild(serviceCard);
                    totalServiciosRendered++;
                }
            });
        });
    }

    // Función para filtrar los servicios ya renderizados en el DOM
    function filterServices(selectedFilter) {
        const serviceCards = document.querySelectorAll('.service-card');
        let visibleCount = 0;

        serviceCards.forEach(card => {
            const category = card.getAttribute('data-category');
            if (selectedFilter === 'all' || category === selectedFilter) {
                card.style.display = 'flex'; // Mostrar la tarjeta (usando flex para el layout)
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
                card.classList.remove('hidden'); // Asegurarse de que no tenga la clase hidden
                visibleCount++;
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.classList.add('hidden'); // Añadir clase hidden para ocultar
                // Retrasar el display: none para permitir la transición de opacidad/transform
                setTimeout(() => {
                    if (card.classList.contains('hidden')) { // Solo ocultar si sigue hidden
                        card.style.display = 'none';
                    }
                }, 300); // Duración de la transición CSS
            }
        });


        // Mostrar mensaje si no hay resultados para el filtro actual
        const existingNoResultsMessage = document.querySelector('.no-services-message.filter-specific');
        if (visibleCount === 0) {
            if (!existingNoResultsMessage) {
                const noResultsDiv = document.createElement('div');
                noResultsDiv.className = 'no-services-message filter-specific';
                noResultsDiv.innerHTML = `
                    <i class="fas fa-search-minus fa-3x" style="margin-bottom: 20px; opacity: 0.5;"></i>
                    <p>No hay servicios activos en esta categoría.</p>
                `;
                servicesGrid.appendChild(noResultsDiv);
            }
        } else {
            if (existingNoResultsMessage) {
                existingNoResultsMessage.remove();
            }
        }
    }

    // Actualizar el filtro activo en la UI
    function updateActiveFilter(selectedFilterValue) {
        filterOptions.forEach(option => {
            if (option.dataset.filter === selectedFilterValue) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }

    // Agregar los eventos de filtro a los botones
    filterOptions.forEach(option => {
        option.addEventListener('click', function () {
            const filter = this.getAttribute('data-filter');
            updateActiveFilter(filter); // Actualiza la clase 'active'
            filterServices(filter); // Aplica el filtro
        });
    });

    // INICIALIZACIÓN PRINCIPAL
    try {
        // 1. Renderizar todos los servicios activos en el DOM
        displayAllActiveServices();

        // 2. Aplicar el filtro por defecto (Talleres niños) y actualizar la UI
        const defaultFilter = 'talleres-ninos';
        updateActiveFilter(defaultFilter);
        filterServices(defaultFilter);
        
    } catch (error) {
        document.getElementById('servicesGrid').innerHTML = `
            <div class="no-services-message">
                <i class="fas fa-exclamation-triangle fa-3x" style="margin-bottom: 20px; color: #dc3545;"></i>
                <p>Ocurrió un error al inicializar los servicios.</p>
            </div>
        `;
    }
}

// Llamar a initServicios cuando el DOM esté completamente cargado
// Esto es importante porque servicios.js se carga como un módulo y no espera DOMContentLoaded por defecto
document.addEventListener('DOMContentLoaded', initServicios);


