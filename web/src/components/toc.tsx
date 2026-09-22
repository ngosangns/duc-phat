import { createEffect, createMemo, For, Show } from "solid-js";
import { countLeaves, displayNum, displayTitle } from "../catalog";
import { parallelEdition } from "../editions";
import { bookmarksFor, placeFor, placeLabel } from "../store";
import { arm } from "../nav";
import { pathOf } from "../paths";
import { asEdition, type VolumeView } from "../resolve";
import type { Catalog, CatNode } from "../types";
import { useApp } from "../app-state";
import { AppLink } from "./link";

function tocNum(id: string): string {
  const num = displayNum(id);
  return num === "·" ? "" : num;
}

function selfText(node: CatNode): string {
  return `${node.title} ${node.pali ?? ""}`.toLowerCase();
}

function visible(node: CatNode, query: string): boolean {
  if (!query) return true;
  if (selfText(node).includes(query)) return true;
  return (node.children ?? []).some((child) => visible(child, query));
}

function TocMarks(props: { href: string | null }) {
  const app = useApp();
  const saved = createMemo(() => {
    app.markRev();
    return props.href ? placeFor(props.href) : undefined;
  });
  const marked = createMemo(() => {
    app.markRev();
    return props.href ? bookmarksFor(props.href).length > 0 : false;
  });
  const hint = () => (saved() ? placeLabel(saved()!) : marked() ? "có dấu" : "");
  return (
    <span class="toc-slot">
      <Show when={saved() || marked()}>
        <span class="mark" classList={{ "is-pin": marked() }} title={hint()} />
      </Show>
    </span>
  );
}

function TocLeaf(props: { node: CatNode; href: string | null; query: string; force: boolean }) {
  const show = () => props.force || visible(props.node, props.query);
  const num = () => tocNum(props.node.id);
  const body = () => (
    <>
      <span class="toc-num">{num()}</span>
      <span class="toc-body">
        <span class="toc-title">{displayTitle(props.node)}</span>
        <Show when={props.node.pali}>
          <span class="toc-en">{props.node.pali}</span>
        </Show>
      </span>
      <TocMarks href={props.href} />
    </>
  );
  return (
    <li hidden={!show()}>
      <Show when={props.href} fallback={<span class="is-missing">{body()}</span>}>
        {(href) => (
          <AppLink href={pathOf(href())} end>
            {body()}
          </AppLink>
        )}
      </Show>
    </li>
  );
}

function TocGroup(props: { node: CatNode; hrefOf: (leaf: CatNode) => string | null; query: string; force: boolean }) {
  let details: HTMLDetailsElement | undefined;
  let opened = false;
  const show = () => props.force || visible(props.node, props.query);
  const openKids = () => props.query !== "" && selfText(props.node).includes(props.query);
  createEffect(() => {
    if (!details) return;
    if (!opened) {
      details.open = true;
      opened = true;
    }
    if (props.query !== "" && show()) details.open = true;
  });
  const num = () => tocNum(props.node.id);
  return (
    <li class="toc-group" hidden={!show()}>
      <details ref={details}>
        <summary>
          <span class="toc-summary">
            <span class="toc-chevron" aria-hidden="true" />
            <span class="toc-body">
              <span class="toc-title">
                <Show when={num()}>
                  <span class="toc-num">{num()}</span>
                </Show>
                {displayTitle(props.node)}
              </span>
              <Show when={props.node.pali}>
                <span class="toc-en">{props.node.pali}</span>
              </Show>
            </span>
            <span class="toc-count">{countLeaves(props.node)}</span>
          </span>
        </summary>
        <ul class="toc-list">
          <For each={props.node.children ?? []}>
            {(child) => (
              <TocNode node={child} hrefOf={props.hrefOf} query={props.query} force={openKids()} />
            )}
          </For>
        </ul>
      </details>
    </li>
  );
}

function TocNode(props: { node: CatNode; hrefOf: (leaf: CatNode) => string | null; query: string; force: boolean }) {
  const group = () => Boolean(props.node.children?.length) && !props.node.path;
  return (
    <Show
      when={group() ? props.node : undefined}
      fallback={<TocLeaf node={props.node} href={props.hrefOf(props.node)} query={props.query} force={props.force} />}
    >
      <TocGroup node={props.node} hrefOf={props.hrefOf} query={props.query} force={props.force} />
    </Show>
  );
}

export function volumeHref(cat: Catalog, view: VolumeView, leaf: CatNode): string | null {
  if (!view.shared) return leaf.route;
  if (!leaf.path) return null;
  if (view.col.id === "new") return leaf.route;
  return parallelEdition(cat, leaf, view.vol.id, asEdition(view.col.id));
}

export function VolumeToc(props: { view: VolumeView; query: string }) {
  const app = useApp();
  const hrefOf = (leaf: CatNode) => volumeHref(app.catalog, props.view, leaf);
  return (
    <ul class="toc-list" id="toc-list">
      <For each={props.view.shown.children ?? []}>
        {(child) => <TocNode node={child} hrefOf={hrefOf} query={props.query} force={false} />}
      </For>
    </ul>
  );
}

function covers(node: CatNode, active: Set<string>): boolean {
  if (node.path && active.has(node.route)) return true;
  return (node.children ?? []).some((child) => covers(child, active));
}

function ReaderGroup(props: {
  node: CatNode;
  active: () => Set<string>;
  hrefOf: (leaf: CatNode) => string | null;
}) {
  let details: HTMLDetailsElement | undefined;
  createEffect(() => {
    if (covers(props.node, props.active()) && details) details.open = true;
  });
  return (
    <details class="rtoc-group" ref={details}>
      <summary>
        <span class="rtoc-sum">
          <span class="rtoc-chev" aria-hidden="true" />
          <span class="rtoc-title">{displayTitle(props.node)}</span>
          <span class="rtoc-count">{countLeaves(props.node)}</span>
        </span>
      </summary>
      <div class="rtoc-kids">
        <For each={props.node.children ?? []}>
          {(child) => <ReaderNode node={child} active={props.active} hrefOf={props.hrefOf} />}
        </For>
      </div>
    </details>
  );
}

function ReaderNode(props: {
  node: CatNode;
  active: () => Set<string>;
  hrefOf: (leaf: CatNode) => string | null;
}) {
  const group = () => Boolean(props.node.children?.length) && !props.node.path;
  return (
    <Show when={group() ? props.node : undefined} fallback={<ReaderLeaf node={props.node} href={props.hrefOf(props.node)} />}>
      <ReaderGroup node={props.node} active={props.active} hrefOf={props.hrefOf} />
    </Show>
  );
}

function ReaderLeaf(props: { node: CatNode; href: string | null }) {
  const num = () => tocNum(props.node.id);
  const inner = () => (
    <>
      <span class="rtoc-num">{num()}</span>
      <span class="rtoc-title">{displayTitle(props.node)}</span>
    </>
  );
  return (
    <Show when={props.href} fallback={<span class="rtoc-link is-missing">{inner()}</span>}>
      {(href) => (
        <AppLink class="rtoc-link" href={pathOf(href())} end activeClass="active" onClick={() => arm("fade")}>
          {inner()}
        </AppLink>
      )}
    </Show>
  );
}

export function ReaderToc(props: {
  outline: CatNode;
  active: () => Set<string>;
  hrefOf: (leaf: CatNode) => string | null;
}) {
  return (
    <nav class="rtoc" aria-label="Mục lục">
      <For each={props.outline.children ?? []}>
        {(child) => <ReaderNode node={child} active={props.active} hrefOf={props.hrefOf} />}
      </For>
    </nav>
  );
}
