"use client";

import { AnimatePresence, motion } from "framer-motion"; 
import { useEffect, useRef, useState } from "react";
import { cn } from "@/utils/cn";

export function PlaceholdersAndVanishInput({
  className,
  placeholders,
  onChange,
  onSubmit,
  onPlusClick,
}: {
  className?: string;
  placeholders: string[];
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  onPlusClick?: () => void;
}) {
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);

  const intervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startAnimation = () => {
    intervalRef.current = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholders.length);
    }, 3000);
  };
  const handleVisibilityChange = () => {
    if (document.visibilityState !== "visible" && intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    } else if (document.visibilityState === "visible") {
      startAnimation();
    }
  };

  useEffect(() => {
    startAnimation();
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [placeholders]);

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [value, setValue] = useState("");

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "3.5rem";
      const scrollHeight = inputRef.current.scrollHeight;
      const fontSize = parseFloat(window.getComputedStyle(inputRef.current).fontSize) || 16;
      const baseHeight = fontSize * 3.5; 
      if (scrollHeight > baseHeight) {
        inputRef.current.style.height = `${Math.min(scrollHeight, 156)}px`;
      }
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmitOriginal(e as any);
    }
  };

  const handleSubmitOriginal = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!value) return;
    onSubmit && onSubmit(e);
    setValue("");
  };

  return (
    <form
      className={cn(
        "w-full relative max-w-2xl mx-auto bg-white dark:bg-zinc-800 min-h-[56px] rounded-[28px] overflow-hidden shadow-[0px_2px_3px_-1px_rgba(0,0,0,0.1),_0px_1px_0px_0px_rgba(25,28,33,0.02),_0px_0px_0px_1px_rgba(25,28,33,0.08)] transition duration-200",
        value && "bg-gray-50",
        className,
      )}
      onSubmit={handleSubmitOriginal}
    >
      {onPlusClick && (
        <button
          type="button"
          onClick={onPlusClick}
          className="absolute left-2.5 bottom-2.5 z-[60] h-9 w-9 shrink-0 rounded-full bg-transparent hover:bg-gray-100 dark:hover:bg-zinc-700 transition-colors duration-200 flex items-center justify-center text-gray-500 dark:text-gray-400 cursor-pointer"
          title="Diyabet Risk Testi"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
        </button>
      )}

      <textarea
        onChange={(e) => {
          setValue(e.target.value);
          onChange && onChange(e);
        }}
        onKeyDown={handleKeyDown}
        ref={inputRef}
        value={value}
        rows={1}
        className={cn(
          "w-full block relative text-sm sm:text-base leading-[24px] z-50 border-none dark:text-white bg-transparent text-black focus:outline-none focus:ring-0 resize-none py-[16px] pr-14 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:bg-gray-300 dark:[&::-webkit-scrollbar-thumb]:bg-neutral-600 [&::-webkit-scrollbar-thumb]:rounded-full",
          onPlusClick ? "pl-14 sm:pl-16" : "pl-6 sm:pl-12",
        )}
      />

      <button
        disabled={!value}
        type="submit"
        className="absolute right-2.5 bottom-2.5 z-[60] h-9 w-9 shrink-0 rounded-full disabled:bg-gray-100 bg-black dark:bg-zinc-900 dark:disabled:bg-zinc-800 transition duration-200 flex items-center justify-center cursor-pointer"
      >
        <motion.svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gray-300 h-4 w-4"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <motion.path
            d="M5 12l14 0"
            initial={{
              strokeDasharray: "50%",
              strokeDashoffset: "50%",
            }}
            animate={{
              strokeDashoffset: value ? 0 : "50%",
            }}
            transition={{
              duration: 0.3,
              ease: "linear",
            }}
          />
          <path d="M13 18l6 -6" />
          <path d="M13 6l6 6" />
        </motion.svg>
      </button>

      <div className="absolute top-0 left-0 right-0 h-14 flex items-center rounded-[28px] pointer-events-none z-40">
        <AnimatePresence mode="wait">
          {!value && (
            <motion.p
              initial={{ y: 5, opacity: 0 }}
              key={`current-placeholder-${currentPlaceholder}`}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -15, opacity: 0 }}
              transition={{ duration: 0.3, ease: "linear" }}
              className={cn(
                "dark:text-zinc-500 text-sm sm:text-base font-normal text-neutral-500 text-left w-[calc(100%-4rem)] truncate",
                onPlusClick ? "pl-14 sm:pl-16" : "pl-6 sm:pl-12",
              )}
            >
              {placeholders[currentPlaceholder]}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </form>
  );
}
