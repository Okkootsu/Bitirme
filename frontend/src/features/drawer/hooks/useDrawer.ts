import { useDrawerStore } from "../store/drawerStore";

export const useDrawer = () => {
  const isOpen = useDrawerStore((state) => state.isOpen);
  const handleToggleButton = useDrawerStore((state) => state.handleToggleButton);

  return {
    isOpen,
    handleToggleButton,
  };
};
