import { cn } from "@/utils/cn";

type CheckboxProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
};

export const Checkbox = ({
  label,
  className,
  ...props
}: CheckboxProps) => {
  return (
    <>
      <label htmlFor={label}>{label}</label>
      <input
        id={label}
        type="checkbox"
        {...props}
        className={cn("w-3 h-3", className)}
      />
    </>
  );
};
