#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : bus.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 30.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
import sys
sys.path.insert(0, '../')
from credentials import *
sys.path.insert(0, 'map_data/')
from distance_compute import distance_compute

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour,PeriodicBehaviour, FSMBehaviour, State
from spade.message import Message

# State declaration
STATE_START             = "STATE_START"
STATE_WAIT              = "STATE_WAIT"
STATE_APPROVE           = "STATE_APPROVE"
STATE_DRIVING           = "STATE_DRIVING"
STATE_PASS_KNOWLEDGE    = "STATE_PASS_KNOWLEDGE"
STATE_GET_COORDS        = "STATE_GET_COORDS"

class Bus(Agent):

    class StartRideBehav(State):
        async def run(self):
            print("StartRideBehav running")

            msg = Message(to = DIRECTOR)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "bus_ready")
            msg.set_metadata("language", "OWL-S")
            msg.body = "I'm ready to ride"

            await self.send(msg)
            print("Message {} sent".format(msg))
            self.set_next_state(STATE_WAIT)

    class WaitForApproval(State):
        async def run(self):
           self.msg = await self.receive(timeout = 10)
           if self.msg and self.msg.get_metadata('ontology') ==             'director_approval':
               print("I've got approval to ride!")
               self.set(name = "approval", value = True)
               print("My current: {}".format(self.agent.get('approval')))
               self.set_next_state(STATE_DRIVING)
           else:
               print("Didn't get approval yet")
               self.set(name = "approval", value = False)
               print("My current state: {}".format(self.agent.get('approval')))
               self.set_next_state(STATE_START)

    class AnswerOnCheck(PeriodicBehaviour):
        async def run(self):
            print("AnswerOnCheck running")
            msg = await self.receive(timeout = 30)
            if msg and msg.get_metadata('ontology') == 'check_bus':
                print("{} -> I'm alive".format(self.agent))
                msg = Message(to = DIRECTOR)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("ontology", "check_bus")
                msg.set_metadata("language", "OWL-S")
                msg.body = "I'm alive"

                await self.send(msg)
                print("Message {} sent!".format(msg))

    class Driving(State):
        async def run(self):
            print("Driving running")
            print("My knowledge: {}".format(self.agent.get('approval')))
            time.sleep(5)
            self.set_next_state(STATE_PASS_KNOWLEDGE)

    class PassYourKnowledge(State):
        async def run(self):
            print("PassYourKnowledge running")
            print("I AM {}".format(self.agent.jid))
            self.set_next_state(STATE_DRIVING)

    class BusCheckMessage(PeriodicBehaviour):
        async def run(self):
            print("BusCheckMessage running")
            msg = await self.receive(timeout = 5)
            if msg:
                print("Bus {} got message: {}".format(self.agent.jid,
                                                     msg.body))
    class BusGetCoords(PeriodicBehaviour):
        async def run(self):
            print("BusGetCoords running")
            # Get bus coordinates
            #bus_coord = 
            #self.agent.set(name = 'coords', value = bus_coord)

    def setup(self):
        print("Agent Bus starting")
        # Create handles for agent's behaviour
        start_ride = self.StartRideBehav()
        answer_check = self.AnswerOnCheck(period = 10)
        message_check = self.BusCheckMessage(period = 10)
        get_coords = self.BusGetCoords(period = 15)
        # Create FSM object
        fsm = FSMBehaviour()
        # Add states to your FSM object
        fsm.add_state(name = STATE_START, state = self.StartRideBehav(),
                      initial = True)
        fsm.add_state(name = STATE_WAIT, state = self.WaitForApproval())
        fsm.add_state(name = STATE_DRIVING, state = self.Driving())
        fsm.add_state(name = STATE_PASS_KNOWLEDGE,
                      state = self.PassYourKnowledge())
        # Add transitions of your FSM object
        fsm.add_transition(source = STATE_START, dest = STATE_WAIT)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_START)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_WAIT)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_DRIVING)
        fsm.add_transition(source = STATE_DRIVING, dest = STATE_DRIVING)
        fsm.add_transition(source = STATE_DRIVING, dest = STATE_PASS_KNOWLEDGE)
        fsm.add_transition(source = STATE_PASS_KNOWLEDGE, dest = STATE_DRIVING)
        # Add agent's behaviour
        self.add_behaviour(answer_check)
        self.add_behaviour(start_ride)
        self.add_behaviour(get_coords)
        self.add_behaviour(fsm)

if __name__ == "__main__":
    bus1 = Bus(BUS1, BUS1_PASSWD)
    bus2 = Bus(BUS2, BUS2_PASSWD)
    bus3 = Bus(BUS3, BUS3_PASSWD)
    bus4 = Bus(BUS4, BUS4_PASSWD)
    bus1.start()
    bus2.start()
    bus3.start()
    bus4.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            bus1.stop()
            bus2.stop()
            bus3.stop()
            bus4.stop()
            break
    print("Bus finished")
