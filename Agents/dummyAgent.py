import random
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId


class DummyAgent(BotAI):
    async def on_step(self, iteration: int):
        print(
            f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},",
            f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},",
            f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}",
            f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}",
            f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}",
        )

        await self.distribute_workers()

        if self.townhalls:
            nexus = self.townhalls.random

            if (
                nexus.is_idle
                and self.can_afford(UnitTypeId.PROBE)
                and self.workers.amount < 17
            ):
                nexus.train(UnitTypeId.PROBE)

            elif (
                not self.structures(UnitTypeId.PYLON)
                and self.already_pending(UnitTypeId.PYLON) == 0
            ):
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus)

            elif self.structures(UnitTypeId.PYLON).amount < 4:
                if self.can_afford(UnitTypeId.PYLON):
                    # build from the closest pylon towards the enemy
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(nexus)
                    # build as far away from target_pylon as possible:
                    pos = target_pylon.position.towards(
                        self.enemy_start_locations[0], random.randrange(8, 15)
                    )
                    await self.build(UnitTypeId.PYLON, near=pos)

            elif self.structures(UnitTypeId.FORGE) == 0:
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(
                        UnitTypeId.FORGE,
                        near=self.structures(UnitTypeId.PYLON).closest_to(nexus),
                    )

            elif (
                self.structures(UnitTypeId.FORGE).ready
                and self.structures(UnitTypeId.PHOTONCANNON).amount < 3
            ):
                if self.can_afford(UnitTypeId.PHOTONCANNON):  # can we afford a cannon?
                    await self.build(
                        UnitTypeId.PHOTONCANNON, near=nexus
                    )  # build one near the nexus

        else:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()
