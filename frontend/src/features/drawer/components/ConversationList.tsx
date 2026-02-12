import { Button } from "@/components/Button";
import { cn } from "@/utils/cn";

type ConversationListProps = {
  isOpen: boolean;
};

export const ConversationList = ({ isOpen }: ConversationListProps) => {
  return (
    <div className="transition-all duration-300 flex-1 h-1 overflow-y-auto no-scrollbar p-5 gap-3 flex flex-col items-center ">
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map((chat) => (
        <Button className={cn(isOpen ? "opacity-100" : "w-0 opacity-0")}>
          <span
            className={cn(
              "whitespace-nowrap overflow-hidden",
              isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
            )}
          >
            Sohbet {chat}
          </span>
        </Button>
      ))}
    </div>
  );
};
