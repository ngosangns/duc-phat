import { useApp } from "../app-state";
import { AppLink } from "../components/link";
import { TopBar } from "../components/top-bar";

export function Missing() {
  const app = useApp();
  return (
    <>
      <TopBar brand={app.catalog.title} sub="" />
      <p class="err">
        Không tìm thấy mục này. <AppLink href="/">Về kệ sách</AppLink>.
      </p>
    </>
  );
}
