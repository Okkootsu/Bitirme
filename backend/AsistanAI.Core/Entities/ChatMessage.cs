using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.Entities;

public class ChatMessage : BaseEntity
{
    public string Content { get; set; } = string.Empty;
    public bool IsUserMessage { get; set; } // True: Kullanıcı, False: AI
    public string? RagSources { get; set; } // JSON serialized List<string>

    // Foreign Key
    public int ChatSessionId { get; set; }
    public ChatSession ChatSession { get; set; } = null!;
}