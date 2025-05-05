document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll(".carousel-slide");
  const nextBtn = document.querySelector(".carousel-btn.next");
  const prevBtn = document.querySelector(".carousel-btn.prev");
  let currentIndex = 0;
  let intervalId;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle("active", i === index);
    });
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
  }

  function prevSlide() {
    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(currentIndex);
  }

  function resetInterval() {
    clearInterval(intervalId);
    intervalId = setInterval(nextSlide, 5000);
  }

  if (nextBtn && prevBtn) {
    nextBtn.addEventListener("click", () => {
      nextSlide();
      resetInterval();
    });

    prevBtn.addEventListener("click", () => {
      prevSlide();
      resetInterval();
    });
  }

  showSlide(currentIndex); 
  intervalId = setInterval(nextSlide, 5000); 
});
