import os
import pyaudio
# Find the absolute path to the 'cogs' directory
COGS_DIRECTORY= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs') 
PERSISTENCE_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Persistence')      

# recoding options
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2  
RATE = 22050  
AMPLIFICATION_FACTOR = 5
