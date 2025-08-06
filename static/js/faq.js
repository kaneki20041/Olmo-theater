document.addEventListener('DOMContentLoaded', function() {
    // FAQ Toggle
    const faqItems = document.querySelectorAll('.faq-item');
    const searchInput = document.getElementById('searchInput');
    const categoryButtons = document.querySelectorAll('.category-btn');
    const faqList = document.getElementById('faqList');

    // Toggle FAQ items
    function setupFAQToggle() {
        const currentFaqItems = document.querySelectorAll('.faq-item');
        
        currentFaqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            
            // Remove existing event listeners to avoid duplicates
            question.replaceWith(question.cloneNode(true));
            const newQuestion = item.querySelector('.faq-question');
            
            newQuestion.addEventListener('click', () => {
                const isActive = item.classList.contains('active');
                
                // Close all other items
                currentFaqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('active');
                    }
                });
                
                // Toggle current item
                item.classList.toggle('active', !isActive);
            });
        });
    }

    // Initial setup
    setupFAQToggle();

    // Search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const currentFaqItems = document.querySelectorAll('.faq-item');
        
        currentFaqItems.forEach(item => {
            const question = item.querySelector('.faq-question').textContent.toLowerCase();
            const answer = item.querySelector('.faq-answer-content').textContent.toLowerCase();
            
            if (searchTerm === '' || question.includes(searchTerm) || answer.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show "no results" message if no items are visible
        showNoResultsMessage();
    });

    // Category filtering
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            const currentFaqItems = document.querySelectorAll('.faq-item');
            
            // Update active button
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter items
            currentFaqItems.forEach(item => {
                if (category === 'all' || item.getAttribute('data-category') === category) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Clear search when filtering by category
            searchInput.value = '';
            
            // Show "no results" message if no items are visible
            showNoResultsMessage();
        });
    });

    // Function to show/hide "no results" message
    function showNoResultsMessage() {
        const currentFaqItems = document.querySelectorAll('.faq-item');
        const visibleItems = Array.from(currentFaqItems).filter(item => 
            item.style.display !== 'none'
        );
        
        // Remove existing "no results" message
        const existingMessage = document.querySelector('.no-results-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Show message if no items are visible
        if (visibleItems.length === 0) {
            const noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'no-results-message faq-item';
            noResultsDiv.innerHTML = `
                <div class="faq-question" style="color: #666; text-align: center; padding: 20px;">
                    No se encontraron resultados para tu búsqueda
                </div>
                <div class="faq-answer">
                    <div class="faq-answer-content" style="text-align: center;">
                        Intenta con otros términos de búsqueda o selecciona una categoría diferente.
                    </div>
                </div>
            `;
            faqList.appendChild(noResultsDiv);
        }
    }

    // Mobile menu toggle (integrating with your existing script)
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });

        // Close mobile menu when clicking on a link
        navLinks.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                navLinks.classList.remove('active');
            }
        });
    }

    // Keyboard navigation for FAQ items
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close all FAQ items when pressing Escape
            const currentFaqItems = document.querySelectorAll('.faq-item');
            currentFaqItems.forEach(item => {
                item.classList.remove('active');
            });
        }
    });

    // Add smooth scrolling when FAQ item is opened
    const style = document.createElement('style');
    style.textContent = `
        .faq-item {
            transition: all 0.3s ease;
        }
        
        .faq-answer {
            transition: max-height 0.3s ease, padding 0.3s ease;
        }
        
        .no-results-message .faq-question {
            cursor: default !important;
        }
        
        .no-results-message .faq-question:hover {
            background-color: transparent !important;
        }
    `;
    document.head.appendChild(style);
});