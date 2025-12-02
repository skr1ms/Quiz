export type Route = {
  path: string;
  component: () => Promise<HTMLElement>;
  title: string;
};

export class Router {
  private routes: Route[] = [];
  private currentRoute: Route | null = null;

  register(route: Route): void {
    this.routes.push(route);
  }

  async navigate(path: string): Promise<void> {
    const route = this.routes.find((r) => r.path === path) || this.routes[0];

    if (!route) {
      throw new Error(`Route not found: ${path}`);
    }

    this.currentRoute = route;
    const container = document.querySelector(".container");

    if (container) {
      const existingPage = container.querySelector(".page");
      if (existingPage) {
        existingPage.remove();
      }

      const component = await route.component();
      container.appendChild(component);
      this.updateActiveLink();
    }
  }

  private updateActiveLink(): void {
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("data-path") === this.currentRoute?.path) {
        link.classList.add("active");
      }
    });
  }

  getRoutes(): Route[] {
    return this.routes;
  }

  getCurrentPath(): string {
    return this.currentRoute?.path || "/";
  }
}

export const router = new Router();
