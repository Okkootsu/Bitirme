namespace AsistanAI.Core.DTOs.ChatMessage;

public class SendMessageResponseDto
{
    public ChatMessageDto UserMessage { get; set; } = null!;
    public ChatMessageDto AiMessage { get; set; } = null!;
    public List<string> RagSources { get; set; } = new();
    public string? GeneratedTitle { get; set; }
}
