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

    public async Task<ChatMessage?> GetMessageAsync(int id)
    {
        return await _context.ChatMessages.FirstOrDefaultAsync(m => m.Id == id);
    }

    public async Task<bool> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync() > 0;
    }
}