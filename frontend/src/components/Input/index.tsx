import { cn } from "@/utils/cn";
import type React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
};

export const Input = ({
  label,
  type = "text",
  className,
  ...props
}: InputProps) => {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={label} className="font-bold text-sm">
        {label}
      </label>
      <input
        id={label}
        type={type}
        className={cn(
          `bg-white rounded py-1 px-3 border-2 focus:bg-gray-100 border-border dark:focus:outline-none  
          dark:bg-zinc-700 dark:focus:bg-zinc-800 dark:focus:ring-2 dark:focus:ring-gray-800`,
          className,
        )}
        {...props}
      />
    </div>
  );
};
