using System.Text.Json;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Interfaces.AI;
using AsistanAI.Core.Wrappers;
using AutoMapper;

namespace AsistanAI.Infrastructure.Services;

public class ChatMessageService : IChatMessageService
{
    private static readonly JsonSerializerOptions _jsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
    };

    private readonly IChatMessageRepository _messageRepo;
    private readonly IChatSessionRepository _sessionRepo;
    private readonly IAIService _aiService;
    private readonly IMapper _mapper;

    public ChatMessageService(
        IChatMessageRepository messageRepo,
        IChatSessionRepository sessionRepo,
        IAIService aiService,
        IMapper mapper)
    {
        _messageRepo = messageRepo;
        _sessionRepo = sessionRepo;
        _aiService = aiService;
        _mapper = mapper;
    }

    public async Task<ServiceResponse<SendMessageResponseDto>> SendMessageAsync(
        CreateChatMessageDto messageDto, int userId)
    {
        // 1. Kullanıcı mesajını oluştur ve önce kaydet (AI history'de görülmesi için)
        var userMessage = new ChatMessage
        {
            Content = messageDto.Content,
            IsUserMessage = true,
            ChatSessionId = messageDto.ChatSessionId
        };

        await _messageRepo.CreateMessageAsync(userMessage);
        await _messageRepo.SaveChangesAsync();

        // 2. Sohbet geçmişini getir (artık kullanıcı mesajı da dahil)
        var history = await _sessionRepo.GetMessagesAsync(messageDto.ChatSessionId, userId)
                      ?? new List<ChatMessageDto>();

        // 3. AI'dan yanıt üret (RAG kaynakları dahil)
        AiResponseResult aiResult;
        try
        {
            aiResult = await _aiService.GenerateResponseAsync(messageDto.Content, history);
        }
        catch (Exception ex)
        {
            return ServiceResponse<SendMessageResponseDto>.Fail(
                $"Yapay zeka servisine ulaşılamadı: {ex.Message}", ServiceResultType.Failure);
        }

        // 4. AI mesajını oluştur ve kaydet
        var aiMessage = new ChatMessage
        {
            Content = aiResult.Content,
            IsUserMessage = false,
            ChatSessionId = messageDto.ChatSessionId
        };

        await _messageRepo.CreateMessageAsync(aiMessage);
        var isSuccess = await _messageRepo.SaveChangesAsync();

        if (!isSuccess)
            return ServiceResponse<SendMessageResponseDto>.Fail(
                "Mesajlar veri tabanına kaydedilemedi.", ServiceResultType.Failure);

        // 5. Başlık hâlâ "Yeni Sohbet" ise kullanıcının ilk mesajından başlık oluştur
        string? generatedTitle = null;
        var session = await _sessionRepo.GetSessionByIdAsync(messageDto.ChatSessionId, userId);
        if (session != null && session.Title == "Yeni Sohbet")
        {
            var title = messageDto.Content.Length > 30
                ? messageDto.Content[..30] + "..."
                : messageDto.Content;
            session.Title = title;
            await _sessionRepo.SaveChangesAsync();
            generatedTitle = title;
        }

        // 6. Her iki mesajı DTO'ya dönüştür ve döndür (RAG kaynakları dahil)
        var response = new SendMessageResponseDto
        {
            UserMessage = _mapper.Map<ChatMessageDto>(userMessage),
            AiMessage = _mapper.Map<ChatMessageDto>(aiMessage),
            RagSources = aiResult.RagSources,
            GeneratedTitle = generatedTitle
        };

        return ServiceResponse<SendMessageResponseDto>.Success(response, ServiceResultType.Success);
    }

    // ── Streaming ──────────────────────────────────────────────────────
    public async IAsyncEnumerable<string> StreamMessageAsync(CreateChatMessageDto messageDto, int userId)
    {
        // 1. Kullanıcı mesajını kaydet
        var userMessage = new ChatMessage
        {
            Content = messageDto.Content,
            IsUserMessage = true,
            ChatSessionId = messageDto.ChatSessionId
        };
        await _messageRepo.CreateMessageAsync(userMessage);
        await _messageRepo.SaveChangesAsync();

        var userDto = _mapper.Map<ChatMessageDto>(userMessage);

        // 2. user_message event'i gonder
        yield return JsonSerializer.Serialize(new
        {
            type = "user_message",
            data = userDto
        }, _jsonOptions);

        // 3. Gecmisi getir
        var history = await _sessionRepo.GetMessagesAsync(messageDto.ChatSessionId, userId)
                      ?? new List<ChatMessageDto>();

        // 4. Streaming AI yaniti
        var fullContent = new System.Text.StringBuilder();
        List<string> ragSources = new();

        var streamResult = await _aiService.StreamResponseAsync(messageDto.Content, history);
        if (streamResult != null)
        {
            ragSources = streamResult.Value.Context.RagSources;

            await foreach (var chunk in streamResult.Value.TextStream)
            {
                fullContent.Append(chunk);
                yield return JsonSerializer.Serialize(new
                {
                    type = "chunk",
                    text = chunk
                }, _jsonOptions);
            }
        }

        // 5. AI mesajini kaydet
        var aiText = fullContent.Length > 0 ? fullContent.ToString() : "Yanıt üretilemedi.";
        var aiMessage = new ChatMessage
        {
            Content = aiText,
            IsUserMessage = false,
            ChatSessionId = messageDto.ChatSessionId
        };
        await _messageRepo.CreateMessageAsync(aiMessage);
        await _messageRepo.SaveChangesAsync();

        // 6. Baslik olustur (ilk mesajsa)
        string? generatedTitle = null;
        var session = await _sessionRepo.GetSessionByIdAsync(messageDto.ChatSessionId, userId);
        if (session != null && session.Title == "Yeni Sohbet")
        {
            var title = messageDto.Content.Length > 30
                ? messageDto.Content[..30] + "..."
                : messageDto.Content;
            session.Title = title;
            await _sessionRepo.SaveChangesAsync();
            generatedTitle = title;
        }

        // 7. done event'i gonder
        var aiDto = _mapper.Map<ChatMessageDto>(aiMessage);
        yield return JsonSerializer.Serialize(new
        {
            type = "done",
            aiMessage = aiDto,
            ragSources,
            generatedTitle
        }, _jsonOptions);
    }

    // LLM tetiklemeden sadece mesajı DB'ye kaydeder (prediction sonuçları için)
    public async Task<ServiceResponse<ChatMessageDto>> SaveMessageAsync(CreateChatMessageDto messageDto)
    {
        var message = _mapper.Map<ChatMessage>(messageDto);

        await _messageRepo.CreateMessageAsync(message);
        var isSuccess = await _messageRepo.SaveChangesAsync();

        if (!isSuccess)
            return ServiceResponse<ChatMessageDto>.Fail(
                "Mesaj veri tabanına kaydedilemedi.", ServiceResultType.Failure);

        var dto = _mapper.Map<ChatMessageDto>(message);
        return ServiceResponse<ChatMessageDto>.Success(dto, ServiceResultType.Success);
    }
}
