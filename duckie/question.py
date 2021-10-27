import re
import asyncio
from collections import Counter


import search

punctuation_to_none = str.maketrans({key: None for key in "!\"#$%&\'()*+,-.:;<=>?@[\\]^_`{|}~�"})
# punctuation_to_space = str.maketrans({key: " " for key in "!\"#$%&\'()*+,-.:;<=>?@[\\]^_`{|}~�"})


async def answer_question(question, original_answers):
    # formatting

    question_lower = question.lower()

    q_split = question_lower.split(" ")
    reverse = "NOT" in question or ("least" in q_split and "at least" not in q_split) or "never" in q_split

    s_ = "".join(e for e in question if (e.isalnum() or e is " "))

    question_keywords = search.find_keywords(s_)

    print(original_answers)
    print(question_keywords)

    tasks = [
        asyncio.ensure_future(sm1(question_keywords, original_answers)),
        asyncio.ensure_future(sm2(question, original_answers)),
        asyncio.ensure_future(sm3(question_keywords, original_answers))
    ]

    done, _ = await asyncio.wait(tasks, timeout=5)
    c = Counter()

    for y in [Counter(obj.result()) for obj in done]:
        c += y
    return (reverse, dict(c))


async def sm1(question_keywords, answers):
    search_results = await search.search_google("+".join(question_keywords), 5)
    search_text = [x.translate(punctuation_to_none) for x in await search.get_clean_texts(search_results)]
    try:
        countz = {answer: {keyword: 0 for keyword in search.find_keywords(answer)} for answer in answers}

        counts = {answer: c + len(re.findall(f" {answer.lower().translate(punctuation_to_none)} ", text)) for text in search_text for answer, c in {answer: 0 for answer in answers}.items()}

        for text in search_text:
            for keyword_counts in countz.values():
                for keyword in keyword_counts:
                    keyword_counts[keyword] += len(re.findall(f" {keyword.lower().translate(punctuation_to_none)} ", text))

        counts_sum = {answer: sum(keyword_counts.values()) for answer, keyword_counts in countz.items()}
        combined = dict(Counter(counts_sum) + Counter(counts))
        final = {key: value for key, value in combined.items()}
        return final
    except:
        return {answer: 0 for answer in answers}


async def sm2(question_keywords, original_answers):
    tasks = [asyncio.ensure_future(search.Wiki(question_keywords, answer_choice).search()) for answer_choice in original_answers]
    done = await asyncio.gather(*tasks)
    try:
        _counter = {wikiObject.answer: wikiObject.count for wikiObject in done}
        return _counter
    except:
        return {answer: 0 for answer in original_answers}


async def sm3(question_keywords, original_answers):
    tasks = [asyncio.ensure_future(search.RS(answer, "%20".join(question_keywords + [answer.lower()])).toll_google()) for answer in original_answers]
    done = await asyncio.gather(*tasks)
    try:
        max_ratio = float(max(RS.result if RS.result != 0 else 1 for RS in done))  # actual max
        # max_ratio = float(min(RS.result if RS.result != 0 else 1 for RS in done))  # min but im lazy
        _counter = {RS.answer: round(float(RS.result) / max_ratio, 2) for RS in done}
        return _counter
    except:
        return {answer: 0 for answer in original_answers}
