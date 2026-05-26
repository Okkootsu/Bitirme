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
  const radius = 70;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - probability);

  return (
    <div className="flex flex-col items-center">
      <svg width="180" height="100" viewBox="0 0 180 100">
        <path
          d="M 10 90 A 70 70 0 0 1 170 90"
          fill="none"
          stroke="currentColor"
          strokeWidth="12"
          className="text-gray-200 dark:text-gray-700"
          strokeLinecap="round"
        />
        <path
          d="M 10 90 A 70 70 0 0 1 170 90"
          fill="none"
          stroke={config.color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
        <text
          x="90"
          y="75"
          textAnchor="middle"
          className="fill-gray-800 dark:fill-gray-100"
          fontSize="28"
          fontWeight="bold"
        >
          %{percentage}
        </text>
        <text x="10" y="98" textAnchor="start" fontSize="9" className="fill-gray-400">Düşük</text>
        <text x="170" y="98" textAnchor="end" fontSize="9" className="fill-gray-400">Yüksek</text>
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

export const RiskDashboard = ({ data }: Props) => {
  const config = categoryConfig[data.riskCategory as keyof typeof categoryConfig] ?? categoryConfig.Medium;

  const hasSymptoms = data.symptomScore > 0;
  const hasClinical = data.clinicalScore > 0;

  return (
    <div className={`rounded-2xl p-5 ${config.bg} border border-border w-full`}>
      {/* Header */}
      <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 text-center">
        Diyabet Risk Değerlendirmesi
      </h3>

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
