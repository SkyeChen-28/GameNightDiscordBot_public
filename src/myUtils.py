'''
Utility functions for the bot
'''

import json
# import asyncio
# from asyncio import tasks


def load_bot_config(filepath: str) -> dict:
    '''
    Loads the bot_config dict

    Args:
        filepath (str): Path to the config.json file

    Returns:
        dict: The bot_config dict
    '''
    with open(filepath, encoding="UTF-8") as fp:
        bot_config = json.load(fp)
    return bot_config


def load_txt_file_contents(filepath: str) -> str:
    '''
    Returns all the text contained inside of a text file.

    Args:
        filepath (str): Path to the text file

    Returns:
        str: File contents
    '''

    with open(filepath, mode='r', encoding="UTF-8") as fp:
        contents = fp.read()

    return contents

# def wait(task_or_coroutine):
#     '''
#     DOESN'T WORK! :(
#     For debugging async functions

#     Args:
#         task_or_coroutine: Function to await

#     Returns:
#         The result of the async function
#     '''
#     task = asyncio.ensure_future(task_or_coroutine)
#     loop, current_task = task.get_loop(), tasks.current_task()
#     tasks._leave_task(loop, current_task)
#     while not task.done():
#         loop._run_once()
#     tasks._enter_task(loop, current_task)
#     return task.result()
