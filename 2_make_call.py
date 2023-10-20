import time
from threading import Thread

import VoiPy
from VoiPy import Call_State
from typing import Optional

import pyaudio


class Agent:
    VOIP_SERVER_IP = "192.168.122.113"
    VOIP_SERVER_PORT = 5060
    AGENT_USERNAME = "6060"
    AGENT_PASSWORD = "ss6060"

    def __init__(self):
        self.phone = VoiPy.Phone(server_ip=self.VOIP_SERVER_IP,  # Voip Server Addr
                                 server_port=self.VOIP_SERVER_PORT,  # Voip Server Port
                                 username=self.AGENT_USERNAME,  # Agent Username
                                 password=self.AGENT_PASSWORD,  # Agent Password
                                 call_back=self.call_back_phone,  # CallBack
                                 voip_status=self.voip_status)  # Voip Status CallBack
        self.current_call: VoiPy.Call = None

        self.phone_status: str = "OFFLINE"
        # self.current_call_status: str

    def call_back_phone(self,
                        call_state: Call_State,  # Current Call State
                        call: dict[str, VoiPy.Call] = None,  # Calls object
                        call_id: Optional[str] = None  # Current Call Id
                        ) -> None:
        print("call_back_phone", call_state, call_id, call)

        if call_state == Call_State.DIALING:
            print("Dialing Alice")
        elif call_state == Call_State.RINGING:
            print("Ringing Alice")
        elif call_state == Call_State.ONLINE:
            print("Alice is Answered and Online")

            # Get Current call objects
            self.current_call = call.get(call_id)

            # send DTMF code
            self.current_call.sendDTMF("1")

            # Enable DTMF catch
            self.current_call.dtmf_enable = True

            audio = Thread(target=self.init_audio)
            audio.name = "audio"
            audio.start()
        elif call_state == Call_State.RINGING_ME:
            print("Ringing your phone")

            # Get Current call objects
            self.current_call = call.get(call_id)

            # Answer call
            self.current_call.answer()

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

    def make_call(self,
                  number: str):
        if self.phone_status != "ONLINE":
            return

        self.phone.call(number=number)
        print("Call To Alice")

    def audio_callback(self,
                       in_data,
                       frame_count,
                       time_info,
                       status):
        data = b'\xff' * (frame_count * 2)

        if self.current_call is None:
            return data, pyaudio.paContinue
        # send audio
        self.current_call.writeAudio(in_data)

        # receive audio
        out_data = self.current_call.readAudio(length=frame_count,
                                               blocking=True)
        if out_data:
            data = out_data

        # get DTMF code
        dtmf_code = self.current_call.getDTMF()
        if dtmf_code:
            # Enable DTMF catch
            self.current_call.dtmf_enable = True
            print(f"DTMF => {dtmf_code}")

        return data, pyaudio.paContinue

    def init_audio(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 8000
        CHUNK = 1024
        audio = pyaudio.PyAudio()

        print("Start Stream")
        try:

            stream = audio.open(format=FORMAT,
                                channels=CHANNELS,
                                output=True,
                                input=True,
                                rate=RATE,
                                frames_per_buffer=CHUNK,
                                stream_callback=self.audio_callback)
            print("Start Stream-3")
            stream.start_stream()
            print("phone_status", self.phone_status)
            while self.current_call is not None:
                time.sleep(0.01)
            print("Stop Stream")
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception:
            audio.terminate()


if __name__ == "__main__":
    agent = Agent()
    agent.start()
    agent.make_call(number="6062")
    t = 0
    running_tims_s = 100
    while t < running_tims_s:
        time.sleep(1)
        t += 1

    if agent.current_call is not None:
        agent.current_call.hangup()
        agent.current_call = None

    agent.phone.stop()
