import { useState, useRef, useEffect } from "react";
import { PlaceholdersAndVanishInput } from "@/components/AceternityInput";
import { Activity, BellPlus } from "lucide-react";
import { cn } from "@/utils/cn";
import { Capacitor } from "@capacitor/core";

type ChatInputProps = {
  setInput: (value: string) => void;
  handleSendMessage: () => void;
  onOpenSymptomForm: () => void;
  onOpenReminderForm: () => void;
};

export const ChatInput = ({
  setInput,
  handleSendMessage,
  onOpenSymptomForm,
  onOpenReminderForm,
}: ChatInputProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const isNative = Capacitor.isNativePlatform();

  // Menü dışına tıklanınca kapatma mantığı
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative w-full" ref={menuRef}>
      {/* DROPDOWN MENU */}
      <div
        className={cn(
          "absolute bottom-16 mb-2 left-2 bg-white dark:bg-zinc-800 border border-border rounded-xl shadow-xl flex flex-col p-2 gap-1 w-64 origin-bottom-left transition-all duration-200 z-[70]",
          isMenuOpen
            ? "scale-100 opacity-100"
            : "scale-95 opacity-0 pointer-events-none",
        )}
      >
        <button
          onClick={() => {
            onOpenSymptomForm();
            setIsMenuOpen(false);
          }}
          className="cursor-pointer flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-700 text-left transition-colors"
        >
          <Activity size={20} className="text-green-500" />
          <span className="font-medium text-sm dark:text-gray-200">
            Diyabet Risk Testi
          </span>
        </button>

        {isNative && (
          <button
            onClick={() => {
              onOpenReminderForm();
              setIsMenuOpen(false);
            }}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-700 text-left transition-colors"
          >
            <BellPlus size={20} className="text-blue-500" />
            <span className="font-medium text-sm dark:text-gray-200">
              İnsülin Hatırlatıcı Kur
            </span>
          </button>
        )}
      </div>

      <PlaceholdersAndVanishInput
        className="w-full shadow-md"
        placeholders={["Merak ettiklerinizi yazın..."]}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSendMessage}
        onPlusClick={() => setIsMenuOpen(!isMenuOpen)}
      />
    </div>
  );
};
