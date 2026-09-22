import { createMemo, Show } from "solid-js";
import { Navigate, useLocation } from "@solidjs/router";
import { useApp } from "../app-state";
import { resolve, type ReaderView, type View, type VolumeView } from "../resolve";
import { Missing } from "./missing";
import { Reader } from "./reader";
import { Volume } from "./volume";

function volumeOf(view: View): VolumeView | undefined {
  return view.kind === "volume" ? view : undefined;
}

function readerOf(view: View): ReaderView | undefined {
  return view.kind === "reader" ? view : undefined;
}

export function LocationPage() {
  const loc = useLocation();
  const app = useApp();
  const view = createMemo(() => resolve(app.catalog, loc.pathname));
  return (
    <Show when={view().kind !== "redirect"} fallback={<Navigate href="/" />}>
      <Show when={volumeOf(view())}>{(item) => <Volume view={item()} />}</Show>
      <Show when={readerOf(view())}>{(item) => <Reader view={item()} />}</Show>
      <Show when={view().kind === "missing"}>
        <Missing />
      </Show>
    </Show>
  );
}
