export function createHeader(): HTMLElement {
  const header = document.createElement("header");
  header.className = "header";

  header.innerHTML = `
    <div class="container">
      <h1>Викторина</h1>
      <p>Получай интересные вопросы викторины</p>
    </div>
  `;

  return header;
}
