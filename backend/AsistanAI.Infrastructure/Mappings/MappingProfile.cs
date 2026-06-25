using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.DTOs.ChatMessage;
using AsistanAI.Core.DTOs.ChatSession;
using AsistanAI.Core.Entities;
using AutoMapper;

namespace AsistanAI.Infrastructure.Mappings;

public class RagSourcesResolver : IValueResolver<ChatMessage, CreateChatMessageDto, List<string>?>
{
    public List<string>? Resolve(ChatMessage source, CreateChatMessageDto dest, List<string>? destMember, ResolutionContext context)
    {
        if (string.IsNullOrEmpty(source.RagSources)) return null;
        return JsonSerializer.Deserialize<List<string>>(source.RagSources);
    }
}

public class RagSourcesReverseResolver : IValueResolver<CreateChatMessageDto, ChatMessage, string?>
{
    public string? Resolve(CreateChatMessageDto source, ChatMessage dest, string? destMember, ResolutionContext context)
    {
        if (source.RagSources == null || source.RagSources.Count == 0) return null;
        return JsonSerializer.Serialize(source.RagSources);
    }
}

public class RagSourcesToDtoResolver : IValueResolver<ChatMessage, ChatMessageDto, List<string>?>
{
    public List<string>? Resolve(ChatMessage source, ChatMessageDto dest, List<string>? destMember, ResolutionContext context)
    {
        if (string.IsNullOrEmpty(source.RagSources)) return null;
        return JsonSerializer.Deserialize<List<string>>(source.RagSources);
    }
}

public class RagSourcesDtoReverseResolver : IValueResolver<ChatMessageDto, ChatMessage, string?>
{
    public string? Resolve(ChatMessageDto source, ChatMessage dest, string? destMember, ResolutionContext context)
    {
        if (source.RagSources == null || source.RagSources.Count == 0) return null;
        return JsonSerializer.Serialize(source.RagSources);
    }
}

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        CreateMap<User, RegisterRequestDto>().ReverseMap();

        CreateMap<ChatMessage, CreateChatMessageDto>()
            .ForMember(d => d.RagSources, opt => opt.MapFrom<RagSourcesResolver>())
            .ReverseMap()
            .ForMember(d => d.RagSources, opt => opt.MapFrom<RagSourcesReverseResolver>());

        CreateMap<ChatMessage, ChatMessageDto>()
            .ForMember(d => d.RagSources, opt => opt.MapFrom<RagSourcesToDtoResolver>())
            .ReverseMap()
            .ForMember(d => d.RagSources, opt => opt.MapFrom<RagSourcesDtoReverseResolver>());

        CreateMap<ChatSession, ChatSessionDto>().ReverseMap();

        CreateMap<ChatSession, ChatSessionMessagesDto>();
    }
}