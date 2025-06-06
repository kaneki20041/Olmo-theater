import { initCarousel } from './carousel.js';
import { initOlmobras } from './olmobras.js';
import { initServicios } from './servicios.js';

document.addEventListener("DOMContentLoaded", () => {
  initCarousel();
  initOlmobras();
  initServicios();

  
  // Ajuste automático de padding-top según altura del header
  const header = document.querySelector('header');
  if (header) {
    const updatePadding = () => {
      const headerHeight = header.offsetHeight;
      document.body.style.paddingTop = `${headerHeight}px`;
      document.documentElement.style.scrollPaddingTop = `${headerHeight}px`;
    };

    updatePadding();
    window.addEventListener('resize', updatePadding);
  }

  // ✅ Agregar menú hamburguesa dentro del DOMContentLoaded
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuToggle && navLinks) {
    mobileMenuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }
});
