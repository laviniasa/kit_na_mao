document.addEventListener("DOMContentLoaded", function () {
  const box = document.querySelector(".carrosselBox");
  const leftBtn = document.querySelector(".switchLeft");
  const rightBtn = document.querySelector(".switchRight");
  const imagePadding = 20;

  let scrollPerClick = 200;

  function ajustarScroll() {
    const primeiraImagem = box.querySelector("img");
    if (primeiraImagem) {
      scrollPerClick = primeiraImagem.clientWidth + imagePadding;
      console.log("scrollPerClick ajustado para:", scrollPerClick);
    } else {
      console.log("Imagem não encontrada para ajuste.");
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

  if (leftBtn && rightBtn && box) {
    leftBtn.addEventListener("click", sliderScrollLeft);
    rightBtn.addEventListener("click", sliderScrollRight);
  }

  ajustarScroll();
  window.addEventListener("resize", ajustarScroll);

  // Oculta mensagem flash depois de 3s
  const flash = document.getElementById("flash-message");
  if (flash) {
    setTimeout(() => {
      flash.style.display = "none";
    }, 3000);
  }
});
