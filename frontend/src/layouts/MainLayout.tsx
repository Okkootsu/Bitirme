import { Outlet, Link } from "react-router-dom";

export const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="p-5 border-b h-12 border-gray-300 flex gap-5 justify-center items-center bg-gray-50">
        {/* Sayfanın yeniden yüklenmesini engellemek için Link kullanılır */}
        <Link
          to="/"
          className="text-gray-800 font-bold no-underline hover:text-blue-600"
        >
          Ana Sayfa
        </Link>
        <Link
          to="/about"
          className="text-gray-800 font-bold no-underline hover:text-blue-600"
        >
          Hakkında
        </Link>
      </nav>

      {/* Sayfa içeriği burada */}
      <main className="flex-1 flex flex-col w-full">
        <Outlet />
      </main>

      <footer className="p-4 bg-gray-200 text-center">Footer</footer>
    </div>
  );
};
