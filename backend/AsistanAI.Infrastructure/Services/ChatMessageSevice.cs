using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.Interfaces;
using AsistanAI.Core.Wrappers;
using AsistanAI.Core.Enums;
using AutoMapper;
using AsistanAI.Core.Entities;

namespace AsistanAI.Infrastructure.Services;

public class ChatMessageSevice : IChatMessageService
{
    private readonly IChatMessageRepository _messageRepo;
    private readonly IMapper _mapper;
    public ChatMessageSevice(IChatMessageRepository messageRepo, IMapper mapper)
    {
        _messageRepo = messageRepo;
        _mapper = mapper;
    }

    public async Task<ServiceResponse> SendMessageAsync(CreateChatMessageDto messageDto)
    {   
        var message = _mapper.Map<ChatMessage>(messageDto);

        await _messageRepo.CreateMessageAsync(message);
        var isSuccess = await _messageRepo.SaveChangesAsync();

        if (!isSuccess)
            return ServiceResponse.Fail("Mesaj veri tabanına eklenemedi", ServiceResultType.Failure);

        return ServiceResponse.Success(ServiceResultType.SuccessNoContent);
    }
}