import { Card } from "@/components/Card";
import { cn } from "@/utils/cn";

type ChatMessageProps = {
  message: string;
  isUser: boolean;
};

export const ChatMessage = ({ message, isUser }: ChatMessageProps) => {
  return (
    <div
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <Card
        className={cn(
          "max-w-[80%]",
          isUser ? "bg-blue-600 text-white border-none" : "bg-card",
        )}
      >
        {message}
      </Card>
    </div>
  );
};
