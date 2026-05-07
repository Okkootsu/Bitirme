namespace AsistanAI.Core.DTOs.Prediction;

public class PredictionRequestDto
{
    public int Age { get; set; }
    public string Gender { get; set; } = null!;
    public string Polyuria { get; set; } = null!;
    public string Polydipsia { get; set; } = null!;
    public string SuddenWeightLoss { get; set; } = null!;
    public string Weakness { get; set; } = null!;
    public string Polyphagia { get; set; } = null!;
    public string GenitalThrush { get; set; } = null!;
    public string VisualBlurring { get; set; } = null!;
    public string Itching { get; set; } = null!;
    public string Irritability { get; set; } = null!;
    public string DelayedHealing { get; set; } = null!;
    public string PartialParesis { get; set; } = null!;
    public string MuscleStiffness { get; set; } = null!;
    public string Alopecia { get; set; } = null!;
    public string Obesity { get; set; } = null!;

    // Hangi chat oturumuna bağlı
    public int ChatSessionId { get; set; }
}
