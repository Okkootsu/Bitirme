# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# 1. Copy only project files first → restore is cached unless dependencies change
COPY AsistanAI.Core/AsistanAI.Core.csproj AsistanAI.Core/
COPY AsistanAI.Infrastructure/AsistanAI.Infrastructure.csproj AsistanAI.Infrastructure/
COPY AsistanAI.API/AsistanAI.API.csproj AsistanAI.API/

RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet restore AsistanAI.API/AsistanAI.API.csproj

# 2. Copy the rest and publish
COPY . .

RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet publish AsistanAI.API/AsistanAI.API.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY --from=build /app/publish .

EXPOSE 8080

ENTRYPOINT ["dotnet", "AsistanAI.API.dll"]
