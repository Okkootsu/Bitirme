using System.Collections.Generic;

namespace AsistanAI.Core.DTOs.Prediction;

public class RiskFactorCardDto
{
    public string Name { get; set; } = null!;
    public string Value { get; set; } = null!;
    public string Status { get; set; } = null!; // "risk", "protective", "neutral"
    public string Detail { get; set; } = null!;
}

public class PredictionResponseDto
{
    public double RiskProbability { get; set; }
    public string RiskCategory { get; set; } = null!;
    public string ConfidenceLevel { get; set; } = null!;
    public List<string> ContributingFactors { get; set; } = new();
    public string FormattedMessage { get; set; } = null!;
    public Dictionary<string, double>? ShapValues { get; set; }

    // Hybrid model layer scores
    public double MlScore { get; set; }
    public double SymptomScore { get; set; }
    public double ClinicalScore { get; set; }
    public List<string> ActiveSymptoms { get; set; } = new();
    public List<RiskFactorCardDto> RiskFactorCards { get; set; } = new();
}
