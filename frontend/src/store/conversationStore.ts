import { create } from "zustand";

export type Conversation = {
  id: number;
  title: string;
};

export type RiskFactorCard = {
  name: string;
  value: string;
  status: "risk" | "protective" | "neutral";
  detail: string;
};

export type PredictionData = {
  riskProbability: number;
  riskCategory: string;
  confidenceLevel: string;
  contributingFactors: string[];
  shapValues?: Record<string, number>;
  // Hybrid model layer scores
  mlScore: number;
  symptomScore: number;
  clinicalScore: number;
  activeSymptoms: string[];
  riskFactorCards: RiskFactorCard[];
};

export type Message = {
  id: number;
  content: string;
  isUserMessage: boolean;
  ragSources?: string[];
  createdAt?: string;
  predictionData?: PredictionData;
};

type ConversationStore = {
  isChatStarted: boolean;
  selectedConversation: number | null;
  conversations: Conversation[];
  currentMessages: Message[];
  skipNextFetch: boolean;
  isAiTyping: boolean;
  darkMode: boolean;

  // setter'lar
  setIsChatStarted: (value: boolean) => void;
  setSelectedConversation: (value: number | null) => void;
  setConversations: (conversations: Conversation[]) => void;
  addConversation: (newConvo: Conversation) => void;
  removeConversation: (id: number) => void;
  setCurrentMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastMessageContent: (content: string) => void;
  updateConversationTitle: (id: number, title: string) => void;
  setSkipNextFetch: (value: boolean) => void;
  setIsAiTyping: (value: boolean) => void;
  toggleDarkMode: () => void;
};

export const useConversationStore = create<ConversationStore>((set) => ({
  isChatStarted: false,
  selectedConversation: null,
  conversations: [],
  currentMessages: [],
  skipNextFetch: false,
  isAiTyping: false,
  darkMode: localStorage.getItem("darkMode") === "true",

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
  updateLastMessageContent: (content) =>
    set((state) => {
      const msgs = [...state.currentMessages];
      if (msgs.length > 0) {
        msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content };
      }
      return { currentMessages: msgs };
    }),
  updateConversationTitle: (id, title) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === id ? { ...c, title } : c
      ),
    })),
  setSkipNextFetch: (value) => set({ skipNextFetch: value }),
  setIsAiTyping: (value) => set({ isAiTyping: value }),
  toggleDarkMode: () =>
    set((state) => {
      const newValue = !state.darkMode;
      localStorage.setItem("darkMode", String(newValue));
      document.documentElement.classList.toggle("dark", newValue);
      return { darkMode: newValue };
    }),
}));
