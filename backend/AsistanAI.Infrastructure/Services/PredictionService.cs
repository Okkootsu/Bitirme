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
        // FastAPI snake_case alanlarına uygun payload
        var payload = new
        {
            age = request.Age,
            gender = request.Gender,
            polyuria = request.Polyuria,
            polydipsia = request.Polydipsia,
            sudden_weight_loss = request.SuddenWeightLoss,
            weakness = request.Weakness,
            polyphagia = request.Polyphagia,
            genital_thrush = request.GenitalThrush,
            visual_blurring = request.VisualBlurring,
            itching = request.Itching,
            irritability = request.Irritability,
            delayed_healing = request.DelayedHealing,
            partial_paresis = request.PartialParesis,
            muscle_stiffness = request.MuscleStiffness,
            alopecia = request.Alopecia,
            obesity = request.Obesity
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("/predict", payload);

            if (!response.IsSuccessStatusCode)
                return ServiceResponse<PredictionResponseDto>.Fail(
                    "ML servisi tahmin yapamadı.", ServiceResultType.Failure);

            var json = await response.Content.ReadFromJsonAsync<JsonElement>();

            var prediction = json.GetProperty("prediction").GetString() ?? "Bilinmiyor";
            double? probability = null;

            if (json.TryGetProperty("risk_probability", out var probElem) &&
                probElem.ValueKind != JsonValueKind.Null)
            {
                probability = probElem.GetDouble();
            }

            var percentage = probability.HasValue
                ? $"%{(probability.Value * 100):F0}"
                : "";

            var isPositive = prediction.Equals("Positive", StringComparison.OrdinalIgnoreCase);
            var riskLabel = isPositive ? "Yüksek Risk" : "Düşük Risk";
            var emoji = isPositive ? "⚠️" : "✅";

            var formattedMessage =
                $"{emoji} **Diyabet Risk Değerlendirmesi**\n\n" +
                $"Sonuç: **{riskLabel}** ({prediction})\n" +
                (probability.HasValue ? $"Olasılık: **{percentage}**\n" : "") +
                "\n*Bu sonuç bir yapay zeka tahminidir. Kesin tanı için doktorunuza başvurun.*";

            var dto = new PredictionResponseDto
            {
                Prediction = prediction,
                RiskProbability = probability,
                FormattedMessage = formattedMessage
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
