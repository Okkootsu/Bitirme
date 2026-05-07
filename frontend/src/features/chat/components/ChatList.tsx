import { cn } from "@/utils/cn";
import React from "react";
import { ChatMessage } from "./ChatMessage";
import type { Message } from "@/store/conversationStore";

type ChatListProps = {
  maxWidthClass: string;
  messages: Message[];
  endOfMessagesRef: React.RefObject<HTMLDivElement | null>;
};

export const ChatList = ({
  maxWidthClass,
  messages,
  endOfMessagesRef,
}: ChatListProps) => {
  return (
    <div className="flex-1 overflow-y-auto no-scrollbar w-full">
      <div className={cn("mx-auto w-full px-4 pt-4 pb-4", maxWidthClass)}>
        {messages.map((msg) => (
          <div key={msg.id} className="mb-3">
            <ChatMessage message={msg.content} isUser={msg.isUserMessage} />
          </div>
        ))}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};
