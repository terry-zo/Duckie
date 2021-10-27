import requests
import discord
import urllib3
import json
import time
from websocket import create_connection
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def joingame(auth_token, user_id):
    with requests.Session() as s:
        ws_rq = s.get(f"https://api-quiz.hype.space/shows/now?type=hq&userId={user_id}", headers={"accept": "*/*", "x-hq-client": "iOS/1.3.5 b88", "authorization": f"Bearer {auth_token}", "x-hq-stk": "MQ==", "x-hq-device": "iPhone9,2", "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0", "accept-language": "en-us", "accept-encoding": "br, gzip, deflate"}, verify=False, timeout=30)
        print(ws_rq.json())
        ws_l = str(ws_rq.json()["broadcast"]["socketUrl"]).replace("https", "wss")
    ws = create_connection(ws_l, header={
        "accept": "*/*",
        "x-hq-client": "iOS/1.3.5 b88",
        "x-hq-stk": "MQ==",
        "x-hq-device": "iPhone9,2",
        "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0",
        "accept-language": "en-us",
        "accept-encoding": "br, gzip, deflate",
        "authorization": f"Bearer {auth_token}"
    })
    print("Websocket Connected.")
    print(ws.recv())
    if "error" in json.loads(ws.recv()):
        raise

def checkresponse(resp, block=1):
    if block == 1:
        if resp.status_code == 200:
            return True
        elif resp.status_code == 429:
            return "Too many requests"
        elif resp.status_code == 400:
            return "Failed to send code"
        else:
            return "Unknown"
    if block == 2:
        if resp.status_code == 200:
            return True
        elif resp.status_code == 429:
            return "Too many requests"
        elif resp.status_code == 400:
            return "Code is invalid"
        else:
            return "Unknown"


def sendcode(number):
    global iphone_headers
    try:
        with requests.Session() as s:
            resp = s.post("https://api-quiz.hype.space/verifications/", json={
                "method": "sms",
                "phone": number
            }, verify=False, headers=iphone_headers, timeout=30)
            json_data = resp.json()
            if not "error" in json_data:
                verfid = json_data["verificationId"]
                return str(verfid)
            else:
                return "**Error**: {}\n**Error Code**: {}".format(json_data["error"], json_data["errorCode"])
    except:
        return "Unknown"


def create_life(code, ref, author, GLOBAL_VARIABLES, name):
    global iphone_headers
    try:
        uuid = GLOBAL_VARIABLES[author]
        with requests.Session() as s:
            resp = s.post("https://api-quiz.hype.space/verifications/" + uuid, json={
                "code": code
            }, verify=False, headers=iphone_headers, timeout=30)
            resp_status = checkresponse(resp, block=2)
            if resp_status == True:
                resp = s.post("https://api-quiz.hype.space/users", json={
                    "country": "US",
                    "language": "en",
                    "referringUsername": ref,
                    "username": name,
                    "verificationId": uuid
                }, verify=False, timeout=30)
                return resp
    except:
        return "Unknown"


def embedder(name, value, status, functionality="HQ"):
    title_names = {"HQ": "HQ Helper", "JIG": "Address Jigger", "LINK": "Cart Links Generator"}
    if status == "Error":
        embed = discord.Embed(title=title_names[functionality], color=0xff0000)
    elif status == "Success":
        embed = discord.Embed(title=title_names[functionality], color=0x00ff00)
    embed.set_author(name="Tools", url="https://twitter.com/zoegodterry", icon_url="https://png.pngtree.com/svg/20161018/wrench_38163.png")
    embed.add_field(name=name, value=value, inline=False)
    embed.set_footer(text="@Terry#6666")
    return embed


def nextgame(block=1):
    global iphone_headers
    with requests.Session() as s:
        resp = s.get("https://api-quiz.hype.space/shows/now?type=hq", headers=iphone_headers, verify=False, timeout=30)
        info = resp.json()
    if block == 1:
        embeds = []
        game_list = info["upcoming"]
        for game in game_list:
            embed = discord.Embed(title="HQ Upcoming Game", color=0x00ff00)
            embed.set_author(name="Duckie Bot", url="https://twitter.com/zoegodterry", icon_url="https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128")
            utc_dt = datetime.strptime(str(game["time"]), '%Y-%m-%dT%H:%M:%S.%fZ')  # "2018-05-25T01:00:00.000Z"
            d = utc_dt - timedelta(hours=4)
            embed.add_field(name="Date", value=d.strftime("%b %e %Y"), inline=True)
            embed.add_field(name="Time", value=d.strftime("%r %ZEST"), inline=True)
            embed.add_field(name="Prize", value=str(game["prize"]), inline=True)
            embed.set_footer(text="@Terry#6666")
            embeds.append(embed)
        return embeds
    elif block == 2:
        if info["active"] is False:
            utc_dt = datetime.strptime(str(info["upcoming"][0]["time"]), '%Y-%m-%dT%H:%M:%S.%fZ')
            return (utc_dt - datetime(1970, 1, 1)).total_seconds() - time.time()
        elif info["active"] is True:
            return 0


def hqstats(username, author_id):
    global iphone_headers
    iphone_headers["authorization"] = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE0NzYxNzM2LCJ1c2VybmFtZSI6InpvZWdvZHRlcnJ5IiwiYXZhdGFyVXJsIjoiczM6Ly9oeXBlc3BhY2UtcXVpei9kZWZhdWx0X2F2YXRhcnMvVW50aXRsZWQtMV8wMDAzX3JlZC5wbmciLCJ0b2tlbiI6IlNYcWtsOSIsInJvbGVzIjpbXSwiY2xpZW50IjoiIiwiZ3Vlc3RJZCI6bnVsbCwidiI6MSwiaWF0IjoxNTI3MTg4NDI1LCJleHAiOjE1MzQ5NjQ0MjUsImlzcyI6Imh5cGVxdWl6LzEifQ.WrmesiU8MiQeRW5qrG4o_BdL6LWjlJ8Hl9aX_fSzo28'
    with requests.Session() as s:
        resp = s.get("https://api-quiz.hype.space/users?q=" + username, headers=iphone_headers, verify=False, timeout=30)
        try:
            if resp.status_code == 200:
                info = resp.json()
                user_id = str(info["data"][0]["userId"])
                resp = s.get("https://api-quiz.hype.space/users/" + user_id, headers=iphone_headers, verify=False, timeout=30)
                if resp.status_code == 200:
                    info = resp.json()
                    embed = discord.Embed(title="HQ Stats for {}".format(username), color=0x00ff00)
                    embed.set_author(name="Duckie Bot", url="https://twitter.com/zoegodterry", icon_url="https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128")
                    embed.set_thumbnail(url=str(info["avatarUrl"]))
                    embed.add_field(name="Games", value="**Played**: {}".format(info["gamesPlayed"]), inline=False)
                    embed.add_field(name="Wins", value="**Total Wins**: {}\n**Total Earnings**: {}\n**Weekly Earnings**: {}".format(info["winCount"], info["leaderboard"]["alltime"]["total"], info["leaderboard"]["weekly"]["total"]), inline=False)
                    embed.add_field(name="Ranking", value="**Weekly**: {}\n**All Time**: {}".format(info["leaderboard"]["weekly"]["rank"], info["leaderboard"]["alltime"]["rank"]), inline=False)
                    embed.set_footer(text="@Terry#6666")
                    return(embed)
                else:
                    raise
            else:
                raise
        except:
            return(embedder("Error", "<@{}> Failed to get stats!".format(author_id), "Error"))

iphone_headers = {
    "accept": "*/*",
    "x-hq-client": "iOS/1.3.5 b88",
    "x-hq-stk": "MQ==",
    "x-hq-device": "iPhone9,2",
    "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0",
    "accept-language": "en-us",
    "accept-encoding": "br, gzip, deflate"
}
