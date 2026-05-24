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
        var userId = GetUserId();
        var result = await _chatMessageService.SendMessageAsync(messageDto, userId);
        return CreateActionResult(result);
    }

    [HttpPost("stream")]
    public async Task StreamMessage(CreateChatMessageDto messageDto)
    {
        var userId = GetUserId();

        Response.ContentType = "text/event-stream";
        Response.Headers.Append("Cache-Control", "no-cache");
        Response.Headers.Append("Connection", "keep-alive");
        Response.Headers.Append("X-Accel-Buffering", "no");

        try
        {
            await foreach (var chunk in _chatMessageService.StreamMessageAsync(messageDto, userId))
            {
                await Response.WriteAsync($"data: {chunk}\n\n");
                await Response.Body.FlushAsync();
            }
        }
        catch (Exception ex)
        {
            var error = System.Text.Json.JsonSerializer.Serialize(new
            {
                type = "error",
                message = ex.Message
            });
            await Response.WriteAsync($"data: {error}\n\n");
            await Response.Body.FlushAsync();
        }
    }
}
