from lights.driver import Pulse


def test_pulse():
    p = Pulse(0xFFFFFF, 0x000000, 1, 10)
    assert p.get_content() == bytearray.fromhex("FFFFFF FEFEFE 07 01 0A")

    p = Pulse(0xFFFFFF, 0x000000, 2, 5)
    assert p.get_content() == bytearray.fromhex("FFFFFF 7E7E7E 07 02 05")

    p = Pulse(0x000000, 0x0000FF, 2, 1)
    assert p.get_content() == bytearray.fromhex("000000 00007E 06 02 01")
