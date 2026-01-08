'''
Defines most of the event listeners of the bot
'''

from interactions import Extension, listen
from interactions.api.events import VoiceUserLeave


class GNListeners(Extension):
    """
    Class containing bot event listeners
    """

    @listen(delay_until_ready=True)
    async def on_ready(self):
        """
        Message to print to terminal once the bot is ready
        """

        print("Bot is ready!")
        print(f"This bot is owned by {self.bot.owner}")

    @listen(VoiceUserLeave, delay_until_ready=True)
    async def on_VoiceUserLeave(self, event: VoiceUserLeave):
        '''
        Adds the user back into the candidate pool upon leaving the voice channel
        '''

        user = event.author
        channel = event.channel

        self.bot.remove_member_from_removed_candidates(channel, user)
