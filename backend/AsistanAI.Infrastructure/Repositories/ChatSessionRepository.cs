using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Interfaces;
using AsistanAI.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AsistanAI.Infrastructure.Repositories;

public class ChatSessionRepository : IChatSessionRepository
{   
    private readonly AppDbContext _context;
    public ChatSessionRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task CreateSessionAsync(ChatSession session)
    {
        await _context.ChatSessions.AddAsync(session);
    }

    public void DeleteSessionAsync(ChatSession session)
    {
        _context.Remove(session);
    }

    public async Task<List<ChatSession>> GetChatSessionsAsync(int userId)
    {
        return await _context.ChatSessions.Where(s => s.UserId == userId)
        .OrderByDescending(s => s.CreatedAt).ToListAsync();
    }

    public async Task<ICollection<ChatMessage>?> GetMessagesAsync(int sessionId, int userId)
    {
        return await _context.ChatSessions.Include(s => s.Messages.OrderBy(m => m.CreatedAt))
        .Where(s => s.Id == sessionId && s.UserId == userId).Select(s => s.Messages).FirstOrDefaultAsync();
    }

    public async Task<bool> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync() > 0;
    }
}