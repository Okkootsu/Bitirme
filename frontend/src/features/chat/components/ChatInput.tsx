import { PlaceholdersAndVanishInput } from "@/components/AceternityInput";

type ChatInputProps = {
  setInput: (value: string) => void;
  handleSendMessage: () => void;
  onPlusClick?: () => void;
};

export const ChatInput = ({
  setInput,
  handleSendMessage,
  onPlusClick,
}: ChatInputProps) => {
  return (
    <PlaceholdersAndVanishInput
      className="h-14 w-full"
      placeholders={["Merak ettiklerinizi yazın..."]}
      onChange={(e) => setInput(e.target.value)}
      onSubmit={handleSendMessage}
      onPlusClick={onPlusClick}
    />
  );
};
