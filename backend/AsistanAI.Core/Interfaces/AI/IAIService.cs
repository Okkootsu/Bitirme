using AsistanAI.Core.DTOs.ChatMessage;

namespace AsistanAI.Core.Interfaces.AI;

public interface IAIService
{
    Task<string> GenerateResponseAsync(string userMessage, List<ChatMessageDto> history);
}
