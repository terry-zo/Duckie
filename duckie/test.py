import sys
sys.path.append("../")
import asyncio
import question
from classes.discord_hooks import Webhook
from time import time
from unidecode import unidecode

message_data = {
    "type": "question",
    "ts": "2017-12-28T20:09:42.040Z",
    "totalTimeMs": 10000,
    "timeLeftMs": 10000,
    "questionId": 16913,
    "question": "What did the USSR call itself?",
    "category": "Literature",
    "answers": [
        {
          "answerId": 52360,
          "text": "SSPU"
        },
        {
            "answerId": 52361,
            "text": "CLRS"
        },
        {
            "answerId": 52362,
            "text": "CCCP"
        }
    ],
    "questionNumber": 7,
    "questionCount": 12,
    "sent": "2017-12-28T20:09:42.073Z"
}


async def hi():

    if "error" in message_data and message_data["error"] == "Auth not valid":
        raise RuntimeError("Connection settings invalid")
    elif message_data["type"] != "interaction" and message_data["type"] == "question":
        question_str = unidecode(message_data["question"])
        qnum = message_data['questionNumber']
        answers = [unidecode(ans["text"]) for ans in message_data["answers"]]
        start = time()
        _rr_ = await question.answer_question(question_str, answers)
        print(_rr_)
        reverse = _rr_[0]
        ans_dict = {key: (_rr_[1][key] if key in _rr_[1] else 0) for key in answers}
        print(ans_dict)
        try:
            maxv = max(ans_dict.values())
            minv = min(value for value in ans_dict.values() if value != 0)

            _output = "\n".join([(f"**{key} - %.2f**" % value if value == minv else f"{key} - %.2f" % value) if reverse else (f"**{key} - %.2f**" % value if value == maxv else f"{key} - %.2f" % value) for key, value in ans_dict.items()])
        except:
            _output = "\n".join([f"{answer} - 0" for answer in answers])

        async_webhooks = [asyncio.ensure_future(wh.apost(qnum, question_str, _output, start)) for wh in webhooks]
        await asyncio.gather(*async_webhooks)

webhooks = [
    Webhook("https://discordapp.com/api/webhooks/450205390089748480/Mi3x4tjkkLTlLIq4X_-0o7hZb9Aky3L_kmaaxllE4m29Vdz_28oOBUDqwfCATJ6bQ1sU", color=0xF6F5AE)  # terry
]


loop = asyncio.get_event_loop()
loop.run_until_complete(hi())
