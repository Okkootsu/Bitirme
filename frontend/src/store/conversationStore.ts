import { create } from "zustand";

export type Conversation = {
  id: number;
  title: string;
};

export type Message = {
  id: number;
  content: string;
  isUserMessage: boolean;
};

type ConversationStore = {
  isChatStarted: boolean;
  selectedConversation: number | null;
  conversations: Conversation[];
  currentMessages: Message[];

  // setter'lar
  setIsChatStarted: (value: boolean) => void;
  setSelectedConversation: (value: number | null) => void;
  setConversations: (conversations: Conversation[]) => void;
  addConversation: (newConvo: Conversation) => void;
  removeConversation: (id: number) => void;
  setCurrentMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
};

export const useConversationStore = create<ConversationStore>((set) => ({
  isChatStarted: false,
  selectedConversation: null,
  conversations: [],
  currentMessages: [],

  setIsChatStarted: (value) => set({ isChatStarted: value }),
  setSelectedConversation: (value) => set({ selectedConversation: value }),
  setConversations: (conversations) => set({ conversations: conversations }),
  addConversation: (newConvo) =>
    set((state) => ({
      conversations: [newConvo, ...state.conversations],
    })),
  removeConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
    })),
  setCurrentMessages: (messages) => set({ currentMessages: messages }),
  addMessage: (message) =>
    set((state) => ({
      currentMessages: [...state.currentMessages, message],
    })),
}));
