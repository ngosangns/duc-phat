import { capturePlace, savePlace, type Place } from "./store";

type Session = {
  route: string;
  title: string;
  root: HTMLElement;
  /** False until the paragraph restore has run, so a half-opened page cannot overwrite the saved place. */
  ready: boolean;
};

let session: Session | null = null;
let pending: Place | null = null;

export function setSession(next: Session | null): void {
  session = next;
}

export function flushSession(): void {
  if (!session?.ready || !session.root.isConnected) return;
  savePlace(capturePlace(session.route, session.title, session.root));
}

export function armPlace(place: Place): void {
  pending = place;
}

export function takePlace(route: string): Place | undefined {
  const place = pending?.route === route ? pending : undefined;
  pending = null;
  return place;
}
