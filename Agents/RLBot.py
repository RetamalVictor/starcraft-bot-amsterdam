#Heavily inspired from https://pythonprogramming.net/scouting-visual-input-starcraft-ii-ai-python-sc2-tutorial/?completed=/deep-learning-starcraft-ii-ai-python-sc2-tutorial/
from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.ids.unit_typeid import UnitTypeId
import random

import cv2
import numpy as np

class RLbot(BotAI): # inhereits from BotAI (part of BurnySC2)
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50

    async def train_probe(self, nexus, supply_remaining):
          if nexus.is_idle and self.can_afford(UnitTypeId.PROBE) and\
               supply_remaining > 4 and self.workers.amount<22:
                nexus.train(UnitTypeId.PROBE) 

    async def build_pylon(self,nexus):
        if not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus)
        
        elif self.structures(UnitTypeId.PYLON).amount < 5:
            if self.can_afford(UnitTypeId.PYLON):
                # build from the closest pylon towards the enemy
                target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                # build as far away from target_pylon as possible:
                pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randrange(8, 15))
                await self.build(UnitTypeId.PYLON, near=pos)

    async def build_assimilator(self,nexus):
       if self.structures(UnitTypeId.ASSIMILATOR).amount <= 1:
                for nexus in self.structures(UnitTypeId.NEXUS):
                    vespenes = self.vespene_geyser.closer_than(15, nexus)
                    for vespene in vespenes:
                        if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                            await self.build(UnitTypeId.ASSIMILATOR, vespene) 

    async def build_forge(self,nexus):
            if not self.structures(UnitTypeId.FORGE) and self.structures(UnitTypeId.ASSIMILATOR).amount > 1:  # if we don't have a forge:
                if self.can_afford(UnitTypeId.FORGE):  # and we can afford one:
                    # build one near the Pylon that is closest to the nexus:
                    await self.build(UnitTypeId.FORGE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))

    async def train_voidray(self):
        # if we have less than 10 voidrays, build one:
        if self.structures(UnitTypeId.VOIDRAY).amount < 10 and self.can_afford(UnitTypeId.VOIDRAY):
            for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                if self.can_afford(UnitTypeId.VOIDRAY):
                    sg.train(UnitTypeId.VOIDRAY)

    async def build_cannon(self,nexus, nb_cannons= 3):
        # if we have less than 3 cannons, let's build some more if possible:
            if self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < nb_cannons:
                if self.can_afford(UnitTypeId.PHOTONCANNON):  # can we afford a cannon?
                    await self.build(UnitTypeId.PHOTONCANNON, near=nexus)  # build one near the nexus
    
    async def build_gateway(self,nexus):    
            # a gateway? this gets us towards cyb core > stargate > void ray
            if not self.structures(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
    
    async def build_cybernetic(self,nexus):
            # a cyber core? this gets us towards stargate > void ray
            if not self.structures(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
 
    async def build_stargate(self, nexus):
            if self.structures(UnitTypeId.STARGATE).amount < 3:
                if self.can_afford(UnitTypeId.STARGATE):
                    await self.build(UnitTypeId.STARGATE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))

    async def expand(self):
        if self.townhalls.amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and\
            self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()

    async def intel(self,nexus_list):
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
        
        for nexus in nexus_list:
            nex_pos = nexus.position
            #print(nex_pos)
            cv2.circle(game_data, (int(nex_pos[0]), int(nex_pos[1])), 10, (0, 255, 0), -1)  # BGR

        # flip horizontally to make our final fix in visual representation:
        flipped = cv2.flip(game_data, 0)
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)

        cv2.imshow('Intel', resized)
        cv2.waitKey(1)

    async def on_step(self, iteration: int): # on_step is a method that is called every step of the game.
        """
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},", \
            f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},", \
            f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}", \
            f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}", \
            f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}")
            """
        
        self.iteration = iteration
        
        # begin logic:

        await self.distribute_workers() # put idle workers back to work

        if self.townhalls:  # do we have a nexus?
            nexus = self.townhalls.random  # select one (will just be one for now)
            await self.train_voidray()
            supply_remaining = self.supply_cap - self.supply_used
            if supply_remaining > 4:
                await self.train_probe(nexus, supply_remaining)
            else:
                # if we dont have *any* pylons, we'll build one close to the nexus.
                await self.build_pylon(nexus)
    
            await self.build_assimilator(nexus)
            await self.build_forge(nexus)
            await self.build_cannon(nexus)
            await self.build_gateway(nexus)
            await self.build_cybernetic(nexus)
            await self.build_stargate(nexus)
            await self.expand()
            await self.intel(self.townhalls)

        else:
            if self.can_afford(UnitTypeId.NEXUS):  # can we afford one?
                await self.expand_now()  # build one!
        
        
        # if we have more than 3 voidrays, let's attack!
        if self.units(UnitTypeId.VOIDRAY).amount >= 3:
            if self.enemy_units:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_units))
            
            elif self.enemy_structures:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_structures))

            # otherwise attack enemy starting position
            else:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(self.enemy_start_locations[0])


