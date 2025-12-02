import { router } from "@/components/router";
import { createHeader } from "@/components/header";
import { createNav } from "@/components/nav";
import { renderHomePage } from "@/pages/home";
import { renderFetchDataPage } from "@/pages/fetch-data";
import { renderDataListPage } from "@/pages/data-list";

router.register({
  path: "/",
  component: renderHomePage,
  title: "Главная",
});

router.register({
  path: "/fetch",
  component: renderFetchDataPage,
  title: "Получить вопрос",
});

router.register({
  path: "/list",
  component: renderDataListPage,
  title: "История",
});

async function init() {
  const app = document.getElementById("app");
  if (!app) {
    throw new Error("App element not found");
  }

  const container = document.createElement("div");
  container.className = "container";

  const header = createHeader();
  const nav = createNav();

  container.appendChild(header);
  container.appendChild(nav);
  app.appendChild(container);

  const initialPath = window.location.pathname || "/";
  await router.navigate(initialPath);

  window.addEventListener("popstate", () => {
    router.navigate(window.location.pathname);
  });
}

init().catch(console.error);
