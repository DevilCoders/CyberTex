(() => {
  const buttons = document.querySelectorAll('[data-section]');
  const content = document.getElementById('content');

  async function loadSection(path) {
    try {
      const response = await fetch(path);
      if (!response.ok) {
        throw new Error(`Failed to load ${path}`);
      }
      const markup = await response.text();
      content.innerHTML = markup;
    } catch (error) {
      content.innerHTML = `<article><h2>Unable to load content</h2><p>${error.message}</p></article>`;
    }
  }

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      buttons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
      loadSection(button.dataset.section);
    });
  });
})();
