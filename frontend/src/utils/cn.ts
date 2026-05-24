import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  // Gelen argümanları (string, object, array), tek bir temiz string'e çevir 
  const mergedClasses = clsx(inputs);
  
  // string içindeki çakışmaları engelle (sonradan gelen öncekileri ezer)
  return twMerge(mergedClasses);
}