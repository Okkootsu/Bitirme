import { Button } from "@/components/Button";
import { cn } from "@/utils/cn";

type ButtonSectionProps = {
  formVariant: "login" | "register";
  handleChangeVariantClick: () => void;
  handleSubmit: () => Promise<void>;
};

export const ButtonSection = ({
  formVariant,
  handleChangeVariantClick,
  handleSubmit,
}: ButtonSectionProps) => {
  return (
    <div className="flex flex-col gap-3">
      <Button
        onClick={handleSubmit}
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
  );
};
