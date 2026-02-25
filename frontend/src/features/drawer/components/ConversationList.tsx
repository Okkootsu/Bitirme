import { Button } from "@/components/Button";
import type { Conversation } from "@/store/conversationStore";
import { cn } from "@/utils/cn";

type ConversationListProps = {
  isOpen: boolean;
  conversations: Conversation[];
  onClick: (id: number) => void;
  selectedConversation: number | null;
};

export const ConversationList = ({
  isOpen,
  conversations,
  onClick,
  selectedConversation,
}: ConversationListProps) => {
  return (
    <div className="transition-all duration-300 flex-1 h-1 overflow-y-auto no-scrollbar p-5 gap-3 flex flex-col items-center ">
      {conversations.map((chat) => (
        <Button
          key={chat.id}
          onClick={() => onClick(chat.id)}
          className={cn(
            isOpen ? "opacity-100" : "w-0 opacity-0",
            selectedConversation === chat.id &&
              "bg-gray-900 hover:bg-gray-950 text-white",
          )}
        >
          <span
            className={cn(
              "whitespace-nowrap overflow-hidden",
              isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
            )}
          >
            {chat.title}
          </span>
        </Button>
      ))}
    </div>
  );
};
