/** Floating scrollbars. Native bars are hidden so they never reserve a gutter. */

type Axis = "x" | "y";

const MIN_THUMB = 28;
const EDGE = 3;

class FloatBar {
  readonly thumb = document.createElement("div");
  private hideTimer = 0;
  private dragOrigin = 0;
  private dragScroll = 0;
  private readonly onScroll = () => this.poke();
  private readonly onEnter = () => this.show();
  private readonly onLeave = () => this.scheduleHide();
  private readonly onDown = (ev: PointerEvent) => this.dragStart(ev);
  private readonly onMove = (ev: PointerEvent) => this.dragMove(ev);
  private readonly onUp = () => this.dragEnd();

  constructor(
    private readonly el: HTMLElement,
    private readonly axis: Axis,
  ) {
    this.thumb.className = `vscroll vscroll-${axis}`;
    this.thumb.setAttribute("aria-hidden", "true");
    document.body.appendChild(this.thumb);
    this.target.addEventListener("scroll", this.onScroll, { passive: true });
    this.el.addEventListener("pointerenter", this.onEnter);
    this.el.addEventListener("pointerleave", this.onLeave);
    this.thumb.addEventListener("pointerdown", this.onDown);
    this.place(false);
  }

  private get target(): HTMLElement | Window {
    return this.el === document.documentElement ? window : this.el;
  }

  private metrics() {
    if (this.el === document.documentElement) {
      const scroll = this.axis === "y" ? window.scrollY : window.scrollX;
      const view = this.axis === "y" ? window.innerHeight : window.innerWidth;
      const size = this.axis === "y" ? document.documentElement.scrollHeight : document.documentElement.scrollWidth;
      return { scroll, view, size, rect: new DOMRect(0, 0, window.innerWidth, window.innerHeight) };
    }
    const scroll = this.axis === "y" ? this.el.scrollTop : this.el.scrollLeft;
    const view = this.axis === "y" ? this.el.clientHeight : this.el.clientWidth;
    const size = this.axis === "y" ? this.el.scrollHeight : this.el.scrollWidth;
    return { scroll, view, size, rect: this.el.getBoundingClientRect() };
  }

  place(reveal: boolean) {
    const { scroll, view, size, rect } = this.metrics();
    const overflow = size - view;
    const onScreen =
      rect.bottom > 0 &&
      rect.right > 0 &&
      rect.top < window.innerHeight &&
      rect.left < window.innerWidth &&
      rect.width > 16 &&
      rect.height > 16;
    if (overflow < 2 || !onScreen) {
      this.thumb.classList.remove("is-on");
      return;
    }
    const track = Math.max(0, view - EDGE * 2);
    const thumb = Math.max(MIN_THUMB, Math.min(track, (view / size) * track));
    const travel = Math.max(1, track - thumb);
    const offset = EDGE + (scroll / overflow) * travel;
    if (this.axis === "y") {
      this.thumb.style.top = `${rect.top + offset}px`;
      this.thumb.style.left = `${rect.right - EDGE - 7}px`;
      this.thumb.style.height = `${thumb}px`;
      this.thumb.style.width = "7px";
    } else {
      this.thumb.style.left = `${rect.left + offset}px`;
      this.thumb.style.top = `${rect.bottom - EDGE - 7}px`;
      this.thumb.style.width = `${thumb}px`;
      this.thumb.style.height = "7px";
    }
    if (reveal) this.show();
  }

  private show() {
    window.clearTimeout(this.hideTimer);
    this.thumb.classList.add("is-on");
  }

  private scheduleHide() {
    window.clearTimeout(this.hideTimer);
    this.hideTimer = window.setTimeout(() => {
      if (!this.thumb.classList.contains("is-drag")) this.thumb.classList.remove("is-on");
    }, 700);
  }

  private poke() {
    this.place(true);
    this.scheduleHide();
  }

  private dragStart(ev: PointerEvent) {
    ev.preventDefault();
    ev.stopPropagation();
    this.thumb.classList.add("is-drag", "is-on");
    this.thumb.setPointerCapture(ev.pointerId);
    this.dragOrigin = this.axis === "y" ? ev.clientY : ev.clientX;
    const m = this.metrics();
    this.dragScroll = m.scroll;
    window.addEventListener("pointermove", this.onMove);
    window.addEventListener("pointerup", this.onUp);
  }

  private dragMove(ev: PointerEvent) {
    const m = this.metrics();
    const overflow = m.size - m.view;
    const track = Math.max(1, m.view - EDGE * 2);
    const thumb = Math.max(MIN_THUMB, Math.min(track, (m.view / m.size) * track));
    const travel = Math.max(1, track - thumb);
    const delta = (this.axis === "y" ? ev.clientY : ev.clientX) - this.dragOrigin;
    const next = this.dragScroll + (delta / travel) * overflow;
    if (this.el === document.documentElement) {
      if (this.axis === "y") window.scrollTo(window.scrollX, next);
      else window.scrollTo(next, window.scrollY);
    } else if (this.axis === "y") {
      this.el.scrollTop = next;
    } else {
      this.el.scrollLeft = next;
    }
  }

  private dragEnd() {
    this.thumb.classList.remove("is-drag");
    window.removeEventListener("pointermove", this.onMove);
    window.removeEventListener("pointerup", this.onUp);
    this.scheduleHide();
  }

  destroy() {
    window.clearTimeout(this.hideTimer);
    this.dragEnd();
    this.target.removeEventListener("scroll", this.onScroll);
    this.el.removeEventListener("pointerenter", this.onEnter);
    this.el.removeEventListener("pointerleave", this.onLeave);
    this.thumb.remove();
  }
}

export function installFloatingScrollbars(): void {
  const bars = new Map<string, FloatBar>();

  const sync = () => {
    const nodes: HTMLElement[] = [
      document.documentElement,
      ...document.querySelectorAll<HTMLElement>(".rtoc"),
    ];
    const keep = new Set<string>();
    for (const el of nodes) {
      for (const axis of ["y"] as Axis[]) {
        const key = `${axis}:${el === document.documentElement ? "doc" : elementKey(el)}`;
        keep.add(key);
        let bar = bars.get(key);
        if (!bar || !bar.thumb.isConnected) {
          bar?.destroy();
          bar = new FloatBar(el, axis);
          bars.set(key, bar);
        }
        bar.place(false);
      }
    }
    for (const [key, bar] of bars) {
      if (!keep.has(key)) {
        bar.destroy();
        bars.delete(key);
      }
    }
  };

  const mo = new MutationObserver(sync);
  const app = document.getElementById("app");
  if (app) mo.observe(app, { childList: true, subtree: true });
  window.addEventListener("resize", sync);
  sync();
}

let keySeq = 0;
const keys = new WeakMap<HTMLElement, string>();

function elementKey(el: HTMLElement): string {
  let key = keys.get(el);
  if (!key) {
    key = String(++keySeq);
    keys.set(el, key);
  }
  return key;
}
