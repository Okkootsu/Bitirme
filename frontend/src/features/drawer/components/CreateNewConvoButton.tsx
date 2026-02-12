import { Button } from "@/components/Button";
import { cn } from "@/utils/cn";
import { Pencil } from "lucide-react";

type CreateNewConvoButtonProps = {
  isOpen: boolean;
};

export const CreateNewConvoButton = ({ isOpen }: CreateNewConvoButtonProps) => {
  return (
    <div className="px-2 py-6 transition-all duration-300 flex justify-center items-center border-border/40 border-b-3">
      <Button
        variant="iconOutline"
        className={cn(
          "bg-[#f5f5f5] hover:bg-[#dfdfdf]",
          !isOpen && "gap-0 px-0",
        )}
        icon={<Pencil />}
      >
        <span
          className={cn(
            "whitespace-nowrap overflow-hidden",
            isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
          )}
        >
          Yeni Sohbet Oluştur
        </span>
      </Button>
    </div>
  );
};
