#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : director.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 27.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
import datetime

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour, FSMBehaviour
from spade.message import Message

BUS_COUNT = 5
BUS1 = "wsd_masters2@xmpp.jp"

# STATES
STATE_WAIT = "STATE_WAIT"
STATE_APPROVE = "STATE_APPROVE"


class Director(Agent):
    class WaitBusBehav(OneShotBehaviour):
        async def run(self):
            print("WaitBusBehav running")

            self.msg = None
            self.msg = await self.receive(timeout = 15)

            if self.msg and self.msg.get_metadata == 'ready':
                self.bus_counter += 1
                if self.myAgent.bus_counter >= BUS_COUNT:
                    print("Got every bus!")
                    #self.exit_code = self.myAgent.TRANSLATION_TO_APPROVE
                else:
                    print("Waiting for more buses")
                    #self.exit_code = self.myAgent.TRANSLATION_TO_DEFAULT
            else:
                print("Still waiting...")
                #self.exit_code = self.myAgent.TRANSLATION_TO_DEFAULT

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

    class BusCheckPeriodic(PeriodicBehaviour):
        async def on_start(self):
            print("BusCheckPeriodic starts")

        async def on_end(self):
            self.agent.stop()

        async def run(self):
            print("BusCheckPeriodic running")
            msg = Message(to = "wsd_masters2@xmpp.jp")
            msg.set_metadata("performative", "query")
            msg.set_metadata("ontology", "busOntology")
            msg.set_metadata("language", "OWL-S")
            msg.body = "Are you alive?"

            await self.send(msg)
            print("Message sent!")


    def setup(self):
        print("Agent Director starting...")
        self.counter = 0
        #wait_behav = self.WaitBusBehav()
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.bus_check = self.BusCheckPeriodic(period = 15, start_at = start_at)
        #self.add_behaviour(wait_behav)
        self.add_behaviour(self.bus_check)

if __name__ == "__main__":
    director = Director("wsd_masters@xmpp.jp", "wsd_masters1234")
    director.start()

    while director.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            director.stop()
            break
    print("Director finished")
