document.addEventListener("DOMContentLoaded", function () {
    const box = document.querySelector('.carrosselBox');
    const leftBtn = document.querySelector(".switchLeft");
    const rightBtn = document.querySelector(".switchRight");
    const imagePadding = 20;
  
    let scrollPerClick = 200;
  
    function ajustarScroll() {
      const primeiraImagem = document.querySelector(".carrosselBox img");
      if (primeiraImagem) {
        scrollPerClick = primeiraImagem.clientWidth + imagePadding;
      }
    }
  
    function sliderScrollLeft() {
      box.scrollBy({
        left: -scrollPerClick,
        behavior: "smooth"
      });
    }
  
    function sliderScrollRight() {
      box.scrollBy({
        left: scrollPerClick,
        behavior: "smooth"
      });
    }
  
    // Liga os botões às funções
    if (leftBtn && rightBtn) {
      leftBtn.addEventListener("click", sliderScrollLeft);
      rightBtn.addEventListener("click", sliderScrollRight);
    }
  
    ajustarScroll();
  
    // Remover flash após 3 segundos
    const flash = document.getElementById("flash-message");
    if (flash) {
      setTimeout(() => {
        flash.style.display = "none";
      }, 3000);
    }
  });
  