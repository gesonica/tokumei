import discord
from discord import Intents
import os
import json
import traceback

from dotenv import load_dotenv
load_dotenv()

class DBot(discord.AutoShardedBot):
    def __init__(self, token:str, intents:Intents) -> None:
        self.token = token
        super().__init__(intents = intents)
        self.load_cogs()

    def load_cogs(self) -> None:
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                cog = file[:-3]
                self.load_extension(f"cogs.{cog}")
                print(cog + "をロードしました")

    # 起動用の補助関数です
    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start(self.token))
        except discord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            print("終了します")
            #self.loop.run_until_complete(self.close())
        except discord.HTTPException as e:
            traceback.print_exc()
