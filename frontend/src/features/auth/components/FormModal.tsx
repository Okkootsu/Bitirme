import { Button } from "@/components/Button";
import { Checkbox } from "@/components/Checkbox";
import { Input } from "@/components/Input";
import { useAuth } from "../hooks/useAuth";
import { cn } from "@/utils/cn";

export const FormModal = () => {
  const {
    showPassword,
    handleCheckboxClick,
    formVariant,
    handleChangeVariantClick,
  } = useAuth();

  return (
    <div className="flex flex-col py-12 px-14 gap-6">
      <div className="flex flex-col gap-1">
        <Input
          placeholder="Kullanıcı adı girin..."
          label="Kullanıcı Adı"
          className="w-70"
        />

        {formVariant === "register" && (
          <Input placeholder="E-posta adresinizi girin..." label="E-posta" />
        )}

        <Input
          placeholder="Şifre girin..."
          label="Şifre"
          type={showPassword ? "text" : "password"}
        />

        {formVariant === "register" && (
          <Input
            placeholder="Tekrar şifre girin..."
            label="Şifre Tekrar"
            type={showPassword ? "text" : "password"}
          />
        )}
      </div>

      <div className=" flex justify-between items-center py-1 px-1">
        <Checkbox onClick={handleCheckboxClick} label="Şifreyi Göster" />
      </div>

      <div className="flex flex-col gap-3">
        <Button
          className={cn(
            formVariant === "login"
              ? "rounded-lg bg-green-400 hover:bg-green-500 active:bg-green-600"
              : "rounded-lg bg-blue-400 hover:bg-blue-500 active:bg-blue-600",
          )}
        >
          {formVariant === "login" ? "Giriş Yap" : "Kayıt Ol"}
        </Button>
        <Button
          onClick={handleChangeVariantClick}
          className="rounded-lg bg-white hover:bg-gray-100 active:bg-gray-200"
        >
          {formVariant === "login" ? "Kayıt Ol" : "Giriş Ekranına Dön"}
        </Button>
      </div>
    </div>
  );
};
