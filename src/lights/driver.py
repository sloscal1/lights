from collections import defaultdict
from datetime import datetime as dt
from itertools import chain
import socket
from time import sleep
from typing import List, Tuple, Dict


def to_bytes(value: int, byte_length: int) -> bytearray:
    return bytearray(value.to_bytes(byte_length, "big"))


MESSAGE_START = bytearray.fromhex("FF FF FF")
BEGIN = bytearray.fromhex("00 00 02")
END_PREAMBLE = bytearray.fromhex("FF")
NUM_MODES = 1  # Must fit in a single byte
NUM_LIGHTS = 75  # Must fit in a single byte
NUM_GROUPS = 1  # Must fit in a single byte
NUM_BANDS = 11
RGB_BYTES = 3
STREAM_SIZE = to_bytes(NUM_BANDS * RGB_BYTES, 2)
STREAMING = bytearray.fromhex("00")


class Assignment:
    def __init__(self, start_time: int, group_id: int, mode_id: int) -> None:
        self.content = (
            to_bytes(start_time, 4)
            + to_bytes(group_id, 1)
            + to_bytes(mode_id, 1)
        )

    def get_content(self) -> bytearray:
        return self.content


class Pulse:
    def __init__(self, start_color: int, end_color: int, num_steps: int, delay: int) -> None:
        self.start_color = to_bytes(start_color, 3)
        end_color = to_bytes(end_color, 3)
        self.num_steps = to_bytes(num_steps, 1)
        self.delay = to_bytes(delay, 1)
        self.inc = bytearray()
        self.dir = ""  # binary string during construction...
        for byte in range(3):
            self.inc.append(max(abs(self.start_color[byte] - end_color[byte]) // num_steps - 1, 0))
            self.dir += "0" if end_color[byte] >= self.start_color[byte] else "1"
        self.dir = to_bytes(int(self.dir, 2), 1)  # Single byte once dir is known

    def get_content(self) -> bytearray:
        return (
            self.start_color
            + self.inc
            + self.dir
            + self.num_steps
            + self.delay
        )


def test_message(assignments: List[Assignment], modes: List[Pulse], groups_to_bands: Dict[int, int]) -> bytearray:
    content = (
        MESSAGE_START
        + to_bytes(10, 2)
        + to_bytes(NUM_MODES, 1)
        + to_bytes(NUM_LIGHTS, 1)
        + to_bytes(NUM_GROUPS, 1)
        + to_bytes(len(assignments), 4)
        + BEGIN
        + bytearray(chain.from_iterable([mode.get_content() for mode in modes]))
        + bytearray(chain.from_iterable([assign.get_content() for assign in assignments]))
        + bytearray([i for i in range(NUM_LIGHTS)])
        + END_PREAMBLE
        + STREAM_SIZE
        + STREAMING
        + to_bytes(len(groups_to_bands), 1)
        + bytearray([groups_to_bands[i] for i in range(NUM_GROUPS)])
    )

    return content

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


def test_send_manual_keyed() -> None:
    groups_to_bands = defaultdict(lambda: 0xFF)
    groups_to_bands[0] = 0
    message = test_message(
        [Assignment(0, 0, 0)],
        [Pulse(0x0000FF, 0x000000, 2, 1)],
        groups_to_bands
    )
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
        diff.append((recorded[pos][0], (recorded[pos + 1][1] - recorded[pos][1]).microseconds / 1e6))
    for key, timing in diff:
        testing.append((key, dt.now()))
        sleep(timing)
    testing.append((recorded[-1][0], dt.now()))
    for pos in range(len(recorded) - 1):
        print(
            diff[pos][1]
            - (testing[pos + 1][1] - testing[pos][1]).microseconds / 1e6
        )


if __name__ == "__main__":
    # main()
    # print(Pulse(0x0000FF, 0x000000, 2, 1).get_content())
    test_send_manual_keyed()
