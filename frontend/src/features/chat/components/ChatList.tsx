import { cn } from "@/utils/cn";
import React from "react";
import { ChatMessage } from "./ChatMessage";
import type { Message } from "@/store/conversationStore";
import { useConversationStore } from "@/store/conversationStore";

type ChatListProps = {
  maxWidthClass: string;
  messages: Message[];
  endOfMessagesRef: React.RefObject<HTMLDivElement | null>;
};

const TypingIndicator = () => (
  <div className="flex justify-start mb-3">
    <div className="max-w-[85%] min-w-[40%]">
      <div className="rounded-2xl px-4 py-3 bg-card">
        <div className="flex items-center gap-1.5">
          <span className="text-sm text-gray-500 dark:text-gray-400 mr-1">AI yazıyor</span>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-2 h-2 rounded-full bg-blue-500"
              style={{
                animation: "typing-dot 1.4s infinite",
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  </div>
);

export const ChatList = ({
  maxWidthClass,
  messages,
  endOfMessagesRef,
}: ChatListProps) => {
  const isAiTyping = useConversationStore((state) => state.isAiTyping);

  return (
    <div className="flex-1 overflow-y-auto no-scrollbar w-full">
      <div className={cn("mx-auto w-full px-4 pt-4 pb-4", maxWidthClass)}>
        {messages.map((msg) => (
          <div key={msg.id} className="mb-3">
            <ChatMessage
              message={msg.content}
              isUser={msg.isUserMessage}
              ragSources={msg.ragSources}
              createdAt={msg.createdAt}
              predictionData={msg.predictionData}
            />
          </div>
        ))}
        {isAiTyping && <TypingIndicator />}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};
