using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.DTOs.Prediction;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Interfaces.Prediction;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AsistanAI.API.Controllers;

[Authorize]
public class PredictionController : BaseController
{
    private readonly IPredictionService _predictionService;
    private readonly IChatMessageService _chatMessageService;

    public PredictionController(IPredictionService predictionService, IChatMessageService chatMessageService)
    {
        _predictionService = predictionService;
        _chatMessageService = chatMessageService;
    }

    [HttpPost("assess")]
    public async Task<IActionResult> Assess(PredictionRequestDto requestDto)
    {
        var result = await _predictionService.PredictAsync(requestDto);

        if (!result.IsSuccess)
            return CreateActionResult(result);

        // Tahmin sonucunu AI mesajı olarak chat oturumuna kaydet (LLM tetiklenmez)
        var aiMessage = new CreateChatMessageDto
        {
            Content = result.Data!.FormattedMessage,
            IsUserMessage = false,
            ChatSessionId = requestDto.ChatSessionId
        };

        await _chatMessageService.SaveMessageAsync(aiMessage);

        return CreateActionResult(result);
    }
}
