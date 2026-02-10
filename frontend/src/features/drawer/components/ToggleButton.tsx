import { Button } from "@/components/Button";
import { cn } from "@/utils/cn";
import { Menu } from "lucide-react";

type ToggleButtonProps = {
  isOpen: boolean;
  handleToggleButton: () => void;
};

export const ToggleButton = ({
  isOpen,
  handleToggleButton,
}: ToggleButtonProps) => {
  return (
    <div
      className={cn(
        "flex items-center p-2 bg-background border-border/40 border-b-3  h-16",
        isOpen ? "justify-end" : "justify-center",
      )}
    >
      <Button variant="icon" onClick={handleToggleButton}>
        <Menu />
      </Button>
    </div>
  );
};
