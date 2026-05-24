import { useConversations } from "@/hooks/useConversations";
import { useConversationStore } from "@/store/conversationStore";
import { useEffect, useRef, useState } from "react";

export const useChat = () => {
  const [input, setInput] = useState<string>("");

  const { currentMessages, sendMessage } = useConversations();
  const isChatStarted = useConversationStore((state) => state.isChatStarted);
  const setIsChatStarted = useConversationStore(
    (state) => state.setIsChatStarted,
  );

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // yeni mesajda en alta otomatik iner
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentMessages]);

  const handleSendMessage = () => {
    if (!input.trim()) return;

    sendMessage(input);

    if (!isChatStarted) setIsChatStarted(true);

    setInput("");
  };

  return {
    setInput,
    isChatStarted,
    handleSendMessage,
    endOfMessagesRef,
  };
};
