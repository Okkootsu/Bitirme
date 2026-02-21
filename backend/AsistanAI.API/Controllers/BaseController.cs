using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using AsistanAI.Core.Enums;
using AsistanAI.Core.Wrappers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore.Infrastructure.Internal;

namespace AsistanAI.API.Controllers;

[Route("api/[controller]")]
[ApiController]
public class BaseController : ControllerBase
{   
    [NonAction]
    public IActionResult CreateActionResult<T>(ServiceResponse<T> response)
    {
        if (response.ResultType == ServiceResultType.Success)
        {
            return Ok(response);
        }

        return CreateErrorResult(response.ResultType, response.ErrorMessage);
    }

    [NonAction]
    public IActionResult CreateActionResult(ServiceResponse response)
    {
        if (response.ResultType == ServiceResultType.Success)
        {
            return Ok(response); 
        }
        else if (response.ResultType == ServiceResultType.SuccessNoContent)
        {
            return NoContent();
        }

        return CreateErrorResult(response.ResultType, response.ErrorMessage);
    }

    private IActionResult CreateErrorResult(ServiceResultType resultType, string errorMessage)
    {   
        var message = errorMessage ?? "Bilinmeyen bir hata oluştu.";

        var errorResponse = new { IsSuccess = false, ErrorMessage = message };

        return resultType switch
        {
            ServiceResultType.NotFound => NotFound(errorResponse), // 404
            ServiceResultType.InvalidInput => BadRequest(errorResponse), // 400
            ServiceResultType.Conflict => Conflict(errorResponse), // 409
            ServiceResultType.Unauthorized => Unauthorized(errorResponse), // 401
            _ => StatusCode(500, errorResponse) // Genel Hata  
        };
    }

    protected int GetUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier) ?? User.FindFirst(JwtRegisteredClaimNames.Sub);

        if (userIdClaim == null)
            throw new UnauthorizedAccessException("Kullanıcı kimliği doğrulanamadı.");
        
        return int.Parse(userIdClaim.Value);
    }
}