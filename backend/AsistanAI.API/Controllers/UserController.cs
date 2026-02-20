using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace AsistanAI.API.Controllers;

public class UserController : BaseController
{   
    private readonly IUserService _userService;
    public UserController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register(RegisterRequestDto requestDto)
    {
        var result = await _userService.RegisterAsync(requestDto);

        return CreateActionResult(result);
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginRequestDto requestDto)
    {
        var result = await _userService.LoginAsync(requestDto);

        return CreateActionResult(result);
    }
}