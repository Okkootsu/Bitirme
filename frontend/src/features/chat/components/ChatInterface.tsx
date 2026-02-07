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

  const maxWidthClass = "w-xl";

  return (
    <div className="relative flex-1 flex flex-col items-center justify-center bg-background gap-8">
      <h1
        className={cn(
          "text-4xl font-extrabold backdrop-blur-3xl flex justify-center text-gray-800 tracking-tight py-2 sticky top-0 w-full bg-background/30 border-border/20",
          isChatStarted && "border-3",
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
