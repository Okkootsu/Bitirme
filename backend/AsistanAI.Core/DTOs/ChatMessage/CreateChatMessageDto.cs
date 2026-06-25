using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.DTOs.ChatMessage;

public class CreateChatMessageDto
{
    public string Content { get; set; } = null!;
    public bool IsUserMessage { get; set; }
    public List<string>? RagSources { get; set; }

    // Foreign Key
    public int ChatSessionId { get; set; }
}