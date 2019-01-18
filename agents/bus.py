#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : bus.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 27.11.2018
# Last Modified Date: 30.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

import time
import datetime
import sys
import asyncio
sys.path.insert(0, '../')
from credentials import *
from simulation_settings import *
sys.path.insert(0, 'map_data/')
from distance_compute import distance_compute

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour,PeriodicBehaviour, FSMBehaviour, State
from spade.message import Message
from spade.template import Template
from bus.bus_velocity_regulator import BusVelocityRegulator;

# State declaration
STATE_START             = "STATE_START"
STATE_WAIT              = "STATE_WAIT"
STATE_APPROVE           = "STATE_APPROVE"
STATE_DRIVING           = "STATE_DRIVING"
STATE_PASS_KNOWLEDGE    = "STATE_PASS_KNOWLEDGE"
STATE_GET_COORDS        = "STATE_GET_COORDS"


class Bus(Agent):
    bus_navigator = None
    desired_distance = 0
    next_bus_position = None
    next_bus_direction = None
    next_bus = None
    next_bus_update_timestamp = 0;
    previous_bus = None
    previous_bus_position = None
    previous_bus_direction = None
    previous_bus_update_timestamp = 0;

    class StartRideBehav(State):
        async def run(self):
            self.agent.better_printer("StartRideBehav running")

            msg = Message(to = DIRECTOR)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "bus_ready")
            msg.set_metadata("language", "OWL-S")
            msg.body = "I'm ready to ride"

            await self.send(msg)
            self.agent.better_printer("Message {} sent".format(msg))
            self.set_next_state(STATE_WAIT)

    class WaitForApproval(State):
        async def run(self):
           self.msg = await self.receive(timeout = 10)
           if self.msg and self.msg.get_metadata('ontology') ==             'director_approval':
               self.agent.better_printer("I've got approval to ride!")
               self.set(name = "approval", value = True)
               self.agent.better_printer("My current: {}".format(self.agent.get('approval')))
               self.agent.bus_navigator.start_time = datetime.datetime.now()
               self.set_next_state(STATE_DRIVING)
           else:
               self.agent.better_printer("Didn't get approval yet")
               self.set(name = "approval", value = False)
               self.agent.better_printer("My current state: {}".format(self.agent.get('approval')))
               self.set_next_state(STATE_START)

    class AnswerOnCheck(PeriodicBehaviour):
        async def run(self):
            self.agent.better_printer("AnswerOnCheck running")
            msg = await self.receive(timeout = 30)
            if msg and msg.get_metadata('ontology') == 'check_bus':
                self.agent.better_printer("{} -> I'm alive".format(self.agent))
                msg = Message(to = DIRECTOR)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("ontology", "check_bus")
                msg.set_metadata("language", "OWL-S")
                msg.body = "I'm alive"

                await self.send(msg)
                self.agent.better_printer("Message {} sent!".format(msg))

    class Driving(State):
        async def send_position_to_neighbours(self):
            for bus in [self.agent.next_bus, self.agent.previous_bus]:
                msg = Message(to=bus)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("information", "my_position")
                msg.set_metadata("timestamp", time.time())
                msg.set_metadata("direction", "{}".format(self.agent.bus_navigator.direction))
                msg.body = "{}".format(self.agent.bus_navigator.position_on_bus_line)
                self.agent.better_printer("{}".format(self.agent.bus_navigator.position_on_bus_line))

                await self.send(msg)

        async def run(self):
            self.agent.bus_navigator.update_position_on_bus_line(datetime.datetime.now());
            # self.agent.better_printer("Driving running")
            self.agent.better_printer(self.agent.bus_navigator.report_position())
            # self.agent.better_printer("My knowledge: {}".format(self.agent.get('approval')))
            await self.send_position_to_neighbours()
            await asyncio.sleep(0.5)
            self.set_next_state(STATE_PASS_KNOWLEDGE)

    class PassYourKnowledge(State):
        async def run(self):
            # self.agent.better_printer("PassYourKnowledge running")
            # self.agent.better_printer("I AM {}".format(self.agent.jid))
            self.set_next_state(STATE_DRIVING)

    class BusCheckMessage(PeriodicBehaviour):
        async def run(self):
            self.agent.better_printer("BusCheckMessage running")
            msg = await self.receive(timeout = 3)
            if msg:
                self.agent.better_printer("Bus got message: {}".format(msg.body))
                if msg.get_metadata("information") == "desired_distance":
                    self.agent.keep_desired_distance(float(msg.body))
                elif msg.get_metadata("information") == "my_position":
                    self.agent.get_position_of_neighbour_buses(msg)

    class BusGetCoords(PeriodicBehaviour):
        async def run(self):
            self.agent.better_printer("BusGetCoords running")
            # Get bus coordinates
            #bus_coord =
            #self.agent.set(name = 'coords', value = bus_coord)

    def better_printer(self, message_to_print):
        print("~~[{}]: {}".format(self.jid, message_to_print))

    def keep_desired_distance(self, desired_distance):
        self.desired_distance = desired_distance
        self.better_printer("Get desired distance: {} " . format(desired_distance))

    def check_if_there_is_a_need_to_change_bus_velocity(self):
        if self.desired_distance == 0:
            return

        max_velocity = (1 + SIMULATION_SETTINGS['max_velocity_change']) * SIMULATION_SETTINGS['bus_nominal_velocity']
        max_velocity_change = SIMULATION_SETTINGS['max_velocity_change'] * SIMULATION_SETTINGS['bus_nominal_velocity']

        neighbours_info = {
            'next_bus': self.next_bus,
            'next_bus_position': self.next_bus_position,
            'next_bus_direction': self.next_bus_direction,
            'next_bus_update_timestamp': self.next_bus_update_timestamp,
            'previous_bus': self.previous_bus,
            'previous_bus_position': self.previous_bus_position,
            'previous_bus_direction': self.previous_bus_direction,
            'previous_bus_update_timestamp': self.previous_bus_update_timestamp,
        }
        velocity_change = BusVelocityRegulator.calculate_new_bus_velocity(self.bus_navigator, max_velocity, max_velocity_change, neighbours_info)

        self.better_printer("Velocity change: {}, now velocity is: {}" . format(velocity_change, self.bus_navigator.velocity))

    def get_position_of_neighbour_buses(self, msg):
        sender = "{}@{}".format(msg.sender[0], msg.sender[1])
        if self.next_bus == sender:
            if msg.get_metadata("timestamp") > self.next_bus_update_timestamp:
                self.next_bus_position = msg.body
                self.next_bus_direction = msg.get_metadata("direction")
                self.next_bus_update_timestamp = msg.get_metadata("timestamp")
        elif self.previous_bus == sender:
            if msg.get_metadata("timestamp") > self.previous_bus_update_timestamp:
                self.previous_bus_position = msg.body
                self.previous_bus_direction = msg.get_metadata("direction")
                self.previous_bus_update_timestamp = msg.get_metadata("timestamp")

        if self.next_bus_position is not None and self.previous_bus_position is not None:
            self.check_if_there_is_a_need_to_change_bus_velocity()

    def setup(self):
        self.better_printer("Agent Bus starting")
        # Create handles for agent's behaviour
        start_ride = self.StartRideBehav()
        answer_check = self.AnswerOnCheck(period = 10)
        message_check = self.BusCheckMessage(period = 10)
        template_desired_distance = Template()
        template_desired_distance.set_metadata("information", "desired_distance")

        template_my_position = Template()
        template_my_position.set_metadata("information", "my_position")
        self.add_behaviour(message_check, template_desired_distance | template_my_position)
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

    def add_bus_navigator(self, bus_navigator):
        self.bus_navigator = bus_navigator

    def add_line(self, bus_line):
        self.bus_navigator.bus_line = bus_line

    def set_neighboring_buses(self, next_bus, previous_bus):
        self.next_bus = next_bus
        self.previous_bus = previous_bus


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
