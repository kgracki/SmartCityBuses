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
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour
from spade.message import Message

STATE_WAIT = "STATE_WAIT"
STATE_APPROVE = "STATE_APPROVE"
STATE_DRIVING = "STATE_DRIVING"

class Bus(Agent):

    class StartRideBehav(OneShotBehaviour):
        async def run(self):
            print("StartRideBehav running")

            msg = Message(to = DIRECTOR)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "bus_ready")
            msg.set_metadata("language", "OWL-S")
            msg.body = "I'm ready to ride"

            await self.send(msg)
            print("Message {} sent".format(msg))

    class WaitForApproval(State):
        async def run(self):
           self.msg = await self.receive(timeout = 10)
           if self.msg and self.msg.get_metadata('ontology') == 'director_approval':
               print("I've got approval to ride!")
               slef.set_next_state(STATE_DRIVING)
           else:
               print("Didn't get approval yet")
               self.set_next_state(STATE_WAIT)

    class Driving(State):
        async def run(self):
            print("Driving running")


    def setup(self):
        print("Agent Bus starting")
        b = self.StartRideBehav()
        self.add_behaviour(b)

        fsm = FSMBehaviour()
        fsm.add_state(name = STATE_WAIT, state = self.WaitForApproval(),
                      initial = True)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_WAIT)
        fsm.add_behaviour(source = STATE_WAIT, dest = STATE_DRIVING)
        self.add_behaviour(fsm)

if __name__ == "__main__":
    bus1 = Bus(BUS1, BUS1_PASSWD)
    bus2 = Bus(BUS2, BUS2_PASSWD)
    bus3 = Bus(BUS3, BUS3_PASSWD)
    bus1.start()
    bus2.start()
    bus3.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            bus1.stop()
            bus2.stop()
            bus3.stop()
            break
    print("Bus finished")
