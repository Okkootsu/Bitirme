using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IChatSessionRepository
{
    public Task<bool> SaveChangesAsync();
    public Task<List<ChatMessageDto>?> GetMessagesAsync(int sessionId, int userId);
    public Task<List<ChatSessionDto>> GetChatSessionsAsync(int userId);
    public void DeleteSession(ChatSession session);
    public Task<ChatSession?> GetSessionByIdAsync(int sessionId, int userId);
    public Task CreateSessionAsync(ChatSession session);
}