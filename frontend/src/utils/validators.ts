import { type AuthForm } from "@/features/auth/hooks/useAuth";

type validation = {
  isValid: boolean;
  errorMessage: string | null;
};

export const isValidMail = (email: string) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
};

export const validateRegisterForm = (form: AuthForm) => {
  const validation: validation = {
    isValid: true,
    errorMessage: null,
  };

  if (!form.username || !form.email || !form.password) {
    validation.isValid = false;
    validation.errorMessage = "Herhangi bir alan boş bırakılamaz";
    return validation;
  }

  if (form.password !== form.confirmPassword) {
    validation.isValid = false;
    validation.errorMessage = "Girilen şifreler uyuşmuyor";
    return validation;
  }

  if (!isValidMail(form.email)) {
    validation.isValid = false;
    validation.errorMessage = "Lütfen doğru bir E-posta adresi giriniz";
    return validation;
  }

  return validation;
};

export const validateLoginForm = (form: AuthForm) => {
  const validation: validation = {
    isValid: true,
    errorMessage: null,
  };

  if (!form.email || !form.password) {
    validation.isValid = false;
    validation.errorMessage = "Herhangi bir alan boş bırakılamaz";
    return validation;
  }

  if (!isValidMail(form.email)) {
    validation.isValid = false;
    validation.errorMessage = "Lütfen doğru bir E-posta adresi giriniz";
    return validation;
  }

  return validation; 
};
