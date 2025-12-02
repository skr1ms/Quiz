import { apiClient } from "@/services/api-client";
import { formatError } from "@/utils/format";

export async function renderHomePage(): Promise<HTMLElement> {
  const page = document.createElement("div");
  page.className = "page";

  let status = "checking";
  let error: string | null = null;

  try {
    await apiClient.healthCheck();
    status = "ok";
  } catch (err) {
    status = "error";
    error = formatError(err);
  }

  page.innerHTML = `
    <h1>Добро пожаловать!</h1>
    <p class="mb-2">Здесь вы можете получить интересные вопросы викторины.</p>
    
    <div class="data-card">
      <h3>Статус сервиса</h3>
      <div class="flex mt-1">
        <span class="status-badge ${status === "ok" ? "ok" : "error"}">
          ${status === "ok" ? "✓ Работает" : "✗ Ошибка"}
        </span>
      </div>
      ${status === "error" && error ? `<div class="error mt-1">${error}</div>` : ""}
      ${
        status === "ok"
          ? `
        <p class="mt-1">Сервис доступен и готов к работе.</p>
      `
          : `
        <p class="mt-1">Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.</p>
      `
      }
    </div>

    <div class="data-card mt-2">
      <h3>Что можно сделать</h3>
      <ul style="padding-left: 1.5rem; margin-top: 1rem;">
        <li><strong>Получить вопрос викторины</strong> - введите любое число или получите случайный вопрос</li>
        <li><strong>Посмотреть историю</strong> - просмотрите все сохраненные вопросы викторины</li>
      </ul>
    </div>
  `;

  return page;
}
