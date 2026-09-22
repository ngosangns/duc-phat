import "./fonts.css";
import "./style.css";
import { render } from "solid-js/web";
import { AppProvider, applySettings } from "./app-state";
import { App } from "./app";
import { loadCatalog } from "./catalog";
import { prepareLocation } from "./paths";
import { loadSettings } from "./store";

prepareLocation();
applySettings(loadSettings());

const root = document.querySelector<HTMLDivElement>("#app");
if (!root) throw new Error("Thiếu #app");

function escapeHtml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

loadCatalog()
  .then((catalog) => {
    document.title = catalog.title;
    render(
      () => (
        <AppProvider catalog={catalog}>
          <App />
        </AppProvider>
      ),
      root,
    );
  })
  .catch((err: Error) => {
    root.innerHTML = `<p class="err">${escapeHtml(err.message)} Hãy chạy <code>python3 scripts/build-web.py</code>.</p>`;
  });
