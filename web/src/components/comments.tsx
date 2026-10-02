import { createEffect, onCleanup } from "solid-js";
import { useLocation } from "@solidjs/router";
import { useApp } from "../app-state";

const COMMENTS_ORIGIN = "https://comments.sang.id.vn";
const SLOT_ID = "phat-comments";

function giscusTheme(theme: string): string {
  if (theme === "night") return "dark";
  if (theme === "sepia") return "gruvbox_light";
  return "light";
}

/**
 * Same stack as sang.id.vn (giscusflare @ comments.sang.id.vn), but discussions live in
 * ngosangns/phat.gnas.dev-comments. Pathname mapping → one thread per sutta/page.
 */
export function Comments() {
  const location = useLocation();
  const app = useApp();
  let release: (() => void) | undefined;
  let returnToComments = window.location.hash.startsWith("#gw-auth=");

  createEffect(() => {
    const pageKey = location.pathname;
    const theme = giscusTheme(app.settings().theme);
    const slot = document.getElementById(SLOT_ID) as
      | (HTMLElement & { __gwCleanup?: () => void })
      | null;
    if (!slot) return;

    if (
      slot.dataset.gwPage === pageKey &&
      slot.dataset.gwTheme === theme &&
      slot.querySelector("iframe.giscus-frame, script[data-repo]")
    ) {
      return;
    }

    release?.();
    release = undefined;
    slot.dataset.gwPage = pageKey;
    slot.dataset.gwTheme = theme;
    slot.replaceChildren();

    const script = document.createElement("script");
    script.src = `${COMMENTS_ORIGIN}/client.js`;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.dataset.repo = "ngosangns/phat.gnas.dev-comments";
    script.dataset.repoId = "R_kgDOU5D_UA";
    script.dataset.category = "Announcements";
    script.dataset.categoryId = "DIC_kwDOU5D_UM4DG5Et";
    script.dataset.mapping = "pathname";
    script.dataset.strict = "1";
    script.dataset.reactionsEnabled = "1";
    script.dataset.inputPosition = "bottom";
    script.dataset.theme = theme;
    script.dataset.lang = "vi";
    script.dataset.loading = "lazy";
    script.dataset.container = SLOT_ID;

    script.addEventListener("load", () => {
      const cleanup = slot.__gwCleanup;
      release = () => {
        cleanup?.();
        if (slot.__gwCleanup === cleanup) slot.__gwCleanup = undefined;
      };
      if (!returnToComments) return;
      returnToComments = false;
      const pinComments = () => {
        const section = document.getElementById("comments");
        if (!section) return;
        if (!window.location.hash || window.location.hash.startsWith("#gw-auth=")) {
          history.replaceState(null, "", `${pageKey}${window.location.search}#comments`);
        }
        const root = document.documentElement;
        const top = Math.max(
          0,
          Math.min(
            root.scrollHeight - window.innerHeight,
            window.scrollY + section.getBoundingClientRect().top - 16,
          ),
        );
        window.scrollTo({ top, behavior: "instant" as ScrollBehavior });
      };
      pinComments();
      if (document.readyState !== "complete") {
        window.addEventListener("load", pinComments, { once: true });
      }
      const timers = [1200, 4000].map((delay) => window.setTimeout(pinComments, delay));
      const layout = new ResizeObserver(() => {
        const section = document.getElementById("comments");
        if (!section || section.getBoundingClientRect().top <= 48) return;
        pinComments();
      });
      layout.observe(document.body);
      const stopLayout = () => {
        layout.disconnect();
        for (const timer of timers) window.clearTimeout(timer);
      };
      window.addEventListener("pointerdown", stopLayout, { once: true, capture: true });
      window.addEventListener("wheel", stopLayout, { once: true, passive: true });
      window.addEventListener("keydown", stopLayout, { once: true });
      window.setTimeout(stopLayout, 8000);
      const onRendered = (event: MessageEvent) => {
        if (event.origin !== COMMENTS_ORIGIN) return;
        const data = event.data?.giscus;
        if (!data || typeof data !== "object" || !("rendered" in data)) return;
        window.removeEventListener("message", onRendered);
        pinComments();
      };
      window.addEventListener("message", onRendered);
    });

    slot.appendChild(script);

    onCleanup(() => {
      release?.();
      release = undefined;
    });
  });

  return (
    <section id="comments" class="comments" aria-labelledby="comments-heading">
      <h2 id="comments-heading">Bình luận</h2>
      <div id={SLOT_ID} />
    </section>
  );
}
