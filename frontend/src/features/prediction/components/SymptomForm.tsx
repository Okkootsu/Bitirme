import { Dialog } from "@/components/Dialog";
import { Button } from "@/components/Button";
import { usePrediction, type BoolKey } from "../hooks/usePrediction";

const riskFactorLabels: Record<string, string> = {
  highBp: "Yüksek tansiyon",
  highChol: "Yüksek kolesterol",
  smoker: "Sigara kullanımı",
  heartDisease: "Kalp hastalığı öyküsü",
  diffWalking: "Yürüme zorluğu",
  heavyAlcohol: "Ağır alkol kullanımı",
  physicalActivity: "Düzenli fiziksel aktivite",
  fruitsDaily: "Her gün meyve tüketimi",
  veggiesDaily: "Her gün sebze tüketimi",
};

const symptomLabels: Record<string, string> = {
  polyuria: "Sık idrara çıkma (poliüri)",
  polydipsia: "Aşırı susama (polidipsi)",
  unexplainedWeightLoss: "Açıklanamayan kilo kaybı",
  fatigue: "Yorgunluk / halsizlik",
  blurredVision: "Bulanık görme",
  slowHealing: "Yara iyileşme gecikmesi",
  frequentInfections: "Sık enfeksiyon geçirme",
  tinglingNumbness: "Karıncalanma / uyuşma",
};

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export const SymptomForm = ({ isOpen, onClose }: Props) => {
  const { symptoms, setSymptoms, toggleBool, handleSubmit, isLoading } =
    usePrediction(onClose);

  return (
    <Dialog isOpen={isOpen} isLocked={false} title="Diyabet Risk Testi" onClose={onClose}>
      <div className="p-6 flex flex-col gap-5 w-[340px] sm:w-[520px] max-h-[80vh] overflow-y-auto">
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

        {/* BMI ve Genel Sağlık */}
        <div className="flex gap-4">
          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">BMI (opsiyonel)</label>
            <input
              type="number"
              step="0.1"
              min={10}
              max={80}
              placeholder="Örn: 27.5"
              value={symptoms.bmi ?? ""}
              onChange={(e) =>
                setSymptoms((prev) => ({
                  ...prev,
                  bmi: e.target.value ? Number(e.target.value) : null,
                }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">Genel Sağlık (1-5)</label>
            <select
              value={symptoms.genHealth}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, genHealth: Number(e.target.value) }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value={1}>1 - Mükemmel</option>
              <option value={2}>2 - Çok İyi</option>
              <option value={3}>3 - İyi</option>
              <option value={4}>4 - Orta</option>
              <option value={5}>5 - Kötü</option>
            </select>
          </div>
        </div>

        {/* Klinik Değerler */}
        <div className="flex gap-4">
          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">Açlık Kan Şekeri (mg/dL)</label>
            <input
              type="number"
              placeholder="Opsiyonel"
              value={symptoms.bloodGlucose ?? ""}
              onChange={(e) =>
                setSymptoms((prev) => ({
                  ...prev,
                  bloodGlucose: e.target.value ? Number(e.target.value) : null,
                }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-medium text-gray-700">HbA1c (%)</label>
            <input
              type="number"
              step="0.1"
              placeholder="Opsiyonel"
              value={symptoms.hba1c ?? ""}
              onChange={(e) =>
                setSymptoms((prev) => ({
                  ...prev,
                  hba1c: e.target.value ? Number(e.target.value) : null,
                }))
              }
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
        </div>

        {/* Semptomlar */}
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-gray-700 mb-1">
            Semptomlar
          </p>
          <p className="text-xs text-gray-400 mb-2">
            ADA/WHO klinik semptomları (kaynak: ADA Standards of Care 2024, PMC9676132)
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(Object.keys(symptomLabels) as BoolKey[]).map((key) => (
              <label
                key={key}
                className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950/20 transition-colors border border-blue-100 dark:border-blue-900/30"
              >
                <input
                  type="checkbox"
                  checked={symptoms[key] as boolean}
                  onChange={() => toggleBool(key)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-sm text-gray-600 dark:text-gray-300">{symptomLabels[key]}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Risk Faktörleri */}
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-gray-700 mb-1">
            Risk Faktörleri
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(Object.keys(riskFactorLabels) as BoolKey[]).map((key) => (
              <label
                key={key}
                className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={symptoms[key] as boolean}
                  onChange={() => toggleBool(key)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-sm text-gray-600">{riskFactorLabels[key]}</span>
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
