using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Wrappers;

namespace AsistanAI.Core.Interfaces;

public interface IChatSessionService
{
    public Task<ServiceResponse<ChatSessionsDto>> GetChatSessionsAsync(int userId);
    public Task<ServiceResponse<ChatSessionMessagesDto>> GetChatMessagesAsync(int sessionId, int userId);
    public Task<ServiceResponse<ChatSessionDto>> CreateChatSessionAsync(int userId);
}