import { cn } from "@/utils/cn";
import { createPortal } from "react-dom";
import { Button } from "../Button";
import { X } from "lucide-react";
import { useRef } from "react";

type DialogProps = React.HTMLAttributes<HTMLDivElement> & {
  isOpen: boolean;
  isLocked?: boolean; // kapanabilir olup olmadığını kontrol eder (true => kapatılamaz)
  title?: string;
  onClose: () => void;
};

export const Dialog = ({
  isOpen,
  isLocked = false,
  title,
  onClose,
  children,
}: DialogProps) => {
  const overlayRef = useRef<HTMLDivElement>(null);

  if (!isOpen) return null;

  // const handleOverlayClick = () => {
  //   if (!isLocked) {
  //     onClose();
  //   }
  // };

  // en önde ve doğru yerde gözüksün diye portal kullandık, bu sayede diğer div'lere sıkışmayacak
  return createPortal(
    // Tüm ekranı kaplayacak olan ana div, "boş gözükecek" kısımlar da dahil
    <div
      ref={overlayRef}
      className={cn(
        `fixed inset-0 z-50 flex items-center justify-center transition-opacity
         animate-in fade-in duration-200`,
        !isLocked ? "bg-black/10" : "bg-black/30 backdrop-blur-2xl",
      )}
      // onClick={handleOverlayClick}
    >
      {/* Asıl dialog'u oluşturan kısım */}
      <div className={cn("bg-card shadow-xl rounded-xl ")}>
        {!isLocked && (
          <div className="relative min-h-14 flex justify-between gap-2 py-1 px-2 border-b-2 border-card-hover ">
            <h2 className="font-bold text-2xl flex flex-1 justify-center items-center ">
              {title}
            </h2>

            <Button
              onClick={onClose}
              variant="iconOutline"
              className="absolute right-1 top-1 w-12 h-12 border-0 hover:bg-card-hover "
            >
              <X />
            </Button>
          </div>
        )}

        <div className="flex-1">{children}</div>
      </div>
    </div>,
    document.body,
  );
};
