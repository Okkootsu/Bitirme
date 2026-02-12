import { cn } from "@/utils/cn";
import { ToggleButton } from "./ToggleButton";
import { CreateNewConvoButton } from "./CreateNewConvoButton";
import { ConversationList } from "./ConversationList";
import { UserCard } from "./UserCard";
import { useDrawer } from "../hooks/useDrawer";

export const DrawerInterface = () => {
  const { isOpen, handleToggleButton } = useDrawer();

  return (
    <div
      className={cn(
        "flex flex-col transition-all h-screen duration-300 ease-in-out bg-drawer",
        isOpen ? "w-64" : "w-20",
      )}
    >
      <ToggleButton isOpen={isOpen} handleToggleButton={handleToggleButton} />

      <CreateNewConvoButton isOpen={isOpen} />

      <ConversationList isOpen={isOpen} />

      <UserCard isOpen={isOpen} />
    </div>
  );
};
