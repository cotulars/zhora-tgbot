import aioredis
import redis
from google import genai
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import *

# Initialize Bot instance with a default parse mode
bot = Bot(token=BOT_TOKEN)

# Initialize Dispatcher
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

redis_client = aioredis.from_url(f"redis://{REDIS_HOST}")     #redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

openai_client = AsyncOpenAI(api_key=OPENAI_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_TOKEN)
