import { createEffect, onCleanup, onMount, type JSX } from "solid-js";
import { Route, Router, useBeforeLeave, useLocation, useNavigate } from "@solidjs/router";
import { installFloatingScrollbars } from "./scrollbar";
import { useApp } from "./app-state";
import { installTransitions } from "./nav";
import { legacyPath } from "./paths";
import { pageTitle, resolve } from "./resolve";
import { flushSession } from "./session";
import { LocationPage } from "./pages/location";
import { Shelf } from "./pages/shelf";

function Root(props: { children?: JSX.Element }) {
  const app = useApp();
  const location = useLocation();
  const navigate = useNavigate();
  useBeforeLeave(installTransitions(app.catalog));

  onMount(() => {
    installFloatingScrollbars();
    const onHash = () => {
      const next = legacyPath();
      if (!next || next === location.pathname) return;
      navigate(next, { replace: true, scroll: false });
    };
    window.addEventListener("hashchange", onHash);
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    const flush = () => flushSession();
    const onHide = () => {
      if (document.visibilityState === "hidden") flush();
    };
    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", onHide);
    onCleanup(() => {
      window.removeEventListener("pagehide", flush);
      document.removeEventListener("visibilitychange", onHide);
      window.removeEventListener("hashchange", onHash);
    });
  });

  let previous = "";
  createEffect(() => {
    const next = location.pathname;
    const from = previous;
    previous = next;
    document.title = pageTitle(app.catalog, next);
    document.body.classList.toggle("has-editions", resolve(app.catalog, next).kind === "reader");
    app.setTocOpen(false);
    const stayed =
      resolve(app.catalog, from).kind === "reader" && resolve(app.catalog, next).kind === "reader";
    if (!stayed) window.scrollTo(0, 0);
  });

  return <div class="stage">{props.children}</div>;
}

export function App() {
  return (
    <Router root={Root}>
      <Route path="/" component={Shelf} />
      <Route path="*path" component={LocationPage} />
    </Router>
  );
}
