import { cn } from "@/utils/cn";
import { ToggleButton } from "./ToggleButton";
import { CreateNewConvoButton } from "./CreateNewConvoButton";
import { ConversationList } from "./ConversationList";
import { UserCard } from "./UserCard";
import { useDrawer } from "../hooks/useDrawer";
import { useConversations } from "@/hooks/useConversations";

export const DrawerInterface = () => {
  const { isOpen, handleToggleButton } = useDrawer();
  const {
    conversations,
    handleCreateConversationClick,
    setSelectedConversation,
    selectedConversation,
    isCreateConversationClicked,
  } = useConversations();

  return (
    <div
      className={cn(
        "flex flex-col transition-all h-screen duration-300 ease-in-out bg-drawer",
        isOpen ? "w-64" : "w-20",
      )}
    >
      <ToggleButton isOpen={isOpen} handleToggleButton={handleToggleButton} />

      <CreateNewConvoButton
        onClick={handleCreateConversationClick}
        isCreateConversationClicked={isCreateConversationClicked}
        isOpen={isOpen}
      />

      <ConversationList
        conversations={conversations}
        isOpen={isOpen}
        onClick={setSelectedConversation}
        selectedConversation={selectedConversation}
      />

      <UserCard isOpen={isOpen} />
    </div>
  );
};
