using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Interfaces.AI;
using AsistanAI.Core.Wrappers;
using AutoMapper;

namespace AsistanAI.Infrastructure.Services;

public class ChatMessageSevice : IChatMessageService
{
    private readonly IChatMessageRepository _messageRepo;
    private readonly IChatSessionRepository _sessionRepo;
    private readonly IAIService _aiService;
    private readonly IMapper _mapper;

    public ChatMessageSevice(
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
        // 1. Kullanıcı mesajını oluştur (IsUserMessage her zaman true)
        var userMessage = new ChatMessage
        {
            Content = messageDto.Content,
            IsUserMessage = true,
            ChatSessionId = messageDto.ChatSessionId
        };

        await _messageRepo.CreateMessageAsync(userMessage);

        // 2. Sohbet geçmişini getir (AI'ya context vermek için)
        var history = await _sessionRepo.GetMessagesAsync(messageDto.ChatSessionId, userId)
                      ?? new List<ChatMessageDto>();

        // 3. OpenAI'dan yanıt üret
        string aiContent;
        try
        {
            aiContent = await _aiService.GenerateResponseAsync(messageDto.Content, history);
        }
        catch (Exception ex)
        {
            // AI servisine ulaşılamazsa kullanıcı mesajını kaydet, hata döndür
            await _messageRepo.SaveChangesAsync();
            return ServiceResponse<SendMessageResponseDto>.Fail(
                $"Yapay zeka servisine ulaşılamadı: {ex.Message}", ServiceResultType.Failure);
        }

        // 4. AI mesajını oluştur
        var aiMessage = new ChatMessage
        {
            Content = aiContent,
            IsUserMessage = false,
            ChatSessionId = messageDto.ChatSessionId
        };

        await _messageRepo.CreateMessageAsync(aiMessage);

        // 5. Her ikisini birlikte kaydet
        var isSuccess = await _messageRepo.SaveChangesAsync();

        if (!isSuccess)
            return ServiceResponse<SendMessageResponseDto>.Fail(
                "Mesajlar veri tabanına kaydedilemedi.", ServiceResultType.Failure);

        // 6. Her iki mesajı DTO'ya dönüştür ve döndür
        var response = new SendMessageResponseDto
        {
            UserMessage = _mapper.Map<ChatMessageDto>(userMessage),
            AiMessage = _mapper.Map<ChatMessageDto>(aiMessage)
        };

        return ServiceResponse<SendMessageResponseDto>.Success(response, ServiceResultType.Success);
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
