import { useState } from "react";

export const useAuth = () => {
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [formVariant, setFormVariant] = useState<"login" | "register">("login");

  const handleCheckboxClick = () => {
    setShowPassword(!showPassword);
  };

  const handleChangeVariantClick = () => {
    switch (formVariant) {
      case "login":
        setFormVariant("register");
        break;
      case "register":
        setFormVariant("login");
        break;
      default:
        setFormVariant("login");
    }
  };

  return {
    showPassword,
    handleCheckboxClick,
    formVariant,
    handleChangeVariantClick,
  };
};
