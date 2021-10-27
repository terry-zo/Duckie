# import sys
# sys.path.append("classes")
# sys.path.append("duckie")
# import asyncio
# import os
# import time
# import network

# # Read in bearer token and user ID
# USER_ID = os.environ['USER_ID']
# BEARER_TOKEN = os.environ['BEARER_TOKEN']

# print("Booting up...")
# main_url = f"https://api-quiz.hype.space/shows/now?type=hq&userId={USER_ID}"
# headers = {"Authorization": f"Bearer {BEARER_TOKEN}",
#            "x-hq-client": "iOS/1.3.5 b88"}

# # "accept": "*/*",
# # "x-hq-client": "iOS/1.3.5 b88",
# # "x-hq-stk": "MQ==",
# # "x-hq-device": "iPhone9,2",
# # "user-agent": "HQ-iOS/88 CFNetwork/894 Darwin/17.4.0",
# # "accept-language": "en-us",
# # "accept-encoding": "br, gzip, deflate"


# while True:
#     try:
#         response_data = asyncio.get_event_loop().run_until_complete(
#             network.get_json_response(main_url, timeout=1.5, headers=headers))
#     except:
#         time.sleep(30)
#         continue
#     if "broadcast" not in response_data or response_data["broadcast"] is None:
#         if "error" in response_data and response_data["error"] == "Auth not valid":
#             raise RuntimeError("Connection settings invalid")
#         else:
#             print("Game has not started.")
#             time.sleep(30)
#     else:
#         socket = response_data["broadcast"]["socketUrl"].replace("https", "wss")
#         print(f"Show active, connecting to socket at {socket}")
#         asyncio.get_event_loop().run_until_complete(network.websocket_handler(socket, headers))


import sys
sys.path.append("classes")
sys.path.append("duckie")
import asyncio
import network

print("Launching Duckie...")


class responseEvent(object):

    def __init__(self, bearerToken, gameRegion):
        self.bearerToken = bearerToken
        self.gameRegion = gameRegion
        self.gameUrl = "https://api-quiz.hype.space/shows/now?type=hq"
        self.gameHeaders = {"x-hq-client": "iOS/1.3.5 b88", "Authorization": bearerToken}

    async def Call(self):
        self.gameResponse = await network.get_json_response(self.gameUrl, timeout=1.5, headers=self.gameHeaders)
        return self


async def receiveObject(responseObject):
    response_data = responseObject.gameResponse
    if "broadcast" not in response_data or response_data["broadcast"] is None:
        if "error" in response_data and response_data["error"] == "Auth not valid":
            raise RuntimeError("Connection settings invalid")
        else:
            await asyncio.sleep(30)
    else:
        socket = response_data["broadcast"]["socketUrl"].replace("https", "wss")
        prize = response_data["prize"]
        print(f"{responseObject.gameRegion} game active: {socket}")
        aw = [asyncio.ensure_future(network.websocket_handler(socket, responseObject.gameHeaders, prize, selfbot))]
        await asyncio.wait(aw)


async def Handler():
    while True:
        try:
            _toll = [
                asyncio.ensure_future(responseEvent("Bearer .", "UK").Call())
            ]

            responseObjects = await asyncio.gather(*_toll)
        except:
            await asyncio.sleep(30)
            continue
        parser = [asyncio.ensure_future(receiveObject(responseObject)) for responseObject in responseObjects]
        await asyncio.gather(*parser)

loop = asyncio.get_event_loop()
loop.create_task(Handler())
loop.run_forever()
