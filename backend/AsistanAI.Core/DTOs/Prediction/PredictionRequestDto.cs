namespace AsistanAI.Core.DTOs.Prediction;

public class PredictionRequestDto
{
    // Required
    public int Age { get; set; }
    public string Gender { get; set; } = null!;

    // Tier 1 - Lifestyle & health history
    public double? Bmi { get; set; }
    public bool? HighBp { get; set; }
    public bool? HighChol { get; set; }
    public bool? PhysicalActivity { get; set; }
    public int? GenHealth { get; set; } // 1-5
    public bool? DiffWalking { get; set; }
    public bool? Smoker { get; set; }

    // Tier 2 - Optional
    public bool? HeartDisease { get; set; }
    public bool? FruitsDaily { get; set; }
    public bool? VeggiesDaily { get; set; }
    public bool? HeavyAlcohol { get; set; }

    // Clinical values
    public double? BloodGlucose { get; set; }
    public double? Hba1c { get; set; }

    // Convenience for BMI
    public double? HeightCm { get; set; }
    public double? WeightKg { get; set; }

    // Symptoms (hybrid model)
    public bool? Polyuria { get; set; }
    public bool? Polydipsia { get; set; }
    public bool? UnexplainedWeightLoss { get; set; }
    public bool? Fatigue { get; set; }
    public bool? BlurredVision { get; set; }
    public bool? SlowHealing { get; set; }
    public bool? FrequentInfections { get; set; }
    public bool? TinglingNumbness { get; set; }

    // Chat session reference
    public int ChatSessionId { get; set; }
}
