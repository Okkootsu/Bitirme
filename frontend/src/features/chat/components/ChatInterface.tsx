import { useState } from "react";
import { useChat } from "../hooks/useChat";
import { cn } from "@/utils/cn";
import { ChatList } from "./ChatList";
import { ChatInput } from "./ChatInput";
import { Dialog } from "@/components/Dialog";
import { FormModal } from "@/features/auth/components/FormModal";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useConversationStore } from "@/store/conversationStore";
import { SymptomForm } from "@/features/prediction/components/SymptomForm";
import { Menu, Moon, Sun } from "lucide-react";
import { useDrawer } from "@/features/drawer/hooks/useDrawer";

export const ChatInterface = () => {
  const { setInput, isChatStarted, handleSendMessage, endOfMessagesRef } =
    useChat();

  const { isDialogOpen, setIsDialogOpen } = useAuth();
  const currentMessages = useConversationStore(
    (state) => state.currentMessages,
  );
  const darkMode = useConversationStore((state) => state.darkMode);
  const toggleDarkMode = useConversationStore((state) => state.toggleDarkMode);
  const [isSymptomFormOpen, setIsSymptomFormOpen] = useState(false);

  const maxWidthClass = "max-w-4xl";

  const { handleToggleButton } = useDrawer();

  return (
    <div
      className={cn(
        "relative flex-1 flex flex-col overflow-hidden bg-background",
        isChatStarted ? "justify-between" : "items-center justify-center gap-8",
      )}
    >
      <div
        className={cn(
          "z-20 h-16 backdrop-blur-3xl flex items-center justify-between px-6 top-0 w-full bg-background/30 border-border/20 shrink-0",
          isChatStarted && "border-b-3",
        )}
      >
        <button
          onClick={handleToggleButton}
          className="md:hidden p-2 -ml-2 rounded-lg hover:bg-card text-gray-600 dark:text-gray-300 transition-colors"
          title="Menüyü Aç"
        >
          <Menu size={24} />
        </button>

        <div className="hidden md:block w-8" />

        <h1 className="text-4xl font-extrabold text-gray-800 dark:text-gray-100 tracking-tight">
          Asistan.ai
        </h1>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-card transition-colors text-gray-600 dark:text-gray-300"
          title={darkMode ? "Açık tema" : "Koyu tema"}
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>

      {/* Mesaj Alanı */}

      {isChatStarted && (
        <ChatList
          maxWidthClass={maxWidthClass}
          messages={currentMessages}
          endOfMessagesRef={endOfMessagesRef}
        />
      )}

      <div
        className={cn(
          "flex flex-col items-center gap-3 w-full shrink-0 px-4 pb-8 pt-5 bg-background/30 backdrop-blur-3xl border-border/20",
          isChatStarted && "border-t-3",
        )}
      >
        <div
          className={cn("w-full mx-auto flex flex-col gap-3", maxWidthClass)}
        >
          <ChatInput
            setInput={setInput}
            handleSendMessage={handleSendMessage}
            onPlusClick={() => setIsSymptomFormOpen(true)}
          />
        </div>
      </div>

      {/* Giriş yapma ekranı */}
      <Dialog
        isLocked={true}
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(!isDialogOpen)}
      >
        <FormModal />
      </Dialog>

      {/* Diyabet Risk Testi Formu */}
      <SymptomForm
        isOpen={isSymptomFormOpen}
        onClose={() => setIsSymptomFormOpen(false)}
      />
    </div>
  );
};
