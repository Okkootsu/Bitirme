import api from "@/utils/axios";
import { validateLoginForm, validateRegisterForm } from "@/utils/validators";
import axios from "axios";
import { useState } from "react";
import { useAuthStore } from "../store/authStore";

export type AuthForm = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
};

type ResponseMessageCard = {
  isHidden: boolean;
  className: string;
  message: string;
};

export const useAuth = () => {
  const INITIAL_FORM_STATE: AuthForm = {
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  };

  const INITIAL_CARD_STATE = {
    isHidden: true,
    className: "",
    message: "",
  };

  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [formVariant, setFormVariant] = useState<"login" | "register">("login");
  const [formValues, setFormValues] = useState<AuthForm>(INITIAL_FORM_STATE);
  const [responseMessageCard, setResponseMessageCard] =
    useState<ResponseMessageCard>(INITIAL_CARD_STATE);

  const { isDialogOpen, setIsDialogOpen } = useAuthStore();

  const handleCheckboxClick = () => {
    setShowPassword(!showPassword);
  };

  const handleChangeVariantClick = () => {
    setResponseMessageCard(INITIAL_CARD_STATE);
    setFormValues(INITIAL_FORM_STATE);

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

  const showResponseMessage = (isSuccess: boolean, message: string) => {
    setResponseMessageCard({
      isHidden: false,
      className: isSuccess
        ? "w-full max-w-full bg-green-300"
        : "w-full max-w-full bg-red-300",
      message: message,
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormValues({ ...formValues, [e.target.name]: e.target.value });
  };

  const handleRegister = async () => {
    const validation = validateRegisterForm(formValues);

    if (!validation.isValid) {
      alert(validation.errorMessage);
      return;
    }

    try {
      const response = await api.post("/User/register", formValues);
      setFormValues(INITIAL_FORM_STATE);

      showResponseMessage(true, "Başarıyla kayıt olundu. Giriş yapabilirsiniz");
    } catch (err) {
      setFormValues(INITIAL_FORM_STATE);

      if (axios.isAxiosError(err) && err.response) {
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        showResponseMessage(false, backendErrorMessage);
      } else {
        showResponseMessage(false, "Sunucuya bağlanılamadı");
      }
    }
  };

  const handleLogout = async () => {
    localStorage.removeItem("token");

    window.location.href = "/";
  };

  const handleLogin = async () => {
    const validation = validateLoginForm(formValues);

    if (!validation.isValid) {
      alert(validation.errorMessage);
      return;
    }

    try {
      const response = await api.post("/User/login", formValues);

      setFormValues(INITIAL_FORM_STATE);
      setResponseMessageCard(INITIAL_CARD_STATE);

      const token = response.data.data.token;
      localStorage.setItem("token", token);
      setIsDialogOpen(false);
    } catch (err) {
      setFormValues(INITIAL_FORM_STATE);

      if (axios.isAxiosError(err) && err.response) {
        const backendErrorMessage =
          err.response.data.errorMessage || "Bilinmeyen bir hata oluştu.";

        showResponseMessage(false, backendErrorMessage);
      } else {
        showResponseMessage(false, "Sunucuya bağlanılamadı");
      }
    }
  };

  const handleSubmit = async () => {
    if (formVariant === "login") {
      await handleLogin();
    } else {
      await handleRegister();
    }
  };

  return {
    showPassword,
    handleCheckboxClick,
    formVariant,
    handleChangeVariantClick,
    handleInputChange,
    handleSubmit,
    responseMessageCard,
    formValues,
    isDialogOpen,
    setIsDialogOpen,
    handleLogout,
  };
};
