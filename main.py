#!/usr/bin/env python3
"""
Runs the Game Night Discord Bot
"""

import os

from interactions import Intents
from src.GNClient import GNClient

def main():
    """
    Entry point for running the Game Night Discord Bot
    """
    token = os.getenv('GNB_CLIENT_SECRET')
    intents = Intents(Intents.DEFAULT + Intents.new(message_content=True))
    GNClient(bot_config_path='data/bot_config_template.json', token=token, intents=intents)

if __name__ == "__main__":
    main()
