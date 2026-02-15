using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.Entities
{
    public class ChatSession : BaseEntity
    {
        public string Title { get; set; } = "Yeni Sohbet";
        
        // Foreign Key ilişkisi
        public int AppUserId { get; set; }
        public AppUser AppUser { get; set; } = null!;

        // Bir sohbetin içinde birden çok mesaj olabilir
        public ICollection<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
    }
}