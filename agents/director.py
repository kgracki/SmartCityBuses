#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : director.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 30.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
import asyncio
from credentials import *
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour, CyclicBehaviour, FSMBehaviour, State
from spade.message import Message

BUS_COUNT = 3

# State declaration
STATE_WAIT = "STATE_WAIT"
STATE_APPROVE = "STATE_APPROVE"


class Director(Agent):
    bus_line = None  # object containing bus line

    class BusWaitBehav(State):
        bus_counter = 0

        async def run(self):
            print("BusWaitBehav running")
            self.msg = None
            self.msg = await self.receive(timeout = 15)
            if self.msg and self.msg.get_metadata('ontology') == 'bus_ready':
                # ugly shit
                sender = "{}@{}".format(self.msg.sender[0], self.msg.sender[1])
                print("Bus {} is ready to ride".format(sender))
                if self.agent.get('{}'.format(sender)) != True:
                    self.bus_counter += 1
                self.agent.set(name = "{}".format(sender),
                               value = True)
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

    # on every three second send to all buses on line desired distance between vehicles
    class TellBusesDesiredDistance(CyclicBehaviour):
        bus_count = 3  # for now it is hardcoded, will by dynamically get from domain environment

        async def run(self):
            desired_distance = self.agent.bus_line.length_of_the_bus_route / self.bus_count

            for bus in [BUS1, BUS2, BUS3]:
                msg = Message(to = bus)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("ontology", "desired_distance")
                msg.body = "{}" . format(desired_distance)

                await self.send(msg)
                print("Message to {}  sent, with desired distance: {}". format(bus, desired_distance))
                await asyncio.sleep(3)

    class BusCheckPeriodic(PeriodicBehaviour):
        async def run(self):
            print("BusCheckPeriodic running")
            for bus in [BUS1, BUS2, BUS3]:
                print("Director knowledge {}: {}".format(bus, self.agent.get('{}'.format(bus))))
                if self.agent.get(bus) == True:
                    msg = Message(to = bus)
                    msg.set_metadata("performative", "query")
                    msg.set_metadata("ontology", "check_bus")
                    msg.set_metadata("language", "OWL-S")
                    msg.body = "Are you alive?"

                    await self.send(msg)
                    print("Message {} sent!".format(msg))
                    msg_respond = await self.receive(timeout = 5)
                    if msg_respond and msg_respond.get_metadata('ontology') == 'check_bus':
                        sender = "{}@{}".format(self.msg.sender[0],
                                                self.msg.sender[1])
                        print("Agent {} responded with message: {}".format(sender, msg_respond.body))
                    else:
                        print("Agent did not responded") 
                else:
                    print("Buses are not ready to ride")

    class DirectorCheckMessage(PeriodicBehaviour):
        async def run(self):
            print("DirectorCheckMessage running")
            msg = await self.receive(timeout = 5)
            if msg:
                print("Director got message: {}".format(msg.body))
            else:
                print("Director got no message")

    def add_bus_line(self, bus_line):
        self.bus_line = bus_line

    def setup(self):
        print("Agent Director starting...")
        # Implement periodic behaviour
        #start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.bus_check = self.BusCheckPeriodic(period = 30)
        self.message_check = self.DirectorCheckMessage(period = 10)
        # Add periodic behaviour
        self.add_behaviour(self.bus_check)
        self.add_behaviour(self.message_check)
        # Create FSB behaviour model
        fsm = FSMBehaviour()
        # Add states to FSM model
        fsm.add_state(name = STATE_WAIT, state = self.BusWaitBehav(),
                      initial = True)
        # Add transition to FSM model's state
        fsm.add_state(name = STATE_APPROVE, state = self.BusApproveBehav())
        fsm.add_transition(source = STATE_WAIT, dest = STATE_WAIT)
        fsm.add_transition(source = STATE_WAIT, dest = STATE_APPROVE)
        self.add_behaviour(fsm)

        tell_buses_desired_distance = self.TellBusesDesiredDistance()
        self.add_behaviour(tell_buses_desired_distance)


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
