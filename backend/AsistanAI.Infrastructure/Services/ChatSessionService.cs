using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Wrappers;
using AutoMapper;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Entities;

namespace AsistanAI.Infrastructure.Services;

public class ChatSessionService : IChatSessionService
{   
    private readonly IChatSessionRepository _sessionRepository;
    public ChatSessionService(IChatSessionRepository sessionRepository)
    {
        _sessionRepository = sessionRepository;
    }

    public async Task<ServiceResponse> CreateChatSessionAsync(int userId)
    {   
        var chatSession = new ChatSession
        {
          UserId = userId,  
        };

        await _sessionRepository.CreateSessionAsync(chatSession);

        var isSuccess = await _sessionRepository.SaveChangesAsync();

        if (!isSuccess)
            return ServiceResponse.Fail("Yeni sohbet oluşturulurken bir hata meydana geldi", ServiceResultType.Failure);
        
        return ServiceResponse.Success(ServiceResultType.SuccessNoContent);
    }

    public async Task<ServiceResponse<ChatSessionMessagesDto>> GetChatMessagesAsync(int sessionId, int userId)
    {
        var chatMessages = await _sessionRepository.GetMessagesAsync(sessionId, userId);

        if (chatMessages == null)
            return ServiceResponse<ChatSessionMessagesDto>.Fail("Mesajlar bulunamadı", ServiceResultType.NotFound);


        var chatMessagesDto = new ChatSessionMessagesDto
        {
          Messages = chatMessages,  
        };

        return ServiceResponse<ChatSessionMessagesDto>.Success(chatMessagesDto, ServiceResultType.Success);
    }

    public async Task<ServiceResponse<ChatSessionsDto>> GetChatSessionsAsync(int userId)
    {
        var sessions = await _sessionRepository.GetChatSessionsAsync(userId);

        var sessionsDto = new ChatSessionsDto
        {
          ChatSessions = sessions  
        };

        return ServiceResponse<ChatSessionsDto>.Success(sessionsDto, ServiceResultType.Success);
    }
}