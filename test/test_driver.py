from lights.driver import Pulse


def test_pulse():
    p = Pulse(0xFFFFFF, 0x000000, 1, 10)
    assert p.get_content() == bytearray.fromhex("FFFFFF FFFFFF 07 01 0A")

    p = Pulse(0xFFFFFF, 0x000000, 2, 5)
    assert p.get_content() == bytearray.fromhex("FFFFFF 7F7F7F 07 02 05")
