using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.Entities;

namespace AsistanAI.Core.Interfaces;

public interface IUserRepository
{
    public Task<User?> GetByIdAsync(int id);
    public Task<User?> GetByEmailAsync(string email);
    public Task<bool> SaveChangesAsync();
    public Task AddUserAsync(User user);
}