import time
from threading import Thread, Timer

import VoiPy
from VoiPy import Call_State
from typing import Optional

import pyaudio


class Agent:
    VOIP_SERVER_IP = "192.168.122.113"
    VOIP_SERVER_PORT = 5060
    AGENT_USERNAME = "6060"
    AGENT_PASSWORD = "ss6060"
    TRANSFER_NUMBER = "6061"

    def __init__(self):
        self.phone = VoiPy.Phone(server_ip=self.VOIP_SERVER_IP,  # Voip Server Addr
                                 server_port=self.VOIP_SERVER_PORT,  # Voip Server Port
                                 username=self.AGENT_USERNAME,  # Agent Username
                                 password=self.AGENT_PASSWORD,  # Agent Password
                                 call_back=self.call_back_phone,  # CallBack
                                 voip_status=self.voip_status,  # Voip Status CallBack
                                 )
        self.current_call: VoiPy.Call = None

        self.phone_status: str = "OFFLINE"
        # self.current_call_status: str

    def call_back_phone(self,
                        call_state: Call_State,  # Current Call State
                        call: dict[str, VoiPy.Call] = None,  # Calls object
                        call_id: Optional[str] = None  # Current Call Id
                        ) -> None:
        print("call_back_phone", call_state, call_id, call)

        if call_state == Call_State.ONLINE:
            print("Alice is Answered and Online")

            # Get Current call objects
            self.current_call = call.get(call_id)

            transfer = Timer(interval=2, function=self.transfer)
            transfer.name = "transfer"
            transfer.start()

        elif call_state == Call_State.RINGING_ME:
            print("Ringing your phone")

            # Get Current call objects
            self.current_call = call.get(call_id)

            # Answer call
            self.current_call.answer()

        elif call_state == Call_State.TRANSFER_ACCEPTED:
            if self.current_call:
                self.current_call = None

        elif call_state == Call_State.DECLINE or \
                call_state == Call_State.END or \
                call_state == Call_State.BUSY:

            if call_state == Call_State.BUSY:
                print("Alice is Busy!")

            print("should end call")
            if self.current_call:
                self.current_call = None
            current_call = call.get(call_id)
            current_call.cancel()


    def voip_status(self,
                    status: str):
        print(f"Call Status {status}")
        self.phone_status = status

    def start(self):

        self.phone.start()  # Start and register voip

    def stop(self):

        self.phone.stop()  # Stop and deregister voip

    def transfer(self):
        # Transfer current call to TRANSFER_NUMBER
        self.current_call.transfer(transfer_to=self.TRANSFER_NUMBER)


if __name__ == "__main__":
    agent = Agent()
    agent.start()
    t = 0
    running_tims_s = 100
    while t < running_tims_s:
        time.sleep(1)
        t += 1

    if agent.current_call is not None:
        agent.current_call.hangup()
        agent.current_call = None

    agent.phone.stop()
