using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Entities;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Wrappers;
using AutoMapper;

namespace AsistanAI.Infrastructure.Services;

public class UserService : IUserService
{   
    private readonly IUserRepository _userRepository;
    private readonly IMapper _mapper;
    private readonly IJwtService _jwtService;
    public UserService(IUserRepository userRepository, IMapper mapper, IJwtService jwtService)
    {
        _userRepository = userRepository;
        _mapper = mapper;
        _jwtService = jwtService;
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        var user = await _userRepository.GetByEmailAsync(email);

        if (user == null)
            return null;
        
        return user;
    }

    public async Task<User?> GetByIdAsync(int id)
    {
        var user = await _userRepository.GetByIdAsync(id);

        if (user == null)
            return null;
        
        return user;
    }

    public async Task<ServiceResponse<LoginResponseDto>> LoginAsync(LoginRequestDto requestDto)
    {
        var user = await _userRepository.GetByEmailAsync(requestDto.Email);

        if (user == null)
            return ServiceResponse<LoginResponseDto>.Fail("Kullanıcı adı veya şifre hatalı", ServiceResultType.Unauthorized);

        var isValidPassword = AuthenticationService.VerifyPassword(requestDto.Password, user.PasswordHash);

        if (!isValidPassword)
            return ServiceResponse<LoginResponseDto>.Fail("Kullanıcı adı veya şifre hatalı", ServiceResultType.Unauthorized);


        var token = await _jwtService.Authenticate(user);

        if (token is null) 
            return ServiceResponse<LoginResponseDto>.Fail("Sistemsel bir hata oluştu", ServiceResultType.Failure);

        return ServiceResponse<LoginResponseDto>.Success(token, ServiceResultType.Success);
    }

    public async Task<ServiceResponse> RegisterAsync(RegisterRequestDto requestDto)
    {
        var user = await _userRepository.GetByEmailAsync(requestDto.Email);

        if (user != null)
            return ServiceResponse.Fail("Bu E-postaya sahip bir kullanıcı zaten var!", ServiceResultType.Conflict);
        
        var newUser = _mapper.Map<User>(requestDto);
        newUser.PasswordHash = AuthenticationService.HashPassword(requestDto.Password);

        await _userRepository.AddUserAsync(newUser);
        await _userRepository.SaveChangesAsync();

        return ServiceResponse.Success(ServiceResultType.SuccessNoContent);
    }

    
}