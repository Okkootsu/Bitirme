import { useChat } from "../hooks/useChat";
import { cn } from "@/utils/cn";
import { ChatList } from "./ChatList";
import { ChatInput } from "./ChatInput";

export const ChatInterface = () => {
  const {
    messages,
    input,
    setInput,
    isChatStarted,
    handleSendMessage,
    endOfMessagesRef,
  } = useChat();

  const maxWidthClass = "w-2xl";

  return (
    <div
      className={cn(
        "relative flex-1 flex flex-col bg-background ",
        isChatStarted ? "justify-between" : "items-center justify-center gap-8",
      )}
    >
      <h1
        className={cn(
          "z-10 h-16 text-4xl font-extrabold backdrop-blur-3xl flex justify-center text-gray-800 tracking-tight py-2 top-0 w-full bg-background/30 border-border/20",
          isChatStarted && "border-b-3",
        )}
      >
        Asistan.ai
      </h1>

      {/* Mesaj Alanı */}
      {isChatStarted && (
        <ChatList
          maxWidthClass={maxWidthClass}
          messages={messages}
          endOfMessagesRef={endOfMessagesRef}
        />
      )}

      <ChatInput
        isChatStarted={isChatStarted}
        maxWidthClass={maxWidthClass}
        setInput={setInput}
        handleSendMessage={handleSendMessage}
      />
    </div>
  );
};
