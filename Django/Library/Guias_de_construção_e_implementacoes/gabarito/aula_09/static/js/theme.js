// Tema claro/escuro: a escolha fica guardada no navegador (localStorage)
(function () {
  const root = document.documentElement; // a tag <html>
  const button = document.getElementById("theme-toggle");

  // Liga ou desliga a classe .theme-dark e ajusta o texto do botão
  function apply(theme) {
    root.classList.toggle("theme-dark", theme === "dark");
    button.textContent = theme === "dark" ? "Tema claro" : "Tema escuro";
  }

  // Na primeira visita, segue a preferência do sistema operacional
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  apply(localStorage.getItem("theme") || (prefersDark ? "dark" : "light"));

  // A cada clique, inverte o tema e guarda a escolha
  button.addEventListener("click", function () {
    const next = root.classList.contains("theme-dark") ? "light" : "dark";
    localStorage.setItem("theme", next);
    apply(next);
  });
})();
