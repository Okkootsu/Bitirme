using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.DTOs.ChatSession;

public class ChatSessionMessagesDto
{
    public ICollection<Entities.ChatMessage> Messages { get; set; } = null!;
}