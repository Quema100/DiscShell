import discord
from discord.ext import commands
import platform

class SessionManager(commands.Cog):
    def __init__(self, app: commands.Bot):
        self.app = app

    @commands.command(name="list", aliases=["ls", "pcs"])
    async def list_pcs(self, ctx):
        my_id = getattr(self.app, 'port_id', 'Unknown')
        my_user = getattr(self.app, 'pc_user', 'Unknown')
        my_ip = getattr(self.app, 'local_ip', 'Unknown')
        is_active = getattr(self.app, 'is_selected', False)

        status_text = "Active (Selected)" if is_active else "Standby"
        embed_color = discord.Color.green() if is_active else discord.Color.light_grey()

        embed = discord.Embed(title=f"PC Info: {my_id}", color=embed_color)
        embed.add_field(name="User", value=f"`{my_user}`", inline=True)
        embed.add_field(name="IP", value=f"`{my_ip}`", inline=True)
        embed.add_field(name="OS", value=f"{platform.system()} {platform.release()}", inline=False)
        embed.add_field(name="Status", value=status_text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="select", aliases=["choice", "sel"])
    async def select_pc(self, ctx, target_id: str):
        my_id = getattr(self.app, 'port_id', None)

        if target_id.lower() == "all":
            if not self.app.is_selected:
                self.app.is_selected = True
                await ctx.send(f"**[{my_id}]** All Connected!")
            else:
                await ctx.send(f"**[{my_id}]** Already activated ")
            return

        if my_id == target_id:
            if not self.app.is_selected:
                self.app.is_selected = True
                await ctx.send(f"**[{my_id}]** Connected! Now accepting commands.")
            else:
                await ctx.send(f"**[{my_id}]** Already activated ")
        else:
            self.app.is_selected = False
    
    @commands.command(name="unselect", aliases=["leave", "exit"])
    async def unselect_pc(self, ctx, target_id: str = None):
        my_id = getattr(self.app, 'port_id', None)

        if target_id.lower() == "all":
            if self.app.is_selected:
                self.app.is_selected = False
                await ctx.send(f"**[{my_id}]** Complete disconnection.")
            return
        
        if my_id == target_id:
            if self.app.is_selected:
                self.app.is_selected = False
                await ctx.send(f"**[{my_id}]** Disconnection (standby mode).")
            else:
                await ctx.send(f"**[{my_id}]** Already in standby mode.")
            return
        else:
            pass

async def setup(app: commands.Bot):
    await app.add_cog(SessionManager(app))