'''
Defines all the slash commands that the bot makes available to users.
'''

import os
import asyncio
import random
from typing import List, Dict

from interactions import Extension, Message, GuildVoice, Member
from interactions import SlashContext, slash_command, OptionType, slash_option
from interactions import check, is_owner, DMChannel
from interactions.client.errors import HTTPException
# import interactions as its


class GNCommands(Extension):
    """
    A class for base slash commands and among us commands of the GNDBot
    """

    @slash_command(name='help',
                   description='Provides info about the bot\'s commands')
    async def help(self,
                   ctx: SlashContext):
        """
        Displays the help text 
        """
        await ctx.respond(self.bot.helpFileContents())

    @slash_command(name='test')
    async def test(self, ctx: SlashContext):
        """
        Basic slash command to test that the bot is online 
        """
        await ctx.respond('I successfully responded to your test', delete_after=self.bot.delete_after_time_secs)

    @slash_command(
        name='sync',
        description='(Alias of `/update`) Updates the bot\'s commands, event listeners, etc. (Bot owner only)'
    )
    async def sync(self, ctx: SlashContext):
        """
        Updates the bot's commands, event listeners, etc.  
        """
        await self.__update_impl(ctx)

    @slash_command(
        name='update',
        description='Updates the bot\'s commands, event listeners, etc. (Bot owner only)'
    )
    async def update(self, ctx: SlashContext):
        """
        Updates the bot's commands, event listeners, etc.  
        """
        await self.__update_impl(ctx)

    async def __update_impl(self, ctx: SlashContext):
        '''
        Updates the bot's event listeners, commands, and any other extensions
        '''
        if is_owner():
            for ext_fp in os.listdir('ext'):
                if ext_fp.endswith('.py'):
                    ext = f'ext.{ext_fp[:-3]}'
                    self.bot.reload_extension(ext)
            await ctx.respond("Bot updated!", delete_after=self.bot.delete_after_time_secs)

    @slash_command(
        name='shutdown',
        description='Shuts down the bot (Bot owner only)'
    )
    @check(is_owner())
    async def shutdown(self, ctx: SlashContext):
        """
        Shuts down the bot
        """
        await ctx.respond("Shutting down bot", delete_after=self.bot.delete_after_time_secs)
        await asyncio.sleep(self.bot.delete_after_time_secs+1)
        await self.bot.stop()

    async def __memberIsInVoiceChannel(self, ctx) -> bool:
        if ctx.member.voice:
            return True
        else:
            await ctx.respond("Error: You need to be in a voice channel to use this command!")
            return False

    def __getCandidatePool(self, ctx: SlashContext) -> List[Member]:
        '''
        Generates the candidate pool of the user's voice channel

        Args:
            ctx (SlashContext): The slash context that called this function

        Returns:
            List[Member]: The candidate pool
        '''

        if ctx.member.voice is not None:

            # Detect who is in the voice channel of the caller
            voice_channel: GuildVoice = ctx.member.voice.channel
            voice_members: List[Member] = voice_channel.voice_members

            # Generate candidate pool
            # Remove any candidates that are in the removed_candidates_pool
            candidate_pool: List[Member] = []
            if (voice_channel.id in self.bot.removed_candidates):
                for member in voice_members:
                    if (member.id not in self.bot.removed_candidates[voice_channel.id]):
                        candidate_pool.append(member)
            else:
                candidate_pool = voice_members

            return candidate_pool

        else:
            return []

    async def __randomlySelectPeopleBaseImplementation(
        self,
        ctx: SlashContext,
        # role_name: str = "Superstar",
        n: int = 1,
        remove_from_candidate_pool: bool = False
    ) -> List[Member]:
        '''
        Randomly selects `n` people, assigns them a role name `role_name` (textually, not a Discord role).

        Optionally, remove them from the candidate pool from future selections.

        Args:
            ctx (SlashContext): The slash command context that called this function.
            role_name (str): The name of the role.
            n (int): The number of people to assign the role to.
            remove_from_candidate_pool (bool): If true, removes members with the role from the candidate pool for future selections.
        '''

        # Enforce that user is in a voice channel
        if await self.__memberIsInVoiceChannel(ctx):

            candidate_pool = self.__getCandidatePool(ctx)

            # Respond with an error message if n is greater than the number of people in the voice call
            if len(candidate_pool) < n:
                err_msg = "ERROR: `n` must be less than or equal to the number of people currently in the candidate pool!\n"
                err_msg += "To view the candidate pool, use the following command:\n"
                err_msg += "```/view-candidate-pool```\n"
                err_msg += "To reset the candidate pool, use the following command:\n"
                err_msg += "```/reset-candidate-pool```\n"
                await ctx.respond(err_msg)
                return []
            # Select N candidates and assign roleName to them
            else:
                selected_members = random.sample(candidate_pool, n)

                # Remove the selected members from the future candidate pool if requested
                if remove_from_candidate_pool:
                    for chosen in selected_members:
                        self.bot.add_removed_candidate(chosen)
                return selected_members

        else:
            return []

    async def __randomlySelectPeoplePubliclyImplementation(self,
                                                           ctx: SlashContext,
                                                           role_name: str = "Superstar",
                                                           n: int = 1,
                                                           remove_from_candidate_pool: bool = False) -> None:
        '''
        Randomly selects `n` people, assigns them a role name `role_name` (textually, not a Discord role), 
        and posts their roles publicly in a text channel reply.

        Optionally, remove them from the candidate pool from future selections.

        Args:
            ctx (SlashContext): The slash command context that called this function.
            role_name (str): The name of the role.
            n (int): The number of people to assign the role to.
            remove_from_candidate_pool (bool): If true, removes members with the role from the candidate pool for future selections.
        '''

        # Extract selected members
        selected_members = await self.__randomlySelectPeopleBaseImplementation(
            ctx=ctx,
            # role_name=role_name,
            n=n,
            remove_from_candidate_pool=remove_from_candidate_pool
        )

        # Only reply if there are selected_members. BaseImplementation handles error cases
        if selected_members != []:
            # Post a public reply with the assigned role
            if n == 1:
                selected_person = selected_members[0]
                await ctx.respond(f"Congrats! {selected_person.mention} has been selected to be the {role_name}")
            else:
                vowel = 'n' if (role_name[0].lower() in [
                                'a', 'e', 'i', 'o', 'u']) else ''
                response_text = f"Congrats! The following people have been selected to be a{vowel} {role_name}:\n"
                for selected in selected_members:
                    response_text += f"- {selected.mention}\n"
                await ctx.respond(response_text)

    @slash_command(
        name='select',
        description='Randomly selects n people to assign role-name to.',
    )
    @slash_option(name='role-name',
                  description='The name of the role you are assigning to N people. Default = Superstar',
                  opt_type=OptionType.STRING,
                  required=False,
                  argument_name='role_name',
                  min_length=1
                  )
    @slash_option(name='n',
                  description='The number of people you are assigning `roleName` to. Default = 1',
                  opt_type=OptionType.INTEGER,
                  required=False,
                  argument_name='n',
                  min_value=1
                  )
    @slash_option(name='remove-from-candidate-pool',
                  description='Whether to remove selected people from future /select candidate pools. Default = False',
                  opt_type=OptionType.BOOLEAN,
                  required=False,
                  argument_name='remove_from_candidate_pool'
                  )
    async def select(self,
                     ctx: SlashContext,
                     role_name: str = "Superstar",
                     n: int = 1,
                     remove_from_candidate_pool: bool = False) -> None:
        """
        Randomly selects n people to be publicly assigned a role. 
        """

        await self.__randomlySelectPeoplePubliclyImplementation(ctx=ctx,
                                                                role_name=role_name,
                                                                n=n,
                                                                remove_from_candidate_pool=remove_from_candidate_pool)

    async def __resetCandidatePoolImpl(self, ctx: SlashContext):
        voice_channel: GuildVoice = ctx.member.voice.channel
        self.bot.remove_channel_from_removed_candidates(voice_channel)
        await ctx.respond(f"Successfully reset the candidate pool for {ctx.member.voice.channel.mention}!")

    @slash_command(name="reset-candidate-pool",
                   description='Resets the candidate pool for your voice channel.')
    async def resetCandidatePool(self, ctx: SlashContext):
        """
        Resets the candidate pool for your voice channel. 
        """
        await self.__resetCandidatePoolImpl(ctx)

    async def __viewCandidatePool(self, ctx: SlashContext) -> None:
        '''
        Responds with the candidate pool of the caller's current voice channel
        '''

        if await self.__memberIsInVoiceChannel(ctx):
            candidate_pool = self.__getCandidatePool(ctx)
            if len(candidate_pool) > 1:
                response_msg = f"There are {len(candidate_pool)} candidates in the pool for {ctx.member.voice.channel.mention}:\n"
                for member in candidate_pool:
                    response_msg += f"- {member.mention}\n"
            elif len(candidate_pool) == 1:
                response_msg = f"There is {len(candidate_pool)} candidate in the pool for {ctx.member.voice.channel.mention}:\n"
                for member in candidate_pool:
                    response_msg += f"- {member.mention}\n"
            else:
                response_msg = f"There are no valid candidates in the pool for {ctx.member.voice.channel.mention}"
            await ctx.respond(response_msg)

    @slash_command(name='view-candidate-pool',
                   description='View the pool of valid candidates for your voice channel.')
    async def viewCandidatePool(self, ctx: SlashContext) -> None:
        """
        View the pool of valid candidates for your voice channel. 
        """
        await self.__viewCandidatePool(ctx)

    async def __sendMassDM(self,
                           msgDict: Dict,
                           ctx: SlashContext = None) -> bool:
        '''
        Sends DMs to multiple members using a Dict to specify what to send. 
        Handles users that don't allow DM from this server.
        Returns a boolean that indicates whether all users were able to be DM'd

        Args:
            msgDict (Dict): A dict of messages to send to each member. 
            msgDict format:
            {
                Member.id: {
                    "member_obj": Member,
                    "message_to_send": str,
                }, ...
            }
        '''

        failed_to_send_DM: List[int] = []
        successful_DMs: List[Message] = []
        for memKey in msgDict:

            # Extract the member's DM channel
            member: Member = msgDict[memKey]["member_obj"]
            dm_channel: DMChannel = await member.user.fetch_dm()

            # Send the DM
            try:
                resultingMessage = await dm_channel.send(msgDict[memKey]["message_to_send"])
                successful_DMs.append(resultingMessage)
            except HTTPException as err:
                if 'Cannot send messages to this user' == err.text:
                    failed_to_send_DM.append(memKey)
                else:
                    raise err

        # Deal with case if there are users that don't allow server DMs
        if ctx and (len(failed_to_send_DM) > 0):
            response_msg = ""
            for member_id in failed_to_send_DM:
                member = msgDict[member_id]["member_obj"]
                response_msg += f"{member.mention} "
            response_msg += ", please adjust your privacy settings for this server so that I can send you a DM.\n"
            response_msg += "All other DMs have been deleted, please call this command again after everyone allows DMs.\n\n"
            response_msg += "## Instructions:\n"

            await ctx.respond(response_msg, files=self.bot.bot_config["allowDmsInstructionsFilePaths"])

            for msg in successful_DMs:
                await msg.delete()

            return False
        else:
            return True

    async def __randomlySelectPeoplePrivatelyImplementation(self,
                                                            ctx: SlashContext,
                                                            imposter_name: str = "Imposter",
                                                            safe_role_name: str = "",
                                                            n: int = 1,
                                                            remove_from_candidate_pool: bool = False,
                                                            imposter_knowledge: bool = True
                                                            ) -> None:
        '''
        Randomly selects `n` people, assigns them a role name `role_name` (textually, not a Discord role), 
        and DMs their roles.

        Optionally, remove them from the candidate pool from future selections.

        Args:
            ctx (SlashContext): The slash command context that called this function.
            imposter_name (str): The name of the imposter role.
            safe_role_name (str): The name of the safe role. Defaults to telling people that they are "Not the imposter"
            n (int): The number of people to assign the role to.
            remove_from_candidate_pool (bool): If true, removes members with the role from the candidate pool for future selections.
        '''

        # Extract the candidate pool
        candidate_pool = self.__getCandidatePool(ctx)

        # Select the imposters
        imposters = await self.__randomlySelectPeopleBaseImplementation(
            ctx=ctx,
            # role_name=imposter_name,
            n=n,
            remove_from_candidate_pool=remove_from_candidate_pool
        )

        if imposters != []:

            # Define imposter ids and vowels
            imposter_ids = [imp.id for imp in imposters]
            safe_vowel = 'n' if ((safe_role_name != "") and (
                safe_role_name[0].lower() in ['a', 'e', 'i', 'o', 'u'])) else ''
            imp_vowel = 'n' if ((imposter_name != "") and (
                imposter_name[0].lower() in ['a', 'e', 'i', 'o', 'u'])) else ''

            # Determine the DMs to send
            if n == 1:
                if safe_role_name == "":
                    safe_DM = f":relieved: Phew! You are NOT the {imposter_name}!"
                else:
                    safe_DM = f":relieved: Phew! You're a{safe_vowel} {safe_role_name}!"
                imposter_DM = f":smiling_imp: Yikes! You are the {imposter_name}!"
            elif n > 1:
                if safe_role_name == "":
                    safe_DM = f":relieved: Phew! You are NOT a{imp_vowel} {imposter_name}!"
                else:
                    safe_DM = f":relieved: Phew! You're a{safe_vowel} {safe_role_name}!"
                imposter_DM = f":smiling_imp: Yikes! You're a{imp_vowel} {imposter_name}!\n"
                if imposter_knowledge:
                    imposter_DM += f"Your fellow {imposter_name}s are:\n"
                    for imp in imposters:
                        imposter_DM += f"- {imp.mention}\n"
            else:
                raise ValueError(f"n must be strictly positive: {n=}")

            # Construct the msgDict to be fed into the sendMassDM method
            msgDict = {}
            for member in candidate_pool:
                if member.id in imposter_ids:
                    msgDict[member.id] = {
                        "member_obj": member,
                        "message_to_send": imposter_DM
                    }
                else:
                    msgDict[member.id] = {
                        "member_obj": member,
                        "message_to_send": safe_DM
                    }

            # Send the mass DM
            if await self.__sendMassDM(msgDict=msgDict,
                                       ctx=ctx):

                # Response message if mass DM is successfully sent
                await ctx.respond("All roles have been sent, check your DMs!")

    @slash_command(
        name='imposter',
        description='Randomly selects n people to assign and privately distribute the `imposter-name` role via DMs.',
    )
    @slash_option(name='imposter-name',
                  description='The name of the role you are assigning to N people. Default = Imposter',
                  opt_type=OptionType.STRING,
                  required=False,
                  argument_name='imposter_name',
                  min_length=1
                  )
    @slash_option(name='safe-role-name',
                  description='The name of the non-imposter role. Default = NOT Imposter',
                  opt_type=OptionType.STRING,
                  required=False,
                  argument_name='safe_role_name',
                  min_length=1
                  )
    @slash_option(name='n',
                  description='The number of people you are assigning `Imposter` to. Default = 1',
                  opt_type=OptionType.INTEGER,
                  required=False,
                  argument_name='n',
                  min_value=1
                  )
    @slash_option(name='remove-from-candidate-pool',
                  description='Whether to remove selected people from future candidate pools. Default = False',
                  opt_type=OptionType.BOOLEAN,
                  required=False,
                  argument_name='remove_from_candidate_pool'
                  )
    @slash_option(name='imposter-knowledge',
                  description='Whether to reveal all imposters to the imposter team. Default = True',
                  opt_type=OptionType.BOOLEAN,
                  required=False,
                  argument_name='imposter_knowledge'
                  )
    async def imposter(self,
                       ctx: SlashContext,
                       imposter_name: str = "Imposter",
                       safe_role_name: str = "",
                       n: int = 1,
                       remove_from_candidate_pool: bool = False,
                       imposter_knowledge: bool = True
                       ) -> None:
        """
        Randomly selects n people to assign and privately distribute the `imposter-name` role via DMs. 
        """

        await self.__randomlySelectPeoplePrivatelyImplementation(
            ctx=ctx,
            imposter_name=imposter_name,
            safe_role_name=safe_role_name,
            n=n,
            remove_from_candidate_pool=remove_from_candidate_pool,
            imposter_knowledge=imposter_knowledge
        )
