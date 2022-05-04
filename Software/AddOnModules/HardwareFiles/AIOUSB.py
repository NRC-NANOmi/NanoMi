# -*- coding: utf-8 -*-
"""
Provide Python access via ctypes to ACCES's USB DAQ devices installed using the AIOUSB.dll (Windows) or AIOUSB.so (Linux) API libraries.

Consult https://accesio.com/MANUALS/USB%20Software%20Reference%20Manual.html for additional information about the underlying functionality exposed by the API.
"""

from ctypes import *
AIOUSB = cdll.LoadLibrary("/usr/local/lib/libaiousb.so")

diOnly = -3
"""AIOUSB sentinel value DeviceIndex meaning "the only device found"."""
                          # procedure ADCallback(pBuf: PWord; BufSize, Flags, Context: LongWord); cdecl;
ADC_Callback_Type = CFUNCTYPE(c_uint32, POINTER(c_uint16), c_uint32, c_uint32, c_uint32)

Ccallback = ADC_Callback_Type(0)

def AIOUSB_Init():
    return AIOUSB.AIOUSB_Init()

def AIOUSB_Exit():
    return AIOUSB.AIOUSB_Exit()

def GetDevices():
    """Return a bitmask of all detected deviceIndices."""
    return AIOUSB.GetDevices()

def GetDeviceByEEPROMByte(boardID):
    """
    Return the deviceIndex of the AIOUSB-using device found with the byte 'boardID' in the user-EEPROM area at offset 0.
    
    Determines the assigned Device Index of a device in a deterministic way, especially if you're controlling more than one device in the same system. It finds the device with the specified “board ID” at address 0x000 in the custom EEPROM area. “Board ID” is arbitrary, but you should avoid 0x00 and 0xFF, since those can match uninitialized EEPROMs.
    For a larger “board ID”, and/or one at an arbitrary location, use GetDeviceByEEPROMData().
    """
    return AIOUSB.GetDeviceByEEPROMByte(c_ubyte(boardID))

def GetDeviceByEEPROMData(offset, len, boardID):
    """
    Finds a device based on custom EEPROM data. Like GetDeviceByEEPROMByte(), except that it can look for more than a single byte, and at any location in the custom EEPROM area. Deterministically translates from non-volatile EEPROM-stored data into a Device Index.
    """
    IDbuf = (c_ubyte * len)(boardID)
    return AIOUSB.GetDeviceByEEPROMData(offset, len, byref(IDbuf))

def QueryDeviceInfo(index):
    """
    This function provides various data about the device at a given Device Index.

    It is common to call this function with “null” for most parameters. Most applications need only the device index and pPID, simply to verify which device type is present at the device index given. The additional parameters allow a more user-friendly experience if your program supports multiple device types.
    """
    PID = c_int()
    len = c_int(20)
    dio = c_int()
    ctrs = c_int()
    name = create_string_buffer(len.value)
    status = AIOUSB.QueryDeviceInfo(index, byref(PID), byref(len), byref(name), byref(dio), byref(ctrs))
    return status, PID.value, name.value.strip().decode(), dio.value, ctrs.value

def GetDeviceSerialNumber(index):
    """
    Provide the on-board "key" serial number. (This serial number is not [usually] related to the serial number on the physical label of the device.)

    For recognizing which device to use, the GetDeviceByEEPROMByte() function is generally superior, both to allow for field replacement and to simply use smaller board IDs. However, the GetDeviceSerialNumber() or GetDeviceBySerialNumber() function may be used in DRM-like situations, where transparent field replacement is undesirable.
    """
    sn = c_longlong(0)
    status = AIOUSB.GetDeviceSerialNumber(index, byref(sn))  
    return status, sn.value

def CustomEEPROMWrite(index, offset, len, value):
    """
    Write to the user-accessible EEPROM.

    If you write a one unique byte to StartAddress zero, then you can use GetDeviceByEEPROMByte() to robustly determine the device index of your devices. Refer to GetDeviceByEEPROMByte() for more information.
    EWriter.exe is provided to perform this and other EEPROM functions, so your code doesn't have to.
    """
    buf = (c_ubyte*len)(value)
    status = AIOUSB.CustomEEPROMWrite(index, offset, len, byref(buf))
    return status

def CustomEEPROMRead(index, offset, len):
    """
    Reads data previously written by CustomEEPROMWrite() or application software.

    Devices are shipped with zeroes in all custom EEPROM bytes, so using all-zeroes as a special "no data written" value is recommended(but not required).
    """
    buf = (c_ubyte * len)()
    length = c_long(len)
    status = AIOUSB.CustomEEPROMRead(index, offset, byref(length), byref(buf))
    return status, buf


def AIOUSB_ClearFIFO(index, cleartype):
    return AIOUSB.AIOUSB_ClearFIFO(index, cleartype)

def DIO_Configure(index, tristate, Outs, Data):
    """
    Configure Digital Input/Output “I/O Groups” for use as input or as output digital bits, and set the state of any output bits. On some products can globally enable/tristate all DIO bits.
    """
    outMask = create_string_buffer(len(Outs))
    for i in range(len(Outs)):
           outMask[i] = Outs[i]
    dataBuf = create_string_buffer(len(Data))
    for i in range(len(Data)):
           dataBuf[i] = Data[i]
    return AIOUSB.DIO_Configure(index, c_ubyte(tristate), byref(outMask), byref(dataBuf))

def DIO_ConfigureEx(index, Tristates, Outs, Data):
    """
    Configure Digital Input/Output “I/O Groups” for use as input or as output digital bits, and set the state of any output bits. On some products can globally enable/tristate all DIO bits.
    """
    trisMask = create_string_buffer(len(Tristates))
    for i in range(len(Tristates)):
        trisMask[i] = Tristates[i]
    outMask = create_string_buffer(len(Outs))
    for i in range(len(Outs)):
        outMask[i] = Outs[i]
    dataBuf = create_string_buffer(len(Data))
    for i in range(len(Data)):
        dataBuf[i] = Data[i]
    return AIOUSB.DIO_Configure(index, byref(outMask), byref(dataBuf), byref(trisMask))

def DIO_ConfigureMasked():
    return #nyi

def DIO_WriteAll(index, Data):
    """
    Write to all digital outputs on a device. Bits written to ports configured as “input” will be ignored.

    This is the most efficient method of writing to digital outputs, because it consumes one USB transaction, regardless of the number of bits on the device.
    """
    dataBuf = create_string_buffer(len(Data))
    for i in range(len(Data)):
        dataBuf[i] = Data[i]
    return AIOUSB.DIO_WriteAll(index, byref(dataBuf))

def DIO_Write8(index, byteIndex, Data):
    """
    Write to a single byte-worth of digital outputs on a device.

    Bytes written to ports configured as “input” are ignored.
    """
    return AIOUSB.DIO_Write8(index, c_int(byteIndex), c_ubyte(Data))

def DIO_Write1(index, bitIndex, Data):
    """Write to a single digital output bit on a device."""
    return AIOUSB.DIO_Write1(index, c_int(bitIndex), c_ubyte(Data))

def DIO_ReadAll(index):
    """Read all digital bits on a device, including read-back of ports configured as “output”."""
    dataBuf = create_string_buffer(12) # no ACCES DAQ devices have more than 12 bytes of DI
    status = AIOUSB.DIO_ReadAll(index, byref(dataBuf))  
    return status, dataBuf.raw

def DIO_Read8(index, byteIndex):
    """Read all digital bits on a device, including read-back of ports configured as “output”."""
    dataBuf = c_ubyte(0)
    status = AIOUSB.DIO_Read8(index, byteIndex, byref(dataBuf))
    return status, dataBuf.value

def DIO_Read1(index, bitIndex):
    """Read one bit of digital data from a device."""
    dataBuf = c_ubyte(0)
    status= AIOUSB.DIO_Read8(index, byteIndex, byref(dataBuf))
    return status, dataBuf.value

def DIO_StreamOpen(index):
    """
    Configure a USB-DIO-16H family device's high-speed digital bus for use as input or output. The high-speed digital bus provided by this family is “Dual Simplex”: it can only operate as output, or input. Although the USB-DIO-16H and USB-DIO-16A can switch the highspeed bus from input to output mode, or output to input, this process is not designed to occur in the course of normal data flow, thus the port is not classified as “Half Duplex”. 
    Note: 	
        Call DIO_ConfigureEx() and DIO_StreamSetClocks() as well, before sending/receiving data using DIO_StreamFrame().
    """
    return #NYI

def DIO_StreamClose():
    """Terminate the buffered input or output operation on a USB-DIO-16H family device."""
    return #NYI

def DIO_StreamSetClocks():
    """
    Configure the highspeed port for external or internal clock source, and, if internal, the frequency thereof.
    
    Note: 	
        Use "0" to indicate “External clock mode”.
        The Read and Write clock variables will be modified to indicate the Hz rate to which the unit will actually be configured: not all frequencies you can specify with a IEEE double can be achieved by the frequency generation circuit. Our DLL calculates the closest achievable frequency. If you're interested, you can consult the LTC6904 chipspec for details, or the provided source for the DLL.
        The slowest available frequency from the onboard generator is 1kHz; the fastest usable is 40MHz (the limit of the standard FIFO); the fastest useful for non-burst operation is ~8MHz (the streaming bandwidth limit of the USB→digital interface logic and code is 8MHz minimum, often as high as 12MHz if your computer is well optimized.)
    """
    return #NYI

def DIO_StreamFrame():
    """
    Send or Receive “fast” data across the DIO bus.

    Note: 	
        This function is used for either input or output operation. “Stream” can be interpreted “upload,” “write,” “read,” “download,” “send,” “receive,” or any similar term.
    """
    return #NYI



def CTR_8254Mode(index, chipIndex, counterIndex, mode):
    """
    Configure the mode of operation for a specified counter. 

    Notes:
        Calling CTR_8254Mode() will halt the counter specified until it gets “loaded” by calling CTR_8254Load() or the like.
        Refer to the 82C54 chipspec for details
    Neat Trick:
        Configuring a counter for Mode 0 will set that counter's output LOW.
        Configuring a counter for Mode 1 will set that counter's output HIGH.

        This can be used to convert a counter into an additional, albeit slow, digital output bit. The output pin will remain as configured until/unless the counter is “loaded” with a count value.
    """
    return AIOUSB.CTR_8254Mode(index, chipIndex, counterIndex, c_short(mode))

def CTR_8254Load(index, chipIndex, counterIndex, load):
    """
    Load a counter with a 16-bit count-down value.

    Notes: 	
        A load value of “0” will behave like a (hypothetical) load value of 65536.
        Some modes do not support “1” as a load value. Other modes support neither “1” nor “2” as load values.
        Refer to the 82C54 chipspec for details
    """
    return AIOUSB.CTR_8254Load(index, chipIndex, counterIndex, c_short(load))

def CTR_8254ModeLoad(index, chipIndex, counterIndex, mode, load):
    """
    Configure the mode of operation for a specified counter, and load that counter with a 16-bit count-down value. 

    Note: 	
        CTR_8254ModeLoad() is similar to CTR_8254Mode() followed by CTR_8254Load(), but takes a single USB transaction, making it at least 250µsec faster than issuing the two operations independently. See CTR_8254Mode() and CTR_8254Load() for more notes.
    """
    return AIOUSB.CTR_8254ModeLoad(index, chipIndex, counterIndex, c_short(mode), c_short(load))

def CTR_StartOutputFreq(index, chipIndex, Hz):
    """
    Output a frequency from a counter 2 of a block, assuming a standard configuration. 

    Note: 	
        This function requires that the individual counters in the specified 8254 be wired up as follows: 10MHz → IN1, and OUT1 → IN2. If the 10MHz is replaced with other frequencies, the pHz calculation will scale predictably.
        For most 8254s in our USB product line, this is the permanent wiring configuration. The exception is the USB-CTR-15, which has more flexibility; this wiring is provided by the USB-CTR-15's “Standard Configuration Adapter”.
        The USB-CTR-15 can output as many as 15 frequencies, if you use CTR_8254ModeLoad() &emdash; but if you use CTR_StartOutputFreq(), you can only achieve 5, on CTR2 of each of the 5 blocks. (Counters 2, 5, 8, 11, and 14 under the secondary numbering convention. See note at the beginning of this section.)
    """
    freq = c_double(Hz)
    status = AIOUSB.CTR_StartOutputFreq(index, chipIndex, byref(freq))
    return status, freq.value

def CTR_8254Read(index, chipIndex, counterIndex):
    """
    Reads the current count value from the indicated counter. 
    
    Note:
        The counts loaded cannot be read back. Only the “current count” is readable, and the current count does not initialize with the “(re-)load count value” until the first input clock occurs. Let us know if you need CTR_8254ReadStatusAll() functionality in your application.   
    """
    counts = c_short(0)
    status = AIOUSB.CTR_8254Read(index, chipIndex, counterIndex, byref(counts))
    return status, counts.value

def CTR_8254ReadAll(index):
    """
    Reads the current count values from all counters.

    Note:
        The counts loaded cannot be read back. Only the “current count” is readable, and the current count does not initialize with the “(re-)load count value” until the first input clock occurs. Let us know if you need CTR_8254ReadStatusAll() functionality in your application.
    """
    counts = create_string_buffer(30)
    status = AIOUSB.CTR_8254ReadAll(index, byref(counts))
    return status, counts

def CTR_8254ReadStatus(index, chipIndex, counterIndex):
    """
    Reads both the current count value and the status from the indicated counter. 

    Note: 
        The meaning of the individual bits in the status byte is best described in the 82C54 chip spec, which is readily found by searching the internet. Most often useful is “null count”, bit 6; when it's high, the count value is not particularly useful.
    """
    counts = c_short(0)
    state = c_ubyte(0)
    status = AIOUSB.CTR_8254ReadStatus(index, chipIndex, counterIndex, byref(counts), byref(state))
    return status, counts.value, state.value

def CTR_8254ReadModeLoad(index, chipIndex, counterIndex, mode, load):
    """
    Read, then mode, then load, the specified counter.

    Note: 
        CTR_8254ReadModeLoad() is similar to CTR_8254Read() followed by CTR_8254Mode() followed by CTR_8254Load(), but takes a single USB transaction, making it at least 500µsec faster than issuing the two operations independently. 
        The reading is taken before the mode and load occur.
        See CTR_8254Read(), CTR_8254Mode(), and CTR_8254Load() for more notes.
    """
    counts = c_short(0)
    status = AIOUSB.CTR_8254ReadModeLoad(index, chipIndex, counterIndex, c_short(mode), c_short(load), byref(counts))
    return status, counts.value



def DACSetBoardRange(index, rangeCode):
    """Enable DAC outputs to generate values other than “near ground”, and select the correct calibration table (on applicable models)."""
    return AIOUSB.DACSetBoardRange(index, rangeCode)

def DACDirect(index, channel, raw):
    """Output a value on a single DAC."""
    return AIOUSB.DACDirect(index, c_short(channel), c_short(raw))

def DACMultiDirect(index, DACValues, count):
    """
    Simultaneously output values on multiple DACs.

    Note: 
        Takes list of channel/count pairs and the count of pairs in the list
    """
    dataBuf = (c_short * count)()
    for i in range(count):
        dataBuf[i] = DACValues[i]   
    return AIOUSB.DACMultiDirect(index, dataBuf, count)
    

def DACOutputProcess(index, Hz, numSamples, sampleData):
    """
    The simplest way to output one or more simultaneous analog output waveforms (buffers of periodically-timed DAC values).

    All DACs in a single “point” will be updated simultaneously (on the same clock tick). The next point will be output on the subsequent clock tick.

    CAUTION:
        USB-DA12-8A requires your waveform to be 65537 samples or larger. If you intend to send waveforms shorter than this, build your shorter waveform as usual, then pad it out to 65537 using a pad value of 0x1nnn, where "nnn" is the count value in your built waveform's first point's first data sample. (The first count value for DAC #0.)
    """
    writeHz = c_double(Hz)
    dataBuf = (c_short * numSamples)()
    for i in range(numSamples):
        dataBuf[i] = sampleData[i]
    status = AIOUSB.DACOutputProcess(index, byref(writeHz), numSamples, byref(dataBuf))
    return status, writeHz.value



def ADC_GetScanV(index):
    """
    Return data from up to all ADC channels via software-start (up to 128 channels with a single call).

    This simple function takes one scan of A/D data and converts it to voltage. It also averages oversamples for each channel. On “DC-Level” boards with A/D that don't support ADC_SetConfig(), it scans all channels, without oversampling.
    This function converts input counts to voltages based on the range previously configured with ADC_Init or ADC_SetConfig. It will take data at the configured number of oversamples or more, average the readings from the channels, and convert the counts to voltage.
    This is the easiest way to read A/D data, but can't achieve more than hundreds of Hz, or even slower depending on options. It should readily achieve 0 to 100 Hz operation, on up to 128 channels.
    The speed limit is because this function performs intro & outro housekeeping USB transactions each call, to make it simple to use. 
    
    Note: 
        For a faster but less-convenient API that moves these housekeeping functions out of the acquisition loop, please refer to the section on ADC_GetFastScanV().
    """
    dataBuf = (c_double * 128)()
    status = AIOUSB.ADC_GetScanV(index, (dataBuf))
    return status, dataBuf

def ADC_GetChannelV(index, channel):
    """
    Acquire the voltage level on one A/D input. 
    
    Use this function when your language doesn't handle implicitly-lengthed arrays of doubles as used by ADC_GetScanV(), or to acquire readings from just a few channels, slowly — during debugging or calibration, for example
    This function is provided only for ease of use, implemented as a convenience wrapper for ADC_GetScanV(); it acquires all configured channels using ADC_GetScanV(), but returns only the specified channel's data. Therefore, reading two channels using ADC_GetChannelV() is at least twice as slow as using ADC_GetScanV().
    """
    data = c_double(0)
    status = AIOUSB.ADC_GetChannelV(index, channel, byref(data))
    return status, data.value

def ADC_SetScanLimits(index, startChannel, endChannel):
    """
    Provides an easier mechanism to modify the Scan Start Channel and Scan End Channel configuration.

    Normally the Scan Start Channel are broken into two four-bit components each, and configured by masking the least-significant nybbles into the ADC_SetConfig() array elements [0x12] and [0x14]. This function performs this bit manipulation for you, and writes the resulting configuration to the card using ADC_SetConfig().
    """
    return AIOUSB.ADC_SetScanLimits(index, startChannel, endChannel)

def ADC_RangeAll(index, gainCodes, bDifferential):
    """
    Configure the Range Code for all ADC channels.

    Normally configuring Range Codes requires bit manipulation to combine the Unipolar/Bipolar bit, the Differential/Single-Ended bit, and the Gain Bits into a single byte value per Range Group. This function performs this operation for you and updates the new configuration to the device using ADC_SetConfig()
    This function is currently implemented as a convenience-wrapper via a read-modify-write algorithm: It calls ADC_GetConfig(), modifies the returned config array as requested, then writes the new config via ADC_SetConfig(). 
    
    Note: 
        Although USB serializes operations across the cable this function performs several sequential transactions and is therefore not process-safe.
    """
    gainBuf = (c_ubyte * 16)()
    for i in range(16):
        gainBuf[i] = gainCodes[i]
    return AIOUSB.ADC_RangeAll(index, byref(gainBuf), bDifferential)

def ADC_Range1(index, channel, gaincode, bDifferential):
    """
    Configure the Range Code for a single “Range Group” of channels, which is a single channel on 16-channel boards.

    Normally the Range Code for each Range Group is configured using the ADC_SetConfig() array byte at [Range Group #]. This function updates the config array for you, and writes the resulting configuration to the card using ADC_SetConfig().
    This function is currently implemented as a convenience-wrapper via a read-modify-write algorithm: it calls ADC_QueryConfig(), modifies the returned config array as requested, then writes the new config via ADC_SetConfig(). 
    
    Note: 
        Although USB serializes operations across the cable this function performs several sequential transactions and is therefore not process-safe.
    """
    return AIOUSB.ADC_Range1(index, channel, c_ubyte(gaincode), bDifferential)

def ADC_SetOversample(index, oversample):
    """This utility function provides read-modify-write access to the “Oversample” configuration byte in the ADC_SetConfig array."""
    return AIOUSB.ADC_SetOversample(index, c_ubyte(oversample))

def ADC_SetCal(index, calname):
    """
    Configure the analog input calibration of a USB-AIx board.

    Note: 
        Some revisions of the driver will return errors under all conditions if you attempt to ADC_SetCal() unsupported hardware; other driver revisions will return ERROR_SUCCESS if you request “:NONE:” (or “:1TO1:”) on a board that does _not_ support calibration, as the request, although skipped, was technically successful - the calibration table of unsupported hardware is always `:NONE:`
        Call ADC_SetCalAndSave() to also receive the calibration table data for use by your application.
    """
    return AIOUSB.ADC_SetCal(index, calname)

def ADC_SetCalAndSave(index, calname, destpath):
    return AIOUSB.ADC_SetCalAndSave(index, calname, destpath)

def ADC_FullStartRing(index, config, calFile, Hz, buffer, depth):
    """Provide a single function to configure and start acquiring ADC readings using a background/async process paird with ADC_ReadData()."""
    rateHz = c_double(Hz)
    L = len(config)
    configLen = c_long(L)
    configBuf = (c_ubyte*L)()

    for i in range(L):
        configBuf[i] = config[i]
    status = AIOUSB.ADC_FullStartRing(index, byref(configBuf), byref(configLen), calFile, byref(rateHz), buffer, depth)
    return status, rateHz.value

def ADC_ReadData(index, config, scans, timeout):
    """
    Retrieves analog input data acquired into a ring buffer via ADC_BulkContinuousRingStart or ADC_FullStartRing. Oversamples, if any, are averaged, and the data is converted to volts.

    timeout:
    A double precision IEEE floating point number indicating the timeout and timeout behavior. Note that, _regardless_ of Timeout, if ADC_ReadData can immediately return all the requested data, then it will do so and return immediately.
        Timeout Value	Resulting Behavior
            0           Data already acquired is returned. ADC_ReadData doesn't wait for more, regardless of the amount.
        Infinity        The specified number of scans(or an error) is returned. So long as the ADC operation is functioning, ADC_ReadData will continue to wait until this request is fulfilled.
        Positive        ADC_ReadData will wait up to Timeout milliseconds in order to return all the requested data. At that time, if a lesser amount of data is available, then ADC_ReadData will return what's available.
        Negative        "All or nothing". ADC_ReadData will wait up to abs(Timeout) milliseconds in order to return all the requested data. If there still isn't that much data available at that time, then ADC_ReadData will time out. 
    """
    dataBuf = (c_double * 1024)()
    scansToRead = c_long(scans)
    L = len(config)
    configBuf = (c_ubyte*L)()
    configLen = c_long(L)
    for i in range(L):
        configBuf[i] = config[i]    
    timeoutDuration = c_double(timeout)
    status = AIOUSB.ADC_ReadData(index, byref(configBuf), byref(scansToRead), byref(dataBuf), timeoutDuration)
    return status, dataBuf

def ADC_BulkContinuousRingStart(index):
    """ acquires data into a ring buffer for reading via ADC_ReadData() """
    return AIOUSB.ADC_BulkContinuousRingStart(index, c_ulong(1024*1024), c_ulong(512))


def ADC_BulkContinuousCallbackStart(index, callback, context):
    """ starts the ADC calling your callback function """
    Ccallback = ADC_Callback_Type(callback)
    return AIOUSB.ADC_BulkContinuousCallbackStart(index, c_uint32(1024*1024), c_uint32(64), c_uint32(context), Ccallback)

def ADC_BulkContinuousEnd(index):
    """ starts the ADC calling your callback function """
    state = c_ulong(0)
    status = AIOUSB.ADC_BulkContinuousEnd(index, byref(state))
    return status, state.value


def ADC_SetConfig(index, config):
    """
    Perform extensive configuration of analog inputs, typically useful only for the "USB-AIx" and "DPK-" product Families.

    Note:
        Read-Modify-Write convenience wrappers are available to simplify modifying individual components of the ADC Configuration structure. See ADC_RangeAll(), ADC_Range1(), ADC_SetOversamples(), and ADC_SetScanLimits() for more information on these convenient setters.
    """
    L = len(config)
    configBuf = (c_ubyte*L)()
    configLen = c_long(L)
    for i in range(L):
        configBuf[i] = config[i]  
    return AIOUSB.ADC_SetConfig(index, byref(configBuf), byref(configLen))

def callCallback(index):
    return AIOUSB.ADC_CallCallback(c_ulong(index))

#end of useful public AIOUSB module stuff

def displayBoardInfo(index):
    status, PID, name, dio, ctrs = QueryDeviceInfo(index)
    status, sn = GetDeviceSerialNumber(index)   
    print ("Board found at index {0} has deviceID {1:x} = {2}, SN= {3:x} [{4} dio bytes]".format(index, PID, name, sn, dio, ctrs))



if __name__ == "__main__":# main code section
    print("AIOUSB Python introductory sample using ctypes\n")

    boardsMask = AIOUSB.GetDevices()
    if boardsMask == 0:
        print("No valid AIOUSB devices were detected.\nPlease confirm your USB device is connected, powered,\nand the drivers are installed correctly (check Device Manager).")
        exit()
    
    boardsFound = 0
    for di in range(31):
        if 0 != boardsMask & (1 << di):
            boardsFound = boardsFound + 1
            displayBoardInfo(di)
    print("\nAIOUSB Boards found:", boardsFound)


    if True: # USB-DIO-96 Sample
        print("Configuring I/O Group 8 as output (P4 Pins 1-15 odd)")
        status = DIO_Configure(diOnly, False, [0x00, 0x01], [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]) # I/O Group 8 as output, 0-7 & 9-11 as inputs.

        print("Writing 0xAA to byteIndex 8")
        status = DIO_Write8(diOnly, 8, 0xAA)  # write AA to I/O Group 8 

        print("Reading byteIndex 0 and 8")
        status, data0 = DIO_Read8(diOnly, 0)
        status, data = DIO_Read8(diOnly, 8)
        print(hex(data0), hex(data))

        print("Reading all 12 DIO bytes:")
        status, data = DIO_ReadAll(diOnly)
        for i, d in enumerate(data):
           print(f"I/O Group: {i:2} is {d:2x}")

    print("\nDone.")
