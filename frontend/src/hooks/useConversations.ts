import { useConversationStore } from "@/store/conversationStore";
import { useUserStore } from "@/store/userStore";
import api from "@/utils/axios";
import axios from "axios";
import { useEffect, useState } from "react";

export const useConversations = () => {
  const [isCreateConversationClicked, setIsCreateConversationClicked] =
    useState<boolean>(true);
  const {
    selectedConversation,
    setSelectedConversation,
    setConversations,
    addConversation,
    removeConversation,
    setCurrentMessages,
    addMessage,
    conversations,
    currentMessages,
    setIsChatStarted,
    isChatStarted,
  } = useConversationStore();

  const user = useUserStore((state) => state.user);

  useEffect(() => {
    if (user) {
      fetchConversationList();
    } else {
      setConversations([]);
      setSelectedConversation(null);
      setCurrentMessages([]);
    }
  }, [user]);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation);
      setIsChatStarted(true);
      setIsCreateConversationClicked(false);
    } else {
      setCurrentMessages([]);
      setIsChatStarted(false);
      setIsCreateConversationClicked(true);
    }
  }, [selectedConversation]);

  const fetchConversationList = async () => {
    try {
      const response = await api.get("/ChatSession/sessions");
      setConversations(response.data.data.chatSessions);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        alert(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        alert("Sunucuya bağlanılamadı");
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
        alert(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        alert("Sunucuya bağlanılamadı");
      }
      return null;
    }
  };

  const handleCreateConversationClick = () => {
    setSelectedConversation(null);
    setCurrentMessages([]);
    setIsChatStarted(false);
  };

  const fetchMessages = async (sessionId: number) => {
    try {
      const response = await api.get(`/ChatSession/${sessionId}`);
      setCurrentMessages(response.data.data.messages);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        alert(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        alert("Sunucuya bağlanılamadı");
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
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        alert(err.response.data.errorMessage || "Sohbet silinemedi.");
      } else {
        alert("Sunucuya bağlanılamadı");
      }
    }
  };

  // Kullanıcı mesajını gönderir; backend GPT yanıtını üretir ve döndürür.
  const sendMessage = async (content: string, providedSessionId?: number | null) => {
    try {
      let activeSessionId = providedSessionId ?? selectedConversation;

      if (!isChatStarted && !activeSessionId && currentMessages.length === 0) {
        const newSessionId = await createConversation();
        if (!newSessionId) return;
        activeSessionId = newSessionId;
      }

      setIsChatStarted(true);

      const response = await api.post("/ChatMessage/send", {
        content,
        isUserMessage: true,
        chatSessionId: activeSessionId,
      });

      const { userMessage, aiMessage } = response.data.data;
      addMessage(userMessage);
      addMessage(aiMessage);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        alert(err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.");
      } else {
        alert("Sunucuya bağlanılamadı");
      }
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
