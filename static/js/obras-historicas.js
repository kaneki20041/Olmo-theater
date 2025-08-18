export function initObrasHistoricas() {
    class ObrasHistoricas {
        constructor() {
            this.currentFilter = 'trayectoria';
            this.currentPage = 1;
            this.itemsPerPage = 9;
            this.totalPages = 2;
            this.data = {};
            
            // Verificar si la sección existe antes de inicializar
            this.sectionElement = document.getElementById('obras_historicas');
            if (!this.sectionElement) {
                console.log('Sección obras_historicas no encontrada');
                return;
            }
            
            // Cargar datos desde el servidor
            this.loadData();
        }
        
        async loadData() {
            try {
                // Intentar obtener datos desde el endpoint API
                const response = await fetch('/api/obras_historicas');
                if (response.ok) {
                    this.data = await response.json();
                } else {
                    // Fallback a datos del script JSON si existe
                    this.loadFallbackData();
                }
            } catch (error) {
                console.log('Error cargando datos del servidor, usando datos locales:', error);
                this.loadFallbackData();
            }
            
            this.init();
        }
        
        loadFallbackData() {
            // Intentar cargar desde script JSON en la página
            const scriptData = document.getElementById('obras-data');
            if (scriptData) {
                try {
                    this.data = JSON.parse(scriptData.textContent);
                } catch (error) {
                    console.log('Error parseando datos JSON:', error);
                    this.data = this.getDefaultData();
                }
            } else {
                this.data = this.getDefaultData();
            }
        }
        
        getDefaultData() {
            // Datos por defecto en caso de no poder cargar desde servidor
            return {
                trayectoria: [
                    {
                        id: 1,
                        title: "Ilusión",
                        year: 2018,
                        description: "Inspirado en la emoción que mantiene nuestros sueños y nos impulsa a alcanzarlos, Ilusión narra las peripecias que vive Max, un niño de 7 años...",
                        image: "/static/images/obras/ilusion.jpg"
                    }
                ],
                proyectos: [
                    {
                        id: 19,
                        title: "Teatro en las Escuelas",
                        year: 2020,
                        description: "Proyecto educativo que lleva el teatro a instituciones educativas de Trujillo, fomentando la creatividad en niños y jóvenes...",
                        image: "/static/images/proyectos/teatro-escuelas.jpg"
                    }
                ]
            };
        }
        
        init() {
            this.setupEventListeners();
            this.renderContent();
        }
        

        

        
        setupEventListeners() {
            // Radio buttons para filtro
            const filterRadios = document.querySelectorAll('input[name="obras-filter"]');
            filterRadios.forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.currentFilter = e.target.value;
                    this.currentPage = 1;
                    this.renderContent();
                });
            });
            
            // Botones de paginación
            const prevBtn = document.getElementById('prevPageBtn');
            const nextBtn = document.getElementById('nextPageBtn');
            
            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    if (this.currentPage > 1) {
                        this.currentPage--;
                        this.renderContent();
                    }
                });
            }
            
            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    if (this.currentPage < this.totalPages) {
                        this.currentPage++;
                        this.renderContent();
                    }
                });
            }
        }
        
        getCurrentData() {
            return this.data[this.currentFilter] || [];
        }
        
        getPaginatedData() {
            const allData = this.getCurrentData();
            const startIndex = (this.currentPage - 1) * this.itemsPerPage;
            const endIndex = startIndex + this.itemsPerPage;
            return allData.slice(startIndex, endIndex);
        }
        
        renderContent() {
            const grid = document.getElementById('obrasHistoricasGrid');
            if (!grid) return;
            
            const paginatedData = this.getPaginatedData();
            
            // Limpiar grid
            grid.innerHTML = '';
            
            if (paginatedData.length === 0) {
                grid.innerHTML = `
                <div class="obras-grid empty">
                    <div class="no-content-message">
                        <i class="fas fa-theater-masks"></i>
                        <p>No hay obras disponibles en esta categoría</p>
                    </div>
                </div>
                `;
                
                // Agregar estilos para el enlace
                this.addNoContentStyles();
                return;
            }
            
            // Renderizar cards
            paginatedData.forEach(obra => {
                const card = this.createObraCard(obra);
                grid.appendChild(card);
            });
            
            this.updatePagination();
        }
        
        addNoContentStyles() {
            if (document.getElementById('no-content-styles')) return;
            
            const noContentStyles = document.createElement('style');
            noContentStyles.id = 'no-content-styles';
            
            document.head.appendChild(noContentStyles);
        }
        
        createObraCard(obra) {
            const card = document.createElement('div');
            card.className = 'obra-card';
            card.innerHTML = `
                <div class="obra-card-image">
                    <img src="${obra.image}" alt="${obra.title}" loading="lazy" 
                         onerror="this.src='/static/images/placeholder-obra.jpg'">
                    <div class="obra-card-year">${obra.year}</div>
                </div>
                <div class="obra-card-content">
                    <h3 class="obra-card-title">${obra.title}</h3>
                    <p class="obra-card-description">${obra.description}</p>
                </div>
            `;
            
            // Agregar evento click para abrir modal
            card.addEventListener('click', () => {
                this.openObraModal(obra.id);
            });
            
            return card;
        }
        
        updatePagination() {
            const allData = this.getCurrentData();
            this.totalPages = Math.ceil(allData.length / this.itemsPerPage);
            
            const prevBtn = document.getElementById('prevPageBtn');
            const nextBtn = document.getElementById('nextPageBtn');
            const paginationInfo = document.getElementById('paginationInfo');
            const paginationContainer = document.getElementById('paginationContainer');
            
            // Ocultar paginación si no hay suficientes elementos
            if (paginationContainer) {
                paginationContainer.style.display = this.totalPages <= 1 ? 'none' : 'flex';
            }
            
            if (prevBtn && nextBtn && paginationInfo) {
                // Actualizar botones
                prevBtn.disabled = this.currentPage === 1;
                nextBtn.disabled = this.currentPage === this.totalPages || this.totalPages === 0;
                
                // Actualizar información
                if (this.totalPages === 0) {
                    paginationInfo.textContent = 'Sin páginas';
                } else {
                    paginationInfo.textContent = `Página ${this.currentPage} de ${this.totalPages}`;
                }
                
                // Agregar clases activas
                prevBtn.classList.toggle('active', this.currentPage > 1);
                nextBtn.classList.toggle('active', this.currentPage < this.totalPages);
            }
        }
        
        openObraModal(obraId) {
            // Buscar la obra en ambos datasets
            let obra = null;
            for (const category in this.data) {
                obra = this.data[category].find(o => o.id === obraId);
                if (obra) break;
            }
            
            if (!obra) {
                console.error('Obra no encontrada:', obraId);
                return;
            }
            
            this.showObraDetails(obra);
        }
        
        showObraDetails(obra) {
            // Crear un modal simple
            const modal = document.createElement('div');
            modal.className = 'obra-modal';
            modal.innerHTML = `
                <div class="modal-backdrop"></div>
                <div class="modal-content-obra">
                    <button class="modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="modal-obra-image">
                        <img src="${obra.image}" alt="${obra.title}" 
                             onerror="this.src='/static/images/placeholder-obra.jpg'">
                    </div>
                    <div class="modal-obra-info">
                        <h2>${obra.title}</h2>
                        <div class="modal-obra-meta">
                            <span class="obra-year">Año: ${obra.year}</span>
                        </div>
                        <div class="modal-obra-description">
                            <p>${obra.description}</p>
                        </div>
                    </div>
                </div>
            `;
            
            this.addModalStyles();
            document.body.appendChild(modal);
            
            // Prevenir scroll del body
            document.body.style.overflow = 'hidden';
            
            // Event listeners para cerrar modal
            const backdrop = modal.querySelector('.modal-backdrop');
            const closeBtn = modal.querySelector('.modal-close');
            
            const closeModal = () => {
                document.body.style.overflow = '';
                modal.remove();
            };
            
            backdrop.addEventListener('click', closeModal);
            closeBtn.addEventListener('click', closeModal);
            
            // Cerrar con ESC
            const handleEsc = (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                    document.removeEventListener('keydown', handleEsc);
                }
            };
            document.addEventListener('keydown', handleEsc);
        }
        
        addModalStyles() {
            // Solo agregar estilos si no existen ya
            if (document.getElementById('obra-modal-styles')) return;
            
            const modalStyles = document.createElement('style');
            modalStyles.id = 'obra-modal-styles';
            modalStyles.textContent = `
                .obra-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .modal-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(5px);
                }
                
                .modal-content-obra {
                    position: relative;
                    background: rgba(5, 10, 36, 0.95);
                    border-radius: 15px;
                    max-width: 800px;
                    max-height: 80vh;
                    overflow-y: auto;
                    border: 1px solid rgba(225, 183, 0, 0.3);
                    backdrop-filter: blur(10px);
                    margin: 20px;
                }
                
                .modal-close {
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: none;
                    border: none;
                    color: #e1b700;
                    font-size: 1.5rem;
                    cursor: pointer;
                    z-index: 1001;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                }
                
                .modal-close:hover {
                    background: rgba(225, 183, 0, 0.2);
                    transform: scale(1.1);
                }
                
                .modal-obra-image {
                    width: 100%;
                    height: 300px;
                    overflow: hidden;
                    border-radius: 15px 15px 0 0;
                }
                
                .modal-obra-image img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }
                
                .modal-obra-info {
                    padding: 30px;
                }
                
                .modal-obra-info h2 {
                    color: #e1b700;
                    font-size: 2rem;
                    margin-bottom: 15px;
                }
                
                .modal-obra-meta {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                    font-size: 1rem;
                }
                
                .obra-year {
                    color: rgba(255, 255, 255, 0.8);
                }
                
                .modal-obra-description {
                    color: rgba(255, 255, 255, 0.9);
                    line-height: 1.6;
                    font-size: 1.1rem;
                    margin-bottom: 20px;
                }
                
                @media (max-width: 768px) {
                    .modal-content-obra {
                        margin: 20px;
                        max-height: calc(100vh - 40px);
                    }
                    
                    .modal-obra-info {
                        padding: 20px;
                    }
                    
                    .modal-obra-info h2 {
                        font-size: 1.5rem;
                    }
                    
                    .modal-obra-meta {
                        flex-direction: column;
                        gap: 10px;
                    }
                }
            `;
            
            document.head.appendChild(modalStyles);
        }
        
        // Método para refrescar datos (útil después de cambios en admin)
        async refreshData() {
            await this.loadData();
            this.renderContent();
        }
    }

    // Inicializar la clase y exponerla globalmente para posible uso
    window.obrasHistoricasInstance = new ObrasHistoricas();
}