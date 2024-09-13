#include <stdio.h>
#include <Windows.h>
#include <math.h>
#include <time.h>

HMODULE scannerDLL;                                 //This is a handle to the DLL that interfaces with the USB chip FT2232H -> ftd2xx.dll
VOID* usbHandle = NULL;                             //handle to the eventually connected USB device

//definitions for function call variables
typedef UINT32 (*USB_CreateDeviceInfoList)();       //This is a definition for the type of the FT_CreateDeviceInfoList() function
typedef UINT32 (*USB_GetDeviceInfoDetail)();        //This is a definition for the type of the FT_GetDeviceInfoDetail() function
typedef UINT32 (*USB_Open)();                       //This is a definition for the type of the FT_Open() function
typedef UINT32 (*USB_OpenEx)();                     //This is a definition for the type of the FT_OpenEx() function
typedef UINT32 (*USB_SetUSBParameters)();           //This is a definition for the type of the FT_SetUSBParameters() function
typedef UINT32 (*USB_SetFlowControl)();             //This is a definition for the type of the FT_SetFlowControl() function
typedef UINT32 (*USB_SetTimeouts)();                //This is a definition for the type of the FT_SetTimeouts() function
typedef UINT32 (*USB_GetStatus)();                  //This is a definition for the type of the FT_GetStatus() function
typedef UINT32 (*USB_PurgeRxTx)();                  //This is a definition for the type of the FT_Purge() function
typedef UINT32 (*USB_GetQueueStatus)();             //This is a definition for the type of the FT_GetQueueStatus() function
typedef UINT32 (*USB_Read)();                       //This is a definition for the type of the FT_Read() function
typedef UINT32 (*USB_Write)();                      //This is a definition for the type of the FT_Write() function
typedef UINT32 (*USB_Close)();                      //This is a definition for the type of the FT_Close() function
typedef UINT32 (*USB_Latency)();                    //This is a definition for the type of the FT_SetLatencyTimer() function

//Variables that serve as function calls
static USB_CreateDeviceInfoList CDIL = NULL;        //This is a variable that holds the function FT_CreateDeviceInfoList()
static USB_GetDeviceInfoDetail GDID = NULL;         //This is a variable that holds the function FT_GetDeviceInfoDetail()
static USB_Open Open = NULL;                        //This is a variable that holds the function FT_Open()
static USB_OpenEx OpenEx = NULL;                    //This is a variable that holds the function FT_OpenEx()
static USB_SetUSBParameters SetUSBParameters = NULL;//This is a variable that holds the function FT_SetUSBParameters()
static USB_SetFlowControl SetFlowControl = NULL;    //This is a variable that holds the function FT_SetFlowControl()
static USB_SetTimeouts SetTimeouts = NULL;          //This is a variable that holds the function FT_SetTimeouts()
static USB_GetStatus GetStatus = NULL;              //This is a variable that holds the function FT_GetStatus()
static USB_PurgeRxTx PurgeRxTx = NULL;              //This is a variable that holds the function FT_Purge()
static USB_GetQueueStatus GetQueue = NULL;          //This is a variable that holds the function FT_GetQueueStatus()
static USB_Read ReadDLL = NULL;                     //This is a variable that holds the function FT_Read()
static USB_Write WriteDLL = NULL;                   //This is a variable that holds the function FT_Write()
static USB_Close CloseDLL = NULL;                   //This is a variable that holds the function FT_Close()
static USB_Latency SetLatency = NULL;               //This is a variable that holds the function FT_SetLatencyTimer()

//Variables for FPGA-PC interfacing
BOOL foundUSB = FALSE;                              //current connection status for the FPGA
BOOL run = FALSE;                                   //current status of the run/stop of image acquisition
UINT16 mode;                                        //mode of operation -> 1 = raster scan; 2 = raster image; 3 = random scan; 4 = random image
UINT16 integrationTime;                             //integration time, where "integration = 2^(value) * 40ns", where value is what is being transmitted
UINT16 lineFlybackTime;                             //line flyback time for raster scan, which is the time to wait for the beam to get back to the other side of the image
UINT16 imageSize;                                   //image size in pixels, square images only
UINT16 pixelWaitTime;                               //time to wait for the beam to get to the next incremental location after an integration completes
__declspec(dllexport) UINT16 image[4096][4096];     //a 2D array for the image, with maximum size preallocated. Smaller images will only take up a portion of this space, but we can't change the size once we've declared it
UINT32 errorCode = 0;                               //a 32-bit error code that is custom to this DLL, but shares some features from ft2dxx.dll
UINT32 writeErrorCode;                              //a 32-bit error code that is custom to this DLL and is specific to writing values to the FPGA
UINT32 readErrorCode;                               //a 32-bit error code that is custom to this DLL and is specific to reading values from the FPGA
BOOL shutdownUI = FALSE;                            //status bit from the UI to say we're shutting down, close everything nicely please
BOOL doneImage = FALSE;                             //variable to determine if the image has been completed or not
BOOL gotRunInfo = FALSE;                            //variable to tell us whether we got new run status info from the rx data loop
BOOL gotModeInfo = FALSE;                           //variable to tell us whether we got new mode info from the rx data loop
BOOL gotIntegrationInfo = FALSE;                    //variable to tell us whether we got new integration time info from the rx data loop
BOOL gotPixelWaitInfo = FALSE;                      //variable to tell us whether we got new pixel wait time info from the rx data loop
BOOL gotImageSizeInfo = FALSE;                      //variable to tell us whether we got new image size info from the rx data loop
BOOL gotLineFlybackInfo = FALSE;                    //variable to tell us whether we got new line flyback time info from the rx data loop

//x86_64-w64-mingw32-gcc -shared cName.c -o dllName.dll
//x86_64-w64-mingw32-gcc  cName.c -o exeName.exe

//function declarations here
__declspec(dllexport) UINT32 initUSB();
__declspec(dllexport) BOOL getConnected();
__declspec(dllexport) UINT32 connectUSB(UINT32, UINT32);
__declspec(dllexport) void rxUSB();
UINT32 purgeUSB();
__declspec(dllexport) void setRun(BOOL);
__declspec(dllexport) BOOL getSetDoneImage(INT32);
__declspec(dllexport) INT32 getSetMode(INT32);
__declspec(dllexport) INT32 getSetIntegrationTime(INT32);
__declspec(dllexport) INT32 getSetLineFlybackTime(INT32);
__declspec(dllexport) INT32 getSetImageSize(INT32);
__declspec(dllexport) INT32 getSetPixelWaitTime(INT32);
__declspec(dllexport) void getImage(INT16*);
__declspec(dllexport) UINT32 generateRandoms(void);
__declspec(dllexport) void closingUSB();

//C does not have threading, so main will be on a constant loop unless we are shutting down.
//Hopefully this doesn't block or cause issues? It will automatically check for connections, and then poll for receive transmissions from the FPGA.
//Note that libraries don't run the main loop, only executables, so this main loop is strictly for testing/debugging purposes.
void main()
{   
    //this is the first initialization of the DLL; loading the DLL and determining the addresses of the processes (functions). If this fails we're effed so just return now and mail it in.
    errorCode = initUSB();
    if (errorCode > 0)
    {
        printf("Issue during initialization: %d\n", errorCode);
        return;
    }
    if (foundUSB == TRUE)
    {
        printf("Found a usb device!\n");
    }

    generateRandoms();
    
    //while loop that runs until USB is connected successfully
    errorCode = 20;                                 //initialize the error code to a "no devices connected" error so the while loop actually runs
    while (errorCode != 0 && shutdownUI == FALSE)   //while loop to run until the proper FPGA-linked USB device is found and connected to successfully (or we give up)
    {
        errorCode = connectUSB(500, 500);           //function that actually tries to connect; returns zero on success, non-zero for errors
        if (errorCode > 0)
        {
            printf("Issue during communications: %d\n", errorCode);
        }
    }

    rxUSB();

    //on shutdown of the UI, we will close the DLL and clear out all memory in this function
    closingUSB();
    return;
}

//The init routine connects to the USB device DLL and dedicates all of the required functions/processes. We will then expand on the DLL functionality for speed purposes
UINT32 initUSB()
{
    //initialization of any variables required
    shutdownUI = FALSE;
    foundUSB = FALSE;
    doneImage = FALSE;
    writeErrorCode = 0;
    readErrorCode = 0;

    //Load the DLL using LoadLibrary, which returns a handle to the DLL
    scannerDLL = LoadLibrary(TEXT("ftd2xx.dll"));
    if (scannerDLL == NULL) {return 21;}

    //after the handle to the DLL is successfully determined, each function (or "process") in the DLL has to be established and assigned to a variable in order to be called

    //function: FT_STATUS = FT_CreateDeviceInfoList(UINT32 &numberOfDevices)     -> note that the argument here is a pointer to a double word
    CDIL = (USB_CreateDeviceInfoList) GetProcAddress(scannerDLL, TEXT("FT_CreateDeviceInfoList"));
    if (CDIL == NULL) {return 22;}

    //function: FT_STATUS = FT_GetDeviceInfoDetail(UINT32 index, UINT32 &flags, UINT32 &type, UINT32 &deviceID, UINT32 &deviceLocation, CHAR &serialNumber, CHAR &description, FT_HANDLE *handle)
    GDID = (USB_GetDeviceInfoDetail) GetProcAddress(scannerDLL, TEXT("FT_GetDeviceInfoDetail"));
    if (GDID == NULL) {return 23;}

    //function: FT_STATUS = FT_OpenEx(VOID &argument1, UINT32 flags, FT_HANDLE *handle)
    OpenEx = (USB_OpenEx) GetProcAddress(scannerDLL, TEXT("FT_OpenEx"));
    if (OpenEx == NULL) {return 24;}

    //function: FT_STATUS = FT_Open(UINT32 index, FT_HANDLE *handle)
    Open = (USB_Open) GetProcAddress(scannerDLL, TEXT("FT_Open"));
    if (Open == NULL) {return 25;}

    //function: FT_STATUS = FT_SetUSBParameters(FT_HANDLE handle, UINT32 InSize, UINT32 OutSize)
    SetUSBParameters = (USB_SetUSBParameters) GetProcAddress(scannerDLL, TEXT("FT_SetUSBParameters"));
    if (SetUSBParameters == NULL) {return 26;}

    //function: FT_STATUS = FT_SetFlowControl(FT_HANDLE handle, USHORT FlowControl, UCHAR xOn, UCHAR xOff)
    SetFlowControl = (USB_SetFlowControl) GetProcAddress(scannerDLL, TEXT("FT_SetFlowControl"));
    if (SetFlowControl == NULL) {return 27;}

    //function: FT_STATUS = FT_SetTimeouts(FT_HANDLE handle, UINT32 readTimeout, UINT32 writeTimeout)
    SetTimeouts = (USB_SetTimeouts) GetProcAddress(scannerDLL, TEXT("FT_SetTimeouts"));
    if (SetTimeouts == NULL) {return 28;}

    //function: FT_STATUS = FT_GetStatus(FT_HANDLE handle, UINT32 &amountInRx, UINT32 &amountInTx, UINT32 &eventStatus)
    GetStatus = (USB_GetStatus) GetProcAddress(scannerDLL, TEXT("FT_GetStatus"));
    if (GetStatus == NULL) {return 29;}

    //function: FT_STATUS = FT_Purge(FT_HANDLE handle, UINT32 mask)              -> mask here is 1 to purge only Rx, 2 to purge only Tx, and 3 to purge both
    PurgeRxTx = (USB_PurgeRxTx) GetProcAddress(scannerDLL, TEXT("FT_Purge"));
    if (PurgeRxTx == NULL) {return 30;}

    //function: FT_STATUS = FT_GetQueueStatus(FT_HANDLE handle, UINT32 &amountInRx)
    GetQueue = (USB_GetQueueStatus) GetProcAddress(scannerDLL, TEXT("FT_GetQueueStatus"));
    if (GetQueue == NULL) {return 31;}

    //function: FT_STATUS = FT_Read(FT_HANDLE handle, VOID &buffer, UINT32 bytesToRead, UINT32 &bytesReceived)
    ReadDLL = (USB_Read) GetProcAddress(scannerDLL, TEXT("FT_Read"));
    if (ReadDLL == NULL) {return 32;}

    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    WriteDLL = (USB_Write) GetProcAddress(scannerDLL, TEXT("FT_Write"));
    if (WriteDLL == NULL) {return 33;}

    //function: FT_STATUS = FT_Close(FT_HANDLE handle)
    CloseDLL = (USB_Close) GetProcAddress(scannerDLL, TEXT("FT_Close"));
    if (CloseDLL == NULL) {return 34;}

    //function: FT_STATUS = FT_SetLatencyTimer(FT_HANDLE handle, UCHAR timer)
    SetLatency = (USB_Latency) GetProcAddress(scannerDLL, TEXT("FT_SetLatencyTimer"));
    if (SetLatency == NULL) {return 35;}

    return 0;
}

//connect routine will handle all connection stuff, python will have it easy for this one
UINT32 connectUSB(UINT32 rxTimeout, UINT32 txTimeout)
{
    UINT32 numDevices;              //variable for the number of devices currently connected to computer
    UINT32 ftStatus;                //variable for function return values
    UINT32 index;                   //index of the current USB device
    UINT32 flags;                   //flags from the current USB device
    UINT32 type;                    //type of the current USB device
    UINT32 deviceId;                //USB deviceId of the current USB device
    UINT32 deviceLocation;          //location of the current USB device
    char serialNumber[16];          //serial number of the current USB device
    char description[64];           //string description of the current USB device

    UINT32 desiredType = 6;         //the desired usb type and description we are looking for
    const char desiredDescription[] = "USB <-> Serial Converter A";
    
    //Create a device information list which updates how many devices are connected, and what they are
    //function: FT_STATUS = FT_CreateDeviceInfoList(UINT32 &numberOfDevices)     -> note that the argument here is a pointer to a double word
    ftStatus = CDIL(&numDevices);

    //if the return value is greater than zero, there was an error, so return it (1 < ftStatus < 18, so my errors here will start with 20)
    if (ftStatus > 0) { return ftStatus; }
    for (index = 0; index < numDevices; index++)
    {
        //Get information on the current device being queried
        //function: FT_STATUS = FT_GetDeviceInfoDetail(UINT32 index, UINT32 &flags, UINT32 &type, UINT32 &deviceID, UINT32 &deviceLocation, CHAR &serialNumber, CHAR &description, FT_HANDLE *handle)
        ftStatus = GDID(index, &flags, &type, &deviceId, &deviceLocation, serialNumber, description, &usbHandle);
        //If an error occured, return the error with an addition of 100*index, which shifts the error up by multiples of 100 so we know which device caused the issue
        if (ftStatus > 0)
        {
            return (ftStatus + (index*100));
        }
        //if the type is 6 and description matches our port's description, we have found the STEM unit USB chip, so stop looking at all others and set things up
        if (type == desiredType && strncmp(description, desiredDescription, sizeof(desiredDescription)) == 0)
        {
            foundUSB = TRUE;
            break;
        }
    }

    //If no usb was found, return an error saying "we didn't find it, sorry"
    if (foundUSB == FALSE) { return 20; }

    //if you made it here, we found the device, so let's open it up
    //function: FT_STATUS = FT_Open(UINT32 index, FT_HANDLE *handle)
    ftStatus = Open(index, &usbHandle);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller

    //from here on out, the usbHandle pointer is our means of accessing the device. It is a global variable so it stays active while the code is running

    //set the latency timer to flush the buffers
    //function: FT_STATUS = FT_SetLatencyTimer(FT_HANDLE handle, UCHAR timer)
    ftStatus = SetLatency(usbHandle, 2);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller

    //set the USB parameters such that we increase the buffer size for input into this DLL
    //function: FT_STATUS = FT_SetUSBParameters(FT_HANDLE handle, UINT32 InSize, UINT32 OutSize)
    ftStatus = SetUSBParameters(usbHandle, 0x10000, 0x10000);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller

    //set flow control - shouldn't be necessary but it found it helped in my python interpretation earlier to do this
    //function: FT_STATUS = FT_SetFlowControl(FT_HANDLE handle, USHORT FlowControl, UCHAR xOn, UCHAR xOff)
    // no control = 0, RTS_CTS = 256, others are others but we don't need those ones
    ftStatus = SetFlowControl(usbHandle, 256, 0, 0);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller

    //set the timeouts for receiving and transmitting in milliseconds
    //function: FT_STATUS = FT_SetTimeouts(FT_HANDLE handle, UINT32 readTimeout, UINT32 writeTimeout)
    ftStatus = SetTimeouts(usbHandle, rxTimeout, txTimeout);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller

    //get the current buffer status of the chip
    UINT32 bytesInRx;
    UINT32 bytesInTx;
    UINT32 eventStatus;
    //function: FT_STATUS = FT_GetStatus(FT_HANDLE handle, UINT32 &amountInRx, UINT32 &amountInTx, UINT32 &eventStatus)
    ftStatus = GetStatus(usbHandle, &bytesInRx, &bytesInTx, &eventStatus);
    if (ftStatus > 0) { return ftStatus; }          //if an error occurs, return it to the caller
    
    //if bytes are present in the RX or TX buffers, clear them all out because they are junk values
    //function: FT_STATUS = FT_Purge(FT_HANDLE handle, UINT32 mask)              -> mask here is 1 to purge only Rx, 2 to purge only Tx, and 3 to purge both
    if (bytesInRx > 0 || bytesInTx > 0)
    {
        ftStatus = PurgeRxTx(usbHandle, 3);
        if (ftStatus > 0) { return ftStatus; }      //if an error occurs, return it to the caller
    }

    //The USB chip is now set up for communications, so exit with code 0 (success!)
    return 0;
}

//function to return whether the DLL has connected to the stem unit or not
BOOL getConnected()
{
    return foundUSB;
}

//quick function to get or set the doneImage variable from python
BOOL getSetDoneImage(INT32 value)
{
    if (value < 0)
    {
        return doneImage;
    }
    else
    {
        doneImage = FALSE;
        return TRUE;
    }
}

// rx routine will handle all things about receiving transmission from the FPGA, including updating variables and filling out images
void rxUSB()
{
    //this function will loop inside of it until UI shutdown, constantly handling UI requests and FPGA data transfers
    while (shutdownUI == FALSE)
    {
        UINT32 bytesInRx;               //a variable to see how many bytes are present in the rx buffer right this instant
        UINT32 roundedBytesInRx;        

        //see if there is anything to read in from the FPGA, be it a reply to a query or image data
        //function: FT_STATUS = FT_GetQueueStatus(FT_HANDLE handle, UINT32 &amountInRx)
        readErrorCode = GetQueue(usbHandle, &bytesInRx);
        if (bytesInRx > 0 && readErrorCode == 0)
        {
            // printf("%d bytes are available - ", bytesInRx);
            roundedBytesInRx = (bytesInRx / 7) * 7;    //make sure we only read in multiples of 7 bytes, as 7 bytes is one signal
            // printf("we're about to read in %d bytes after rounding. That is %d data points.\n", roundedBytesInRx, roundedBytesInRx/7);

            unsigned char rxBuffer[65536];       //a 65536-byte buffer for the input from the FPGA
            UINT32 bytesRead;           //a value for how many bytes were actually read during the read

            //actually read in that many bytes and then deal with them
            //function: FT_STATUS = FT_Read(FT_HANDLE handle, VOID &buffer, UINT32 bytesToRead, UINT32 &bytesReceived)
            readErrorCode = ReadDLL(usbHandle, rxBuffer, roundedBytesInRx, &bytesRead);
            if (readErrorCode > 0) { return; }
            if (bytesRead != roundedBytesInRx) { return; }

            //iterate through the data we've received
            for (int index = 0; index < bytesRead; index += 7)
            {
                if ((UINT8) rxBuffer[index] == 240)         //if the first byte is integer 240, or hex 0xF0, then this is image data in the form 'F0' 'X' 'X' 'Y' 'Y' 'I' 'I', where XX is a word for x position, YY is a word for y position, and II is a word for intensity
                {
                    UINT16 x, y, i;
                    DOUBLE temp;
                    temp = (double)(rxBuffer[index+1]*256 + rxBuffer[index+2])*(imageSize-1)/65535;     x = ceil(temp);
                    temp = (double)(rxBuffer[index+3]*256 + rxBuffer[index+4])*(imageSize-1)/65535;     y = ceil(temp);
                    temp = (double)(rxBuffer[index+5]*256 + rxBuffer[index+6]);                         i = ceil(temp);
                    // printf("Byte data is %02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX  -  ", rxBuffer[index+0], rxBuffer[index+1], rxBuffer[index+2], rxBuffer[index+3], rxBuffer[index+4], rxBuffer[index+5], rxBuffer[index+6]);
                    // printf("Image data: (x,y,i) = (%d,%d,%d).\n", x, y, i);
                    if (y > imageSize || x > imageSize || x < 0 || y < 0)
                    {
                        printf("Latest pixel was ignored due to being out-of-bounds.");
                        continue;
                    }
                    image[y][x] = i;
                }
                if ((UINT8) rxBuffer[index] == 241)         //if the first byte is integer 241, or hex 0xF1, then this signals the end of image transmission
                {
                    if (mode == 1 | mode == 3)              //if we are in a continuous acquisition mode, send back a "F2" character to say "please continue with acquisition, we are ready"
                    {
                        UINT32 bytesWritten;
                        const char txBuffer[] = {(char)0xF2, (char)0, (char)0, (char)0};
                        //write immediately to the FPGA to set/get the mode
                        //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
                        writeErrorCode = WriteDLL(usbHandle, (void*)txBuffer, sizeof(txBuffer), &bytesWritten);
                        if (writeErrorCode > 0)
                        {
                            printf("Error in sending the FPGA the continue code F2. Whoops?\n");
                        }
                    }
                    else                                    //if we are in single-image mode, stop acquisition and say that the image is done now
                    {
                        setRun(FALSE);
                        doneImage = TRUE;
                    }
                }
                if ((UINT8) rxBuffer[index] == 243)         //if the first byte is integer 243, or hex 0xF3, then this signals a pause in transmission from the FPGA until we acknowledge
                {
                    printf("Got F3: %02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX\n", rxBuffer[index+0], rxBuffer[index+1], rxBuffer[index+2], rxBuffer[index+3], rxBuffer[index+4], rxBuffer[index+5], rxBuffer[index+6]);
                    UINT32 bytesWritten;
                    const char txBuffer[] = {(char)0xF4, (char)0, (char)0, (char)0};
                    //write immediately to the FPGA to set/get the mode
                    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
                    writeErrorCode = WriteDLL(usbHandle, (void*)txBuffer, sizeof(txBuffer), &bytesWritten);
                    if (writeErrorCode > 0)
                    {
                        printf("Error in sending the FPGA the continue code F4. Whoops?\n");
                    }
                }
                if ((UINT8) rxBuffer[index] == 225)         //if the first byte is integer 225, or hex 0xE1, then the next six bytes are the mode
                {
                    mode = (UINT16)rxBuffer[index+6];
                    gotModeInfo = TRUE;
                    // printf("Mode in DLL is: %d\n", mode);
                }
                if ((UINT8) rxBuffer[index] == 226)         //if the first byte is integer 226, or hex 0xE2, then the next six bytes are the integration time
                {
                    integrationTime = (UINT16)(rxBuffer[index+5]*256 + rxBuffer[index+6]);
                    gotIntegrationInfo = TRUE;
                    // printf("Integration time in DLL is: %d\n", integrationTime);
                }
                if ((UINT8) rxBuffer[index] == 227)         //if the first byte is integer 227, or hex 0xE3, then the next six bytes are the line flyback time
                {
                    lineFlybackTime = (UINT16)(rxBuffer[index+5]*256 + rxBuffer[index+6]);
                    gotLineFlybackInfo = TRUE;
                    // printf("Line Flyback in DLL is: %d\n", lineFlybackTime);
                }
                if ((UINT8) rxBuffer[index] == 229)         //if the first byte is integer 229, or hex 0xE5, then the next six bytes are the image size on a side - square images only!
                {
                    imageSize = (UINT16)(rxBuffer[index+5]*256 + rxBuffer[index+6]);
                    gotImageSizeInfo = TRUE;
                    // printf("Image size in DLL is: %d x %d\n", imageSize, imageSize);
                }
                if ((UINT8) rxBuffer[index] == 233)         //if the first byte is integer 233, or hex 0xE9, then the next six bytes are the pixel wait time
                {
                    pixelWaitTime = (UINT16)(rxBuffer[index+5]*256 + rxBuffer[index+6]);
                    gotPixelWaitInfo = TRUE;
                    // printf("Pixel wait time in DLL is: %d\n", pixelWaitTime);
                }
            }
        }
    }
}

//function to simply purge the Rx/Tx buffer of the USB chip on the board
UINT32 purgeUSB()
{
    //function: FT_STATUS = FT_Purge(FT_HANDLE handle, UINT32 mask)
    //mask here is 1 to purge only Rx, 2 to purge only Tx, and 3 to purge both
    return PurgeRxTx(usbHandle, 1);
}

//function to adjust the mode of the scanner. Only sets the FPGA, does not feed back
void setRun(BOOL runValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    char reg = 0xC0;
    doneImage = FALSE;
    purgeUSB();
    run = runValue;
    //zero out the image space if run is true so that the new image shows up blank until something arrives
    if (run == TRUE)
    {
        ZeroMemory(image, 4096*4096);
    }
    //define the buffer that will be sent to the FPGA
    const unsigned char txBuffer[] = {reg, 0, 0, runValue};
    UINT32 bytesWritten;
    //write immediately to the FPGA to usually perform a set for the run variable
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, txBuffer, 4, &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the run variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing run variable on the FPGA.\n", bytesWritten);
    }
    return;
}

//function to adjust the mode of the scanner. If the INT32 is set to a non-negative value, it will send to the FPGA; if -1, it will get the value from the FPGA and wait until it arrives
INT32 getSetMode(INT32 modeValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    unsigned char reg;
    BOOL getRequest;
    if (modeValue < 0)       //if negative, perform get on FPGA. Send a "Ex" register value which tells the FPGA to send it's value to the DLL/python
    {
        reg = 0xE1;
        modeValue = 0;
        getRequest = TRUE;
    }
    else                    //if a non-negative number, send that value value to the FPGA via a "Cx" register value
    {
        reg = 0xC1;
        mode = (UINT8)modeValue;
        getRequest = FALSE;
    }
    //define the buffer that will be sent to the FPGA
    char txBuffer[] = {(char)reg, (char)0, (char)0, (char)modeValue};
    UINT32 bytesWritten;
    //write immediately to the FPGA to set/get the mode
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, (void*)txBuffer, sizeof(txBuffer), &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the mode variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
        return -1;
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing mode variable on the FPGA.\n", bytesWritten);
        return -2;
    }
    //if the register was in the E's hang out here and wait for a response from the FPGA
    if (getRequest)
    {
        clock_t start = clock();
        while (gotModeInfo == FALSE) 
        {
            //this calculates the elapsted time since the loop has been waiting in milliseconds; if more than 500 ms have passed, time out
            if( (FLOAT)((clock() - start) / (CLOCKS_PER_SEC) * 1000) > 500)
            {
                return -3;
            }
        }
        gotModeInfo = FALSE;
        return mode;
    }
    //otherwise if the register was in the C's, just return 0 to say everything went ok
    else
    {
        return 0;
    }
}

//function to adjust the integration time of the scanner. If the INT32 is set to a non-negative value, it will send to the FPGA; if -1, it will get the value from the FPGA and wait until it arrives
INT32 getSetIntegrationTime(INT32 integrationValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    unsigned char reg;
    BOOL getRequest;
    if (integrationValue < 0)       //if negative, perform get on FPGA. Send a "Ex" register value which tells the FPGA to send it's value to the DLL/python
    {
        reg = 0xE2;
        integrationValue = 0;
        getRequest = TRUE;
    }
    else                            //if a non-negative number, send that value value to the FPGA via a "Cx" register value
    {
        reg = 0xC2;
        integrationTime = (UINT16)integrationValue;
        getRequest = FALSE;
    }
    //define the buffer that will be sent to the FPGA
    const unsigned char txBuffer[] = {(char)reg, 0, (char)(integrationValue/256), (char)(integrationValue - (integrationValue/256) * 256)};
    UINT32 bytesWritten;
    //write immediately to the FPGA to get/set the integration time
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, txBuffer, 4, &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the integration time variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
        return -1;
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing the integration time variable on the FPGA.\n", bytesWritten);
        return -2;
    }
    //if the register was in the E's hang out here and wait for a response from the FPGA
    if (getRequest)
    {
        clock_t start = clock();
        while (gotIntegrationInfo == FALSE)
        {
            //this calculates the elapsted time since the loop has been waiting in milliseconds; if more than 500 ms have passed, time out
            if( (FLOAT)((clock() - start) / (CLOCKS_PER_SEC) * 1000) > 500)
            {
                return -3;
            }
        }
        gotIntegrationInfo = FALSE;
        return integrationTime;
    }
    //otherwise if the register was in the C's, just return 0 to say everything went ok
    else
    {
        return 0;
    }
}

//function to adjust the line flyback time of the scanner. If the INT32 is set to a non-negative value, it will send to the FPGA; if -1, it will get the value from the FPGA and wait until it arrives
INT32 getSetLineFlybackTime(INT32 lineFlybackValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    unsigned char reg;
    BOOL getRequest;
    if (lineFlybackValue < 0)       //if negative, perform get on FPGA. Send a "Ex" register value which tells the FPGA to send it's value to the DLL/python
    {
        reg = 0xE3;
        lineFlybackValue = 0;
        getRequest = TRUE;
    }
    else                            //if a non-negative number, send that value value to the FPGA via a "Cx" register value
    {
        reg = 0xC3;
        lineFlybackTime = (UINT16)lineFlybackValue;
        getRequest = FALSE;
    }
    //define the buffer that will be sent to the FPGA
    const unsigned char  txBuffer[] = {(char)reg, 0, (char)(lineFlybackValue/256), (char)(lineFlybackValue - (lineFlybackValue/256) * 256)};
    UINT32 bytesWritten;
    //write immediately to the FPGA to get/set the line flyback time
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, txBuffer, 4, &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the line flyback time variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
        return -1;
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing the line flyback time variable on the FPGA.\n", bytesWritten);
        return -2;
    }
    //if the register was in the E's hang out here and wait for a response from the FPGA
    if (getRequest)
    {
        clock_t start = clock();
        while (gotLineFlybackInfo == FALSE)
        {
            //this calculates the elapsted time since the loop has been waiting in milliseconds; if more than 500 ms have passed, time out
            if( (FLOAT)((clock() - start) / (CLOCKS_PER_SEC) * 1000) > 500)
            {
                return -3;
            }
        }
        gotLineFlybackInfo = FALSE;
        return lineFlybackTime;
    }
    //otherwise if the register was in the C's, just return 0 to say everything went ok
    else
    {
        return 0;
    }
}

//function to adjust the image size of the scanner. If the INT32 is set to a non-negative value, it will send to the FPGA; if -1, it will get the value from the FPGA and wait until it arrives
INT32 getSetImageSize(INT32 imageValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    unsigned char reg;
    BOOL getRequest;
    if (imageValue < 0)       //if negative, perform get on FPGA. Send a "Ex" register value which tells the FPGA to send it's value to the DLL/python
    {
        reg = 0xE5;
        imageValue = 0;
        getRequest = TRUE;
    }
    else                            //if a non-negative number, send that value value to the FPGA via a "Cx" register value
    {
        reg = 0xC5;
        imageSize = (UINT16)imageValue;
        getRequest = FALSE;
    }
    //define the buffer that will be sent to the FPGA
    const unsigned char  txBuffer[] = {(char)reg, 0, (char)(imageValue/256), (char)(imageValue - (imageValue/256) * 256)};
    UINT32 bytesWritten;
    //write immediately to the FPGA to get/set the image size
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, txBuffer, 4, &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the image size variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
        return -1;
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing the image size variable on the FPGA.\n", bytesWritten);
        return -2;
    }
    //if the register was in the E's hang out here and wait for a response from the FPGA
    if (getRequest)
    {
        clock_t start = clock();
        while (gotImageSizeInfo == FALSE)
        {
            //this calculates the elapsted time since the loop has been waiting in milliseconds; if more than 500 ms have passed, time out
            if( (FLOAT)((clock() - start) / (CLOCKS_PER_SEC) * 1000) > 500)
            {
                return -3;
            }
        }
        gotImageSizeInfo = FALSE;
        return imageSize;
    }
    //otherwise if the register was in the C's, just return 0 to say everything went ok
    else
    {
        return 0;
    }
}

//function to adjust the pixel wait time of the scanner. If the INT32 is set to a non-negative value, it will send to the FPGA; if -1, it will get the value from the FPGA and wait until it arrives
INT32 getSetPixelWaitTime(INT32 pixelWaitValue)
{
    //define a char for the register, which is two hex digits (8 bits)
    unsigned char reg;
    BOOL getRequest;
    if (pixelWaitValue < 0)       //if negative, perform get on FPGA. Send a "Ex" register value which tells the FPGA to send it's value to the DLL/python
    {
        reg = 0xE9;
        pixelWaitValue = 0;
        getRequest = TRUE;
    }
    else                            //if a non-negative number, send that value value to the FPGA via a "Cx" register value
    {
        reg = 0xC9;
        imageSize = (UINT16)pixelWaitValue;
        getRequest = FALSE;
    }
    //define the buffer that will be sent to the FPGA
    const unsigned char  txBuffer[] = {(char)reg, 0, (char)(pixelWaitValue/256), (char)(pixelWaitValue - (pixelWaitValue/256) * 256)};
    UINT32 bytesWritten;
    //write immediately to get/set the pixel wait time
    //function: FT_STATUS = FT_Write(FT_HANDLE handle, VOID buffer, UINT32 bytesToWrite, UINT32 &bytesWritten)
    writeErrorCode = WriteDLL(usbHandle, txBuffer, 4, &bytesWritten);
    //if the error code returns greater than zero, there was an issue, so bail out
    if (writeErrorCode > 0)
    {
        printf("Error in writing %s, addressing the pixel wait time variable on the FPGA: %d.\n", txBuffer, writeErrorCode);
        return -1;
    }
    //if more or less than four bytes were written, something went wrong, so bail out
    if (bytesWritten != 4)
    {
        printf("Only wrote %d bytes out of 4 while addressing the pixel wait time variable on the FPGA.\n", bytesWritten);
        return -2;
    }
    //if the register was in the E's hang out here and wait for a response from the FPGA
    if (getRequest)
    {
        clock_t start = clock();
        while (gotPixelWaitInfo == FALSE)
        {
            //this calculates the elapsted time since the loop has been waiting in milliseconds; if more than 500 ms have passed, time out
            if( (FLOAT)((clock() - start) / (CLOCKS_PER_SEC) * 1000) > 500)
            {
                return -3;
            }
        }
        gotPixelWaitInfo = FALSE;
        return pixelWaitTime;
    }
    //otherwise if the register was in the C's, just return 0 to say everything went ok
    else
    {
        return 0;
    }
}

//function to return the image to python
void getImage(INT16* img)
{
    img = &image[0][0];
    return;
}

//function to generate an image worth of X and Y random position data that is unique - no duplicate pixels
UINT32 generateRandoms()
{
    // //make a master list of indexed pixels possible in an image, in a 1D array.
    // //Hence pixel 5 would be (x,y)=(5,0) and pixel 62 would be (x,y)=(7,6) etc
    // //This array will have a max size of 4096*4096, but will only use a portion if less pixels exist
    // UINT32 pixels[16777216];
    // UINT32 numPixels = imageSize*imageSize;

    // //instantiate the array counting from 0 to numPixels-1
    // for (int i = 0; i < numPixels; i++)
    // {
    //     pixels[i] = i;
    // }

    // time_t t;
    // srand((unsigned) time(&t));
    // //shuffle the array using the Fisher-Yates shuffle
    // for (int i = numPixels-1; i > 0; i++)
    // {
    //     UINT64 n = rand();
    // }
    
    return 0;
}

//The UI is shutting down, so we need to free up all of the allocated memory.
void closingUSB()
{   
    //uh oh, the communications to the device is closing. This is C, so we do our own garbage collection here
    //function: FT_STATUS = FT_Close(FT_HANDLE handle)
    errorCode = CloseDLL(usbHandle);

    //clear all function declarations
    free(CDIL);                 CDIL = NULL;
    free(GDID);                 GDID = NULL;
    free(Open);                 Open = NULL;
    free(SetUSBParameters);     SetUSBParameters = NULL;
    free(SetFlowControl);       SetFlowControl = NULL;
    free(SetTimeouts);          SetTimeouts = NULL;
    free(GetStatus);            GetStatus = NULL;
    free(PurgeRxTx);            PurgeRxTx = NULL;
    free(GetQueue);             GetQueue = NULL;
    free(ReadDLL);              ReadDLL = NULL;
    free(WriteDLL);             WriteDLL = NULL;
    free(CloseDLL);             CloseDLL = NULL;
    free(usbHandle);            usbHandle = NULL;

    //free the DLL from memory
    FreeLibrary(scannerDLL);
    free(scannerDLL);
    return;
}