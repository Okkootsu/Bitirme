using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AsistanAI.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class VarNamesUpdated : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_ChatSessions_Users_AppUserId",
                table: "ChatSessions");

            migrationBuilder.RenameColumn(
                name: "AppUserId",
                table: "ChatSessions",
                newName: "UserId");

            migrationBuilder.RenameIndex(
                name: "IX_ChatSessions_AppUserId",
                table: "ChatSessions",
                newName: "IX_ChatSessions_UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_ChatSessions_Users_UserId",
                table: "ChatSessions",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_ChatSessions_Users_UserId",
                table: "ChatSessions");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "ChatSessions",
                newName: "AppUserId");

            migrationBuilder.RenameIndex(
                name: "IX_ChatSessions_UserId",
                table: "ChatSessions",
                newName: "IX_ChatSessions_AppUserId");

            migrationBuilder.AddForeignKey(
                name: "FK_ChatSessions_Users_AppUserId",
                table: "ChatSessions",
                column: "AppUserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
