import { Checkbox } from "@/components/Checkbox";
import { useAuth } from "../hooks/useAuth";
import { ButtonSection } from "./ButtonSection";
import { InputSection } from "./InputSection";
import { Card } from "@/components/Card";

export const FormModal = () => {
  const {
    showPassword,
    handleCheckboxClick,
    formVariant,
    handleChangeVariantClick,
    handleInputChange,
    handleSubmit,
    responseMessageCard,
    formValues,
  } = useAuth();

  return (
    <div className="flex flex-col py-12 px-14 gap-6">
      <InputSection
        formValues={formValues}
        showPassword={showPassword}
        formVariant={formVariant}
        onChange={handleInputChange}
      />

      <div className=" flex justify-between items-center py-1 px-1">
        <Checkbox onClick={handleCheckboxClick} label="Şifreyi Göster" />
      </div>

      <div hidden={responseMessageCard.isHidden}>
        <Card className={responseMessageCard.className}>
          {responseMessageCard.message}
        </Card>
      </div>

      <ButtonSection
        handleSubmit={handleSubmit}
        formVariant={formVariant}
        handleChangeVariantClick={handleChangeVariantClick}
      />
    </div>
  );
};
