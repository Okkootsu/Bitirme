import { create } from "zustand";

export type User = {
  id: number;
  email: string;
  username: string;
};

type UserStore = {
  user: User | null;
  setUser: (value: User | null) => void;
};

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (value) => set({ user: value }),
}));
