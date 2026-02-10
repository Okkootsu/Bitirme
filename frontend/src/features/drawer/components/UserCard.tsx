import { Button } from "@/components/Button";
import { cn } from "@/utils/cn";

type UserCardProps = {
  isOpen: boolean;
};

export const UserCard = ({ isOpen }: UserCardProps) => {
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
      >
        <span
          className={cn(
            "whitespace-nowrap overflow-hidden",
            isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
          )}
        >
          Test
        </span>
      </Button>
    </div>
  );
};
