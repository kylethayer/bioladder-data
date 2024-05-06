#!/usr/bin/env python3.11

# From: https://stackoverflow.com/questions/34020599/asynchronously-receive-output-from-long-running-shell-commands-with-asyncio-pyt

import asyncio
import sys
from asyncio.subprocess import PIPE, STDOUT

async def get_lines(shell_command):
    p = await asyncio.create_subprocess_shell(shell_command,
            stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    return (await p.communicate())[0].splitlines()

async def main():
    # get commands output concurrently
    coros = [get_lines('"{e}" -c "print({i:d}); import time; time.sleep({i:d})"'
                       .format(i=i, e=sys.executable))
             for i in reversed(range(5))]
    for f in asyncio.as_completed(coros): # print in the order they finish
        print(await f)


if sys.platform.startswith('win'):
    loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()