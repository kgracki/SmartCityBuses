#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : director.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 27.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, FSMBehaviour
from spade.message import Message

BUS_COUNT = 5

class Director(Agent):

    class WaitBusBehav(OneShotBehaviour):
        async def run(self):
            print("WaitBusBehav running")

            msg = None
            msg = await self.receive(timeout = 15)

            if msg and msg.get_metadata == 'ready':
                self.counter += 1
                if self.counter >= BUS_COUNT:
                    self.exit_code = self.agent.TRANSLATION_TO_APPROVE
                else:
                    self.exit_code = self.agent.TRANSLATION_TO_DEFAULT
            else:
                self.exit_code = self.agent.TRANSLATION_TO_DEFAULT

    class BusApproveBehav(OneShotBehaviour):
        async def run(self):

            for bus in self.agent:
                msg = Message(to = bus)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("ontology", "busOntology")
                msg.set_metadata("language", "OWL-S")
                msg.body("You have permission to ride")

                await self.send(msg)
                print("Message to {}  sent!".format(bus))


    def setup(self):
        print("Agent Director starting...")
        b = self.WaitBusBehav()
        self.add_behaviour(b)


if __name__ == "__main__":
    director = Director("wsd_masters@xmpp.jp", "wsd_masters1234")
    director.start()

    while director.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            director.stop()
            break
    print("Director finished with code: {}".format(self.b.exit_code))
