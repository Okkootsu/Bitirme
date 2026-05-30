import { cn } from "@/utils/cn";
import React from "react";

type ButtonVariant = "primary" | "icon" | "iconOutline";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  icon?: React.ReactNode;
};

export const Button = ({
  className,
  variant = "primary",
  icon,
  children,
  ...props
}: ButtonProps) => {
  const baseStyles =
    "flex justify-center items-center gap-4 px-4 py-2 rounded-3xl font-bold transition cursor-pointer";

  const variants = {
    primary:
      "w-full bg-button text-black border border-border hover:bg-button-hover dark:text-white ",
    icon: "bg-transparent hover:bg-[#f0efeb] dark:hover:bg-[#27272a] border border-transparent",
    iconOutline:
      "w-full bg-transparent hover:bg-[#f0efeb] border border-border",
  };

  return (
    <button className={cn(baseStyles, variants[variant], className)} {...props}>
      {icon && <span className="shrink-0">{icon}</span>}

      {children}
    </button>
  );
};
