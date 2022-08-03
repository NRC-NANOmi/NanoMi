from HardwareFiles import AIOUSB

def main():
    AIOUSB.AIOUSB_Init()
    #enquire about what hardware is currently connected
    devMask = AIOUSB.GetDevices()
    for boardIndex in range(31):
        if 0 != (devMask & (1 << boardIndex)):
            status, serial, name, digitalIo, ctrs = AIOUSB.QueryDeviceInfo(boardIndex)    
            print("Board found at index", boardIndex, ", with serial number", serial, ", board name:", name, ", and", digitalIo, "digital I/O bytes available")
                
            if name == 'USB-AIO16-16F':
                AIOUSB.ADC_Range1(boardIndex, 0, 1, 0)
                AIOUSB.DACSetBoardRange(boardIndex, 1)
                AIOUSB.DIO_Configure(boardIndex, False, [0], [0,0])
                    
            if name == 'USB-AO16-16':
                AIOUSB.DACSetBoardRange(boardIndex, 1)
                AIOUSB.DIO_Configure(boardIndex, False, [3], [0,0])
    boardIndex = 1
    channel = int(input("Enter channel: "))
    while True:
        value = input("Enter Value:")
        if value == "q":
            break
        if value == "r":
            channel = int(input("Enter channel: "))
        else:
            value = float(value)
            AIOUSB.DACDirect(boardIndex, channel, round(float((value + 5) * 65535.0 / 10)))
    AIOUSB.AIOUSB_Exit()

main()
