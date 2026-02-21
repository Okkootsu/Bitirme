using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AsistanAI.API.Controllers;

[Authorize]
public class ChatMessageController : BaseController
{   
    private readonly IChatMessageService _chatMessageService;
    public ChatMessageController(IChatMessageService chatMessageService)
    {
        _chatMessageService = chatMessageService;   
    }

    [HttpPost("send")]
    public async Task<IActionResult> SendMessage(CreateChatMessageDto messageDto)
    {
        var result = await _chatMessageService.SendMessageAsync(messageDto);

        return CreateActionResult(result);
    }
}