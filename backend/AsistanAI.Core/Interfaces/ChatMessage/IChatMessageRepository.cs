using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IChatMessageRepository
{   
    public Task<bool> SaveChangesAsync();
    public Task<ChatMessage?> GetMessageAsync(int id);
    public Task CreateMessageAsync(ChatMessage message);
    public void DeleteMessageAsync(ChatMessage message);
}