import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useAuth } from "@/features/auth/hooks/useAuth";

export const SettingsModal = () => {
  const { handleLogout } = useAuth();

  return (
    <div className="flex flex-col p-4 w-108 h-96">
      <Card className="w-full max-w-full flex justify-between items-center">
        <span className="font-bold text-lg">Hesaptan Çıkış Yap?</span>
        <Button
          className="rounded-xl w-fit text-sm text-white bg-gray-800 hover:bg-gray-900 active:bg-gray-950"
          onClick={handleLogout}
        >
          Oturumu Kapat
        </Button>
      </Card>
    </div>
  );
};
