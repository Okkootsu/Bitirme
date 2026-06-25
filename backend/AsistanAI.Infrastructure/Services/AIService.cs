using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.DTOs.Prediction;
using AsistanAI.Core.Interfaces.AI;
using AsistanAI.Core.Interfaces.Prediction;
using System.Collections.Generic;
using Microsoft.Extensions.Configuration;

namespace AsistanAI.Infrastructure.Services;

public class AIService : IAIService
{
    private readonly HttpClient _httpClient;
    private readonly IPredictionService _predictionService;
    private readonly string _apiKey;
    private readonly string _mlServiceUrl;

    private const string GeminiModel = "gemini-2.5-flash";
    private const string GeminiBaseUrl = "https://generativelanguage.googleapis.com/v1beta/models";

    // ── Sistem Prompt'u ───────────────────────────────────────────────
    private const string SystemPrompt =
        "Sen 'Asistan.ai' adlı bir yapay zeka destekli diyabet sağlık asistanısın. " +
        "Görevin; kullanıcılara diyabet hastalığı, belirtileri, risk faktörleri, beslenme, " +
        "egzersiz ve genel yaşam tarzı değişiklikleri konularında bilimsel, güvenilir ve " +
        "anlaşılır bilgiler sunmaktır.\n\n" +

        "YANIT FORMATI VE UZUNLUĞU:\n" +
        "- KISA ve ÖZ yanıtlar ver. Bir sohbet asistanı gibi davran, ansiklopedi gibi değil.\n" +
        "- Her yanıt en fazla 4-6 paragraf olsun. Kullanıcı daha fazla detay isterse o zaman derinleştir.\n" +
        "- Önemli bilgileri **kalın** yaz.\n" +
        "- Listeleme gerektiğinde madde işaretleri kullan.\n" +
        "- Her cümleyi yeni satırda yazmak yerine doğal paragraflar oluştur.\n" +
        "- Yanıtlarını Markdown formatında yaz (başlıklar için ##, kalın için **, liste için - kullan).\n" +
        "- Samimi ve destekleyici bir dil kullan, akademik makale gibi yazma.\n\n" +

        "RİSK DEĞERLENDİRME KURALLARI:\n" +
        "- Kullanıcı diyabet riski hakkında bilgi istediğinde veya sağlık bilgilerini paylaştığında, " +
        "yaşını ve cinsiyetini de belirtmişse 'assess_diabetes_risk' fonksiyonunu çağır.\n" +
        "- Kullanıcı sağlık bilgisi belirtti ama yaş veya cinsiyet eksikse, önce bunları kibarca sor. " +
        "Fonksiyonu yaş ve cinsiyet bilgisi olmadan ÇAĞIRMA.\n" +
        "- Kullanıcıya tansiyon, kolesterol, BMI, sigara, fiziksel aktivite, genel sağlık durumu gibi " +
        "risk faktörlerini sor. Varsa kan şekeri ve HbA1c değerlerini de iste.\n" +
        "- Kullanıcının bahsetmediği alanları boş bırak (null).\n" +
        "- Sohbet geçmişinde daha önce belirtilen yaş, cinsiyet veya sağlık bilgilerini de dikkate al.\n\n" +

        "RİSK DEĞERLENDİRME SONRASI:\n" +
        "- Risk skorunu kullanıcıya yüzde olarak bildir.\n" +
        "- Sonucu kısaca yorumla: en önemli 2-3 risk faktörünü vurgula.\n" +
        "- Kısa ve uygulanabilir öneriler sun.\n" +
        "- Kullanıcıyı mutlaka doktor kontrolüne yönlendir.\n" +
        "- Sohbet geçmişinde daha önce yapılmış bir diyabet risk değerlendirmesi varsa " +
        "(risk kategorisi, olasılık, katman skorları içeren mesaj), kullanıcı bu skor hakkında " +
        "soru sorduğunda o değerlendirmeyi referans alarak yorum yap. " +
        "'Skor sunmadım' veya 'geçmişte değerlendirme yok' gibi yanıtlar VERME — " +
        "geçmişteki değerlendirme senin tarafından yapılmış kabul et ve yorumla.\n\n" +

        "GENEL KURALLAR:\n" +
        "1. Yalnızca Türkçe yanıt ver.\n" +
        "2. Kesinlikle tıbbi tanı koyma; sonuçların farkındalık amaçlı olduğunu belirt.\n" +
        "3. Diyabetle ilgisi olmayan konularda kibarca konuyu diyabete yönlendir.\n" +
        "4. Tüm bilgilerin profesyonel tıbbi tavsiye yerine geçmediğini hatırlat.";

    // ── Function Tool Tanımı (Gemini formatı) ─────────────────────────
    private static JsonObject GetToolDefinition() => new()
    {
        ["functionDeclarations"] = new JsonArray
        {
            new JsonObject
            {
                ["name"] = "assess_diabetes_risk",
                ["description"] =
                    "Kullanıcının belirttiği sağlık bilgilerine ve demografik verilere göre " +
                    "makine öğrenmesi modeli ile diyabet risk değerlendirmesi yapar. " +
                    "Kullanıcı yaşını, cinsiyetini ve en az bir sağlık bilgisini belirttiğinde bu aracı kullan.",
                ["parameters"] = new JsonObject
                {
                    ["type"] = "OBJECT",
                    ["properties"] = new JsonObject
                    {
                        ["age"] = Param("INTEGER", "Kullanıcının yaşı"),
                        ["gender"] = ParamEnum("STRING", "Cinsiyet", "Male", "Female"),
                        ["bmi"] = Param("NUMBER", "Vücut kitle indeksi (BMI)"),
                        ["high_bp"] = ParamEnum("STRING", "Yüksek tansiyon var mı", "Yes", "No"),
                        ["high_chol"] = ParamEnum("STRING", "Yüksek kolesterol var mı", "Yes", "No"),
                        ["physical_activity"] = ParamEnum("STRING", "Düzenli fiziksel aktivite yapıyor mu", "Yes", "No"),
                        ["gen_health"] = Param("INTEGER", "Genel sağlık durumu (1=Mükemmel, 5=Kötü)"),
                        ["diff_walking"] = ParamEnum("STRING", "Yürüme zorluğu var mı", "Yes", "No"),
                        ["smoker"] = ParamEnum("STRING", "Sigara kullanıyor mu", "Yes", "No"),
                        ["heart_disease"] = ParamEnum("STRING", "Kalp hastalığı öyküsü var mı", "Yes", "No"),
                        ["fruits_daily"] = ParamEnum("STRING", "Her gün meyve tüketiyor mu", "Yes", "No"),
                        ["veggies_daily"] = ParamEnum("STRING", "Her gün sebze tüketiyor mu", "Yes", "No"),
                        ["heavy_alcohol"] = ParamEnum("STRING", "Ağır alkol kullanımı var mı", "Yes", "No"),
                        ["blood_glucose"] = Param("NUMBER", "Açlık kan şekeri (mg/dL)"),
                        ["hba1c"] = Param("NUMBER", "HbA1c yüzdesi"),
                        ["height_cm"] = Param("NUMBER", "Boy (cm)"),
                        ["weight_kg"] = Param("NUMBER", "Kilo (kg)")
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

        _mlServiceUrl = configuration["MLServiceUrl"] ?? "http://ml:8000";
    }

    // ── Ana Metod ─────────────────────────────────────────────────────
    public async Task<AiResponseResult> GenerateResponseAsync(string userMessage, List<ChatMessageDto> history)
    {
        // 1. RAG: Kullanıcı mesajına göre bilgi tabanından ilgili bölümleri getir
        var (ragContext, ragSources) = await RetrieveRAGContextAsync(userMessage);

        // 2. Mesaj geçmişini Gemini formatında oluştur
        var contents = new JsonArray();

        var recentHistory = history.TakeLast(10).ToList();
        foreach (var msg in recentHistory)
        {
            var msgText = StripPredictionMetadata(msg.Content);
            contents.Add(new JsonObject
            {
                ["role"] = msg.IsUserMessage ? "user" : "model",
                ["parts"] = new JsonArray { new JsonObject { ["text"] = msgText } }
            });
        }

        contents.Add(new JsonObject
        {
            ["role"] = "user",
            ["parts"] = new JsonArray { new JsonObject { ["text"] = userMessage } }
        });

        // 3. Gemini'ye gönder (RAG context + function tool ile)
        var responseJson = await CallGeminiAsync(contents, ragContext);

        // 4. Function call var mı kontrol et
        var candidate = responseJson?["candidates"]?[0]?["content"];
        var firstPart = candidate?["parts"]?[0];

        if (firstPart?["functionCall"] != null)
        {
            var text = await HandleFunctionCallAsync(contents, firstPart["functionCall"]!, ragContext);
            return new AiResponseResult(text, ragSources);
        }

        // 5. Normal metin yanıtı
        var content = firstPart?["text"]?.GetValue<string>() ?? "Yanıt üretilemedi.";
        return new AiResponseResult(content, ragSources);
    }

    // ── Streaming Ana Metod ──────────────────────────────────────────
    public async Task<(IAsyncEnumerable<string> TextStream, AiStreamContext Context)?> StreamResponseAsync(
        string userMessage, List<ChatMessageDto> history)
    {
        var (ragContext, ragSources) = await RetrieveRAGContextAsync(userMessage);

        var contents = new JsonArray();
        var recentHistory = history.TakeLast(10).ToList();
        foreach (var msg in recentHistory)
        {
            var msgText = StripPredictionMetadata(msg.Content);
            contents.Add(new JsonObject
            {
                ["role"] = msg.IsUserMessage ? "user" : "model",
                ["parts"] = new JsonArray { new JsonObject { ["text"] = msgText } }
            });
        }

        contents.Add(new JsonObject
        {
            ["role"] = "user",
            ["parts"] = new JsonArray { new JsonObject { ["text"] = userMessage } }
        });

        var context = new AiStreamContext(ragSources);
        var stream = StreamGeminiAsync(contents, ragContext);
        return (stream, context);
    }

    // ── Gemini Streaming API ──────────────────────────────────────────
    private async IAsyncEnumerable<string> StreamGeminiAsync(JsonArray contents, string ragContext = "")
    {
        var fullSystemPrompt = BuildFullSystemPrompt(ragContext);

        var requestBody = new JsonObject
        {
            ["contents"] = JsonNode.Parse(contents.ToJsonString()),
            ["systemInstruction"] = new JsonObject
            {
                ["parts"] = new JsonArray { new JsonObject { ["text"] = fullSystemPrompt } }
            },
            ["generationConfig"] = new JsonObject
            {
                ["maxOutputTokens"] = 8192,
                ["thinkingConfig"] = new JsonObject
                {
                    ["thinkingBudget"] = 0
                }
            }
        };

        var url = $"{GeminiBaseUrl}/{GeminiModel}:streamGenerateContent?alt=sse&key={_apiKey}";
        var jsonOptions = new JsonSerializerOptions { DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull };

        var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = JsonContent.Create(requestBody, options: jsonOptions)
        };

        var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);

        if (!response.IsSuccessStatusCode)
        {
            var errorBody = await response.Content.ReadAsStringAsync();
            throw new HttpRequestException(
                $"Yapay zeka servisine ulaşılamadı (HTTP {(int)response.StatusCode}): {errorBody}");
        }

        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);

        while (!reader.EndOfStream)
        {
            var line = await reader.ReadLineAsync();
            if (line == null || !line.StartsWith("data: ")) continue;

            var jsonStr = line["data: ".Length..];
            if (string.IsNullOrWhiteSpace(jsonStr)) continue;

            JsonNode? chunk;
            try { chunk = JsonNode.Parse(jsonStr); }
            catch { continue; }

            var text = chunk?["candidates"]?[0]?["content"]?["parts"]?[0]?["text"]?.GetValue<string>();
            if (!string.IsNullOrEmpty(text))
                yield return text;
        }
    }

    // ── Sistem Prompt Oluşturucu ──────────────────────────────────────
    private string BuildFullSystemPrompt(string ragContext)
    {
        var fullSystemPrompt = SystemPrompt;
        if (!string.IsNullOrEmpty(ragContext))
        {
            fullSystemPrompt += "\n\n" +
                "BİLGİ TABANI REFERANSLARI:\n" +
                "Aşağıda kullanıcının sorusuyla doğrudan ilgili bilgi tabanından alınmış referans bilgiler var.\n\n" +
                "KULLANIM KURALLARI:\n" +
                "1. Yanıtını ÖNCELİKLE bu referans bilgilere dayandır. Referanslardaki spesifik verileri " +
                "(eşik değerler, yüzdeler, kılavuz önerileri, Türkiye'ye özgü bilgiler) yanıtına dahil et.\n" +
                "2. Genel bilgi yerine referanslardaki SOMUT bilgiyi kullan. Örneğin 'kan şekeri yüksek olabilir' yerine " +
                "'ADA/TEMD kılavuzuna göre açlık kan şekeri ≥126 mg/dL diyabet tanı eşiğidir' gibi spesifik değerler ver.\n" +
                "3. Bilgiyi hangi kaynaktan aldığını parantez içinde belirt, örn: (Kaynak: TEMD Diyabet Kılavuzu 2024).\n" +
                "4. Referanslarda BULUNMAYAN bir bilgi veriyorsan, bunu kendi genel bilgin olarak belirt.\n" +
                "5. Tüm referansları listeleme, sadece soruyla en ilgili kısımları sohbet havasında aktar.\n\n" +
                ragContext;
        }
        return fullSystemPrompt;
    }

    // ── Geçmiş mesajlardan frontend metadata'sını temizle ──────────────
    private static string StripPredictionMetadata(string content) =>
        Regex.Replace(content, @"\s*<!--\s*PREDICTION_DATA:.*?-->", "", RegexOptions.Singleline).TrimEnd();

    // ── Prediction Request Oluşturucu ─────────────────────────────────
    private static PredictionRequestDto BuildPredictionRequest(JsonNode args) => new()
    {
        Age = GetIntArg(args, "age", 40),
        Gender = GetStringArg(args, "gender", "Male"),
        Bmi = GetNullableDoubleArg(args, "bmi"),
        HighBp = GetNullableBoolArg(args, "high_bp"),
        HighChol = GetNullableBoolArg(args, "high_chol"),
        PhysicalActivity = GetNullableBoolArg(args, "physical_activity"),
        GenHealth = GetNullableIntArg(args, "gen_health"),
        DiffWalking = GetNullableBoolArg(args, "diff_walking"),
        Smoker = GetNullableBoolArg(args, "smoker"),
        HeartDisease = GetNullableBoolArg(args, "heart_disease"),
        FruitsDaily = GetNullableBoolArg(args, "fruits_daily"),
        VeggiesDaily = GetNullableBoolArg(args, "veggies_daily"),
        HeavyAlcohol = GetNullableBoolArg(args, "heavy_alcohol"),
        BloodGlucose = GetNullableDoubleArg(args, "blood_glucose"),
        Hba1c = GetNullableDoubleArg(args, "hba1c"),
        HeightCm = GetNullableDoubleArg(args, "height_cm"),
        WeightKg = GetNullableDoubleArg(args, "weight_kg"),
        ChatSessionId = 0
    };

    // ── RAG Retrieval ─────────────────────────────────────────────────
    private async Task<(string Context, List<string> Sources)> RetrieveRAGContextAsync(string query)
    {
        try
        {
            var ragRequest = new { query, top_k = 5 };
            var response = await _httpClient.PostAsJsonAsync($"{_mlServiceUrl}/rag/retrieve", ragRequest);

            if (!response.IsSuccessStatusCode)
                return ("", new List<string>());

            var chunks = await response.Content.ReadFromJsonAsync<JsonArray>();
            if (chunks == null || chunks.Count == 0)
                return ("", new List<string>());

            var contextParts = new List<string>();
            var sources = new HashSet<string>();
            foreach (var chunk in chunks)
            {
                var text = chunk?["text"]?.GetValue<string>();
                var source = chunk?["source"]?.GetValue<string>();
                if (!string.IsNullOrEmpty(text))
                {
                    contextParts.Add($"[Kaynak: {source}]\n{text}");
                    if (!string.IsNullOrEmpty(source))
                        sources.Add(source);
                }
            }

            return (string.Join("\n\n---\n\n", contextParts), sources.ToList());
        }
        catch
        {
            return ("", new List<string>());
        }
    }

    // ── Function Call İşleme ──────────────────────────────────────────
    private async Task<string> HandleFunctionCallAsync(JsonArray contents, JsonNode functionCall, string ragContext)
    {
        var functionName = functionCall["name"]!.GetValue<string>();
        var args = functionCall["args"]!;

        if (functionName != "assess_diabetes_risk")
            return "Bilinmeyen fonksiyon çağrısı.";

        // a) Argümanlardan PredictionRequestDto oluştur
        var predictionRequest = BuildPredictionRequest(args);

        // b) ML API'ye gönder
        var predictionResult = await _predictionService.PredictAsync(predictionRequest);

        JsonObject functionResultData;
        if (predictionResult.IsSuccess)
        {
            var data = predictionResult.Data!;
            functionResultData = new JsonObject
            {
                ["risk_category"] = data.RiskCategory,
                ["risk_probability"] = data.RiskProbability,
                ["risk_percentage"] = $"%{(data.RiskProbability * 100):F0}",
                ["confidence_level"] = data.ConfidenceLevel,
                ["contributing_factors"] = new JsonArray(
                    data.ContributingFactors.Select(f => (JsonNode)JsonValue.Create(f)!).ToArray()),
                ["formatted_message"] = data.FormattedMessage
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

        // d) Gemini'ye tekrar gönder → risk skoru + RAG context ile kişiselleştirilmiş yanıt
        var finalResponse = await CallGeminiAsync(contents, ragContext);
        var finalText = finalResponse?["candidates"]?[0]?["content"]?["parts"]?[0]?["text"]?.GetValue<string>();

        return finalText ?? "Risk değerlendirmesi tamamlandı ancak yanıt üretilemedi.";
    }

    // ── Gemini API Çağrısı ────────────────────────────────────────────
    private async Task<JsonNode?> CallGeminiAsync(JsonArray contents, string ragContext = "")
    {
        var fullSystemPrompt = BuildFullSystemPrompt(ragContext);

        var requestBody = new JsonObject
        {
            ["contents"] = JsonNode.Parse(contents.ToJsonString()),
            ["systemInstruction"] = new JsonObject
            {
                ["parts"] = new JsonArray { new JsonObject { ["text"] = fullSystemPrompt } }
            },
            ["tools"] = new JsonArray { GetToolDefinition() },
            ["generationConfig"] = new JsonObject
            {
                ["maxOutputTokens"] = 8192
            }
        };

        var url = $"{GeminiBaseUrl}/{GeminiModel}:generateContent?key={_apiKey}";
        var jsonOptions = new JsonSerializerOptions { DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull };

        // Retry with exponential backoff for 429/503
        int[] delaysMs = [3000, 6000, 12000, 20000];
        for (int attempt = 0; attempt <= delaysMs.Length; attempt++)
        {
            var response = await _httpClient.PostAsJsonAsync(url, requestBody, jsonOptions);

            if (response.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable && attempt < delaysMs.Length)
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

    private static bool? GetNullableBoolArg(JsonNode args, string key)
    {
        var val = args[key];
        if (val == null) return null;
        var str = val.GetValue<string>();
        return str.Equals("Yes", StringComparison.OrdinalIgnoreCase);
    }

    private static double? GetNullableDoubleArg(JsonNode args, string key)
    {
        var val = args[key];
        if (val == null) return null;
        try { return val.GetValue<double>(); }
        catch { return null; }
    }

    private static int? GetNullableIntArg(JsonNode args, string key)
    {
        var val = args[key];
        if (val == null) return null;
        try { return val.GetValue<int>(); }
        catch
        {
            try { return (int)val.GetValue<double>(); }
            catch { return null; }
        }
    }

}
