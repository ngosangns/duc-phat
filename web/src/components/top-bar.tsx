import { Show } from "solid-js";
import { themeLabel, useApp } from "../app-state";
import { AppLink } from "./link";
import { IconBookmark, IconList } from "./icons";

export function TopBar(props: {
  brand: string;
  sub: string;
  reader?: boolean;
  marked?: boolean;
  onMark?: () => void;
}) {
  const app = useApp();
  const label = () => (props.marked ? "Bỏ đánh dấu (B)" : "Đánh dấu chỗ đang đọc (B)");
  return (
    <header class="top">
      <AppLink class="brand" href="/">
        {props.brand}
        <small>{props.sub}</small>
      </AppLink>
      <nav>
        <Show when={props.reader}>
          <button
            class="icon-btn icon-only toc-drawer"
            type="button"
            title="Mục lục (T)"
            aria-label="Mục lục"
            onClick={() => app.toggleToc()}
          >
            <IconList />
          </button>
          <button
            class="icon-btn icon-only"
            classList={{ "is-on": Boolean(props.marked) }}
            type="button"
            title={label()}
            aria-label={label()}
            aria-pressed={props.marked ? "true" : "false"}
            onClick={() => props.onMark?.()}
          >
            <IconBookmark />
          </button>
          <button class="icon-btn type-size" type="button" title="Chữ nhỏ hơn" onClick={() => app.bumpFont(-0.05)}>
            A−
          </button>
          <button class="icon-btn type-size" type="button" title="Chữ lớn hơn" onClick={() => app.bumpFont(0.05)}>
            A+
          </button>
          <button class="icon-btn" type="button" title="Đổi nền giấy" onClick={() => app.cycleTheme()}>
            {themeLabel(app.settings().theme)}
          </button>
        </Show>
      </nav>
    </header>
  );
}
