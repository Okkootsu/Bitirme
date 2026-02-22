using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.DTOs;
using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IJwtService
{
    public Task<LoginResponseDto?> Authenticate(User user);
}