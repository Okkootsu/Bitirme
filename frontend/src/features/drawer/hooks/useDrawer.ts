import { useState } from "react";

export const useDrawer = () => {
  const [isOpen, setIsOpen] = useState<boolean>(true);

  const handleToggleButton = () => {
    setIsOpen((prev) => !prev);
  };

  return {
    isOpen,
    handleToggleButton,
  };
};
