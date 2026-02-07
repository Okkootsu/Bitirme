import { cn } from "@/utils/cn";
import React from "react";
import { ChatMessage } from "./ChatMessage";

type ChatListProps = {
  maxWidthClass: string;
  messages: string[];
  endOfMessagesRef: React.RefObject<HTMLDivElement | null>;
};

export const ChatList = ({
  maxWidthClass,
  messages,
  endOfMessagesRef,
}: ChatListProps) => {
  return (
    <div className={cn(maxWidthClass, "no-scrollbar min-h-126")}>
      {messages.map((msg, index) => (
        <ChatMessage key={index} message={msg} isUser={index % 2 === 0} />
      ))}
      <div ref={endOfMessagesRef} />
    </div>
  );
};
