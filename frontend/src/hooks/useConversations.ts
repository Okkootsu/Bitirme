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
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        alert(backendErrorMessage);
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
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        alert(backendErrorMessage);
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
      const messages = response.data.data.messages;
      setCurrentMessages(messages);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        alert(backendErrorMessage);
      } else {
        alert("Sunucuya bağlanılamadı");
      }
    }
  };

  const sendMessage = async (
    content: string,
    isUserMessage: boolean,
    providedSessionId?: number | null,
  ) => {
    try {
      let activeSessionId = providedSessionId || selectedConversation;

      if (
        !isChatStarted &&
        isUserMessage &&
        !activeSessionId &&
        currentMessages.length === 0
      ) {
        const newSessionId = await createConversation();

        if (!newSessionId) return;

        activeSessionId = newSessionId;
      }

      setIsChatStarted(true);

      const messageObj = {
        content: content,
        isUserMessage: isUserMessage,
        chatSessionId: activeSessionId,
      };

      const response = await api.post("/ChatMessage/send", messageObj);
      const message = response.data.data;

      addMessage(message);

      if (isUserMessage) {
        getAIResponse(activeSessionId);
      }
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        alert(backendErrorMessage);
      } else {
        alert("Sunucuya bağlanılamadı");
      }
    }
  };

  const getAIResponse = (sessionId: number | null) => {
    const message = "AI Cevabı";

    setTimeout(() => {
      sendMessage(message, false, sessionId);
    }, 500);
  };

  return {
    conversations,
    currentMessages,
    sendMessage,
    handleCreateConversationClick,
    setSelectedConversation,
    selectedConversation,
    isCreateConversationClicked,
  };
};
