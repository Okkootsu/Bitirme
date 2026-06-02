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
    deleteConversation,
    setSelectedConversation,
    selectedConversation,
    isCreateConversationClicked,
  } = useConversations();

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden animate-in fade-in duration-200"
          onClick={handleToggleButton}
        />
      )}

      <div
        className={cn(
          "flex flex-col transition-all h-screen duration-300 ease-in-out bg-drawer shrink-0 z-40",
          "absolute top-0 left-0 md:relative",
          isOpen
            ? "w-64 translate-x-0"
            : "w-64 -translate-x-full md:w-20 md:translate-x-0",
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
          onDelete={deleteConversation}
          selectedConversation={selectedConversation}
        />
        <UserCard isOpen={isOpen} />
      </div>
    </>
  );
};
