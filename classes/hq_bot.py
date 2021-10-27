import discord
import urllib3
import sys
sys.path.append("classes")
from functions import *
from hq_life import *
from discord.ext import commands
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class hqBot(discord.Client):

    def __init__(self):
        HQ = commands.Bot(command_prefix="!", case_insensitive=True)
        HQ.remove_command('help')
        self.HQ = HQ

    @HQ.command(pass_context=True)
    async def hq(self, ctx, function="", *args):
        function = function.lower()
        if "nextgame" in function:
            ng_embeds = nextgame()
            for _embed in ng_embeds:
                await self.HQ.send_message(ctx.message.author, embed=_embed)

        elif function == "stats":
            username = args[0]
            stat_embed = hqstats(username, ctx.message.author.id)
            await self.HQ.send_message(ctx.message.author, embed=stat_embed)

        elif function == "life":
            try:
                if str(ctx.message.author.id) not in self.GLOBAL_VARIABLES:
                    acc_obj = LifeSession(self.HQ, ctx)
                    await acc_obj.Account(args[0])
                    self.GLOBAL_VARIABLES[ctx.message.author.id] = acc_obj
                    await self.HQ.send_message(ctx.message.author, f"<@{ctx.message.author.id}>: Created session with number `{args[0]}`. Use `$hq confirm [Verification Code] [Referral]`")
                else:
                    await self.HQ.send_message(ctx.message.author, f"<@{ctx.message.author.id}>: You already have an active session. To cancel use `$hq cancel`")
            except:
                return

        elif function == "confirm":
            # looks for acc obj
            list_of_sessions = [session for d_id, session in self.GLOBAL_VARIABLES.items() if d_id == ctx.message.author.id]
            print(list_of_sessions)
            if len(list_of_sessions) != 0:
                first_session = list_of_sessions[0]
                await first_session.Create(args[0], args[1])
                try:
                    del self.GLOBAL_VARIABLES[ctx.message.author.id]
                except:
                    pass
                await first_session.JoinGame()
                # find next game
                # remove session from global var n put in queue
                # asyncio wait until next game
                # call join game on session
            else:
                await self.HQ.send_message(ctx.message.author, f"<@{ctx.message.author.id}>: No active session found, create one with `$life [number]`")

        elif "cancel" in function:
            try:
                del self.GLOBAL_VARIABLES[ctx.message.author.id]
            except:
                await self.HQ.send_message(ctx.message.author, f"<@{ctx.message.author.id}>: Failed to destroy all sessions.")
                return
            await self.HQ.send_message(ctx.message.author, f"<@{ctx.message.author.id}>: Destroyed all sessions.")

    @HQ.event
    async def on_ready(self):
        print("{}({}) connected!".format(self.HQ.user.name, self.HQ.user.id))
        all_servers = [server for server in self.HQ.servers]
        for _server in all_servers:
            if _server.id in self.allowedServers:
                print(f"Authorized - Name: {_server.name} ID: {_server.id}")
            else:
                await self.HQ.leave_server(_server)
                print(f"Left - Name: {_server.name} ID: {_server.id}")

        self.allowedServers = [
            "218063927207133184"
        ]
        self.GLOBAL_VARIABLES = {}
