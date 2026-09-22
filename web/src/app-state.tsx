import { createContext, createEffect, createSignal, useContext, type ParentProps } from "solid-js";
import { loadSettings, saveSettings } from "./store";
import type { Catalog, Settings, Theme } from "./types";

type AppState = {
  catalog: Catalog;
  settings: () => Settings;
  markRev: () => number;
  bumpMarks: () => void;
  bumpFont: (delta: number) => void;
  cycleTheme: () => void;
  setTheme: (theme: Theme) => void;
  tocOpen: () => boolean;
  setTocOpen: (open: boolean) => void;
  toggleToc: () => void;
};

const AppContext = createContext<AppState>();

export function applySettings(settings: Settings): void {
  document.documentElement.dataset.theme = settings.theme;
  document.documentElement.style.setProperty("--font-size", `${settings.fontSize}rem`);
  const themeColor = settings.theme === "night" ? "#1b1814" : settings.theme === "sepia" ? "#ead7b2" : "#f3ead6";
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", themeColor);
}

export function themeLabel(theme: Theme): string {
  return theme === "night" ? "Đêm" : theme === "sepia" ? "Sẹpia" : "Giấy";
}

export function AppProvider(props: ParentProps<{ catalog: Catalog }>) {
  const [settings, setSettings] = createSignal(loadSettings());
  const [markRev, setMarkRev] = createSignal(0);
  const [tocOpen, setTocOpen] = createSignal(false);
  const write = (next: Settings) => {
    setSettings(next);
    saveSettings(next);
  };
  const api: AppState = {
    catalog: props.catalog,
    settings,
    markRev,
    bumpMarks: () => setMarkRev((n) => n + 1),
    bumpFont: (delta) => {
      const fontSize = Math.min(1.8, Math.max(0.9, +(settings().fontSize + delta).toFixed(2)));
      write({ ...settings(), fontSize });
    },
    setTheme: (theme) => write({ ...settings(), theme }),
    cycleTheme: () => {
      const order: Theme[] = ["paper", "sepia", "night"];
      const next = order[(order.indexOf(settings().theme) + 1) % order.length];
      write({ ...settings(), theme: next });
    },
    tocOpen,
    setTocOpen,
    toggleToc: () => setTocOpen((open) => !open),
  };
  createEffect(() => applySettings(settings()));
  createEffect(() => {
    document.body.classList.toggle("toc-lock", tocOpen());
  });
  return <AppContext.Provider value={api}>{props.children}</AppContext.Provider>;
}

export function useApp(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp ngoài AppProvider");
  return ctx;
}
