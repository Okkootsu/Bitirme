import { useState } from "react";
import { Info } from "lucide-react";
import { Dialog } from "@/components/Dialog";
import type { PredictionData, RiskFactorCard } from "@/store/conversationStore";

type Props = {
  data: PredictionData;
};

const categoryConfig = {
  Low: { label: "Düşük Risk", color: "#22c55e", bg: "bg-green-50 dark:bg-green-950/30" },
  Medium: { label: "Orta Risk", color: "#f59e0b", bg: "bg-amber-50 dark:bg-amber-950/30" },
  High: { label: "Yüksek Risk", color: "#ef4444", bg: "bg-red-50 dark:bg-red-950/30" },
} as const;

const confidenceLabels: Record<string, string> = {
  very_high: "Çok Yüksek (klinik veri + semptom mevcut)",
  high: "Yüksek (klinik veri mevcut)",
  moderate: "Orta (semptom verisi mevcut)",
  low: "Düşük (yalnızca risk faktörleri)",
};

const RiskGauge = ({ probability, category }: { probability: number; category: string }) => {
  const config = categoryConfig[category as keyof typeof categoryConfig] ?? categoryConfig.Medium;
  const percentage = Math.round(probability * 100);

  return (
    <div className="flex flex-col items-center">
      <svg width="200" height="110" viewBox="0 0 200 110">
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="currentColor"
          strokeWidth="12"
          className="text-gray-200 dark:text-gray-700"
          strokeLinecap="round"
        />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={config.color}
          strokeWidth="12"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray="1"
          strokeDashoffset={1 - probability}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
        <text
          x="100"
          y="85"
          textAnchor="middle"
          className="fill-gray-800 dark:fill-gray-100"
          fontSize="28"
          fontWeight="bold"
        >
          %{percentage}
        </text>
        <text x="20" y="108" textAnchor="start" fontSize="9" className="fill-gray-400">Düşük</text>
        <text x="180" y="108" textAnchor="end" fontSize="9" className="fill-gray-400">Yüksek</text>
      </svg>
      <span
        className="mt-1 px-3 py-1 rounded-full text-sm font-semibold text-white"
        style={{ backgroundColor: config.color }}
      >
        {config.label}
      </span>
    </div>
  );
};

const LayerBar = ({ label, score, color }: { label: string; score: number; color: string }) => {
  const pct = Math.round(score * 100);
  return (
    <div className="flex items-center gap-2">
      <span className="w-20 text-xs text-gray-600 dark:text-gray-400 text-right shrink-0">{label}</span>
      <div className="flex-1 h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="w-10 text-xs font-mono text-gray-700 dark:text-gray-300 shrink-0">%{pct}</span>
    </div>
  );
};

const statusStyles = {
  risk: { icon: "⚠️", color: "text-red-600 dark:text-red-400", bg: "bg-red-50 dark:bg-red-950/30", border: "border-red-200 dark:border-red-800" },
  protective: { icon: "✅", color: "text-green-600 dark:text-green-400", bg: "bg-green-50 dark:bg-green-950/30", border: "border-green-200 dark:border-green-800" },
  neutral: { icon: "ℹ️", color: "text-gray-600 dark:text-gray-400", bg: "bg-gray-50 dark:bg-gray-800/30", border: "border-gray-200 dark:border-gray-700" },
} as const;

const FactorCard = ({ card }: { card: RiskFactorCard }) => {
  const cfg = statusStyles[card.status] ?? statusStyles.neutral;
  return (
    <div
      className={`flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs border ${cfg.bg} ${cfg.border}`}
      title={card.detail}
    >
      <span className="text-xs shrink-0">{cfg.icon}</span>
      <span className={`font-semibold truncate ${cfg.color}`}>{card.name}</span>
      <span className="font-medium text-gray-700 dark:text-gray-300 ml-auto shrink-0">{card.value}</span>
    </div>
  );
};

const ModelInfoContent = () => (
  <div className="p-4 space-y-4 text-sm text-gray-700 dark:text-gray-300 overflow-y-auto max-h-[70vh]">
    {/* Model Nedir */}
    <section>
      <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-1.5 flex items-center gap-1.5">
        <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">1</span>
        Model Nedir?
      </h4>
      <p className="text-xs leading-relaxed ml-8">
        CDC'nin <strong>70.000+ kişilik</strong> sağlık anketi verisinde (BRFSS) eğitilmiş bir yapay zeka modelidir.
        Üç farklı algoritmanın (<strong>RandomForest</strong>, <strong>XGBoost</strong>, <strong>LogisticRegression</strong>)
        birleştirilmesiyle oluşturulan bir topluluk modeli kullanılır.
      </p>
    </section>

    {/* 3 Katmanlı Skorlama */}
    <section>
      <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-1.5 flex items-center gap-1.5">
        <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">2</span>
        3 Katmanlı Skorlama
      </h4>
      <div className="ml-8 space-y-1.5">
        <div className="flex items-start gap-2">
          <span className="w-3 h-3 rounded-full bg-indigo-500 shrink-0 mt-0.5" />
          <p className="text-xs"><strong>ML Model:</strong> Yaş, BMI, tansiyon, kolesterol gibi 13 risk faktöründen hesaplanan yapay zeka skoru</p>
        </div>
        <div className="flex items-start gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500 shrink-0 mt-0.5" />
          <p className="text-xs"><strong>Klinik:</strong> Açlık kan şekeri ve HbA1c değerlerinden ADA 2024 tanı eşiklerine göre hesaplanan skor</p>
        </div>
        <div className="flex items-start gap-2">
          <span className="w-3 h-3 rounded-full bg-amber-500 shrink-0 mt-0.5" />
          <p className="text-xs"><strong>Semptom:</strong> Sık idrara çıkma, aşırı susama gibi bildirilen belirtilerden hesaplanan skor</p>
        </div>
      </div>
    </section>

    {/* Final Skor Formülü */}
    <section>
      <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-1.5 flex items-center gap-1.5">
        <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">3</span>
        Final Skor Nasıl Hesaplanır?
      </h4>
      <div className="ml-8 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden text-xs">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-800">
              <th className="text-left px-2.5 py-1.5 font-semibold">Mevcut Veri</th>
              <th className="text-left px-2.5 py-1.5 font-semibold">Formül</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            <tr>
              <td className="px-2.5 py-1.5">Klinik + Semptom</td>
              <td className="px-2.5 py-1.5 font-mono text-[11px]">0.35×ML + 0.45×Klinik + 0.20×Semptom</td>
            </tr>
            <tr>
              <td className="px-2.5 py-1.5">Sadece Klinik</td>
              <td className="px-2.5 py-1.5 font-mono text-[11px]">0.35×ML + 0.65×Klinik</td>
            </tr>
            <tr>
              <td className="px-2.5 py-1.5">Sadece Semptom</td>
              <td className="px-2.5 py-1.5 font-mono text-[11px]">0.60×ML + 0.40×Semptom (tavanlı)</td>
            </tr>
            <tr>
              <td className="px-2.5 py-1.5">Hiçbiri</td>
              <td className="px-2.5 py-1.5 font-mono text-[11px]">ML skoru direkt</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-1 ml-8">
        Klinik veri (lab sonuçları) ADA tanı standardı olduğundan en yüksek ağırlığı alır.
      </p>
    </section>

    {/* Risk Kategorileri */}
    <section>
      <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-1.5 flex items-center gap-1.5">
        <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">4</span>
        Risk Kategorileri
      </h4>
      <div className="ml-8 flex gap-2">
        <span className="flex-1 text-center rounded-lg py-1.5 text-xs font-semibold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
          &lt; %30 — Düşük
        </span>
        <span className="flex-1 text-center rounded-lg py-1.5 text-xs font-semibold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
          %30-59 — Orta
        </span>
        <span className="flex-1 text-center rounded-lg py-1.5 text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
          &ge; %60 — Yüksek
        </span>
      </div>
    </section>

    {/* Disclaimer */}
    <p className="text-[10px] text-gray-400 text-center pt-2 border-t border-gray-200 dark:border-gray-700">
      Bu değerlendirme tıbbi tanı yerine geçmez. Sonuçlarınız hakkında mutlaka doktorunuza danışın.
    </p>
  </div>
);

export const RiskDashboard = ({ data }: Props) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const config = categoryConfig[data.riskCategory as keyof typeof categoryConfig] ?? categoryConfig.Medium;

  const hasSymptoms = data.symptomScore > 0;
  const hasClinical = data.clinicalScore > 0;

  return (
    <div className={`rounded-2xl p-5 ${config.bg} border border-border w-full`}>
      {/* Header */}
      <div className="relative mb-4">
        <button
          onClick={() => setIsInfoOpen(true)}
          className="absolute -top-1 -right-1 w-7 h-7 rounded-full border-2 border-amber-400 dark:border-amber-500 bg-white dark:bg-gray-800 flex items-center justify-center hover:bg-amber-50 dark:hover:bg-amber-900/30 transition-colors"
          title="Nasıl hesaplanıyor?"
        >
          <Info className="w-4 h-4 text-amber-500 dark:text-amber-400" />
        </button>
        <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 text-center">
          Diyabet Risk Değerlendirmesi
        </h3>
      </div>

      <Dialog isOpen={isInfoOpen} onClose={() => setIsInfoOpen(false)} title="Nasıl Hesaplanıyor?">
        <ModelInfoContent />
      </Dialog>

      {/* Gauge */}
      <RiskGauge probability={data.riskProbability} category={data.riskCategory} />

      {/* Confidence */}
      <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-2">
        Güven: {confidenceLabels[data.confidenceLevel] ?? data.confidenceLevel}
      </p>

      {/* Layer Scores */}
      <div className="mt-4">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Katman Skorları</p>
        <div className="flex flex-col gap-1.5">
          <LayerBar label="ML Model" score={data.mlScore} color="#6366f1" />
          <LayerBar label="Semptom" score={data.symptomScore} color={hasSymptoms ? "#f59e0b" : "#d1d5db"} />
          <LayerBar label="Klinik" score={data.clinicalScore} color={hasClinical ? "#ef4444" : "#d1d5db"} />
        </div>
        {!hasSymptoms && !hasClinical && (
          <p className="text-[10px] text-gray-400 mt-1">
            Semptom ve klinik veri girilmedi — yalnızca ML model skoru kullanıldı
          </p>
        )}
      </div>

      {/* Active Symptoms */}
      {data.activeSymptoms && data.activeSymptoms.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Bildirilen Semptomlar</p>
          <div className="flex flex-wrap gap-1.5">
            {data.activeSymptoms.map((symptom, i) => (
              <span
                key={i}
                className="inline-block rounded-lg bg-amber-100/60 dark:bg-amber-900/20 px-2.5 py-1 text-xs text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-700"
              >
                {symptom}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Risk Factor Cards */}
      {data.riskFactorCards && data.riskFactorCards.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Faktör Detayları</p>
          <div className="grid grid-cols-2 gap-1.5">
            {data.riskFactorCards.map((card, i) => (
              <FactorCard key={i} card={card} />
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <p className="mt-4 text-[10px] text-gray-400 text-center">
        Bu değerlendirme tıbbi tanı yerine geçmez. Sonuçlar için doktorunuza danışın.
      </p>
    </div>
  );
};
