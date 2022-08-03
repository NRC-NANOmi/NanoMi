import time

from ..HardwareFiles import AIOUSB


def main():
    AIOUSB.AIOUSB_Exit()
    AIOUSB.AIOUSB_Init()
    boardIndex = 1
    channel = 0
    while channel < 32:
        value = 0
        print("checking channel", channel)
        while value < 5:
            AIOUSB.DACDirect(boardIndex, channel, int(float((value + 5) * 65536.0 / 10)))
            value += 1
            time.sleep(0.3)
        channel += 1
    AIOUSB.AIOUSB_Exit()

main()
