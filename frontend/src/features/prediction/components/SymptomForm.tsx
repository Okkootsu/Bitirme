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
      <div className="p-6 flex flex-col gap-5 w-full max-h-[80vh] overflow-y-auto no-scrollbar text-gray-900 dark:text-zinc-100 rounded-b-xl">
        {/* Yaş ve Cinsiyet */}
        <div className="flex gap-4">
          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">Yaş</label>
            <input
              type="number"
              min={1}
              max={120}
              value={symptoms.age}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, age: Number(e.target.value) }))
              }
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all shadow-sm"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">Cinsiyet</label>
            <select
              value={symptoms.gender}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, gender: e.target.value }))
              }
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all cursor-pointer shadow-sm"
            >
              <option value="Male">Erkek</option>
              <option value="Female">Kadın</option>
            </select>
          </div>
        </div>

        {/* BMI ve Genel Sağlık */}
        <div className="flex gap-4">
          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">BMI (opsiyonel)</label>
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
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all shadow-sm"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">Genel Sağlık (1-5)</label>
            <select
              value={symptoms.genHealth}
              onChange={(e) =>
                setSymptoms((prev) => ({ ...prev, genHealth: Number(e.target.value) }))
              }
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all cursor-pointer shadow-sm"
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
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">Açlık Kan Şekeri (mg/dL)</label>
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
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all shadow-sm"
            />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            <label className="text-sm font-semibold text-gray-800 dark:text-zinc-200">HbA1c (%)</label>
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
              className="bg-white dark:bg-zinc-900 border border-border dark:border-zinc-700/60 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-gray-900 dark:text-white transition-all shadow-sm"
            />
          </div>
        </div>

        {/* Semptomlar */}
        <div className="flex flex-col gap-1 mt-1">
          <p className="text-sm font-bold text-gray-800 dark:text-zinc-200 mb-0.5">
            Semptomlar
          </p>
          <p className="text-xs text-gray-400 dark:text-zinc-500 mb-2">
            ADA/WHO klinik semptomları (kaynak: ADA Standards of Care 2024, PMC9676132)
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(Object.keys(symptomLabels) as BoolKey[]).map((key) => (
              <label
                key={key}
                className="flex items-center gap-3 cursor-pointer p-3 rounded-xl bg-white/60 dark:bg-zinc-900/40 border border-amber-200/60 dark:border-amber-900/30 hover:bg-amber-500/5 dark:hover:bg-amber-500/10 hover:border-amber-300 dark:hover:border-amber-700/50 transition-all shadow-sm"
              >
                <input
                  type="checkbox"
                  checked={symptoms[key] as boolean}
                  onChange={() => toggleBool(key)}
                  className="w-4 h-4 accent-amber-500 rounded cursor-pointer"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-zinc-300 select-none">{symptomLabels[key]}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Risk Faktörleri */}
        <div className="flex flex-col gap-1 mt-1">
          <p className="text-sm font-bold text-gray-800 dark:text-zinc-200 mb-1">
            Risk Faktörleri
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(Object.keys(riskFactorLabels) as BoolKey[]).map((key) => (
              <label
                key={key}
                className="flex items-center gap-3 cursor-pointer p-3 rounded-xl bg-white/60 dark:bg-zinc-900/40 border border-blue-200/60 dark:border-blue-900/30 hover:bg-blue-500/5 dark:hover:bg-blue-500/10 hover:border-blue-300 dark:hover:border-blue-700/50 transition-all shadow-sm"
              >
                <input
                  type="checkbox"
                  checked={symptoms[key] as boolean}
                  onChange={() => toggleBool(key)}
                  className="w-4 h-4 accent-blue-500 rounded cursor-pointer"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-zinc-300 select-none">{riskFactorLabels[key]}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Gönder Butonu */}
        <Button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full mt-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 transition-all cursor-pointer disabled:opacity-50"
        >
          {isLoading ? "Değerlendiriliyor..." : "Risk Değerlendir"}
        </Button>

        <p className="text-[10px] text-gray-400 dark:text-zinc-500 text-center">
          Bu değerlendirme tıbbi tanı yerine geçmez. Sonuçlar için doktorunuza danışın.
        </p>
      </div>
    </Dialog>
  );
};
