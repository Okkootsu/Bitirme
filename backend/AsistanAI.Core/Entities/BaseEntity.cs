using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.Entities
{
    public abstract class BaseEntity
    {
        public int Id { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}