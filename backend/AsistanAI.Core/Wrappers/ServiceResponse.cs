using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.Enums;

namespace AsistanAI.Core.Wrappers;

public class ServiceResponse<T>
{
    public T? Data { get; private set; }
    public bool IsSuccess { get; private set; }
    public string? ErrorMessage { get; private set; }
    public ServiceResultType ResultType { get; private set; }

    public static ServiceResponse<T> Success(T data, ServiceResultType resultType = ServiceResultType.Success)
    {
        return new ServiceResponse<T>
        {
            Data = data,
            IsSuccess = true,
            ResultType = resultType,
        };
    }

    public static ServiceResponse<T> Fail(string errorMessage, ServiceResultType resultType)
    {
        if (resultType == ServiceResultType.Success)
            resultType = ServiceResultType.Failure;

        return new ServiceResponse<T>
        {
            IsSuccess = false,
            ErrorMessage = errorMessage,
            ResultType = resultType,
        };
    }
}

public class ServiceResponse
{
    public bool IsSuccess { get; private set; }
    public string? ErrorMessage { get; private set; }
    public ServiceResultType ResultType { get; private set; }

    public static ServiceResponse Success(ServiceResultType resultType = ServiceResultType.Success)
    {
        if (resultType == ServiceResultType.NotFound || 
            resultType == ServiceResultType.InvalidInput || 
            resultType == ServiceResultType.Conflict || 
            resultType == ServiceResultType.Failure)
        {
            resultType = ServiceResultType.Success;
        }

        return new ServiceResponse
        {
            IsSuccess = true,
            ResultType = resultType,
        };
    }

    public static ServiceResponse Fail(string errorMessage, ServiceResultType resultType)
    {
        if (resultType == ServiceResultType.Success || 
            resultType == ServiceResultType.SuccessNoContent)
        {
            resultType = ServiceResultType.Failure;
        }
        

        return new ServiceResponse
        {
            IsSuccess = false,
            ErrorMessage = errorMessage,
            ResultType = resultType,
        };
    }
}