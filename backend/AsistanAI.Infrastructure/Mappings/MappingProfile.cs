using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Entities;
using AutoMapper;

namespace AsistanAI.Infrastructure.Mappings;

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        CreateMap<User, RegisterRequestDto>().ReverseMap();
    }
}