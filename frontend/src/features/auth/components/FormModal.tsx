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
    <div className="flex flex-1 flex-col py-6 px-6 md:py-12 md:px-14 gap-6 overflow-y-auto">
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
