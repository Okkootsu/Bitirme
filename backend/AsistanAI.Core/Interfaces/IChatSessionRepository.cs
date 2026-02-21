using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IChatSessionRepository
{
    public Task<bool> SaveChangesAsync();
    public Task<ICollection<ChatMessage>?> GetMessagesAsync(int sessionId, int userId);
    public Task<List<ChatSession>> GetChatSessionsAsync(int userId);
    public void DeleteSessionAsync(ChatSession session);
    public Task CreateSessionAsync(ChatSession session);
}