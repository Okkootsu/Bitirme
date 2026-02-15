using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.Entities
{
    public class AppUser : BaseEntity
    {
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string PasswordHash { get; set; } = string.Empty;
        
        // Bir kullanıcının birden çok sohbeti olabilir
        public ICollection<ChatSession> ChatSessions { get; set; } = new List<ChatSession>();
    }
}