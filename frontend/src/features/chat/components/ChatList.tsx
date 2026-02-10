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
    <div
      className={cn(
        maxWidthClass,
        "absolute z-0 no-scrollbar w-full mt-0 flex flex-col pt-20 pb-34 items-center flex-1 h-screen overflow-y-auto",
      )}
    >
      {messages.map((msg, index) => (
        <div className={cn(maxWidthClass)}>
          <ChatMessage key={index} message={msg} isUser={index % 2 === 0} />
        </div>
      ))}
      <div ref={endOfMessagesRef} />
    </div>
  );
};
