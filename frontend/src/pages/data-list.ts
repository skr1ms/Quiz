import { apiClient } from "@/services/api-client";
import { formatError, formatDate } from "@/utils/format";
import type { ApiDataList } from "@/types/api";

export async function renderDataListPage(): Promise<HTMLElement> {
  const page = document.createElement("div");
  page.className = "page";

  let data: ApiDataList | null = null;
  let error: string | null = null;
  let loading = false;
  let limit = 10;
  let offset = 0;

  const loadData = async () => {
    loading = true;
    error = null;
    render();

    try {
      data = await apiClient.getAllData(limit, offset);
      error = null;
    } catch (err) {
      error = formatError(err);
      data = null;
    } finally {
      loading = false;
      render();
    }
  };

  const render = () => {
    page.innerHTML = `
      <h1>История вопросов</h1>
      <p class="mb-2">Все полученные вопросы викторины сохраняются здесь. Вы можете просмотреть всю историю.</p>
      
      <div class="flex mb-2">
        <div class="form-group" style="flex: 1; margin-bottom: 0;">
          <label for="limit-input">Лимит:</label>
          <input
            type="number"
            id="limit-input"
            value="${limit}"
            min="1"
            max="100"
            style="max-width: 100px;"
          />
        </div>
        <button type="button" class="btn" id="reload-btn" ${loading ? "disabled" : ""}>
          ${loading ? "Загрузка..." : "Обновить"}
        </button>
      </div>

      ${error ? `<div class="error">${error}</div>` : ""}
      
      ${loading && !data ? `<div class="loading">Загрузка данных...</div>` : ""}
      
      ${
        data
          ? `
        <div class="mb-1">
          <p><strong>Всего записей:</strong> ${data.total}</p>
          <p><strong>Показано:</strong> ${data.items.length} из ${data.total}</p>
        </div>
        
        ${
          data.items.length === 0
            ? `
          <div class="data-card">
            <p>История пуста. Попробуйте получить вопрос викторины на странице "Получить вопрос".</p>
          </div>
        `
            : `
          ${data.items
            .map(
              (item) => `
            <div class="data-card">
              <h3>${item.title}</h3>
              <p><strong>Источник:</strong> ${item.source}</p>
              <p><strong>Содержание:</strong> ${item.content.substring(0, 200)}${item.content.length > 200 ? "..." : ""}</p>
              <div class="meta">
                <p><strong>ID:</strong> ${item.id}</p>
                <p><strong>Получено:</strong> ${formatDate(item.fetched_at)}</p>
              </div>
            </div>
          `,
            )
            .join("")}
          
          <div class="flex mt-2">
            <button 
              class="btn btn-secondary" 
              id="prev-btn" 
              ${offset === 0 ? "disabled" : ""}
            >
              Назад
            </button>
            <span style="flex: 1; text-align: center; padding: 0.75rem;">
              Страница ${Math.floor(offset / limit) + 1} из ${Math.ceil(data.total / limit) || 1}
            </span>
            <button 
              class="btn btn-secondary" 
              id="next-btn" 
              ${offset + limit >= data.total ? "disabled" : ""}
            >
              Вперед
            </button>
          </div>
        `
        }
      `
          : ""
      }
    `;

    const limitInput = page.querySelector("#limit-input") as HTMLInputElement;
    const reloadBtn = page.querySelector("#reload-btn");
    const prevBtn = page.querySelector("#prev-btn");
    const nextBtn = page.querySelector("#next-btn");

    if (limitInput) {
      limitInput.addEventListener("change", () => {
        limit = parseInt(limitInput.value, 10) || 10;
        offset = 0;
        loadData();
      });
    }

    if (reloadBtn) {
      reloadBtn.addEventListener("click", loadData);
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        offset = Math.max(0, offset - limit);
        loadData();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (data && offset + limit < data.total) {
          offset += limit;
          loadData();
        }
      });
    }
  };

  loadData();
  return page;
}
