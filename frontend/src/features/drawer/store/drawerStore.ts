import { create } from "zustand";

type DrawerStore = {
  isOpen: boolean;
  handleToggleButton: () => void;
};

export const useDrawerStore = create<DrawerStore>((set) => ({
  isOpen: false,
  handleToggleButton: () => set((state) => ({ isOpen: !state.isOpen })),
}));
