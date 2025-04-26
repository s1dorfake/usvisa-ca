import asyncio
from telethon import TelegramClient
from settings import TG_USERS, BOT_TOKEN, API_HASH

class TelegramAlertBot:
    def __init__(self, name = ""):
        self.api_id = 8
        self.api_hash = API_HASH
        self.bot_token = BOT_TOKEN
        self.users = TG_USERS
        self.client = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._initialize_bot(name))

    async def _initialize_bot(self, name):
        self.client = TelegramClient('bot' + name, self.api_id, self.api_hash)
        await self.client.start(bot_token=self.bot_token)

    async def send_message(self, message):
        if self.client is None:
            raise Exception("Bot not initialized. Call _initialize_bot() first.")
        for user in self.users:
            await self.client.send_message(user, message)

    def send_mes(self, message):
        if self.client is None:
            raise Exception("Bot not initialized. Call _initialize_bot() first.")
        tasks = [
            self.send_message(message),
        ]
        self.loop.run_until_complete(asyncio.gather(*tasks))