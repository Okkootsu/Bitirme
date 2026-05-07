namespace AsistanAI.Core.DTOs.Prediction;

public class PredictionResponseDto
{
    public string Prediction { get; set; } = null!;
    public double? RiskProbability { get; set; }
    public string FormattedMessage { get; set; } = null!;
}
