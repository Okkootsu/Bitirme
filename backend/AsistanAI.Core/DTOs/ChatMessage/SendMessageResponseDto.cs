namespace AsistanAI.Core.DTOs.ChatMessage;

public class SendMessageResponseDto
{
    public ChatMessageDto UserMessage { get; set; } = null!;
    public ChatMessageDto AiMessage { get; set; } = null!;
}
