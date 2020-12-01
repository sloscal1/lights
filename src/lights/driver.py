import socket
from datetime import datetime as dt
from time import sleep
from typing import List, Tuple

from lights.core import Assignment, Group, Pulse, create_message

# General constants
RATE = 10
NUM_LIGHTS = 75  # Must fit in a single byte


# Send in a something
def main() -> None:
    recorded = []
    running = True
    while running:
        key = input()
        if key == "q":
            running = False
        else:
            recorded.append((key, dt.now()))
    playback(recorded)


def test_send_manual_keyed() -> bytearray:
    return create_message(
        [Assignment(0, 0, 0),],
        [Pulse(0xFF0000, 0x303030, 7, 20),],
        [Group(list(range(0, NUM_LIGHTS, 1))),],
    )


def lightsabers() -> bytearray:
    return create_message(
        [Assignment(0, 0, 0), Assignment(0, 1, 1), Assignment(0, 2, 2),],
        [
            Pulse(0x00060A, 0x303030, 7, 20),
            Pulse(0x001000, 0x303030, 7, 25),
            Pulse(0x100000, 0x303030, 7, 15),
        ],
        [
            Group(list(range(0, NUM_LIGHTS, 3))),
            Group(list(range(1, NUM_LIGHTS, 3))),
            Group(list(range(2, NUM_LIGHTS, 3))),
        ],
    )


def send_message(message: bytearray) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.2.113", 2113))
    print(sock.sendall(message))
    print(repr(message))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def playback(recorded: List[Tuple[str, dt]]) -> None:
    testing = []
    diff = []
    for pos in range(len(recorded) - 1):
        diff.append(
            (
                recorded[pos][0],
                (recorded[pos + 1][1] - recorded[pos][1]).microseconds / 1e6,
            )
        )
    for key, timing in diff:
        testing.append((key, dt.now()))
        sleep(timing)
    testing.append((recorded[-1][0], dt.now()))
    for pos in range(len(recorded) - 1):
        print(diff[pos][1] - (testing[pos + 1][1] - testing[pos][1]).microseconds / 1e6)


if __name__ == "__main__":
    # main()
    test_send_manual_keyed()
