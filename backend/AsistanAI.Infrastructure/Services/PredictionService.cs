using System.Net.Http.Json;
using System.Text.Json;
using AsistanAI.Core.DTOs.Prediction;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Interfaces.Prediction;
using AsistanAI.Core.Wrappers;
using Microsoft.Extensions.Configuration;

namespace AsistanAI.Infrastructure.Services;

public class PredictionService : IPredictionService
{
    private readonly HttpClient _httpClient;

    public PredictionService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _httpClient.BaseAddress = new Uri(configuration["MLServiceUrl"] ?? "http://ml:8000");
    }

    public async Task<ServiceResponse<PredictionResponseDto>> PredictAsync(PredictionRequestDto request)
    {
        // FastAPI snake_case payload (hybrid model schema)
        var payload = new
        {
            age = request.Age,
            gender = request.Gender,
            bmi = request.Bmi,
            high_bp = request.HighBp,
            high_chol = request.HighChol,
            physical_activity = request.PhysicalActivity,
            gen_health = request.GenHealth,
            diff_walking = request.DiffWalking,
            smoker = request.Smoker,
            heart_disease = request.HeartDisease,
            fruits_daily = request.FruitsDaily,
            veggies_daily = request.VeggiesDaily,
            heavy_alcohol = request.HeavyAlcohol,
            blood_glucose = request.BloodGlucose,
            hba1c = request.Hba1c,
            height_cm = request.HeightCm,
            weight_kg = request.WeightKg,
            // Symptoms
            polyuria = request.Polyuria,
            polydipsia = request.Polydipsia,
            unexplained_weight_loss = request.UnexplainedWeightLoss,
            fatigue = request.Fatigue,
            blurred_vision = request.BlurredVision,
            slow_healing = request.SlowHealing,
            frequent_infections = request.FrequentInfections,
            tingling_numbness = request.TinglingNumbness
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("/predict", payload);

            if (!response.IsSuccessStatusCode)
                return ServiceResponse<PredictionResponseDto>.Fail(
                    "ML servisi tahmin yapamadı.", ServiceResultType.Failure);

            var json = await response.Content.ReadFromJsonAsync<JsonElement>();

            var riskProbability = json.GetProperty("risk_probability").GetDouble();
            var riskCategory = json.GetProperty("risk_category").GetString() ?? "Medium";
            var confidenceLevel = json.GetProperty("confidence_level").GetString() ?? "low";

            // Layer scores
            var mlScore = json.GetProperty("ml_score").GetDouble();
            var symptomScore = json.GetProperty("symptom_score").GetDouble();
            var clinicalScore = json.GetProperty("clinical_score").GetDouble();

            var contributingFactors = new List<string>();
            if (json.TryGetProperty("contributing_factors", out var factorsElem))
            {
                foreach (var factor in factorsElem.EnumerateArray())
                {
                    contributingFactors.Add(factor.GetString() ?? "");
                }
            }

            var activeSymptoms = new List<string>();
            if (json.TryGetProperty("active_symptoms", out var symptomsElem))
            {
                foreach (var sym in symptomsElem.EnumerateArray())
                {
                    activeSymptoms.Add(sym.GetString() ?? "");
                }
            }

            var riskFactorCards = new List<RiskFactorCardDto>();
            if (json.TryGetProperty("risk_factor_cards", out var cardsElem))
            {
                foreach (var card in cardsElem.EnumerateArray())
                {
                    riskFactorCards.Add(new RiskFactorCardDto
                    {
                        Name = card.GetProperty("name").GetString() ?? "",
                        Value = card.GetProperty("value").GetString() ?? "",
                        Status = card.GetProperty("status").GetString() ?? "neutral",
                        Detail = card.GetProperty("detail").GetString() ?? ""
                    });
                }
            }

            Dictionary<string, double>? shapValues = null;
            if (json.TryGetProperty("shap_values", out var shapElem) && shapElem.ValueKind == JsonValueKind.Object)
            {
                shapValues = new Dictionary<string, double>();
                foreach (var prop in shapElem.EnumerateObject())
                {
                    shapValues[prop.Name] = prop.Value.GetDouble();
                }
            }

            var percentage = $"%{(riskProbability * 100):F0}";
            var categoryTr = riskCategory switch
            {
                "Low" => "Düşük Risk",
                "Medium" => "Orta Risk",
                "High" => "Yüksek Risk",
                _ => "Bilinmiyor"
            };
            var emoji = riskCategory switch
            {
                "Low" => "✅",
                "Medium" => "⚠️",
                "High" => "🔴",
                _ => "❓"
            };
            var confidenceTr = confidenceLevel switch
            {
                "very_high" => "Çok Yüksek (klinik veri + semptom mevcut)",
                "high" => "Yüksek (klinik veri mevcut)",
                "moderate" => "Orta (semptom verisi mevcut)",
                "low" => "Düşük (yalnızca risk faktörleri)",
                _ => "Bilinmiyor"
            };

            var factorsText = contributingFactors.Count > 0
                ? "\n\n**Katkı yapan faktörler:**\n" + string.Join("\n", contributingFactors.Select(f => $"• {f}"))
                : "";

            var layerText =
                $"\n\n**Katman Skorları:**\n" +
                $"• ML Model: %{(mlScore * 100):F0}\n" +
                $"• Semptom: %{(symptomScore * 100):F0}\n" +
                $"• Klinik: %{(clinicalScore * 100):F0}";

            var formattedMessage =
                $"{emoji} **Diyabet Risk Değerlendirmesi (Hybrid)**\n\n" +
                $"Risk Kategorisi: **{categoryTr}**\n" +
                $"Olasılık: **{percentage}**\n" +
                $"Güven Düzeyi: {confidenceTr}" +
                layerText +
                factorsText;

            var dto = new PredictionResponseDto
            {
                RiskProbability = riskProbability,
                RiskCategory = riskCategory,
                ConfidenceLevel = confidenceLevel,
                ContributingFactors = contributingFactors,
                FormattedMessage = formattedMessage,
                ShapValues = shapValues,
                MlScore = mlScore,
                SymptomScore = symptomScore,
                ClinicalScore = clinicalScore,
                ActiveSymptoms = activeSymptoms,
                RiskFactorCards = riskFactorCards
            };

            return ServiceResponse<PredictionResponseDto>.Success(dto);
        }
        catch (Exception ex)
        {
            return ServiceResponse<PredictionResponseDto>.Fail(
                $"ML servisine bağlanılamadı: {ex.Message}", ServiceResultType.Failure);
        }
    }
}
