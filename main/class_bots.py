import asyncio
import os

import sys
sys.path.append("classes")
from hq_bot import hqBot


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    hqBot_ = hqBot()
    loop.create_task(hqBot_.start(os.environ['HQ_TOKEN']))
    loop.run_forever()
