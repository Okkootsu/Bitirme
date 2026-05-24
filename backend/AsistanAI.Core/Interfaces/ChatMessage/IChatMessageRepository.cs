using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IChatMessageRepository
{
    public Task<bool> SaveChangesAsync();
    public Task<ChatMessage?> GetMessageAsync(int id);
    public Task CreateMessageAsync(ChatMessage message);
}