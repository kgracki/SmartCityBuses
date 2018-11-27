#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : bus.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 27.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
from credentials import *

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, FSMBehaviour
from spade.message import Message


class Bus(Agent):

    class StartRideBehav(OneShotBehaviour):
        async def run(self):
            print("StartRideBehav running")

            msg = Message(to = DIRECTOR)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "busOntology")
            msg.set_metadata("language", "OWL-S")
            msg.body("I'm ready to ride")

            await self.send(msg)
            print("Message to {} sent".format(DIRECTOR))

    def setup(self):
        print("Agent Bus starting")
        b = self.StartRideBehav()
        self.add_behaviour(b)

if __name__ == "__main__":
    bus = Bus(BUS1, BUS1_PASSWD)
    bus.start()

    while bus.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            bus.stop()
            break
    print("Bus finished")
