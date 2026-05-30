import { Button } from "@/components/Button";
import type { Conversation } from "@/store/conversationStore";
import { cn } from "@/utils/cn";
import { Trash2 } from "lucide-react";

type ConversationListProps = {
  isOpen: boolean;
  conversations: Conversation[];
  onClick: (id: number) => void;
  onDelete: (id: number) => void;
  selectedConversation: number | null;
};

export const ConversationList = ({
  isOpen,
  conversations,
  onClick,
  onDelete,
  selectedConversation,
}: ConversationListProps) => {
  return (
    <div className="transition-all duration-300 flex-1 h-1 overflow-y-auto no-scrollbar p-5 gap-3 flex flex-col items-center ">
      {conversations.map((chat) => (
        <div
          key={chat.id}
          className={cn(
            "group relative w-full",
            isOpen ? "opacity-100" : "w-0 opacity-0",
          )}
        >
          <Button
            onClick={() => onClick(chat.id)}
            className={cn(
              "pr-10",
              selectedConversation === chat.id &&
                "bg-gray-900 hover:bg-gray-950 text-white dark:bg-zinc-950 dark:hover:bg-black",
            )}
          >
            <span
              className={cn(
                "whitespace-nowrap overflow-hidden text-ellipsis",
                isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
              )}
            >
              {chat.title}
            </span>
          </Button>
          {isOpen && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(chat.id);
              }}
              className={cn(
                "absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer",
                selectedConversation === chat.id
                  ? "hover:bg-gray-700 text-gray-300"
                  : "hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400",
              )}
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      ))}
    </div>
  );
};
