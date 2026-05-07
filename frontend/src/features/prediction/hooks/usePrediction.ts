import { useState } from "react";
import api from "@/utils/axios";
import axios from "axios";
import { useConversationStore } from "@/store/conversationStore";
import { useConversations } from "@/hooks/useConversations";

export type SymptomValues = {
  age: number;
  gender: string;
  polyuria: string;
  polydipsia: string;
  suddenWeightLoss: string;
  weakness: string;
  polyphagia: string;
  genitalThrush: string;
  visualBlurring: string;
  itching: string;
  irritability: string;
  delayedHealing: string;
  partialParesis: string;
  muscleStiffness: string;
  alopecia: string;
  obesity: string;
};

export const defaultSymptoms: SymptomValues = {
  age: 40,
  gender: "Male",
  polyuria: "No",
  polydipsia: "No",
  suddenWeightLoss: "No",
  weakness: "No",
  polyphagia: "No",
  genitalThrush: "No",
  visualBlurring: "No",
  itching: "No",
  irritability: "No",
  delayedHealing: "No",
  partialParesis: "No",
  muscleStiffness: "No",
  alopecia: "No",
  obesity: "No",
};

export const usePrediction = (onClose: () => void) => {
  const [symptoms, setSymptoms] = useState<SymptomValues>(defaultSymptoms);
  const [isLoading, setIsLoading] = useState(false);

  const { selectedConversation, addMessage, setIsChatStarted } =
    useConversationStore();
  const { createConversation } = useConversations();

  const toggleSymptom = (key: keyof SymptomValues) => {
    setSymptoms((prev) => ({
      ...prev,
      [key]: prev[key as keyof typeof prev] === "Yes" ? "No" : "Yes",
    }));
  };

  const handleSubmit = async () => {
    setIsLoading(true);

    try {
      let sessionId = selectedConversation;

      if (!sessionId) {
        sessionId = await createConversation();
        if (!sessionId) return;
        setIsChatStarted(true);
      }

      const predictionResponse = await api.post("/Prediction/assess", {
        age: symptoms.age,
        gender: symptoms.gender,
        polyuria: symptoms.polyuria,
        polydipsia: symptoms.polydipsia,
        suddenWeightLoss: symptoms.suddenWeightLoss,
        weakness: symptoms.weakness,
        polyphagia: symptoms.polyphagia,
        genitalThrush: symptoms.genitalThrush,
        visualBlurring: symptoms.visualBlurring,
        itching: symptoms.itching,
        irritability: symptoms.irritability,
        delayedHealing: symptoms.delayedHealing,
        partialParesis: symptoms.partialParesis,
        muscleStiffness: symptoms.muscleStiffness,
        alopecia: symptoms.alopecia,
        obesity: symptoms.obesity,
        chatSessionId: sessionId,
      });

      const predictionResult = predictionResponse.data.data;
      addMessage({
        id: Date.now(),
        content: predictionResult.formattedMessage,
        isUserMessage: false,
      });

      // Formu sıfırla ve kapat
      setSymptoms(defaultSymptoms);
      onClose();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        alert(err.response.data.errorMessage || "Tahmin yapılamadı.");
      } else {
        alert("Sunucuya bağlanılamadı.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return { symptoms, setSymptoms, toggleSymptom, handleSubmit, isLoading };
};
