import { For, Show } from "solid-js";
import { countLeaves } from "../catalog";
import { useApp } from "../app-state";
import { pathOf } from "../paths";
import { armPlace } from "../session";
import { loadBookmarks, mostRecent, placeLabel, removeBookmark, type Place } from "../store";
import type { CatNode, Collection } from "../types";
import { AppLink } from "../components/link";

function finePointer(): boolean {
  return (
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
    !window.matchMedia("(hover: none)").matches
  );
}

function tilt(event: PointerEvent): void {
  if (!finePointer()) return;
  const el = event.currentTarget as HTMLElement;
  const rect = el.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;
  el.style.setProperty("--tilt-x", `${(-y * 9).toFixed(2)}deg`);
  el.style.setProperty("--tilt-y", `${(x * 12 - 6).toFixed(2)}deg`);
}

function untilt(event: PointerEvent): void {
  const el = event.currentTarget as HTMLElement;
  el.style.removeProperty("--tilt-x");
  el.style.removeProperty("--tilt-y");
}

function Cover(props: { col: Collection; vol: CatNode }) {
  return (
    <AppLink
      class="cover"
      href={pathOf(props.vol.route)}
      aria-label={props.vol.title}
      onPointerMove={tilt}
      onPointerLeave={untilt}
    >
      <span class="cover-spine" />
      <span class="cover-body">
        <span class="cover-pali">{props.vol.pali ?? props.col.title}</span>
        <span class="cover-title">{props.vol.title}</span>
        <span class="cover-meta">{countLeaves(props.vol)} mục</span>
      </span>
      <span class="cover-pages" aria-hidden="true" />
    </AppLink>
  );
}

function Continue(props: { place: Place }) {
  const extra = () => [placeLabel(props.place), props.place.snippet].filter(Boolean).join(" · ");
  return (
    <section class="hero">
      <AppLink class="continue" href={pathOf(props.place.route)}>
        <span>
          Đọc tiếp · <em>{props.place.title}</em>
        </span>
        <Show when={extra()}>
          <small>{extra()}</small>
        </Show>
      </AppLink>
    </section>
  );
}

export function Shelf() {
  const app = useApp();
  const recent = () => {
    app.markRev();
    const place = mostRecent();
    return place?.route.startsWith("new/") ? place : undefined;
  };
  const marks = () => {
    app.markRev();
    return loadBookmarks().filter((mark) => mark.route.startsWith("new/"));
  };
  const cols = app.catalog.collections.filter((col) => col.id === "new");
  return (
    <main class="wrap">
      <Show when={recent()}>{(place) => <Continue place={place()} />}</Show>
      <Show when={marks().length > 0}>
        <section class="marks-shelf">
          <h2>Đánh dấu</h2>
          <ul>
            <For each={marks()}>
              {(mark) => (
                <li>
                  <AppLink href={pathOf(mark.route)} onClick={() => armPlace(mark)}>
                    <strong>{mark.title}</strong>
                    <span>
                      {placeLabel(mark)}
                      {mark.snippet ? ` · ${mark.snippet}` : ""}
                    </span>
                  </AppLink>
                  <button
                    type="button"
                    class="icon-btn"
                    title="Xóa dấu"
                    onClick={() => {
                      removeBookmark(mark.id);
                      app.bumpMarks();
                    }}
                  >
                    ×
                  </button>
                </li>
              )}
            </For>
          </ul>
        </section>
      </Show>
      <For each={cols}>
        {(col) => (
          <section class={`shelf col-${col.id}`} id={`shelf-${col.id}`}>
            <div class="shelf-bay">
              <div class="shelf-plank">
                <For each={col.volumes}>{(vol) => <Cover col={col} vol={vol} />}</For>
              </div>
            </div>
          </section>
        )}
      </For>
    </main>
  );
}
