import { useEffect, useRef, useState } from "react";

export const useChat = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>("");
  const [isChatStarted, setIsChatStarted] = useState<boolean>(false);

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // yeni mesajda en alta otomatik iner
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, input]);

    if (!isChatStarted) setIsChatStarted(true);

    setTimeout(() => {
      setMessages((prev) => [...prev, "AI cevabı"]);
    }, 500);

    setInput("");
  };

  return {
    messages,
    input,
    setInput,
    isChatStarted,
    handleSendMessage,
    endOfMessagesRef,
  };
};
