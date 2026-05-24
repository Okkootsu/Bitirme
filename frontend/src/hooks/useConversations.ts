import { useConversationStore } from "@/store/conversationStore";
import { useUserStore } from "@/store/userStore";
import api from "@/utils/axios";
import axios from "axios";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

export const useConversations = () => {
  const [isCreateConversationClicked, setIsCreateConversationClicked] =
    useState<boolean>(true);
  const isSendingRef = useRef(false);
  const {
    selectedConversation,
    setSelectedConversation,
    setConversations,
    addConversation,
    removeConversation,
    setCurrentMessages,
    addMessage,
    updateLastMessageContent,
    updateConversationTitle,
    skipNextFetch,
    setSkipNextFetch,
    conversations,
    currentMessages,
    setIsChatStarted,
    isChatStarted,
    setIsAiTyping,
  } = useConversationStore();

  const user = useUserStore((state) => state.user);

  useEffect(() => {
    let cancelled = false;

    if (user) {
      fetchConversationList(cancelled);
    } else {
      setConversations([]);
      setSelectedConversation(null);
      setCurrentMessages([]);
    }

    return () => { cancelled = true; };
  }, [user]);

  useEffect(() => {
    let cancelled = false;

    if (selectedConversation) {
      if (skipNextFetch) {
        setSkipNextFetch(false);
      } else {
        fetchMessages(selectedConversation, cancelled);
      }
      setIsChatStarted(true);
      setIsCreateConversationClicked(false);
    } else {
      setCurrentMessages([]);
      setIsChatStarted(false);
      setIsCreateConversationClicked(true);
    }

    return () => { cancelled = true; };
  }, [selectedConversation]);

  const fetchConversationList = async (cancelled = false) => {
    try {
      const response = await api.get("/ChatSession/sessions");
      if (!cancelled) {
        setConversations(response.data.data.chatSessions);
      }
    } catch (err) {
      if (cancelled) return;
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        toast.error("Sunucuya bağlanılamadı");
      }
    }
  };

  const createConversation = async () => {
    try {
      const response = await api.post("/ChatSession/create");
      const newConvo = response.data.data;

      addConversation(newConvo);
      setSelectedConversation(newConvo.id);

      return newConvo.id;
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        toast.error("Sunucuya bağlanılamadı");
      }
      return null;
    }
  };

  const handleCreateConversationClick = () => {
    setSelectedConversation(null);
    setCurrentMessages([]);
    setIsChatStarted(false);
  };

  const fetchMessages = async (sessionId: number, cancelled = false) => {
    try {
      const response = await api.get(`/ChatSession/${sessionId}`);
      if (!cancelled) {
        setCurrentMessages(response.data.data.messages);
      }
    } catch (err) {
      if (cancelled) return;
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        toast.error("Sunucuya bağlanılamadı");
      }
    }
  };

  const deleteConversation = async (sessionId: number) => {
    try {
      await api.delete(`/ChatSession/${sessionId}`);
      removeConversation(sessionId);

      if (selectedConversation === sessionId) {
        setSelectedConversation(null);
        setCurrentMessages([]);
        setIsChatStarted(false);
      }
      toast.success("Sohbet silindi");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Sohbet silinemedi.");
      } else {
        toast.error("Sunucuya bağlanılamadı");
      }
    }
  };

  // Kullanıcı mesajını gönderir; SSE streaming ile AI yanıtını parça parça alır.
  const sendMessage = async (content: string, providedSessionId?: number | null) => {
    if (isSendingRef.current) return;
    isSendingRef.current = true;

    try {
      let activeSessionId = providedSessionId ?? selectedConversation;

      if (!isChatStarted && !activeSessionId && currentMessages.length === 0) {
        setSkipNextFetch(true);
        const newSessionId = await createConversation();
        if (!newSessionId) return;
        activeSessionId = newSessionId;
      }

      setIsChatStarted(true);
      setIsAiTyping(true);

      const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8080/api";
      const token = localStorage.getItem("token");

      const response = await fetch(`${baseURL}/ChatMessage/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          content,
          isUserMessage: true,
          chatSessionId: activeSessionId,
        }),
      });

      if (!response.ok) {
        toast.error("Mesaj gönderilemedi.");
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        toast.error("Streaming desteklenmiyor.");
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let streamingContent = "";
      let aiPlaceholderAdded = false;

      const processLine = (line: string) => {
        if (!line.startsWith("data: ")) return;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) return;

        try {
          const event = JSON.parse(jsonStr);

          if (event.type === "user_message") {
            addMessage(event.data);
          } else if (event.type === "chunk") {
            if (!aiPlaceholderAdded) {
              setIsAiTyping(false);
              addMessage({ id: -1, content: "", isUserMessage: false });
              aiPlaceholderAdded = true;
            }
            streamingContent += event.text;
            updateLastMessageContent(streamingContent);
          } else if (event.type === "done") {
            setIsAiTyping(false);
            const finalMsg = {
              ...event.aiMessage,
              ragSources: event.ragSources ?? [],
            };
            useConversationStore.setState((state) => {
              const msgs = [...state.currentMessages];
              msgs[msgs.length - 1] = finalMsg;
              return { currentMessages: msgs };
            });

            if (event.generatedTitle && activeSessionId) {
              updateConversationTitle(activeSessionId, event.generatedTitle);
            }
          } else if (event.type === "error") {
            toast.error(event.message || "Bir hata oluştu.");
          }
        } catch {
          // JSON parse hatası — atla
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          processLine(line);
        }
      }

      // Stream bitti — buffer'da kalan son event'i işle
      buffer += decoder.decode();
      if (buffer.trim()) {
        processLine(buffer.trim());
      }
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        toast.error("Sunucuya bağlanılamadı");
      }
    } finally {
      isSendingRef.current = false;
      setIsAiTyping(false);
    }
  };

  return {
    conversations,
    currentMessages,
    sendMessage,
    createConversation,
    deleteConversation,
    handleCreateConversationClick,
    setSelectedConversation,
    selectedConversation,
    isCreateConversationClicked,
  };
};
