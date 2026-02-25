using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.DTOs.ChatMessage;

public class ChatMessageDto
{
    public int Id { get; set; }
    public string Content { get; set; } = null!;
    public bool IsUserMessage { get; set; }
}