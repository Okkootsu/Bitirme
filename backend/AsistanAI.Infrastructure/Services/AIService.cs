using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Nodes;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.DTOs.Prediction;
using AsistanAI.Core.Interfaces.AI;
using AsistanAI.Core.Interfaces.Prediction;
using Microsoft.Extensions.Configuration;

namespace AsistanAI.Infrastructure.Services;

public class AIService : IAIService
{
    private readonly HttpClient _httpClient;
    private readonly IPredictionService _predictionService;
    private readonly string _apiKey;

    private const string GeminiModel = "gemini-2.5-flash";
    private const string GeminiBaseUrl = "https://generativelanguage.googleapis.com/v1beta/models";

    // ── Sistem Prompt'u ───────────────────────────────────────────────
    private const string SystemPrompt =
        "Sen 'Asistan.ai' adlı bir yapay zeka destekli diyabet sağlık asistanısın. " +
        "Görevin; kullanıcılara diyabet hastalığı, belirtileri, risk faktörleri, beslenme, " +
        "egzersiz ve genel yaşam tarzı değişiklikleri konularında bilimsel, güvenilir ve " +
        "anlaşılır bilgiler sunmaktır.\n\n" +

        "SEMPTOM ANALİZİ KURALLARI:\n" +
        "- Kullanıcı diyabetle ilişkili semptomlardan bahsettiğinde, yaşını ve cinsiyetini de " +
        "belirtmişse 'assess_diabetes_risk' fonksiyonunu çağır.\n" +
        "- Kullanıcı semptom belirtti ama yaş veya cinsiyet eksikse, önce bunları kibarca sor. " +
        "Fonksiyonu yaş ve cinsiyet bilgisi olmadan ÇAĞIRMA.\n" +
        "- Kullanıcının bahsetmediği semptomları 'No' olarak işaretle.\n" +
        "- Sohbet geçmişinde daha önce belirtilen yaş, cinsiyet veya semptomları da dikkate al.\n\n" +

        "RİSK DEĞERLENDİRME SONRASI:\n" +
        "- Risk skorunu kullanıcıya yüzde olarak bildir.\n" +
        "- Sonucu yorumla: hangi semptomların risk artışına katkıda bulunduğunu açıkla.\n" +
        "- Beslenme, egzersiz ve yaşam tarzı önerileri sun.\n" +
        "- Kullanıcıyı mutlaka doktor kontrolüne yönlendir.\n\n" +

        "GENEL KURALLAR:\n" +
        "1. Yalnızca Türkçe yanıt ver.\n" +
        "2. Kesinlikle tıbbi tanı koyma; sonuçların farkındalık amaçlı olduğunu belirt.\n" +
        "3. Yanıtların kısa, net ve kişiselleştirilmiş olsun.\n" +
        "4. Diyabetle ilgisi olmayan konularda kibarca konuyu diyabete yönlendir.\n" +
        "5. Tüm bilgilerin profesyonel tıbbi tavsiye yerine geçmediğini hatırlat.";

    // ── Function Tool Tanımı (Gemini formatı) ─────────────────────────
    private static JsonObject GetToolDefinition() => new()
    {
        ["functionDeclarations"] = new JsonArray
        {
            new JsonObject
            {
                ["name"] = "assess_diabetes_risk",
                ["description"] =
                    "Kullanıcının belirttiği semptomlara ve demografik bilgilere göre " +
                    "makine öğrenmesi modeli ile diyabet risk değerlendirmesi yapar. " +
                    "Kullanıcı yaşını, cinsiyetini ve en az bir semptomunu belirttiğinde bu aracı kullan.",
                ["parameters"] = new JsonObject
                {
                    ["type"] = "OBJECT",
                    ["properties"] = new JsonObject
                    {
                        ["age"] = Param("INTEGER", "Kullanıcının yaşı"),
                        ["gender"] = ParamEnum("STRING", "Cinsiyet", "Male", "Female"),
                        ["polyuria"] = ParamEnum("STRING", "Sık idrara çıkma", "Yes", "No"),
                        ["polydipsia"] = ParamEnum("STRING", "Aşırı susama / çok su içme", "Yes", "No"),
                        ["sudden_weight_loss"] = ParamEnum("STRING", "Ani kilo kaybı", "Yes", "No"),
                        ["weakness"] = ParamEnum("STRING", "Halsizlik / güçsüzlük / yorgunluk", "Yes", "No"),
                        ["polyphagia"] = ParamEnum("STRING", "Aşırı açlık", "Yes", "No"),
                        ["genital_thrush"] = ParamEnum("STRING", "Genital mantar enfeksiyonu", "Yes", "No"),
                        ["visual_blurring"] = ParamEnum("STRING", "Bulanık görme", "Yes", "No"),
                        ["itching"] = ParamEnum("STRING", "Kaşıntı", "Yes", "No"),
                        ["irritability"] = ParamEnum("STRING", "Sinirlilik / huzursuzluk", "Yes", "No"),
                        ["delayed_healing"] = ParamEnum("STRING", "Yaraların geç iyileşmesi", "Yes", "No"),
                        ["partial_paresis"] = ParamEnum("STRING", "Kısmi felç / kas güçsüzlüğü", "Yes", "No"),
                        ["muscle_stiffness"] = ParamEnum("STRING", "Kas sertliği", "Yes", "No"),
                        ["alopecia"] = ParamEnum("STRING", "Saç dökülmesi", "Yes", "No"),
                        ["obesity"] = ParamEnum("STRING", "Obezite", "Yes", "No")
                    },
                    ["required"] = new JsonArray { "age", "gender" }
                }
            }
        }
    };

    private static JsonObject Param(string type, string desc) =>
        new() { ["type"] = type, ["description"] = desc };

    private static JsonObject ParamEnum(string type, string desc, params string[] values)
    {
        var obj = new JsonObject { ["type"] = type, ["description"] = desc };
        var arr = new JsonArray();
        foreach (var v in values) arr.Add(v);
        obj["enum"] = arr;
        return obj;
    }

    // ── Constructor ───────────────────────────────────────────────────
    public AIService(IConfiguration configuration, IPredictionService predictionService, IHttpClientFactory httpClientFactory)
    {
        _predictionService = predictionService;
        _httpClient = httpClientFactory.CreateClient();

        _apiKey = configuration["Gemini:ApiKey"]
            ?? throw new InvalidOperationException("Gemini:ApiKey yapılandırma değeri eksik.");
    }

    // ── Ana Metod ─────────────────────────────────────────────────────
    public async Task<string> GenerateResponseAsync(string userMessage, List<ChatMessageDto> history)
    {
        // 1. Mesaj geçmişini Gemini formatında oluştur
        var contents = new JsonArray();

        var recentHistory = history.TakeLast(10).ToList();
        foreach (var msg in recentHistory)
        {
            contents.Add(new JsonObject
            {
                ["role"] = msg.IsUserMessage ? "user" : "model",
                ["parts"] = new JsonArray { new JsonObject { ["text"] = msg.Content } }
            });
        }

        contents.Add(new JsonObject
        {
            ["role"] = "user",
            ["parts"] = new JsonArray { new JsonObject { ["text"] = userMessage } }
        });

        // 2. Gemini'ye gönder (function tool ile)
        var responseJson = await CallGeminiAsync(contents);

        // 3. Function call var mı kontrol et
        var candidate = responseJson?["candidates"]?[0]?["content"];
        var firstPart = candidate?["parts"]?[0];

        if (firstPart?["functionCall"] != null)
        {
            return await HandleFunctionCallAsync(contents, firstPart["functionCall"]!);
        }

        // 4. Normal metin yanıtı
        return firstPart?["text"]?.GetValue<string>() ?? "Yanıt üretilemedi.";
    }

    // ── Function Call İşleme ──────────────────────────────────────────
    private async Task<string> HandleFunctionCallAsync(JsonArray contents, JsonNode functionCall)
    {
        var functionName = functionCall["name"]!.GetValue<string>();
        var args = functionCall["args"]!;

        if (functionName != "assess_diabetes_risk")
            return "Bilinmeyen fonksiyon çağrısı.";

        // a) Argümanlardan PredictionRequestDto oluştur
        var predictionRequest = new PredictionRequestDto
        {
            Age = GetIntArg(args, "age", 40),
            Gender = GetStringArg(args, "gender", "Male"),
            Polyuria = GetStringArg(args, "polyuria", "No"),
            Polydipsia = GetStringArg(args, "polydipsia", "No"),
            SuddenWeightLoss = GetStringArg(args, "sudden_weight_loss", "No"),
            Weakness = GetStringArg(args, "weakness", "No"),
            Polyphagia = GetStringArg(args, "polyphagia", "No"),
            GenitalThrush = GetStringArg(args, "genital_thrush", "No"),
            VisualBlurring = GetStringArg(args, "visual_blurring", "No"),
            Itching = GetStringArg(args, "itching", "No"),
            Irritability = GetStringArg(args, "irritability", "No"),
            DelayedHealing = GetStringArg(args, "delayed_healing", "No"),
            PartialParesis = GetStringArg(args, "partial_paresis", "No"),
            MuscleStiffness = GetStringArg(args, "muscle_stiffness", "No"),
            Alopecia = GetStringArg(args, "alopecia", "No"),
            Obesity = GetStringArg(args, "obesity", "No"),
            ChatSessionId = 0
        };

        // b) ML API'ye gönder
        var predictionResult = await _predictionService.PredictAsync(predictionRequest);

        JsonObject functionResultData;
        if (predictionResult.IsSuccess)
        {
            functionResultData = new JsonObject
            {
                ["prediction"] = predictionResult.Data!.Prediction,
                ["risk_probability"] = predictionResult.Data.RiskProbability,
                ["risk_percentage"] = predictionResult.Data.RiskProbability.HasValue
                    ? $"%{(predictionResult.Data.RiskProbability.Value * 100):F0}"
                    : "Hesaplanamadı"
            };
        }
        else
        {
            functionResultData = new JsonObject
            {
                ["error"] = "ML modeline şu anda ulaşılamıyor. Kullanıcıya genel bilgi ver."
            };
        }

        // c) Model'in function call mesajını ve sonucu geçmişe ekle
        contents.Add(new JsonObject
        {
            ["role"] = "model",
            ["parts"] = new JsonArray
            {
                new JsonObject
                {
                    ["functionCall"] = new JsonObject
                    {
                        ["name"] = functionName,
                        ["args"] = JsonNode.Parse(args.ToJsonString())
                    }
                }
            }
        });

        contents.Add(new JsonObject
        {
            ["role"] = "function",
            ["parts"] = new JsonArray
            {
                new JsonObject
                {
                    ["functionResponse"] = new JsonObject
                    {
                        ["name"] = functionName,
                        ["response"] = functionResultData
                    }
                }
            }
        });

        // d) Gemini'ye tekrar gönder → risk skoru ile kişiselleştirilmiş yanıt
        var finalResponse = await CallGeminiAsync(contents);
        var finalText = finalResponse?["candidates"]?[0]?["content"]?["parts"]?[0]?["text"]?.GetValue<string>();

        return finalText ?? "Risk değerlendirmesi tamamlandı ancak yanıt üretilemedi.";
    }

    // ── Gemini API Çağrısı ────────────────────────────────────────────
    private async Task<JsonNode?> CallGeminiAsync(JsonArray contents)
    {
        var requestBody = new JsonObject
        {
            ["contents"] = JsonNode.Parse(contents.ToJsonString()),
            ["systemInstruction"] = new JsonObject
            {
                ["parts"] = new JsonArray { new JsonObject { ["text"] = SystemPrompt } }
            },
            ["tools"] = new JsonArray { GetToolDefinition() },
            ["generationConfig"] = new JsonObject
            {
                ["thinkingConfig"] = new JsonObject
                {
                    ["thinkingBudget"] = 0
                }
            }
        };

        var url = $"{GeminiBaseUrl}/{GeminiModel}:generateContent?key={_apiKey}";
        var jsonOptions = new JsonSerializerOptions { DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull };

        // Retry with exponential backoff for 429/503
        int[] delaysMs = [3000, 6000, 12000, 20000];
        for (int attempt = 0; attempt <= delaysMs.Length; attempt++)
        {
            var response = await _httpClient.PostAsJsonAsync(url, requestBody, jsonOptions);

            if ((response.StatusCode == System.Net.HttpStatusCode.TooManyRequests ||
                 response.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable) && attempt < delaysMs.Length)
            {
                await Task.Delay(delaysMs[attempt]);
                continue;
            }

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Yapay zeka servisine ulaşılamadı (HTTP {(int)response.StatusCode}): {errorBody}");
            }

            return await response.Content.ReadFromJsonAsync<JsonNode>();
        }

        throw new HttpRequestException("Gemini API'ye ulaşılamıyor. Lütfen birkaç dakika bekleyip tekrar deneyin.");
    }

    // ── Yardımcılar ──────────────────────────────────────────────────
    private static string GetStringArg(JsonNode args, string key, string defaultValue)
    {
        var val = args[key];
        return val != null ? val.GetValue<string>() : defaultValue;
    }

    private static int GetIntArg(JsonNode args, string key, int defaultValue)
    {
        var val = args[key];
        if (val == null) return defaultValue;
        // Gemini bazen integer'ı double olarak döndürebilir
        try { return val.GetValue<int>(); }
        catch { return (int)val.GetValue<double>(); }
    }
}
