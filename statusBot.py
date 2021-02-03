import os

import discord
from discord.ext import tasks


class StatusBotClient(discord.Client):
    client = discord.Client()

    def __init__(self, realms_api):
        super().__init__()
        self.realms_api = realms_api
        self.channel = None
        self.main_loop.start()

    async def on_ready(self):
        print(str(self.user) + ' has connected to Discord!')
        self.channel = self.get_channel()
        print(self.channel)

    @tasks.loop(minutes=1)
    async def main_loop(self):
        if self.channel:
            player_status_updates = self.realms_api.update_player_statuses()
            await self.send_player_status_updates(player_status_updates)
            print(player_status_updates)

    async def send_player_status_updates(self, player_status_updates):
        for player_name, status in player_status_updates.items():
            online_status_message = "online!" if status else "no longer online."
            await self.channel.send(player_name + " is " + online_status_message)

    def get_channel(self):
        guild_name = os.getenv("GUILD_NAME")
        channel_name = os.getenv("CHANNEL_NAME")
        return discord.utils.get(self.get_all_channels(), guild__name=guild_name, name=channel_name)
