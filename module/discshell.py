import os
import socket
import getpass
import discord
from discord.ext import commands
from .constants import COGS_DIRECTORY

class DiscShell(commands.Bot):

    def __init__(self, port_id: str):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None
        )
        
        self.pc_user = getpass.getuser()
        self.port_id = port_id 
        self.local_ip = None
        self.is_selected = False
        
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.get_internal_ip()
        await self.tree.sync()
    
    async def setup_hook(self):
        if os.path.exists(COGS_DIRECTORY) and os.path.isdir(COGS_DIRECTORY):
            for filename in os.listdir(COGS_DIRECTORY):
                if filename.endswith(".py") and filename != "__init__.py":
                    ext = f"module.cogs.{filename[:-3]}"
                    try:
                        await self.load_extension(ext)
                        print(f"Loaded extension: {ext}")
                    except Exception as e:
                        print(f"Failed to load extension {ext}: {e}")
        else:
            print(f"COGS_DIRECTORY does not exist: {COGS_DIRECTORY}")

    def get_internal_ip(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            self.local_ip = ip_address
            print(f"The local IP address has been confirmed as {ip_address}.")
        except Exception as e:
            self.local_ip = None
            print(f"Failed to obtain local IP address (gethostname): {e}")
