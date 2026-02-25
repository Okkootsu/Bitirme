using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AsistanAI.API.Controllers;

[Authorize]
public class ChatSessionController : BaseController
{   
    private readonly IChatSessionService _chatSessionService;
    public ChatSessionController(IChatSessionService chatSessionService)
    {
        _chatSessionService = chatSessionService;
    }

    [HttpGet("sessions")]
    public async Task<IActionResult> GetChatSessions()
    {
        int userId = GetUserId();

        var result = await _chatSessionService.GetChatSessionsAsync(userId);

        return CreateActionResult(result);
    }

    [HttpPost("create")]
    public async Task<IActionResult> CreateChatSession()
    {   
        var userId = GetUserId();
        var result = await _chatSessionService.CreateChatSessionAsync(userId);

        return CreateActionResult(result);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetChatMessages(int id)
    {   
        var userId = GetUserId();

        var result = await _chatSessionService.GetChatMessagesAsync(id, userId);

        return CreateActionResult(result);
    }
}