using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using AsistanAI.Core.Entities;
using Microsoft.EntityFrameworkCore;

namespace AsistanAI.Infrastructure.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        
        public DbSet<AppUser> Users { get; set; }
        public DbSet<ChatSession> ChatSessions { get; set; }
        public DbSet<ChatMessage> ChatMessages { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            
        }
    }
}