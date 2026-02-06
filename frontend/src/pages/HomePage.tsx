import { PlaceholdersAndVanishInput } from "@/components/AceternityInput";
import { Card } from "@/components/Card";
import { useEffect, useRef, useState } from "react";

export const HomePage = () => {
  const [isMessageSectionHidden, setIsMessageSectionHidden] =
    useState<boolean>(true);
  const [messages, setMessages] = useState<Array<string>>([]);
  const [input, setInput] = useState<string>("");

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const maxWidht = "w-xl";

  const submitInput = () => {
    setMessages((prev) => [...prev, input]);
    setInput("");
    setMessages((prev) => [...prev, "Çıktı"]);

    if (isMessageSectionHidden) setIsMessageSectionHidden(false);
  };

  return (
    <div className="relative flex-1 flex flex-col items-center justify-center bg-[#FDFBF7] gap-8">
      <h1 className="text-4xl font-extrabold backdrop-blur-3xl flex justify-center text-gray-800 tracking-tight py-2 sticky top-0 w-full bg-[#E8DFCC]/30 border-[#E8DFCC]/20">
        Asistan.ai
      </h1>
      {/* mesaj alanı */}
      <div
        hidden={isMessageSectionHidden}
        className={maxWidht + " no-scrollbar min-h-126"}
      >
        {messages.map((msg, index) => {
          const isUserInput = index % 2 === 0 ? true : false;
          return (
            <div
              className={`flex ${isUserInput ? "justify-end" : "justify-start"}`}
            >
              <Card className="bg-[#F7F3E8]">{msg}</Card>
            </div>
          );
        })}
        <div ref={endOfMessagesRef} />
      </div>

      <div className="bottom-0 sticky w-full pb-8 pt-5 backdrop-blur-3xl bg-[#E8DFCC]/30 border-[#E8DFCC]/20">
        <PlaceholdersAndVanishInput
          className={maxWidht + " h-14"}
          placeholders={["Merak ettiklerinizi yazın"]}
          onChange={(e) => setInput(e.target.value)}
          onSubmit={() => submitInput()}
        />
      </div>
    </div>
  );
};
