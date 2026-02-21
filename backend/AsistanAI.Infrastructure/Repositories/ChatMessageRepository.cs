using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Interfaces;
using AsistanAI.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AsistanAI.Infrastructure.Repositories;

public class ChatMessageRepository : IChatMessageRepository
{   
    private readonly AppDbContext _context;
    public ChatMessageRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task CreateMessageAsync(ChatMessage message)
    {
        await _context.ChatMessages.AddAsync(message);
    }

    public void DeleteMessageAsync(ChatMessage message)
    {
        _context.ChatMessages.Remove(message);
    }

    public async Task<ChatMessage?> GetMessageAsync(int id)
    {
        return await _context.ChatMessages.FirstOrDefaultAsync(m => m.Id == id);
    }

    public async Task<bool> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync() > 0;
    }
}