import { Card } from "@/components/Card";
import { cn } from "@/utils/cn";
import { useState } from "react";
import Markdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import type { PredictionData, RiskFactorCard } from "@/store/conversationStore";
import { RiskDashboard } from "@/features/prediction/components/RiskDashboard";

type ChatMessageProps = {
  message: string;
  isUser: boolean;
  ragSources?: string[];
  createdAt?: string;
  predictionData?: PredictionData;
};

const formatTime = (dateStr?: string) => {
  if (!dateStr) return null;
  try {
    const date = new Date(dateStr);
    return date.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
  } catch {
    return null;
  }
};

const parsePredictionMessage = (content: string): PredictionData | undefined => {
  try {
    if (!content.includes("Diyabet Risk Değerlendirmesi")) return undefined;

    // Check if there is hidden metadata
    const commentMatch = content.match(/<!-- PREDICTION_DATA:(.*?) -->/);
    if (commentMatch) {
      try {
        const data = JSON.parse(commentMatch[1]);
        return {
          riskProbability: data.riskProbability,
          riskCategory: data.riskCategory,
          confidenceLevel: data.confidenceLevel,
          contributingFactors: data.contributingFactors || [],
          mlScore: data.mlScore || 0,
          symptomScore: data.symptomScore || 0,
          clinicalScore: data.clinicalScore || 0,
          activeSymptoms: data.activeSymptoms || [],
          riskFactorCards: data.riskFactorCards || [],
          shapValues: data.shapValues
        };
      } catch (jsonErr) {
        console.error("Failed to parse prediction JSON metadata", jsonErr);
      }
    }

    let riskCategory = "Medium";
    const categoryMatch = content.match(/Risk Kategorisi:\s*\*\*(.*?)\*\*/);
    if (categoryMatch) {
      const cat = categoryMatch[1].trim();
      if (cat.includes("Düşük")) riskCategory = "Low";
      else if (cat.includes("Yüksek")) riskCategory = "High";
      else riskCategory = "Medium";
    }

    let riskProbability = 0.5;
    const probMatch = content.match(/Olasılık:\s*\*\*(.*?)\*\*/);
    if (probMatch) {
      const pct = parseInt(probMatch[1].replace(/[^0-9]/g, ""), 10);
      if (!isNaN(pct)) riskProbability = pct / 100;
    }

    let confidenceLevel = "low";
    const confMatch = content.match(/Güven Düzeyi:\s*(.*?)(\n|$)/);
    if (confMatch) {
      const conf = confMatch[1].trim();
      if (conf.includes("Çok Yüksek")) confidenceLevel = "very_high";
      else if (conf.includes("Yüksek")) confidenceLevel = "high";
      else if (conf.includes("Orta")) confidenceLevel = "moderate";
      else confidenceLevel = "low";
    }

    let mlScore = 0;
    let symptomScore = 0;
    let clinicalScore = 0;

    const mlMatch = content.match(/ML Model:\s*%?([0-9]+)/);
    if (mlMatch) mlScore = parseInt(mlMatch[1], 10) / 100;

    const symptomMatch = content.match(/Semptom:\s*%?([0-9]+)/);
    if (symptomMatch) symptomScore = parseInt(symptomMatch[1], 10) / 100;

    const clinicalMatch = content.match(/Klinik:\s*%?([0-9]+)/);
    if (clinicalMatch) clinicalScore = parseInt(clinicalMatch[1], 10) / 100;

    const contributingFactors: string[] = [];
    const activeSymptoms: string[] = [];
    const riskFactorCards: RiskFactorCard[] = [];

    const symptomList = [
      "sık idrara çıkma (poliüri)",
      "aşırı susama (polidipsi)",
      "açıklanamayan kilo kaybı",
      "yorgunluk / halsizlik",
      "bulanık görme",
      "yara iyileşme gecikmesi",
      "sık enfeksiyon geçirme",
      "karıncalanma / uyuşma"
    ];

    if (content.includes("Katkı yapan faktörler:")) {
      const parts = content.split("Katkı yapan faktörler:");
      if (parts.length > 1) {
        const factorLines = parts[1].split("\n");
        for (const line of factorLines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("•") || trimmed.startsWith("-") || trimmed.startsWith("*")) {
            let factor = trimmed.slice(1).trim();
            // Remove markdown bold markings like **
            factor = factor.replace(/^\*+|\*+$/g, "").trim();
            if (!factor || factor.toLowerCase().includes("katkı yapan faktörler")) {
              continue;
            }
            contributingFactors.push(factor);
            const lowerFactor = factor.toLowerCase();

            // Check if it's a symptom
            if (symptomList.some(s => lowerFactor.includes(s) || s.includes(lowerFactor))) {
              activeSymptoms.push(factor);
            } else {
              // Map to RiskFactorCard
              let cardName = factor;
              let cardValue = "Var";
              let cardStatus: "risk" | "protective" | "neutral" = "risk";

              if (lowerFactor.includes("tansiyon")) {
                cardName = "Yüksek Tansiyon";
                cardValue = "Var";
                cardStatus = "risk";
              } else if (lowerFactor.includes("kolesterol")) {
                cardName = "Yüksek Kolesterol";
                cardValue = "Var";
                cardStatus = "risk";
              } else if (lowerFactor.includes("sigara")) {
                cardName = "Sigara Kullanımı";
                cardValue = "Kullanıyor";
                cardStatus = "risk";
              } else if (lowerFactor.includes("kalp")) {
                cardName = "Kalp Hastalığı";
                cardValue = "Var";
                cardStatus = "risk";
              } else if (lowerFactor.includes("yürüme")) {
                cardName = "Yürüme Zorluğu";
                cardValue = "Var";
                cardStatus = "risk";
              } else if (lowerFactor.includes("alkol")) {
                cardName = "Alkol Kullanımı";
                cardValue = "Var";
                cardStatus = "risk";
              } else if (lowerFactor.includes("fiziksel")) {
                cardName = "Fiziksel Aktivite";
                cardValue = "Düzenli";
                cardStatus = "protective";
              } else if (lowerFactor.includes("meyve")) {
                cardName = "Meyve Tüketimi";
                cardValue = "Her gün";
                cardStatus = "protective";
              } else if (lowerFactor.includes("sebze")) {
                cardName = "Sebze Tüketimi";
                cardValue = "Her gün";
                cardStatus = "protective";
              } else if (lowerFactor.includes("sağlık")) {
                cardName = "Genel Sağlık";
                cardStatus = "neutral";
                if (lowerFactor.includes("kötü")) {
                  cardValue = "Kötü";
                  cardStatus = "risk";
                } else if (lowerFactor.includes("orta")) {
                  cardValue = "Orta";
                  cardStatus = "neutral";
                } else if (lowerFactor.includes("iyi")) {
                  cardValue = "İyi";
                  cardStatus = "protective";
                } else if (lowerFactor.includes("çok iyi")) {
                  cardValue = "Çok İyi";
                  cardStatus = "protective";
                } else if (lowerFactor.includes("mükemmel")) {
                  cardValue = "Mükemmel";
                  cardStatus = "protective";
                }
              }

              riskFactorCards.push({
                name: cardName,
                value: cardValue,
                status: cardStatus,
                detail: factor
              });
            }
          }
        }
      }
    }

    return {
      riskProbability,
      riskCategory,
      confidenceLevel,
      contributingFactors,
      mlScore,
      symptomScore,
      clinicalScore,
      activeSymptoms,
      riskFactorCards
    };
  } catch (e) {
    console.error("Error parsing prediction message", e);
    return undefined;
  }
};

export const ChatMessage = ({
  message,
  isUser,
  ragSources,
  createdAt,
  predictionData,
}: ChatMessageProps) => {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const hasSources = !isUser && ragSources && ragSources.length > 0;
  const time = formatTime(createdAt);

  const finalPredictionData = !predictionData && !isUser && message.includes("Diyabet Risk Değerlendirmesi")
    ? parsePredictionMessage(message)
    : predictionData;

  return (
    <div
      className={cn(
        "flex w-full",
        finalPredictionData ? "justify-center" : isUser ? "justify-end" : "justify-start"
      )}
    >
      <div className={cn(
        finalPredictionData ? "w-full max-w-[520px]" : "max-w-[85%]",
        !isUser && !finalPredictionData && "min-w-[40%]"
      )}>
        {finalPredictionData ? (
          <RiskDashboard data={finalPredictionData} />
        ) : (
          <Card
            className={cn(
              isUser ? "bg-blue-600 text-white border-none" : "bg-card",
            )}
          >
            {isUser ? (
              message
            ) : (
              <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2">
                <Markdown rehypePlugins={[rehypeSanitize]}>{message}</Markdown>
              </div>
            )}
          </Card>
        )}
        <div className="flex items-center justify-between mt-1 px-1">
          {hasSources ? (
            <button
              onClick={() => setSourcesOpen(!sourcesOpen)}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={cn(
                  "transition-transform",
                  sourcesOpen && "rotate-90",
                )}
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
              <span>Kaynaklar ({ragSources!.length})</span>
            </button>
          ) : (
            <span />
          )}
          {time && (
            <span className="text-[10px] text-gray-400 dark:text-gray-500">{time}</span>
          )}
        </div>
        {sourcesOpen && hasSources && (
          <div className="mt-1 ml-1 flex flex-wrap gap-1.5">
            {ragSources!.map((source, i) => (
              <span
                key={i}
                className="inline-block rounded-md bg-gray-200 dark:bg-gray-700 px-2 py-0.5 text-xs text-gray-600 dark:text-gray-300"
              >
                {source}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
