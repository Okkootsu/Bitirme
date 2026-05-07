using AsistanAI.Core.DTOs.Prediction;
using AsistanAI.Core.Wrappers;

namespace AsistanAI.Core.Interfaces.Prediction;

public interface IPredictionService
{
    Task<ServiceResponse<PredictionResponseDto>> PredictAsync(PredictionRequestDto request);
}
