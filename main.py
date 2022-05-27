from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
from sc2.main import (
    run_game,
)  # function that facilitates actually running the agents in games
from sc2.player import (
    Bot,
    Computer,
)  # wrapper for whether or not the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.

from Agents.dummyAgent import DummyAgent
from Agents.RLBot import RLbot
from Agents.CannonRush import CannonRushBot


run_game(  # run_game is a function that runs the game.
    maps.get("2000AtmospheresAIE"),  # the map we are playing on
    [
        Bot(
            Race.Protoss, RLbot()
        ),  # runs our coded bot, protoss race, and we pass our bot object
        Computer(Race.Terran, Difficulty.Hard),
    ],  # runs a pre-made computer agent, zerg race, with a hard difficulty.
    realtime=False,  # When set to True, the agent is limited in how long each step can take to process.
)
