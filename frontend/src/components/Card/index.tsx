import { cn } from "@/utils/cn";
import React from "react";

type CardProps = React.HTMLAttributes<HTMLDivElement>;

export const Card = ({ className, ...props }: CardProps) => {
  const baseClass = "bg-gray-200 flex rounded-lg p-3 w-fit break-words";

  return <div className={cn(baseClass, className)}>{props.children}</div>;
};
