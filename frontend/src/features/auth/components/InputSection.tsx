import { Input } from "@/components/Input";
import type { AuthForm } from "../hooks/useAuth";

type InputSectionProps = {
  formVariant: "login" | "register";
  showPassword: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  formValues: AuthForm;
};

export const InputSection = ({
  formVariant,
  showPassword,
  onChange,
  formValues,
}: InputSectionProps) => {
  return (
    <div className="flex flex-col gap-1">
      {formVariant === "register" && (
        <Input
          placeholder="Kullanıcı adı girin..."
          name="username"
          label="Kullanıcı Adı"
          value={formValues.username}
          onChange={onChange}
        />
      )}

      <Input
        placeholder="E-posta adresinizi girin..."
        name="email"
        label="E-posta"
        value={formValues.email}
        onChange={onChange}
        className="min-w-70"
      />

      <Input
        placeholder="Şifre girin..."
        name="password"
        label="Şifre"
        value={formValues.password}
        type={showPassword ? "text" : "password"}
        onChange={onChange}
      />

      {formVariant === "register" && (
        <Input
          placeholder="Tekrar şifre girin..."
          name="confirmPassword"
          label="Şifre Tekrar"
          value={formValues.confirmPassword}
          type={showPassword ? "text" : "password"}
          onChange={onChange}
        />
      )}
    </div>
  );
};
