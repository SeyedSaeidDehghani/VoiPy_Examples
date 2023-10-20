import time

import VoiPy
from VoiPy import Call_State
from typing import Optional

VOIP_SERVER_IP = "192.168.122.113"
VOIP_SERVER_PORT = 5060
AGENT_USERNAME = "6060"
AGENT_PASSWORD = "ss6060"


def call_back_phone(call_state: Call_State,  # Current Call State
                    call: dict[str, VoiPy.Call] = None,  # Calls object
                    call_id: Optional[str] = None  # Current Call Id
                    ) -> None:
    print("call_back_phone", call_state, call_id, call)

    if call_id is None:
        return

    current_call = call.get(call_id, None)  # Get Current call objects

    if current_call:
        pass


def voip_status(status: str):
    print(f"Call Status {status}")


def run():
    phone = VoiPy.Phone(server_ip=VOIP_SERVER_IP,  # Voip Server Addr
                        server_port=VOIP_SERVER_PORT,  # Voip Server Port
                        username=AGENT_USERNAME,  # Agent Username
                        password=AGENT_PASSWORD,  # Agent Password
                        call_back=call_back_phone,  # CallBack
                        voip_status=voip_status)  # Voip Status CallBack

    # Start and register voip
    phone.start()

    t = 0
    # Running Time Second
    running_tims_s = 100
    while t < running_tims_s:
        time.sleep(1)
        t += 1

    # Stop and deregister voip
    phone.stop()


if __name__ == "__main__":
    run()
