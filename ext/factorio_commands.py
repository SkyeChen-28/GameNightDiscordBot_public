"""
Defines slash commands relevant to Factorio gaming
"""
# import os
# import asyncio
# from typing import List, Dict
from enum import StrEnum, auto

import numpy as np
import interactions as its

THRUSTER_WIDTH = 4


class Quality(StrEnum):
    """
    An Enum for qualities
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


def v_max(F_thrust_MN: float, mass: float, width: int) -> float:
    """
    Calculates the max speed of the space platform

    Args:
        F_thrust_MN (float): The thrust force of all thrusters in mega-newtons
        mass (float): The mass of the space platform in tonnes
        width (int): The max width of the space platform in tiles

    Returns:
        float: The max speed of the space platform
    """

    inner = (((480000 * F_thrust_MN) / (mass + 10000) - 480) / width) + 9
    ans = 10 * np.sqrt(inner) - 30
    return ans


def F_thrust_max(num_of_thrusters: int, quality_of_thrusters: Quality) -> float:
    """
    Calculates the max thrust given some number of thrusters and their quality. 

    Args:
        num_of_thrusters (int): 
        quality_of_thrusters (Quality): 

    Returns:
        float: The max thrust of all the thrusters on your space platform
    """

    F_per_thruster_dict = {
        Quality.COMMON: 102,
        Quality.UNCOMMON: 132,
        Quality.RARE: 163,
        Quality.EPIC: 193,
        Quality.LEGENDARY: 254,
    }

    F_per_thruster = F_per_thruster_dict[quality_of_thrusters]
    return F_per_thruster * num_of_thrusters


class FactorioCommands(its.Extension):
    """
    A class for Factorio related commands
    """

    @its.slash_command(
        name="space_platform_max_speed_calc",
        description="Calculates the max speed of your space platform."
    )
    @its.slash_option(
        name="max_width",
        description="The max width of your platform in tiles.",
        opt_type=its.OptionType.INTEGER,
        required=True,
        min_value=1,
    )
    @its.slash_option(
        name="num_of_thrusters",
        description="The number of thrusters on your platform.",
        opt_type=its.OptionType.INTEGER,
        required=True,
        min_value=1,
    )
    @its.slash_option(
        name="mass",
        description="The mass of your platform in tonnes.",
        opt_type=its.OptionType.NUMBER,
        required=True,
        min_value=0.1,
    )
    @its.slash_option(
        name="quality_of_thrusters",
        description="Specify the quality of your thrusters here",
        required=True,
        opt_type=its.OptionType.STRING,
        choices=[
            its.SlashCommandChoice(name=quality, value=quality)
            for quality in Quality
        ],
    )
    async def space_platform_max_speed_calc(
        self,
        ctx: its.SlashContext,
        max_width: int,
        num_of_thrusters: int,
        mass: float,
        quality_of_thrusters: str,
    ):
        """
        Calculates the max speed of your space platform

        Args:
            ctx (its.SlashContext): _description_
            max_width (int): The max width of your platform in tiles.
            num_of_thrusters (int): The number of thrusters on your platform.
            mass (float): The mass of your platform in tonnes.
            quality_of_thrusters (str): The quality of your thrusters. 
        """

        if THRUSTER_WIDTH * num_of_thrusters > max_width:
            response = f"Error: It's impossible to fit {num_of_thrusters} thrusters on a space platform with max width = {max_width}.\n"
            response += "Each thruster has width = 4, thus, we require that 4 * num_of_thrusters <= max_width."
            await ctx.respond(response)
        else:
            max_v = v_max(
                F_thrust_MN=F_thrust_max(
                    num_of_thrusters=num_of_thrusters, quality_of_thrusters=quality_of_thrusters),
                mass=mass,
                width=max_width,
            )
            response  = f"The max speed of your space platform after departure is: {max_v - 10:.2f} km/s\n"
            response += f"The max speed of your space platform upon arrival is: {max_v + 10:.2f} km/s"
            await ctx.respond(response)
