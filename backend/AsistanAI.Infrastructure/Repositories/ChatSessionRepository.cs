using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
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

    public void DeleteSession(ChatSession session)
    {
        _context.Remove(session);
    }

    public async Task<ChatSession?> GetSessionByIdAsync(int sessionId, int userId)
    {
        return await _context.ChatSessions
            .FirstOrDefaultAsync(s => s.Id == sessionId && s.UserId == userId);
    }

    public async Task<List<ChatSessionDto>> GetChatSessionsAsync(int userId)
    {
        return await _context.ChatSessions.Where(s => s.UserId == userId)
        .OrderByDescending(s => s.CreatedAt).Select(s => new ChatSessionDto
        {
            Id = s.Id,
            Title = s.Title,
        }).ToListAsync();
    }

    public async Task<List<ChatMessageDto>?> GetMessagesAsync(int sessionId, int userId)
    {
        // return await _context.ChatSessions.Include(s => s.Messages.OrderBy(m => m.CreatedAt))
        // .Where(s => s.Id == sessionId && s.UserId == userId).Select(s => s.Messages).FirstOrDefaultAsync();

        return await _context.ChatSessions
        .Where(s => s.Id == sessionId && s.UserId == userId)
        .SelectMany(s => s.Messages)
        .OrderBy(m => m.CreatedAt)
        .Select(m => new ChatMessageDto
        {
            Id = m.Id,
            Content = m.Content,
            IsUserMessage = m.IsUserMessage,
        })
        .ToListAsync();
    }

    public async Task<bool> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync() > 0;
    }
}