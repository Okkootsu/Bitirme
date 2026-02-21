using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.DTOs.ChatSession;

public class CreateChatSessionDto
{
    public string? Title { get; set; } 
    
    // Foreign Key ilişkisi
    public int UserId { get; set; }
}