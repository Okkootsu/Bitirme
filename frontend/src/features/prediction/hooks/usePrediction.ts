import { useState } from "react";
import api from "@/utils/axios";
import axios from "axios";
import { useConversationStore } from "@/store/conversationStore";
import { useConversations } from "@/hooks/useConversations";
import { toast } from "sonner";

export type SymptomValues = {
  age: number;
  gender: string;
  bmi: number | null;
  highBp: boolean;
  highChol: boolean;
  physicalActivity: boolean;
  genHealth: number;
  diffWalking: boolean;
  smoker: boolean;
  heartDisease: boolean;
  fruitsDaily: boolean;
  veggiesDaily: boolean;
  heavyAlcohol: boolean;
  bloodGlucose: number | null;
  hba1c: number | null;
  // Symptoms (hybrid model)
  polyuria: boolean;
  polydipsia: boolean;
  unexplainedWeightLoss: boolean;
  fatigue: boolean;
  blurredVision: boolean;
  slowHealing: boolean;
  frequentInfections: boolean;
  tinglingNumbness: boolean;
};

export const defaultSymptoms: SymptomValues = {
  age: 40,
  gender: "Male",
  bmi: null,
  highBp: false,
  highChol: false,
  physicalActivity: true,
  genHealth: 3,
  diffWalking: false,
  smoker: false,
  heartDisease: false,
  fruitsDaily: true,
  veggiesDaily: true,
  heavyAlcohol: false,
  bloodGlucose: null,
  hba1c: null,
  polyuria: false,
  polydipsia: false,
  unexplainedWeightLoss: false,
  fatigue: false,
  blurredVision: false,
  slowHealing: false,
  frequentInfections: false,
  tinglingNumbness: false,
};

export type BoolKey = {
  [K in keyof SymptomValues]: SymptomValues[K] extends boolean ? K : never;
}[keyof SymptomValues];

export const usePrediction = (onClose: () => void) => {
  const [symptoms, setSymptoms] = useState<SymptomValues>(defaultSymptoms);
  const [isLoading, setIsLoading] = useState(false);

  const { selectedConversation, addMessage, setIsChatStarted } =
    useConversationStore();
  const { createConversation } = useConversations();

  const toggleBool = (key: BoolKey) => {
    setSymptoms((prev) => ({
      ...prev,
      [key]: !prev[key],
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
        bmi: symptoms.bmi,
        highBp: symptoms.highBp,
        highChol: symptoms.highChol,
        physicalActivity: symptoms.physicalActivity,
        genHealth: symptoms.genHealth,
        diffWalking: symptoms.diffWalking,
        smoker: symptoms.smoker,
        heartDisease: symptoms.heartDisease,
        fruitsDaily: symptoms.fruitsDaily,
        veggiesDaily: symptoms.veggiesDaily,
        heavyAlcohol: symptoms.heavyAlcohol,
        bloodGlucose: symptoms.bloodGlucose,
        hba1c: symptoms.hba1c,
        // Symptoms
        polyuria: symptoms.polyuria,
        polydipsia: symptoms.polydipsia,
        unexplainedWeightLoss: symptoms.unexplainedWeightLoss,
        fatigue: symptoms.fatigue,
        blurredVision: symptoms.blurredVision,
        slowHealing: symptoms.slowHealing,
        frequentInfections: symptoms.frequentInfections,
        tinglingNumbness: symptoms.tinglingNumbness,
        chatSessionId: sessionId,
      });

      const predictionResult = predictionResponse.data.data;
      addMessage({
        id: Date.now(),
        content: predictionResult.formattedMessage,
        isUserMessage: false,
        predictionData: {
          riskProbability: predictionResult.riskProbability,
          riskCategory: predictionResult.riskCategory,
          confidenceLevel: predictionResult.confidenceLevel,
          contributingFactors: predictionResult.contributingFactors,
          shapValues: predictionResult.shapValues,
          mlScore: predictionResult.mlScore,
          symptomScore: predictionResult.symptomScore,
          clinicalScore: predictionResult.clinicalScore,
          activeSymptoms: predictionResult.activeSymptoms,
          riskFactorCards: predictionResult.riskFactorCards ?? [],
        },
      });

      setSymptoms(defaultSymptoms);
      onClose();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        toast.error(err.response.data.errorMessage || "Tahmin yapılamadı.");
      } else {
        toast.error("Sunucuya bağlanılamadı.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return { symptoms, setSymptoms, toggleBool, handleSubmit, isLoading };
};
