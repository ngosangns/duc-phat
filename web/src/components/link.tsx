import { A, type AnchorProps } from "@solidjs/router";

/** In-app link. The page does not jump to the top; each view restores its own scroll. */
export function AppLink(props: AnchorProps) {
  return <A {...props} noScroll />;
}
