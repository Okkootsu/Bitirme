using AsistanAI.Core.DTOs.ChatMessage;

namespace AsistanAI.Core.Interfaces.AI;

public record AiResponseResult(string Content, List<string> RagSources);

public record AiStreamContext(List<string> RagSources);

public interface IAIService
{
    Task<AiResponseResult> GenerateResponseAsync(string userMessage, List<ChatMessageDto> history);
    Task<(IAsyncEnumerable<string> TextStream, AiStreamContext Context)?> StreamResponseAsync(string userMessage, List<ChatMessageDto> history);
}
