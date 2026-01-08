'''
Loads in the bot's configuration    
'''

from typing import Any, Dict

import interactions
from interactions import Intents, Member, GuildVoice

from src.myUtils import load_bot_config, load_txt_file_contents


class GNClient(interactions.Client):
    '''    
    "Game Night Client" A wrapper class for a discord.Client
    '''

    def __init__(
        self,
        bot_config_path: str,
        token: str,
        intents: Intents = Intents.DEFAULT,
        **options: Any,
    ) -> None:
        """...
        """
        self.bot_config: dict = load_bot_config(bot_config_path)
        self.delete_after_time_secs: int = self.bot_config['delete_after_time_secs']
        self.timeout_mins: int = self.bot_config['timeout_mins']
        self.debug_scope: int = self.bot_config['debug_scope']
        self.label_max_len: int = self.bot_config['label_max_len']
        self._removed_candidates: Dict = {}
        super().__init__(token=token, debug_scope=self.debug_scope, intents=intents, **options)

        self.load_extensions('ext', recursive=True)
        print('bot about to start')
        self.start()

    @property
    def removed_candidates(self) -> Dict:
        return self._removed_candidates

    def helpFileContents(self) -> str:
        return load_txt_file_contents(self.bot_config["helpFilePath"])

    def add_removed_candidate(self, member: Member) -> None:
        if member.voice.channel.id not in self._removed_candidates:
            self._removed_candidates[member.voice.channel.id] = {}
        self._removed_candidates[member.voice.channel.id][member.id] = member

    def remove_member_from_removed_candidates(self, channel: GuildVoice, member: Member) -> None:
        if channel.id in self._removed_candidates:
            self._removed_candidates[channel.id].pop(member.id, None)

    def remove_channel_from_removed_candidates(self, voiceChannel: GuildVoice) -> None:
        self._removed_candidates.pop(voiceChannel.id, None)
