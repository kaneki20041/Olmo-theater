// servicios.js
export function initServicios() {
    const filterOptions = document.querySelectorAll('.filter-option');
    const serviceCards = document.querySelectorAll('.service-card');
    const servicesGrid = document.getElementById('servicesGrid');

    function filterServices(selectedFilter) {
        serviceCards.forEach(card => {
            const category = card.getAttribute('data-category');
            if (selectedFilter === 'todos' || category === selectedFilter) {
                card.classList.remove('hidden');
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100);
            } else {
                card.classList.add('hidden');
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            }
        });

        const visibleCards = document.querySelectorAll('.service-card:not(.hidden)');
        if (visibleCards.length === 0) {
            showNoResults();
        } else {
            hideNoResults();
        }
    }

    function showNoResults() {
        const existingMessage = document.querySelector('.no-results');
        if (!existingMessage) {
            const noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'no-results';
            noResultsDiv.textContent = 'No se encontraron servicios para este filtro.';
            servicesGrid.appendChild(noResultsDiv);
        }
    }

    function hideNoResults() {
        const existingMessage = document.querySelector('.no-results');
        if (existingMessage) {
            existingMessage.remove();
        }
    }

    function updateActiveFilter(selectedOption) {
        filterOptions.forEach(option => option.classList.remove('active'));
        selectedOption.classList.add('active');
    }

    filterOptions.forEach(option => {
        option.addEventListener('click', function () {
            const filter = this.getAttribute('data-filter');
            if (!this.classList.contains('active')) {
                updateActiveFilter(this);
                filterServices(filter);
            }
        });

        option.addEventListener('mouseenter', function () {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(-2px)';
            }
        });

        option.addEventListener('mouseleave', function () {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });

        card.addEventListener('click', function () {
            console.log('Tarjeta clickeada:', this.getAttribute('data-category'));
        });
    });

    filterServices('talleres-ninos');

    serviceCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    servicesGrid.classList.remove('loading');

}
