import { create } from "zustand";

type AuthStore = {
  isDialogOpen: boolean;
  setIsDialogOpen: (value: boolean) => void;
};

export const useAuthStore = create<AuthStore>((set) => ({
  isDialogOpen: true,
  setIsDialogOpen: (value) => set({ isDialogOpen: value }),
}));
