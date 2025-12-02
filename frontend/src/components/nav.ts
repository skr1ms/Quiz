import { router, type Route } from "./router";

export function createNav(): HTMLElement {
  const nav = document.createElement("nav");
  nav.className = "nav";

  const navList = document.createElement("ul");
  navList.className = "nav-list";

  router.getRoutes().forEach((route: Route) => {
    const listItem = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#";
    link.className = "nav-link";
    link.setAttribute("data-path", route.path);
    link.textContent = route.title;

    link.addEventListener("click", (e) => {
      e.preventDefault();
      router.navigate(route.path);
      window.history.pushState({}, "", route.path);
    });

    listItem.appendChild(link);
    navList.appendChild(listItem);
  });

  nav.appendChild(navList);
  return nav;
}
