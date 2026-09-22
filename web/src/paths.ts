/** Absolute URL under the Vite base for a file in `public/data`. */
export function dataUrl(path: string): string {
  const base = import.meta.env.BASE_URL;
  const prefix = base.endsWith("/") ? base : `${base}/`;
  return `${prefix}data/${path.replace(/^\/+/, "")}`;
}

/** Catalog routes are stored without a leading slash (`new/dn/…`). */
export function pathOf(route: string): string {
  const clean = route.replace(/^\/+/, "");
  return clean ? `/${clean}` : "/";
}

/** `#/new/dn/…` from the previous reader, or null when the hash is not a route. */
export function legacyPath(): string | null {
  const hash = window.location.hash;
  if (!hash || hash === "#") return null;
  let raw: string;
  try {
    raw = decodeURIComponent(hash.slice(1));
  } catch {
    raw = hash.slice(1);
  }
  const path = (raw.startsWith("/") ? raw : `/${raw}`).split(/[?#]/, 1)[0];
  if (!path || path === "/") return null;
  return path;
}

/**
 * Old links used the hash. Rewrite them onto the history path before the
 * router reads the location, so a refresh still opens the sutta.
 */
export function prepareLocation(): void {
  const path = legacyPath();
  if (!path) return;
  window.history.replaceState(window.history.state, "", path + window.location.search);
}
