import { Button } from "@/components/Button";
import { Dialog } from "@/components/Dialog";
import { SettingsModal } from "@/features/settings";
import { cn } from "@/utils/cn";
import { useState } from "react";

type UserCardProps = {
  isOpen: boolean;
};

export const UserCard = ({ isOpen }: UserCardProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);

  return (
    <div className="p-3 flex justify-center items-center h-15 bg-background border-border/40 border-t-3 ">
      <Button
        variant="primary"
        className={cn(
          "flex justify-start bg-[#f0f0f0] hover:bg-[#e1e3e6] cursor-pointer border border-border rounded-xl py-2 px-3 gap-3",
          !isOpen && "gap-0 px-0 py-1 justify-center",
        )}
        icon={
          <img
            src="blank-profile.webp"
            alt="Resim"
            className="w-12 h-12 rounded-3xl border border-gray-500"
          />
        }
        onClick={() => setIsDialogOpen(!isDialogOpen)}
      >
        <span
          className={cn(
            "whitespace-nowrap overflow-hidden",
            isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
          )}
        >
          John Doe
        </span>
      </Button>

      <Dialog
        title="Ayarlar"
        isLocked={false}
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(!isDialogOpen)}
      >
        <SettingsModal />
      </Dialog>
    </div>
  );
};
