using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace AsistanAI.API.Controllers;

public class AuthController : BaseController
{   
    private readonly IAuthService _authService;
    public AuthController(IAuthService authService)
    {
        _authService = authService;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register(RegisterRequestDto requestDto)
    {
        var result = await _authService.RegisterAsync(requestDto);

        return CreateActionResult(result);
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginRequestDto requestDto)
    {
        var result = await _authService.LoginAsync(requestDto);

        return CreateActionResult(result);
    }
}