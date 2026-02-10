import { useState } from "react";
import { Button } from "../Button";

import { Menu, Pencil } from "lucide-react";
import { cn } from "@/utils/cn";

export const Drawer = () => {
  const [isOpen, setIsOpen] = useState<boolean>(true);

  const handleToggleButton = () => {
    setIsOpen((prev) => !prev);
  };

  return (
    <div
      className={cn(
        "flex flex-col transition-all h-screen duration-300 ease-in-out bg-drawer",
        isOpen ? "w-64" : "w-20",
      )}
    >
      <div
        className={cn(
          "flex items-center p-2 bg-background border-border/40 border-b-3  h-16",
          isOpen ? "justify-end" : "justify-center",
        )}
      >
        <Button variant="icon" onClick={handleToggleButton}>
          <Menu />
        </Button>
      </div>

      <div className="px-2 py-6 transition-all duration-300 flex justify-center items-center border-border/40 border-b-3">
        <Button
          variant="iconOutline"
          className={cn(
            "bg-[#f5f5f5] hover:bg-[#dfdfdf]",
            !isOpen && "gap-0 px-0",
          )}
          icon={<Pencil />}
        >
          <span
            className={cn(
              "whitespace-nowrap overflow-hidden",
              isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
            )}
          >
            Yeni Sohbet Oluştur
          </span>
        </Button>
      </div>

      <div className="transition-all duration-300 flex-1 h-1 overflow-y-auto no-scrollbar p-5 gap-3 flex flex-col items-center ">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map((chat) => (
          <Button className={cn(isOpen ? "opacity-100" : "w-0 opacity-0")}>
            <span
              className={cn(
                "whitespace-nowrap overflow-hidden",
                isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
              )}
            >
              Sohbet {chat}
            </span>
          </Button>
        ))}
      </div>

      <div className="p-3 flex justify-center items-center h-15 bg-background border-border/40 border-t-3 ">
        <Button
          variant="primary"
          className={cn(
            "flex justify-start bg-[#f0f0f0] hover:bg-[#e1e3e6] cursor-pointer border border-border rounded-xl py-2 px-3 gap-3",
            !isOpen && "gap-0 px-0 py-1 justify-center",
          )}
          icon={
            <img
              src="blank-profile.webp"
              alt="Resim"
              className="w-12 h-12 rounded-3xl border border-gray-500"
            />
          }
        >
          <span
            className={cn(
              "whitespace-nowrap overflow-hidden",
              isOpen ? "w-auto opacity-100" : "w-0 opacity-0",
            )}
          >
            Test
          </span>
        </Button>
      </div>
    </div>
  );
};
