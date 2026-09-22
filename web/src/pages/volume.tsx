import { createEffect, createSignal, For, Show } from "solid-js";
import { countLeaves, crumbParts } from "../catalog";
import { useApp } from "../app-state";
import { motionOk } from "../nav";
import { pathOf } from "../paths";
import type { VolumeView } from "../resolve";
import type { CatNode } from "../types";
import { AppLink } from "../components/link";
import { TopBar } from "../components/top-bar";
import { VolumeToc } from "../components/toc";

function Crumbs(props: { view: VolumeView }) {
  const node = () => (props.view.shared ? props.view.vol : props.view.node);
  const labels = () => {
    const map: Record<string, string> = {
      [props.view.col.id]: props.view.col.title,
      [props.view.vol.id]: props.view.vol.title,
    };
    const walk = (item: CatNode) => {
      map[item.id] = item.title;
      item.children?.forEach(walk);
    };
    walk(props.view.vol);
    return map;
  };
  return (
    <nav class="crumb">
      <AppLink href="/">Kệ sách</AppLink>
      <For each={crumbParts(node().route)}>
        {(part) => {
          const id = part.split("/").pop() ?? part;
          const label = labels()[id] ?? id;
          const here = () => part === node().route;
          return (
            <>
              <span aria-hidden="true"> · </span>
              <Show when={here()} fallback={<AppLink href={pathOf(part)}>{label}</AppLink>}>
                <span class="here">{label}</span>
              </Show>
            </>
          );
        }}
      </For>
    </nav>
  );
}

export function Volume(props: { view: VolumeView }) {
  const app = useApp();
  const [query, setQuery] = createSignal("");
  let pane: HTMLElement | undefined;
  let seen = "";
  createEffect(() => {
    const route = props.view.node.route;
    if (seen && seen !== route) setQuery("");
    if (pane && seen && seen !== route && motionOk()) {
      pane.animate(
        [
          { opacity: 0.45, transform: "translateY(10px)" },
          { opacity: 1, transform: "none" },
        ],
        { duration: 240, easing: "cubic-bezier(0.2, 0.7, 0.2, 1)" },
      );
    }
    seen = route;
  });
  return (
    <>
      <TopBar brand={app.catalog.title} sub={props.view.col.title} />
      <main class="wrap toc-page" ref={pane}>
        <Crumbs view={props.view} />
        <header class="toc-head">
          <h1>{props.view.shown.title || props.view.vol.title}</h1>
          <Show when={props.view.shown.pali}>
            <p class="pali">{props.view.shown.pali}</p>
          </Show>
          <p class="toc-meta">{countLeaves(props.view.shown)} mục</p>
        </header>
        <input
          class="filter"
          type="search"
          placeholder="Lọc tên kinh trong tập này…"
          aria-label="Lọc mục lục"
          value={query()}
          onInput={(event) => setQuery(event.currentTarget.value)}
        />
        <VolumeToc view={props.view} query={query().trim().toLowerCase()} />
      </main>
    </>
  );
}
