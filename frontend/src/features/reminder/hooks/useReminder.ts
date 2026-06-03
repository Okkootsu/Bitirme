import { useState, useEffect } from "react";
import { LocalNotifications } from "@capacitor/local-notifications";
import { toast } from "sonner";

export type Reminder = {
  id: number;
  time: string;
};

export const useReminder = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);

  // Kayıtlı hatırlatıcıları yükle
  const loadReminders = async () => {
    const pending = await LocalNotifications.getPending();
    const loadedReminders = pending.notifications.map((n) => ({
      id: n.id,
      time: `${n.schedule?.on?.hour?.toString().padStart(2, "0")}:${n.schedule?.on?.minute?.toString().padStart(2, "0")}`,
    }));
    setReminders(loadedReminders);
  };

  useEffect(() => {
    loadReminders();
  }, []);

  const addReminder = async (time: string) => {
    // Bildirim izni isteme
    let permStatus = await LocalNotifications.checkPermissions();
    if (permStatus.display !== "granted") {
      permStatus = await LocalNotifications.requestPermissions();
    }

    if (permStatus.display !== "granted") {
      toast.error("Bildirim gönderebilmek için izin vermeniz gerekiyor.");
      return;
    }

    const [hour, minute] = time.split(":").map(Number);
    const notificationId = new Date().getTime() % 100000; // Rastgele ID

    try {
      await LocalNotifications.schedule({
        notifications: [
          {
            title: "İnsülin Vakti!",
            body: "Planlanan insülin dozunuzu alma zamanı geldi. Lütfen ölçümlerinizi yapmayı unutmayın.",
            id: notificationId,
            schedule: {
              on: { hour, minute }, // Her gün bu saatte çalar
              allowWhileIdle: true, // Telefon uyku modundayken bile çalar
            },
            actionTypeId: "",
            extra: null,
          },
        ],
      });

      toast.success(`Hatırlatıcı ${time} saatine kuruldu.`);
      loadReminders();
    } catch (error) {
      toast.error("Hatırlatıcı kurulamadı.");
    }
  };

  const removeReminder = async (id: number) => {
    await LocalNotifications.cancel({ notifications: [{ id }] });
    toast.success("Hatırlatıcı silindi.");
    loadReminders();
  };

  return {
    reminders,
    addReminder,
    removeReminder,
  };
};