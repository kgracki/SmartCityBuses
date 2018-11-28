#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : director.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 28.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
import datetime
from credentials import *
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour, FSMBehaviour, State
from spade.message import Message

BUS_COUNT = 3

# STATES
STATE_WAIT = "STATE_WAIT"
STATE_APPROVE = "STATE_APPROVE"


class Director(Agent):

    class BusWaitBehav(State):
        bus_counter = 0

        async def run(self):
            print("BusWaitBehav running")
            self.msg = None
            self.msg = await self.receive(timeout = 15)
            if self.msg and self.msg.get_metadata('ontology') == 'bus_ready':
                print("Bus {} is ready to ride".format(self.msg.sender))
                self.bus_counter += 1
                if self.bus_counter >= BUS_COUNT:
                    print("Got every bus!")
                    self.set_next_state(STATE_APPROVE)
                    #self.exit_code = self.myAgent.TRANSLATION_TO_APPROVE
                else:
                    print("Waiting for more buses. I've got {}/{}".
                          format(self.bus_counter, BUS_COUNT))
                    self.set_next_state(STATE_WAIT)
                    #self.exit_code = self.myAgent.TRANSLATION_TO_DEFAULT
            else:
                print("Still waiting...")
                self.set_next_state(STATE_WAIT)
                #self.exit_code = self.myAgent.TRANSLATION_TO_DEFAULT

    class BusApproveBehav(State):
        async def run(self):
            for bus in [BUS1, BUS2, BUS3]:
                msg = Message(to = bus)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("ontology", "director_approval")
                msg.set_metadata("language", "OWL-S")
                msg.body = "You have permission to ride"

                await self.send(msg)
                print("Message to {}  sent!".format(bus))

    class BusCheckPeriodic(PeriodicBehaviour):
        async def run(self):
            print("BusCheckPeriodic running")
            for bus in [BUS1, BUS2, BUS3]:
                msg = Message(to = bus)
                msg.set_metadata("performative", "query")
                msg.set_metadata("ontology", "check_bus")
                msg.set_metadata("language", "OWL-S")
                msg.body = "Are you alive?"

                await self.send(msg)
                print("Message {} sent!".format(msg))


    def setup(self):
        print("Agent Director starting...")
        #self.wait_behav = self.BsWaitBehav()
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.bus_check = self.BusCheckPeriodic(period = 30, start_at = start_at)
        #self.add_behaviour(self.wait_behav)
        self.add_behaviour(self.bus_check)

        fsm = FSMBehaviour()
        fsm.add_state(name = STATE_WAIT, state = self.BusWaitBehav(),
                      initial = True)
        fsm.add_state(name = STATE_APPROVE, state = self.BusApproveBehav())
        fsm.add_transition(source = STATE_WAIT, dest = STATE_WAIT)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_APPROVE)
        self.add_behaviour(fsm)

if __name__ == "__main__":
    director = Director(DIRECTOR, DIRECTOR_PASSWD)
    director.start()

    while director.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            director.stop()
            break
    print("Director finished")
