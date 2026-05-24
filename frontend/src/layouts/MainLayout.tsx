
import { DrawerInterface } from "@/features/drawer/components/DrawerInterface";
import { Outlet } from "react-router-dom";

export const MainLayout = () => {
  return (
    <div className="relative h-screen flex overflow-hidden">
      {/* Sayfanın sol tarafında kalan ve sohbetler/hesap-ayarları kısmını barındırır */}
      <DrawerInterface />

      {/* Sayfa içeriği burada */}
      <main className="flex-1 flex flex-col w-full">
        <Outlet />
      </main>
    </div>
  );
};
