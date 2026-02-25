using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Wrappers;

namespace AsistanAI.Core.Interfaces;

public interface IAuthService
{
    public Task<User?> GetByIdAsync(int id);
    public Task<User?> GetByEmailAsync(string email);
    public Task<ServiceResponse> RegisterAsync(RegisterRequestDto requestDto);
    public Task<ServiceResponse<LoginResponseDto>> LoginAsync(LoginRequestDto requestDto);
}