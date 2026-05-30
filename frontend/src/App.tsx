import { BrowserRouter } from "react-router";
import { AppRouter } from "./routes";
import { Toaster } from "sonner";
import { useEffect } from "react";
import { useConversationStore } from "./store/conversationStore";

function App() {
  const darkMode = useConversationStore((state) => state.darkMode);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <BrowserRouter>
      <AppRouter />
      <Toaster
        position="top-center"
        richColors
        toastOptions={{ duration: 3000 }}
        theme={darkMode ? "dark" : "light"}
        style={{ zIndex: 9999 }}
      />
    </BrowserRouter>
  );
}

export default App;
