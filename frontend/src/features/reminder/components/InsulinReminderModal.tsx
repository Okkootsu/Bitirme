import { useState } from "react";
import { useReminder } from "../hooks/useReminder";
import { Button } from "@/components/Button";
import { Bell, Trash2 } from "lucide-react";

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export const InsulinReminderModal = ({ isOpen }: Props) => {
  const { reminders, addReminder, removeReminder } = useReminder();
  const [time, setTime] = useState("");

  if (!isOpen) return null;

  const handleAdd = () => {
    if (!time) return;
    addReminder(time);
    setTime("");
  };

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div className="flex flex-col gap-2">
        <label className="font-bold text-sm text-gray-700 dark:text-gray-300">
          İnsülin Saati Seçin
        </label>
        <div className="flex gap-3">
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            className="flex-1 bg-white dark:bg-zinc-700 rounded-lg px-4 py-2 border-2 border-border focus:ring-2 focus:ring-blue-400 dark:text-white outline-none"
          />
          <Button onClick={handleAdd} className="w-auto px-6 bg-blue-500 hover:bg-blue-600 text-white">
            Ekle
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-3 mt-4">
        <h3 className="font-bold text-lg border-b border-border pb-2">Aktif Hatırlatıcılar</h3>
        {reminders.length === 0 ? (
          <p className="text-gray-500 text-sm italic">Henüz bir hatırlatıcı kurmadınız.</p>
        ) : (
          reminders.map((reminder) => (
            <div key={reminder.id} className="flex justify-between items-center bg-card p-3 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <Bell size={20} className="text-blue-500" />
                <span className="font-bold text-lg">{reminder.time}</span>
              </div>
              <button
                onClick={() => removeReminder(reminder.id)}
                className="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-full transition-colors"
              >
                <Trash2 size={20} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};