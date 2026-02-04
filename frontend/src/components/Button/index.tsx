import { cn } from "@/utils/cn";
import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "danger";
};

export const Button = ({
  className,
  variant = "primary",
  ...props
}: ButtonProps) => {
  const baseClass = "px-4 py-2 rounded-lg font-bold transition-colors";

  return (
    <button
      className={cn(
        baseClass,
        {
          "bg-blue-600 text-white hover:bg-blue-700": variant === "primary",
          "bg-red-500 text-white hover:bg-red-600": variant === "danger",
        },
        className,
      )}
      {...props}
    >
      {props.children}
    </button>
  );
};
