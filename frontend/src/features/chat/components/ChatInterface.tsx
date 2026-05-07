import { useState } from "react";
import { useChat } from "../hooks/useChat";
import { cn } from "@/utils/cn";
import { ChatList } from "./ChatList";
import { ChatInput } from "./ChatInput";
import { Dialog } from "@/components/Dialog";
import { FormModal } from "@/features/auth/components/FormModal";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useConversations } from "@/hooks/useConversations";
import { SymptomForm } from "@/features/prediction/components/SymptomForm";
import { Button } from "@/components/Button";

export const ChatInterface = () => {
  const {
    setInput,
    isChatStarted,
    handleSendMessage,
    endOfMessagesRef,
  } = useChat();

  const { isDialogOpen, setIsDialogOpen } = useAuth();
  const { currentMessages } = useConversations();
  const [isSymptomFormOpen, setIsSymptomFormOpen] = useState(false);

  const maxWidthClass = "max-w-2xl";

  return (
    <div
      className={cn(
        "relative flex-1 flex flex-col bg-background overflow-hidden",
        isChatStarted ? "justify-between" : "items-center justify-center gap-8",
      )}
    >
      <h1
        className={cn(
          "z-10 h-16 text-4xl font-extrabold backdrop-blur-3xl flex justify-center text-gray-800 tracking-tight py-2 top-0 w-full bg-background/30 border-border/20 shrink-0",
          isChatStarted && "border-b-3",
        )}
      >
        Asistan.ai
      </h1>

      {/* Mesaj Alanı */}
      {isChatStarted && (
        <ChatList
          maxWidthClass={maxWidthClass}
          messages={currentMessages}
          endOfMessagesRef={endOfMessagesRef}
        />
      )}

      <div className={cn(
        "flex flex-col items-center gap-3 w-full shrink-0 px-4 pb-8 pt-5 bg-background/30 backdrop-blur-3xl border-border/20",
        isChatStarted && "border-t-3",
      )}>
        <div className={cn("w-full mx-auto flex flex-col gap-3", maxWidthClass)}>
          <Button
            variant="iconOutline"
            onClick={() => setIsSymptomFormOpen(true)}
            className="w-full text-sm py-2 rounded-xl border-blue-300 text-blue-600 hover:bg-blue-50"
          >
            Diyabet Risk Testi
          </Button>

          <ChatInput
            isChatStarted={isChatStarted}
            maxWidthClass={maxWidthClass}
            setInput={setInput}
            handleSendMessage={handleSendMessage}
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
