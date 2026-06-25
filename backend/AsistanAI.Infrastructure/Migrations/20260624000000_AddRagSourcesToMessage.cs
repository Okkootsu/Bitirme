using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AsistanAI.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddRagSourcesToMessage : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "RagSources",
                table: "ChatMessages",
                type: "text",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RagSources",
                table: "ChatMessages");
        }
    }
}
