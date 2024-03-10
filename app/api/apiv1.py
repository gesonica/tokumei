from fastapi import APIRouter,Request
from starlette.requests import Request

import os

from discord.ext import commands
try:
    from core.start import DBot
except ModuleNotFoundError:
    from app.core.start import DBot
    
class Index(commands.Cog):
    def __init__(self, bot: DBot):
        self.bot = bot
        self.router = APIRouter()

        @self.router.get("/")
        async def index(request: Request):
	    return {'message':f'bot id:{self.bot.application_id}'}
