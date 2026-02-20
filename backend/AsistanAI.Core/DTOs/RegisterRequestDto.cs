using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AsistanAI.Core.DTOs
{
    public class RegisterRequestDto
    {
        public string Email { get; set; } = null!;
        public string Username { get; set; } = null!;
        public string Password { get; set; } = null!;
    }
}