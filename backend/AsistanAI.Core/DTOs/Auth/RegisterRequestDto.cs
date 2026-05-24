using System.ComponentModel.DataAnnotations;

namespace AsistanAI.Core.DTOs;

public class RegisterRequestDto
{
    [Required(ErrorMessage = "E-posta adresi gereklidir.")]
    [EmailAddress(ErrorMessage = "Geçerli bir e-posta adresi giriniz.")]
    public string Email { get; set; } = null!;

    [Required(ErrorMessage = "Kullanıcı adı gereklidir.")]
    [MinLength(2, ErrorMessage = "Kullanıcı adı en az 2 karakter olmalıdır.")]
    [MaxLength(50, ErrorMessage = "Kullanıcı adı en fazla 50 karakter olabilir.")]
    public string Username { get; set; } = null!;

    [Required(ErrorMessage = "Şifre gereklidir.")]
    [MinLength(6, ErrorMessage = "Şifre en az 6 karakter olmalıdır.")]
    public string Password { get; set; } = null!;
}