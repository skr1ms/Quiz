import { apiClient } from "@/services/api-client";
import { formatError, formatDate } from "@/utils/format";
import type { ApiData } from "@/types/api";

export async function renderFetchDataPage(): Promise<HTMLElement> {
  const page = document.createElement("div");
  page.className = "page";

  let result: ApiData | null = null;
  let error: string | null = null;
  let loading = false;

  const updateContent = () => {
    const formContainer = page.querySelector("#form-container");
    const resultContainer = page.querySelector("#result-container");
    const errorContainer = page.querySelector("#error-container");

    if (formContainer) {
      const submitBtn = formContainer.querySelector(
        'button[type="submit"]',
      ) as HTMLButtonElement;
      if (submitBtn) {
        submitBtn.disabled = loading;
        submitBtn.textContent = loading ? "Загрузка..." : "Получить вопрос";
      }
    }

    if (errorContainer) {
      errorContainer.innerHTML = error
        ? `<div class="error">${error}</div>`
        : "";
    }

    if (resultContainer) {
      if (result) {
        resultContainer.innerHTML = `
          <div class="data-card mt-2">
            <h3>${result.title}</h3>
            <p><strong>Источник:</strong> ${result.source}</p>
            <p><strong>Содержание:</strong> ${result.content}</p>
            ${result.external_id ? `<p><strong>ID:</strong> ${result.external_id}</p>` : ""}
            <div class="meta">
              <p><strong>ID записи:</strong> ${result.id}</p>
              <p><strong>Получено:</strong> ${formatDate(result.fetched_at)}</p>
              <p><strong>Создано:</strong> ${formatDate(result.created_at)}</p>
            </div>
          </div>
        `;
      } else {
        resultContainer.innerHTML = "";
      }
    }
  };

  page.innerHTML = `
    <h1>Получить вопрос викторины</h1>
    <p class="mb-2">Введите любое число, чтобы получить интересный вопрос викторины, или оставьте поле пустым для случайного вопроса.</p>
    
    <div id="form-container">
      <form id="fetch-form">
        <div class="form-group">
          <label for="number-input">Число (необязательно):</label>
          <input
            type="number"
            id="number-input"
            name="number"
            placeholder="Например: 42"
            min="1"
          />
        </div>
        
        <button type="submit" class="btn">Получить вопрос</button>
      </form>
    </div>

    <div id="error-container"></div>
    <div id="result-container"></div>
  `;

  const form = page.querySelector("#fetch-form") as HTMLFormElement;
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      loading = true;
      error = null;
      result = null;
      updateContent();

      const formData = new FormData(form);
      const numberValue = formData.get("number");
      const number = numberValue
        ? parseInt(numberValue as string, 10)
        : undefined;

      try {
        result = await apiClient.fetchData({ number });
        error = null;
      } catch (err) {
        error = formatError(err);
        result = null;
      } finally {
        loading = false;
        updateContent();
      }
    });
  }

  return page;
}
