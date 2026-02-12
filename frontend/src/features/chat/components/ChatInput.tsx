import { PlaceholdersAndVanishInput } from "@/components/AceternityInput";
import { cn } from "@/utils/cn";

type ChatInputProps = {
  isChatStarted: boolean;
  maxWidthClass: string;
  setInput: (value: string) => void;
  handleSendMessage: () => void;
};

export const ChatInput = ({
  isChatStarted,
  maxWidthClass,
  setInput,
  handleSendMessage,
}: ChatInputProps) => {
  return (
    <div
      className={cn(
        "bottom-0 z-10 w-full h-15 pb-8 pt-5 backdrop-blur-3xl bg-background/30 border-border/20",
        isChatStarted && "border-t-3",
      )}
    >
      <PlaceholdersAndVanishInput
        className={cn("h-14", maxWidthClass)}
        placeholders={["Merak ettiklerinizi yazın..."]}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSendMessage}
      />
    </div>
  );
};
