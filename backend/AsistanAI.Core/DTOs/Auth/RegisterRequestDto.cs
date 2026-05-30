using System.ComponentModel.DataAnnotations;

namespace AsistanAI.Core.DTOs;

public class RegisterRequestDto
{
    public string Email { get; set; } = null!;
    public string Username { get; set; } = null!;
    public string Password { get; set; } = null!;
}