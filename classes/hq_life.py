import asyncio
import aiohttp
import socket
import names
import websockets
import json
from . import functions
from random import randint


class LifeSession():

    def __init__(self, client, ctx):
        self.ctx = ctx
        self.client = client
        self.author = ctx.message.author
        self.codeUrl = "https://api-quiz.hype.space/verifications/"
        self.accUrl = "https://api-quiz.hype.space/users"
        self.scheduleUrl = "https://api-quiz.hype.space/shows/now?type=hq&userId={}"
        self.headers = {"x-hq-client": "iOS/1.3.5 b88", "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0"}

    def Name(self):
        name = names.get_first_name().lower() + str(randint(1, 1000000))
        return name[:15]

    # def Scheduler(self):
    #     pass

    async def Account(self, number):
        print(number)
        number = ''.join([c for c in ''.join(number) if c.isdigit()])
        try:
            async with aiohttp.ClientSession(headers=self.headers, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as s:
                async with s.post(self.codeUrl, data={"method": "sms", "phone": f"+1{number}"}, timeout=7) as response:
                    json_data = await response.json()
                if "error" not in json_data:
                    self.number = number
                    self.verfid = json_data["verificationId"]
                    await self.client.say(f"<@{self.author.id}>: Created session with number `{number}`. Use `hq confirm [Verification Code] [Referral]`")
                else:
                    raise KeyError(json_data["error"])
        except KeyError as e:
            await self.client.say(f"<@{self.author.id}>: {str(e)[1:-1]}")
            raise

    async def Create(self, code, referral):
        try:
            async with aiohttp.ClientSession(headers=self.headers, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as s:
                async with s.post(self.codeUrl + self.verfid, data={"code": code}, timeout=7) as response:
                    json_data = await response.json()
                if "error" not in json_data:
                    if json_data["auth"] != None:
                        existingUser = json_data["auth"]["username"]
                        raise KeyError(f"The account `{existingUser}` is already linked to `{self.number}`.")
                    rname = self.Name()
                    async with s.post(self.accUrl, data={"country": "US", "language": "en", "referringUsername": referral, "username": rname, "verificationId": self.verfid}, timeout=7) as response:
                        json_data = await response.json()
                    if "error" not in json_data:
                        self.token = json_data["accessToken"]
                        self.userId = json_data["userId"]
                        self.accName = rname
                        await self.client.say(f"<@{self.author.id}>: Created an account with the name `{rname}`. Life queued for next game.")
                        return self
                    else:
                        raise KeyError(json_data["error"])
                else:
                    raise KeyError(json_data["error"])
        except KeyError as e:
            await self.client.say(f"<@{self.author.id}>: {str(e)[1:-1]}")

    async def JoinGame(self):
        try:
            try:
                wait_time = functions.nextgame(block=2)
            except:
                wait_time = 0
            await asyncio.sleep(wait_time)
            clone = {"content-type": "application/json", "x-hq-client": "iOS/1.3.5 b88", "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0", "authorization": f"Bearer {self.token}"}
            async with aiohttp.ClientSession(headers=clone, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as s:
                async with s.get(self.scheduleUrl.format(self.userId), timeout=7) as response:
                    json_data = await response.json()
                    try:
                        self.broadcastID = json_data["broadcast"]["broadcastId"]
                        # self.hype_link = json_data["broadcast"]["permalink"]
                        # self.joinUrl = "https://api-quiz.hype.space{}?mode=watching".format(json_data["broadcast"]["links"]["viewers"])
                    except:
                        raise KeyError("Failed to find current game.")

            async with websockets.connect(f"wss://ws-quiz.hype.space/ws/{self.broadcastID}", extra_headers={"Authorization": f"Bearer {self.token}"}) as websocket:
                for _ in range(5):
                    resp_msg = await websocket.recv()
                await websocket.send(json.dumps({'type': 'subscribe', 'broadcastId': str(self.broadcastID)}))
                await asyncio.sleep(3)
                await websocket.send(json.dumps({'type': 'interaction', 'broadcastId': str(self.broadcastID), 'message': 'hello everyone'}))
                await asyncio.sleep(3)

            await self.client.say(f"<@{self.author.id}>: `{self.accName}` linked to {self.number} joined current game.")
        except Exception as e:
            await self.client.say(f"<@{self.author.id}>: {str(e)[1:-1]}")
