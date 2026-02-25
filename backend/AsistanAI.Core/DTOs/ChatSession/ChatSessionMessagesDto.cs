using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;

namespace AsistanAI.Core.DTOs.ChatSession;

public class ChatSessionMessagesDto
{
    public List<ChatMessageDto> Messages { get; set; } = null!;
}