from collections import defaultdict
from functools import partial
from itertools import chain
from typing import List


def to_bytes(value: int, byte_length: int) -> bytearray:
    return bytearray(value.to_bytes(byte_length, "big"))


NUM_BANDS = 11
RGB_BYTES = 3

# Message parts
MESSAGE_START = bytearray.fromhex("FF FF FF")
BEGIN = bytearray.fromhex("00 00 02")
END_PREAMBLE = bytearray.fromhex("FF")
END_GROUP = bytearray.fromhex("FF")
NOT_STREAM_SIZE = to_bytes(0, 2)
NOT_STREAMING = bytearray.fromhex("00")
STREAM_SIZE = to_bytes(NUM_BANDS * RGB_BYTES, 2)
STREAMING = bytearray.fromhex("01")


class Assignment:
    def __init__(self, start_time: int, group_id: int, mode_id: int) -> None:
        self.content = (
            to_bytes(start_time, 4) + to_bytes(group_id, 1) + to_bytes(mode_id, 1)
        )

    def get_content(self) -> bytearray:
        return self.content


class Group:
    bit = partial(to_bytes, byte_length=1)

    def __init__(self, members: List[int] = None) -> None:
        self.members = list(members) or []

    def add(self, value: int) -> None:
        self.members.append(value)

    def get_content(self) -> bytearray:
        content = bytearray(chain.from_iterable(map(Group.bit, self.members)))
        content += END_GROUP
        return content


class Pulse:
    def __init__(
        self, start_color: int, end_color: int, num_steps: int, delay: int
    ) -> None:
        self.start_color = to_bytes(start_color, 3)
        end_color = to_bytes(end_color, 3)
        self.num_steps = to_bytes(num_steps, 1)
        self.delay = to_bytes(delay, 1)
        self.inc = bytearray()
        self.dir = ""  # binary string during construction...
        for byte in range(3):
            self.inc.append(
                max(abs(self.start_color[byte] - end_color[byte]) // num_steps - 1, 0)
            )
            self.dir += "0" if end_color[byte] > self.start_color[byte] else "1"
        print(self.dir)
        self.dir = to_bytes(int(self.dir, 2), 1)  # Single byte once dir is known

    def get_content(self) -> bytearray:
        return self.start_color + self.inc + self.dir + self.num_steps + self.delay


def create_message(
    assignments: List[Assignment],
    modes: List[Pulse],
    groups: List[Group],
    streaming: bool = False,
    rate: int = 10,
    num_lights: int = 75,
) -> bytearray:
    content = (
        MESSAGE_START
        + to_bytes(rate, 2)
        + to_bytes(len(modes), 1)
        + to_bytes(num_lights, 1)
        + to_bytes(len(groups), 1)
        + to_bytes(len(assignments), 4)
        + BEGIN
        + bytearray(chain.from_iterable([mode.get_content() for mode in modes]))
        + bytearray(
            chain.from_iterable([assign.get_content() for assign in assignments])
        )
        + bytearray(chain.from_iterable([group.get_content() for group in groups]))
        + END_PREAMBLE
    )
    if streaming:
        groups_to_bands = defaultdict(lambda: 0xFF)
        groups_to_bands[0] = 0
        content = (
            content
            + STREAM_SIZE
            + STREAMING
            + to_bytes(len(groups_to_bands), 1)
            + bytearray([groups_to_bands[i] for i in range(3)])
        )
    else:
        content += NOT_STREAM_SIZE + NOT_STREAMING

    return content
