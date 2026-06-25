import { Card } from "@/components/Card";
import { cn } from "@/utils/cn";
import { useState } from "react";
import Markdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import type { PredictionData } from "@/store/conversationStore";
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
    // Sadece PREDICTION_DATA metadata'sı olan mesajları dashboard olarak göster
    const commentMatch = content.match(/<!-- PREDICTION_DATA:(.*?) -->/s);
    if (!commentMatch) return undefined;

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

  const finalPredictionData = !predictionData && !isUser
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
