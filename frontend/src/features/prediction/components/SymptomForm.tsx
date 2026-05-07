import { Dialog } from "@/components/Dialog";
import { Button } from "@/components/Button";
import { usePrediction, type SymptomValues } from "../hooks/usePrediction";

type SymptomKey = keyof Omit<SymptomValues, "age" | "gender">;

const symptomLabels: Record<SymptomKey, string> = {
  polyuria: "Çok sık idrara çıkma (Polyuria)",
  polydipsia: "Aşırı susama (Polydipsia)",
  suddenWeightLoss: "Ani kilo kaybı",
  weakness: "Halsizlik / Güçsüzlük",
  polyphagia: "Aşırı açlık (Polyphagia)",
  genitalThrush: "Genital mantar enfeksiyonu",
  visualBlurring: "Görme bulanıklığı",
  itching: "Kaşıntı",
  irritability: "Sinirlilik / Huzursuzluk",
  delayedHealing: "Yaraların geç iyileşmesi",
  partialParesis: "Kısmi felç / Kas güçsüzlüğü",
  muscleStiffness: "Kas sertliği",
  alopecia: "Saç dökülmesi",
  obesity: "Obezite",
};

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export const SymptomForm = ({ isOpen, onClose }: Props) => {
  const { symptoms, setSymptoms, toggleSymptom, handleSubmit, isLoading } =
    usePrediction(onClose);

  return (
    <Dialog isOpen={isOpen} isLocked={false} title="Diyabet Risk Testi" onClose={onClose}>
      <div className="p-6 flex flex-col gap-5 w-[340px] sm:w-[480px] max-h-[80vh] overflow-y-auto">
        {/* Yaş ve Cinsiyet */}
        <div className="flex gap-4">
          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">Yaş</label>
            <input
              type="number"
              min={1}
              max={120}
              value={symptoms.age}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, age: Number(e.target.value) }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">Cinsiyet</label>
            <select
              value={symptoms.gender}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, gender: e.target.value }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="Male">Erkek</option>
              <option value="Female">Kadın</option>
            </select>
          </div>
        </div>

        {/* Semptomlar */}
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-gray-700 mb-1">
            Aşağıdaki semptomlardan hangilerini yaşıyorsunuz?
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(Object.keys(symptomLabels) as SymptomKey[]).map((key) => (
              <label
                key={key}
                className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={symptoms[key] === "Yes"}
                  onChange={() => toggleSymptom(key)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-sm text-gray-600">{symptomLabels[key]}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Gönder Butonu */}
        <Button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full mt-2"
        >
          {isLoading ? "Değerlendiriliyor..." : "Risk Değerlendir"}
        </Button>

        <p className="text-xs text-gray-400 text-center">
          Bu değerlendirme tıbbi tanı yerine geçmez. Sonuçlar için doktorunuza danışın.
        </p>
      </div>
    </Dialog>
  );
};
