import discord
from discord.ext import commands
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from dotenv import load_dotenv
load_dotenv()

from app.api.apiv1.index import Index

try:
    from core.start import DBot
except ModuleNotFoundError:
    from app.core.start import DBot


class ReadyLoad(commands.Cog):
    def __init__(self, bot : DBot):
        self.bot = bot

    # DiscordからLINEへ
    @commands.Cog.listener(name='on_ready')
    async def on_message(self):

        await self.bot.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(name='起動中...................',type=discord.ActivityType.watching)
        )

        self.app = FastAPI(
            docs_url=None,
            redoc_url=None,
            openapi_url=None
        )
        
        self.app.include_router(router=Index(bot=self.bot).router)

        if os.environ.get("PORTS") != None:
            hostname = "localhost"
            portnumber = int(os.getenv("PORTS", default=5000))
        else:
            hostname = "0.0.0.0"
            portnumber = int(os.getenv("PORT", default=8080))

        config = uvicorn.Config(
            app=self.app,
            host=hostname,
            port=portnumber,
            log_level="info"
        )
        server = uvicorn.Server(config)

        print('起動しました')

        # 終了時
        if os.environ.get("PORTS") != None:
            await server.serve()
            print("exit")
            await server.shutdown()
            await self.bot.close()
        else:
            await server.serve()
            print("exit")
            await server.shutdown()
            await self.bot.close()
	    
def setup(bot:DBot):
    return bot.add_cog(ReadyLoad(bot))
