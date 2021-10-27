import asyncio
import json
import re
import aiohttp
import socket
import os
import question
from aiohttp import ClientSession
from lomond import WebSocket
from unidecode import unidecode
from time import time

import sys
sys.path.append("../")
from classes.discord_hooks import Webhook
from classes.slack_hooks import Slackhook
from classes.configuration import channelId, crowdsourceInformation
from main.bots import crowdSource


async def get_webhooks(wColor=0xf9d423, sColor="0xf9d423"):
    return [
        Webhook(os.environ['T'], color=wColor),
        Slackhook("https://hooks.slack.com/services/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", color=sColor)
    ]


async def fetch(url, session, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()
    except Exception as e:
        print(e)
        return ""


async def get_responses(urls, timeout, headers):
    tasks = []
    async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session, timeout))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


async def get_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as session:
        return await fetch(url, session, timeout)


async def get_json_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()


async def websocket_handler(uri, headers, prize, selfbot):
    websocket = WebSocket(uri)
    for header, value in headers.items():
        websocket.add_header(str.encode(header), str.encode(value))

    # await selfbot.wait_until_ready()

    for msg in websocket.connect(ping_rate=2):
        if msg.name == "text":

            message = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", msg.text)
            message_data = json.loads(message)
            if "error" in message_data and message_data["error"] == "Auth not valid":
                raise RuntimeError("Connection settings invalid")

            elif message_data["type"] != "interaction" and message_data["type"] == "question":

                question_str = unidecode(message_data["question"])
                qnum = message_data['questionNumber']
                answers = [unidecode(ans["text"]) for ans in message_data["answers"]]

                # informationObject = crowdsourceInformation("hqTrivia", question_str, qnum, answers)
                # channels = channelId().channels["hqTrivia"]

                # start = time()
                # newInformationObject = await crowdSource(informationObject, selfbot, channels)

                # # try:
                # newTriviaAnswers = {triviaInformation['triviaAnswers']: triviaInformation['triviaCount'] for _, triviaInformation in newInformationObject.triviaAnswers.items()}
                # maxv = max(newTriviaAnswers.values())
                # _output = "\n".join([(f"**{key} - %.2f**" % value if value == maxv else f"{key} - %.2f" % value) for key, value in newTriviaAnswers.items()])
                # # except:
                # #     _output = "\n".join([f"{triviaAnswer} - 0" for triviaAnswer in answers])

                # webhooks = await get_webhooks()
                # async_webhooks = [asyncio.ensure_future(wh.apost(question=question_str, output=_output, startingTime=start, questionNumber=qnum)) for wh in webhooks]
                # await asyncio.wait(async_webhooks)

                start = time()
                _rr_ = await question.answer_question(question_str, answers)
                print(_rr_)
                reverse = _rr_[0]
                ans_dict = {key: (_rr_[1][key] if key in _rr_[1] else 0) for key in answers}
                print(ans_dict)
                try:
                    maxv = max(ans_dict.values())
                    minv = min(value for value in ans_dict.values())

                    _output = "\n".join([(f"**{key} - %.2f**" % value if value == minv else f"{key} - %.2f" % value) if reverse else (f"**{key} - %.2f**" % value if value == maxv else f"{key} - %.2f" % value) for key, value in ans_dict.items()])
                except:
                    _output = "\n".join([f"{answer} - 0" for answer in answers])

                webhooks = await get_webhooks()

                async_webhooks = [asyncio.ensure_future(wh.apost(question=question_str, output=_output, startingTime=start, questionNumber=qnum)) for wh in webhooks]
                await asyncio.wait(async_webhooks)

            elif message_data["type"] != "interaction" and message_data["type"] == "questionSummary":

                question_yeah = message_data["question"]
                output = "\n".join([f":white_check_mark: {answerObject['answer']} **[{answerObject['count']}]**" if answerObject["correct"] is True else f":regional_indicator_x: {answerObject['answer']} **[{answerObject['count']}]**" for answerObject in message_data["answerCounts"]]) + "\n\n:money_with_wings: **%.2f**" % (prize / message_data["advancingPlayersCount"])

                webhooks = await get_webhooks(0x00FF00, "0x00FF00")

                async_webhooks = [asyncio.ensure_future(wh.apost(question=question_yeah, output=output)) for wh in webhooks]

                await asyncio.wait(async_webhooks)

            elif message_data["type"] != "interaction" and message_data["type"] == "gameSummary":
                webhooks = await get_webhooks(0xff0000, "0xff0000")
                amountOfWinningPlayers = len(message_data["winners"])
                output = "See you next game!"

                async_webhooks = [asyncio.ensure_future(wh.apost(Ended=output)) for wh in webhooks]

                await asyncio.wait(async_webhooks)
