// @ts-check

export function initApp(doc = document) {
  const button = doc.getElementById('action-button');
  const output = doc.getElementById('output');

  if (!button || !output) {
    return;
  }

  button.addEventListener('click', () => {
    output.textContent = 'Gotowe! Kliknięcie działa bez przeładowania strony.';
  });
}

initApp();
