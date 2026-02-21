using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Wrappers;

namespace AsistanAI.Core.Interfaces;

public interface IChatMessageService
{
    public Task<ServiceResponse> SendMessageAsync(CreateChatMessageDto messageDto);
}