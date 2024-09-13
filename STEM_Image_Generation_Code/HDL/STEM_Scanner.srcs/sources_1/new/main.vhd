library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
library UNISIM;
use UNISIM.VComponents.all;
Library xpm;
use xpm.vcomponents.all;

--a note on USB communications:
--  There are three types of communications that can be established using the FT2232H IC:
--      -> RS-232           - single RX line, single TX line, runs at arbitrary baud rate setting
--      -> 245 FIFO ASYNCH  - an 8-bit bus transmits and receives data at an arbitrary baud rate
--      -> 245 FIFO SYNCH   - an 8-bit bus transmits and receives data via a clock emitted by the USB IC.
--  There is a program called FT PROG that can change between these communication styles.
--      -> for RS-232:  with at least one of the two ports, select RS232 UART in the hardware section, and the driver should be a virtual COM port (default factory setting)
--      -> for 245 FIFO ASYNCH: with at least one of the two ports, select 245 FIFO in the hardware section, and the driver should be the D2XX Direct (programmable in python via DLL)
--      -> for 245 FIFO SYNCH: both of the ports need to be selected as 245 FIFO in the hardware section, and the driver should be the D2XX Direct (programmable in python via DLL).
--          -> SYNCH requires the UI in python to send a command on power-up to convert from ASYNCH 245 mode to SYNCH 245 mode.
--  Also note that the Digilent FPGA programmer has one of these chips on it, and will appear in FT PROG. Don't accidentally overwrite that one, that would be VERY BAD.
--
--  When swapping from FIFO mode to RS232 mode, one may also have to go into the device manager to change a setting so it is recognized as a virtual com port instead of a USB device.
--          --> Properties, advanced tab, "Load VCP" for loading the virtual com port. Otherwise it won't talk on RS232 mode.
--
--  This version (1.6) of the firmware is targeting 245 FIFO ASYNCH mode.

--main IO pins
entity main is
Port (
    clk_100MHz                      : in        std_logic; -- 100MHz PCB clock
    bank14_led                      : out       std_logic;
    bank15_led                      : out       std_logic;
    bank16_led                      : out       std_logic;
    bank35_led                      : out       std_logic;
    
    --Analog output signals
    x_analog_out                    : out       std_logic_vector(15 downto 0);
    y_analog_out                    : out       std_logic_vector(15 downto 0);
    
    --UART / USB signals
    usb_data                        : inout     std_logic_vector(7 downto 0);
    usb_rxf                         : in        std_logic;
    usb_txe                         : in        std_logic;
    usb_rd                          : out       std_logic;
    usb_wr                          : out       std_logic;
    usb_siwu                        : out       std_logic;
--    rx_pin                          : in        std_logic;
--    tx_pin                          : out       std_logic;
    
    --Analog input signals
    adc_data_p_0                    : in        std_logic;
    adc_data_n_0                    : in        std_logic;

    adc_data_p_1                    : in        std_logic;
    adc_data_n_1                    : in        std_logic;

    adc_data_p_2                    : in        std_logic;
    adc_data_n_2                    : in        std_logic;

    adc_data_p_3                    : in        std_logic;
    adc_data_n_3                    : in        std_logic;
    
    adc_data_p_4                    : in        std_logic;
    adc_data_n_4                    : in        std_logic;
    
    adc_data_p_5                    : in        std_logic;
    adc_data_n_5                    : in        std_logic;

    adc_data_p_6                    : in        std_logic;
    adc_data_n_6                    : in        std_logic;

    adc_data_p_7                    : in        std_logic;
    adc_data_n_7                    : in        std_logic;
    
    adc_bit_clk_p                   : in        std_logic;
    adc_bit_clk_n                   : in        std_logic;
    adc_frame_p                     : in        std_logic;
    adc_frame_n                     : in        std_logic;
    adc_cs                          : out       std_logic;
    adc_sclk                        : out       std_logic;
    adc_sdata                       : out       std_logic;
    adc_pdwn                        : out       std_logic;
    
    --DDR3 Signals
    ddr3_dq                         : inout     std_logic_vector(15 downto 0);
    ddr3_dqs_n                      : inout     std_logic_vector(1 downto 0);
    ddr3_dqs_p                      : inout     std_logic_vector(1 downto 0);
    ddr3_addr                       : out       std_logic_vector(13 downto 0);
    ddr3_ba                         : out       std_logic_vector(2 downto 0); 
    ddr3_ras_n                      : out       std_logic;
    ddr3_cas_n                      : out       std_logic;
    ddr3_we_n                       : out       std_logic;
    ddr3_ck_p                       : out       std_logic_vector(0 downto 0);
    ddr3_ck_n                       : out       std_logic_vector(0 downto 0);
    ddr3_cke                        : out       std_logic_vector(0 downto 0);
    ddr3_cs_n                       : out       std_logic_vector(0 downto 0);
    ddr3_dm                         : out       std_logic_vector(1 downto 0);
    ddr3_odt                        : out       std_logic_vector(0 downto 0);
    ddr3_reset_n                    : out       std_logic
 );
end main;

architecture Behavioral of main is
    
--Declarations of IP
    
    --clocking wizard takes in 100MHz clock, spits out RAM clock (200MHz), scan clock (25MHz) and communication clock (5MHz)
    component clocking_wizard
    port (
        clk_RAM                     : out std_logic;
        clk_100MHz                  : in  std_logic;
        clk_scan                    : out std_logic;
        clk_comms                   : out std_logic
    );
    end component;
    --memory interface generator (MIG) used to interface to the RAM. The ui_clk output runs at around 85MHz or so and needs to drive the RAM process.
    component mig_7series_0
    port (
        ddr3_dq                     : inout std_logic_vector(15 downto 0);
        ddr3_dqs_p                  : inout std_logic_vector(1 downto 0);
        ddr3_dqs_n                  : inout std_logic_vector(1 downto 0);
        ddr3_addr                   : out   std_logic_vector(13 downto 0);
        ddr3_ba                     : out   std_logic_vector(2 downto 0);
        ddr3_ras_n                  : out   std_logic;
        ddr3_cas_n                  : out   std_logic;
        ddr3_we_n                   : out   std_logic;
        ddr3_reset_n                : out   std_logic;
        ddr3_ck_p                   : out   std_logic_vector(0 downto 0);
        ddr3_ck_n                   : out   std_logic_vector(0 downto 0);
        ddr3_cke                    : out   std_logic_vector(0 downto 0);
        ddr3_cs_n                   : out   std_logic_vector(0 downto 0);
        ddr3_dm                     : out   std_logic_vector(1 downto 0);
        ddr3_odt                    : out   std_logic_vector(0 downto 0);
        app_addr                    : in    std_logic_vector(27 downto 0);
        app_cmd                     : in    std_logic_vector(2 downto 0);
        app_en                      : in    std_logic;
        app_wdf_data                : in    std_logic_vector(127 downto 0);
        app_wdf_end                 : in    std_logic;
        app_wdf_mask                : in    std_logic_vector(15 downto 0);
        app_wdf_wren                : in    std_logic;
        app_rd_data                 : out   std_logic_vector(127 downto 0);
        app_rd_data_end             : out   std_logic;
        app_rd_data_valid           : out   std_logic;
        app_rdy                     : out   std_logic;
        app_wdf_rdy                 : out   std_logic;
        app_sr_req                  : in    std_logic;
        app_ref_req                 : in    std_logic;
        app_zq_req                  : in    std_logic;
        app_sr_active               : out   std_logic;
        app_ref_ack                 : out   std_logic;
        app_zq_ack                  : out   std_logic;
        ui_clk                      : out   std_logic;
        ui_clk_sync_rst             : out   std_logic;
        init_calib_complete         : out   std_logic;
        -- System Clock Ports
        sys_clk_i                   : in    std_logic;
        -- Reference Clock Ports
        clk_ref_i                   : in    std_logic;
        sys_rst                     : in    std_logic
    );
    end component mig_7series_0;
    --A separate module for dealing with the eight simultaneous analog inputs properly based on the frame clock (25MHz) and bit clock (175MHz)
    component Analog_Inputs is
    Port (
        frame                       : in std_logic;
        bit_clk                     : in std_logic;
        scan_clk                    : in std_logic;
        clk_RAM                     : in std_logic;
        data_p0                     : in std_logic;
        data_n0                     : in std_logic;
        data_p1                     : in std_logic;
        data_n1                     : in std_logic;
        data_p2                     : in std_logic;
        data_n2                     : in std_logic;
        data_p3                     : in std_logic;
        data_n3                     : in std_logic;
        data_p4                     : in std_logic;
        data_n4                     : in std_logic;
        data_p5                     : in std_logic;
        data_n5                     : in std_logic;
        data_p6                     : in std_logic;
        data_n6                     : in std_logic;
        data_p7                     : in std_logic;
        data_n7                     : in std_logic;
        adc_out_0                   : out std_logic_vector(13 downto 0);
        adc_out_1                   : out std_logic_vector(13 downto 0);
        adc_out_2                   : out std_logic_vector(13 downto 0);
        adc_out_3                   : out std_logic_vector(13 downto 0);
        adc_out_4                   : out std_logic_vector(13 downto 0);
        adc_out_5                   : out std_logic_vector(13 downto 0);
        adc_out_6                   : out std_logic_vector(13 downto 0);
        adc_out_7                   : out std_logic_vector(13 downto 0)
    );
    end component;
    --A generic FIFO that takes information from the communications process or image generation process and passes them to the RAM clock domain.
    --Writes in 2-byte segments (16-bit) at a time from the system clock domain, and reads in 16-byte segments (128-bit) at a time from the RAM clock domain
    component writeTowardsRamFIFO is
    port (
        wr_clk                      : IN  std_logic := '0';
        rd_clk                      : IN  std_logic := '0';
        rst                         : IN  std_logic := '0';
        wr_rst_busy                 : OUT  std_logic := '0';
        rd_rst_busy                 : OUT  std_logic := '0';
        wr_en                       : IN  std_logic := '0';
        rd_en                       : IN  std_logic := '0';
        din                         : IN  std_logic_vector(16-1 DOWNTO 0) := (OTHERS => '0');
        dout                        : OUT std_logic_vector(128-1 DOWNTO 0) := (OTHERS => '0');
        full                        : OUT std_logic := '0';
        empty                       : OUT std_logic := '1'
    );
    end component;
    --A generic FIFO that takes information from the RAM process and clock domain and passes it to the communications process or image generation process.
    --Writes in 16-byte segments (128-bit) at a time from the RAM clock domain, and reads in 2-byte segments (16-bit) at a time from the system clock domain
    component readFromRamFIFO is
    port (
        wr_clk                      : IN  std_logic := '0';
        rd_clk                      : IN  std_logic := '0';
        rst                         : IN  std_logic := '0';
        wr_rst_busy                 : OUT  std_logic := '0';
        rd_rst_busy                 : OUT  std_logic := '0';
        wr_en                       : IN  std_logic := '0';
        rd_en                       : IN  std_logic := '0';
        din                         : IN  std_logic_vector(128-1 DOWNTO 0) := (OTHERS => '0');
        dout                        : OUT std_logic_vector(16-1 DOWNTO 0) := (OTHERS => '0');
        full                        : OUT std_logic := '0';
        empty                       : OUT std_logic := '1'
    );
    end component;
    --A generic FIFO that takes information from the RAM process and clock domain and passes it to the communications process or image generation process.
    --Writes in 16-byte segments (128-bit) at a time from the RAM clock domain, and reads in 2-byte segments (16-bit) at a time from the system clock domain
    component readFromRamFIFOAlmostEmpty is
    port (
        wr_clk                      : IN  std_logic := '0';
        rd_clk                      : IN  std_logic := '0';
        rst                         : IN  std_logic := '0';
        wr_rst_busy                 : OUT  std_logic := '0';
        rd_rst_busy                 : OUT  std_logic := '0';
        wr_en                       : IN  std_logic := '0';
        rd_en                       : IN  std_logic := '0';
        din                         : IN  std_logic_vector(128-1 DOWNTO 0) := (OTHERS => '0');
        dout                        : OUT std_logic_vector(16-1 DOWNTO 0) := (OTHERS => '0');
        full                        : OUT std_logic := '0';
        empty                       : OUT std_logic := '1';
        almost_empty                : OUT std_logic := '1';
        prog_full                   : OUT std_logic := '1'
    );
    end component;
    
--
--Declarations of variables and constants here
--

--DDR3L SDRAM
    signal clk_RAM                  : std_logic;
    signal clk_scan                 : std_logic;
    signal clk_comms                : std_logic;
    signal init_calib_complete      : std_logic;
    signal app_addr                 : std_logic_vector(27 downto 0) := (others=>'0');
    signal app_cmd                  : std_logic_vector(2 downto 0) := (others=>'0');
    signal app_en                   : std_logic;
    signal app_rdy                  : std_logic;
    signal app_wdf_end              : std_logic := '1';
    signal app_wdf_wren             : std_logic;
    signal app_wdf_rdy              : std_logic;
    signal app_rd_data_end          : std_logic;
    signal app_rd_data_valid        : std_logic;
    signal app_sr_req               : std_logic := '0';
    signal app_ref_req              : std_logic := '0';
    signal app_zq_req               : std_logic := '0';
    signal app_sr_active            : std_logic;
    signal app_ref_ack              : std_logic;
    signal app_zq_ack               : std_logic;
    signal ui_clk                   : std_logic;
    signal ui_clk_sync_rst          : std_logic;
    signal app_wdf_data             : std_logic_vector(127 downto 0);
    signal app_rd_data              : std_logic_vector(127 downto 0);
    signal app_wdf_mask             : std_logic_vector (15 downto 0):= (others => '0');
    signal sys_rst                  : std_logic := '1';
    --finite state machine for RAM handling
    type FSM_STATE is (IDLE, WRITE, WRITE_WAIT, READ, READ_WAIT, WRITE_RANDOM_X, WRITE_RANDOM_Y, RANDOM_WRITE_WAIT, READ_RANDOMS, READ_RANDOMS_WAIT, READ_RANDOMS_2, READ_RANDOMS_WAIT_2);
    signal stateRam                 : FSM_STATE := IDLE;
    --Addresses for RAM, acts as pointers that can shift around
    signal readAddress0             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress1             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress2             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress3             : std_logic_vector(27 downto 0) := (others => '0');  
    signal readAddress4             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress5             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress6             : std_logic_vector(27 downto 0) := (others => '0');   
    signal readAddress7             : std_logic_vector(27 downto 0) := (others => '0'); 
    signal readAddressX             : std_logic_vector(27 downto 0) := (others => '0');
    signal readAddressY             : std_logic_vector(27 downto 0) := (others => '0');  
    signal writeAddress0            : std_logic_vector(27 downto 0) := (others => '0'); 
    signal writeAddress1            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress2            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress3            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress4            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress5            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress6            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddress7            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddressX            : std_logic_vector(27 downto 0) := (others => '0');
    signal writeAddressY            : std_logic_vector(27 downto 0) := (others => '0');
    signal writer                   : integer range 0 to 7 := 0;
    signal reader                   : integer range 0 to 7 := 0;
    
--Analog input variables
    signal adcShifter               : std_logic_vector(7 downto 0) := (others => '0');      --holds 8-cycle delayed count of if we sample now or not
    signal bit_clk                  : std_logic;
    signal bit_clkr                 : std_logic;
    signal frame                    : std_logic;
    signal controlReady             : std_logic;
    signal controlReset             : std_logic := '0';
    signal AIN0                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN1                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN2                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN3                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN4                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN5                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN6                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal AIN7                     : std_logic_vector(13 downto 0);                       --Analog input 0's value, 14-bit number
    signal dataSum0                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum1                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum2                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum3                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum4                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum5                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum6                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal dataSum7                 : std_logic_vector(31 downto 0) := (others => '0');   --this is the largest value of summing possible for a 14-bit number (16384 x 2^17) without overflow -> 2.621 milliseconds dwell time maximum
    signal adcTestTrigger           : std_logic := '0';
    signal adcTestMode              : std_logic_vector(15 downto 0) := x"0000";
    signal adcSpiCounter            : integer range 0 to 511 := 0;
    
--UART over USB
    signal transmitX                : integer range 0 to 8191 := 0;
    signal transmitY                : integer range 0 to 8191 := 0;
    signal reg                      : std_logic_vector(7 downto 0) := x"00";
    signal setValue                 : std_logic_vector(23 downto 0) := x"000000";
    
    signal rxByteIndex              : integer range 0 to 3 := 0;
    signal rxOffCheck               : integer range 0 to 50000 := 0;
    signal rxEnable                 : std_logic := '0';
    signal txByteIndex              : integer range 0 to 7 := 0;
    signal txData                   : std_logic_vector(55 downto 0) := (others => '0');
    signal txTestData               : std_logic_vector(7 downto 0) := (others => '0');
    signal txEnable                 : std_logic := '0';
    signal txImage                  : std_logic := '0';
--    signal txPause                  : std_logic := '0';
--    signal txPixelCounter           : integer range 0 to 9362 := 0;
    constant commsPeriod            : integer := 200;               --the clock period for the comms loop in nanoseconds
    constant pulseWidth             : integer := 30;                --the minimum pulse width for read and write signals in async mode
    signal commsCounter             : integer range 0 to 7 := 0;    --counter for pulse width minimums
    --communication finite state machine
--    type COMMUNICATION_STATES is (IDLE, RX, RX_PROCESSING, TX, TX_IMAGE_END, TX_PAUSE);
    type COMMUNICATION_STATES is (IDLE, RX, RX_PROCESSING, TX, TX_IMAGE_END);
    signal communicationState       : COMMUNICATION_STATES := IDLE;
    
--Image generation variables
    signal run                      : std_logic := '0';
    signal pause                    : std_logic := '0';
    signal dwellCounter             : integer range 0 to 500000 := 0;                             -- counter for dwell timing [clock cycles]
    signal sampleCounter            : integer range 0 to 500000 := 0;                             -- counter for dwell timing [clock cycles]
    signal waitCounter              : integer range 0 to 500000 := 0;                             -- counter for dwell timing [clock cycles]
    signal lineCounter              : integer range 0 to 500000 := 0;                             -- counter for dwell timing [clock cycles]
    signal frameCounter             : integer range 0 to 500000 := 0;                             -- counter for dwell timing [clock cycles]
    signal dwell_time               : integer range 0 to 16 := 0;                                 -- exponential value of dwell time, aka how many bits to shift to get average [2^value x 40 ns]
    signal dwellCycles              : integer range 1 to 131072;                                  -- number of cycles to dwell on any given pixel for [2^value cycles]
    constant baseDwell              : unsigned := "00000000000000001";
    signal pixel_move_time          : integer range 1 to 500000 := 12;                            -- time to wait between moving the beam to the next pixel and starting the next sample [value x 40ns]
    signal line_end_time            : integer range 1 to 500000 := 125;                           -- time to wait between moving the beam to the next line and starting the next sample [value x 40 ns]
    signal imageSideLengthPixels    : integer range 8 to 4096 := 1024;                            -- total number of pixels in x [pixels], values are powers of 2 (i.e. 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192)
    signal pixelStepSize            : integer range 0 to 9362 := 0;                               -- step in x_DAC_output [counts] per movement, predetermined before moving;
    signal x_location               : integer range 0 to 8192 := 0;                               -- current location in the x-direction [pixels]
    signal y_location               : integer range 0 to 8192 := 0;                               -- current location in the y-direction [pixels]
    signal x_DAC_output             : std_logic_vector(15 downto 0) := x"0000";                   -- 16-bit DAC x output value [counts]
    signal y_DAC_output             : std_logic_vector(15 downto 0) := x"0000";                   -- 16-bit DAC y output value [counts]
    --Raster scan finite state machine
    type Raster_Scan_States is (IDLING, MEASURE_AND_MOVE, SCAN_WAIT_FOR_PIXEL, SCAN_END_OF_LINE, SCAN_END_OF_FRAME);
    signal Raster_Scan_State        : Raster_Scan_States := IDLING;
    --Random scan finite state machine
    type Random_Scan_States is (IDLING, READ_POSITIONS, SCAN_WAIT_FOR_PIXEL, MEASURE_AND_MOVE, HYSTERESIS, SCAN_END_OF_FRAME);
    signal Random_Scan_State        : Random_Scan_States := IDLING;
    signal usingRandomScan_src      : std_logic := '0';
    signal usingRandomScan_dest     : std_logic := '0';
    --Mode selection finite state machine
    type Modes is (IDLING, RASTER_SCAN, RANDOM_SCAN, FIXED_VOLTAGE, TESTING);
    signal AcquisitionMode          : Modes := raster_scan;
    signal pauseReset               : std_logic := '0';
    signal set_mode                 : integer range 0 to 7 := 1;
    signal set_x_voltage            : std_logic_vector(15 downto 0) := x"8000"; --x8000 is mid-point value, which corresponds to 0V (0x0000(0) = -1V, 0x8000(32768) = 0V, 0xFFFF(65535) = +1V)
    signal set_y_voltage            : std_logic_vector(15 downto 0) := x"8000";
    
--FIFO variables
    signal beenReset                : std_logic := '0';             --bit to tell if the FIFOs have been reset since the last image was taken
    signal resetCounter             : integer range 0 to 7 := 7;
    signal fifoReset                : std_logic := '0';
    --Random position readout from image 6 (X) and image 7 (Y) uses a FIFO that throws in 8 16-bit positions from RAM at a time and reads out one 16-bit position at a time to the image generation process
    signal randomScanXWriteIsReset  : std_logic := '0';
    signal randomScanXReadIsReset   : std_logic := '0';
    signal randomScanXWriteEnable   : std_logic := '0';
    signal randomScanXReadEnable    : std_logic := '0';
    signal randomScanXWriteData     : std_logic_vector(127 downto 0) := (others => '0');
    signal randomScanXReadData      : std_logic_vector( 15 downto 0) := (others => '0');
    signal randomScanXFull          : std_logic := '0';
    signal randomScanXEmpty         : std_logic := '0';
    signal randomScanYWriteIsReset  : std_logic := '0';
    signal randomScanYReadIsReset   : std_logic := '0';
    signal randomScanYWriteEnable   : std_logic := '0';
    signal randomScanYReadEnable    : std_logic := '0';
    signal randomScanYWriteData     : std_logic_vector(127 downto 0) := (others => '0');
    signal randomScanYReadData      : std_logic_vector( 15 downto 0) := (others => '0');
    signal randomScanYFull          : std_logic := '0';
    signal randomScanYEmpty         : std_logic := '0';
    --Random positions written to the communications process via a FIFO in 16-bit chunks and read in to image 6 (X) and image 7 (Y) in 8 16-bit positions to RAM
    signal randomUartXWriteIsReset  : std_logic := '0';
    signal randomUartXReadIsReset   : std_logic := '0';
    signal randomUartXWriteEnable   : std_logic := '0';
    signal randomUartXReadEnable    : std_logic := '0';
    signal randomUartXWriteData     : std_logic_vector( 15 downto 0) := (others => '0');
    signal randomUartXReadData      : std_logic_vector(127 downto 0) := (others => '0');
    signal randomUartXFull          : std_logic := '0';
    signal randomUartXEmpty         : std_logic := '0';
    signal randomUartYWriteIsReset  : std_logic := '0';
    signal randomUartYReadIsReset   : std_logic := '0';
    signal randomUartYWriteEnable   : std_logic := '0';
    signal randomUartYReadEnable    : std_logic := '0';
    signal randomUartYWriteData     : std_logic_vector( 15 downto 0) := (others => '0');
    signal randomUartYReadData      : std_logic_vector(127 downto 0) := (others => '0');
    signal randomUartYFull          : std_logic := '0';
    signal randomUartYEmpty         : std_logic := '0';
    --Image data from scan from each analog input (0 through 7) use their own FIFO that throws in one 16-bit intensity at a time and reads out 8 16-bit intensities into RAM
    signal scan0FifoWriteIsReset    : std_logic := '0';
    signal scan0FifoReadIsReset     : std_logic := '0';
    signal scan0FifoWriteEnable     : std_logic := '0';
    signal scan0FifoReadEnable      : std_logic := '0';
    signal scan0FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan0FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan0FifoFull            : std_logic := '0';
    signal scan0FifoEmpty           : std_logic := '0';
    signal scan1FifoWriteIsReset    : std_logic := '0';
    signal scan1FifoReadIsReset     : std_logic := '0';
    signal scan1FifoWriteEnable     : std_logic := '0';
    signal scan1FifoReadEnable      : std_logic := '0';
    signal scan1FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan1FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan1FifoFull            : std_logic := '0';
    signal scan1FifoEmpty           : std_logic := '0';
    signal scan2FifoWriteIsReset    : std_logic := '0';
    signal scan2FifoReadIsReset     : std_logic := '0';
    signal scan2FifoWriteEnable     : std_logic := '0';
    signal scan2FifoReadEnable      : std_logic := '0';
    signal scan2FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan2FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan2FifoFull            : std_logic := '0';
    signal scan2FifoEmpty           : std_logic := '0';
    signal scan3FifoWriteIsReset    : std_logic := '0';
    signal scan3FifoReadIsReset     : std_logic := '0';
    signal scan3FifoWriteEnable     : std_logic := '0';
    signal scan3FifoReadEnable      : std_logic := '0';
    signal scan3FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan3FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan3FifoFull            : std_logic := '0';
    signal scan3FifoEmpty           : std_logic := '0';
    signal scan4FifoWriteIsReset    : std_logic := '0';
    signal scan4FifoReadIsReset     : std_logic := '0';
    signal scan4FifoWriteEnable     : std_logic := '0';
    signal scan4FifoReadEnable      : std_logic := '0';
    signal scan4FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan4FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan4FifoFull            : std_logic := '0';
    signal scan4FifoEmpty           : std_logic := '0';
    signal scan5FifoWriteIsReset    : std_logic := '0';
    signal scan5FifoReadIsReset     : std_logic := '0';
    signal scan5FifoWriteEnable     : std_logic := '0';
    signal scan5FifoReadEnable      : std_logic := '0';
    signal scan5FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan5FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan5FifoFull            : std_logic := '0';
    signal scan5FifoEmpty           : std_logic := '0';
    signal scan6FifoWriteIsReset    : std_logic := '0';
    signal scan6FifoReadIsReset     : std_logic := '0';
    signal scan6FifoWriteEnable     : std_logic := '0';
    signal scan6FifoReadEnable      : std_logic := '0';
    signal scan6FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan6FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan6FifoFull            : std_logic := '0';
    signal scan6FifoEmpty           : std_logic := '0';
    signal scan7FifoWriteIsReset    : std_logic := '0';
    signal scan7FifoReadIsReset     : std_logic := '0';
    signal scan7FifoWriteEnable     : std_logic := '0';
    signal scan7FifoReadEnable      : std_logic := '0';
    signal scan7FifoWriteData       : std_logic_vector( 15 downto 0) := (others => '0');
    signal scan7FifoReadData        : std_logic_vector(127 downto 0) := (others => '0');
    signal scan7FifoFull            : std_logic := '0';
    signal scan7FifoEmpty           : std_logic := '0';
    --Image data for readout to PC (0 through 7) each use their own FIFO that throws in 8 16-bit intensities at a time from RAM and reads out 1 16-bit intensity for UART to PC
    signal usb0FifoWriteIsReset     : std_logic := '0';
    signal usb0FifoReadIsReset      : std_logic := '0';
    signal usb0FifoWriteEnable      : std_logic := '0';
    signal usb0FifoReadEnable       : std_logic := '0';
    signal usb0FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb0FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb0FifoFull             : std_logic := '0';
    signal usb0FifoEmpty            : std_logic := '0';
    signal usb0FifoAlmostEmpty      : std_logic := '0';
    signal usb0FifoAlmostFull       : std_logic := '0';
    signal usb1FifoWriteIsReset     : std_logic := '0';
    signal usb1FifoReadIsReset      : std_logic := '0';
    signal usb1FifoWriteEnable      : std_logic := '0';
    signal usb1FifoReadEnable       : std_logic := '0';
    signal usb1FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb1FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb1FifoFull             : std_logic := '0';
    signal usb1FifoEmpty            : std_logic := '0';
    signal usb2FifoWriteIsReset     : std_logic := '0';
    signal usb2FifoReadIsReset      : std_logic := '0';
    signal usb2FifoWriteEnable      : std_logic := '0';
    signal usb2FifoReadEnable       : std_logic := '0';
    signal usb2FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb2FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb2FifoFull             : std_logic := '0';
    signal usb2FifoEmpty            : std_logic := '0';
    signal usb3FifoWriteIsReset     : std_logic := '0';
    signal usb3FifoReadIsReset      : std_logic := '0';
    signal usb3FifoWriteEnable      : std_logic := '0';
    signal usb3FifoReadEnable       : std_logic := '0';
    signal usb3FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb3FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb3FifoFull             : std_logic := '0';
    signal usb3FifoEmpty            : std_logic := '0';
    signal usb4FifoWriteIsReset     : std_logic := '0';
    signal usb4FifoReadIsReset      : std_logic := '0';
    signal usb4FifoWriteEnable      : std_logic := '0';
    signal usb4FifoReadEnable       : std_logic := '0';
    signal usb4FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb4FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb4FifoFull             : std_logic := '0';
    signal usb4FifoEmpty            : std_logic := '0';
    signal usb5FifoWriteIsReset     : std_logic := '0';
    signal usb5FifoReadIsReset      : std_logic := '0';
    signal usb5FifoWriteEnable      : std_logic := '0';
    signal usb5FifoReadEnable       : std_logic := '0';
    signal usb5FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb5FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb5FifoFull             : std_logic := '0';
    signal usb5FifoEmpty            : std_logic := '0';
    signal usb6FifoWriteIsReset     : std_logic := '0';
    signal usb6FifoReadIsReset      : std_logic := '0';
    signal usb6FifoWriteEnable      : std_logic := '0';
    signal usb6FifoReadEnable       : std_logic := '0';
    signal usb6FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb6FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb6FifoFull             : std_logic := '0';
    signal usb6FifoEmpty            : std_logic := '0';
    signal usb7FifoWriteIsReset     : std_logic := '0';
    signal usb7FifoReadIsReset      : std_logic := '0';
    signal usb7FifoWriteEnable      : std_logic := '0';
    signal usb7FifoReadEnable       : std_logic := '0';
    signal usb7FifoWriteData        : std_logic_vector(127 downto 0) := (others => '0');
    signal usb7FifoReadData         : std_logic_vector( 15 downto 0) := (others => '0');
    signal usb7FifoFull             : std_logic := '0';
    signal usb7FifoEmpty            : std_logic := '0';

--    attribute mark_debug : string;
    
--    attribute mark_debug of transmitX : signal is "true";
--    attribute mark_debug of transmitY : signal is "true";
--    attribute mark_debug of communicationState : signal is "true";
    
--    attribute mark_debug of rxByteIndex : signal is "true";
--    attribute mark_debug of reg : signal is "true";
--    attribute mark_debug of setValue : signal is "true";
--    attribute mark_debug of rxEnable : signal is "true";
    
--    attribute mark_debug of txData : signal is "true";
--    attribute mark_debug of txByteIndex : signal is "true";
--    attribute mark_debug of txEnable : signal is "true";
--    attribute mark_debug of txImage : signal is "true";
--    attribute mark_debug of txTestData : signal is "true";
--    attribute mark_debug of usb_txe : signal is "true";
----    attribute mark_debug of txPause : signal is "true";
----    attribute mark_debug of txPixelCounter : signal is "true";

--    attribute mark_debug of usb0FifoWriteEnable : signal is "true";
--    attribute mark_debug of usb0FifoFull : signal is "true";
--    attribute mark_debug of usb0FifoAlmostFull : signal is "true";
--    attribute mark_debug of usb0FifoWriteData : signal is "true";
    
--    attribute mark_debug of usb0FifoReadEnable : signal is "true";
--    attribute mark_debug of usb0FifoReadData : signal is "true";
--    attribute mark_debug of usb0FifoEmpty : signal is "true";
--    attribute mark_debug of usb0FifoAlmostEmpty : signal is "true";

--          _____       _____       _____       _____
--    _____|     |_____|     |_____|     |_____|     |____

begin

--Instantiations of IP

--random XY positions coming in from UART to be written into RAM
usbRandomPositionsX : writeTowardsRamFIFO
port map (
    wr_clk              => clk_comms,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => randomUartXWriteIsReset,
    rd_rst_busy         => randomUartXReadIsReset,
    wr_en 		        => randomUartXWriteEnable,
    rd_en               => randomUartXReadEnable,
    din                 => randomUartXWriteData,
    dout                => randomUartXReadData,
    full                => randomUartXFull,
    empty               => randomUartXEmpty
);
usbRandomPositionsY : writeTowardsRamFifo
port map (
    wr_clk              => clk_comms,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => randomUartYWriteIsReset,
    rd_rst_busy         => randomUartYReadIsReset,
    wr_en 		        => randomUartYWriteEnable,
    rd_en               => randomUartYReadEnable,
    din                 => randomUartYWriteData,
    dout                => randomUartYReadData,
    full                => randomUartYFull,
    empty               => randomUartYEmpty
);
--random XY positions being written from RAM into the image generation process for use
scanRandomPositionsX : readFromRamFIFO
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_scan,
    rst                 => fifoReset,
    wr_rst_busy         => randomScanXWriteIsReset,
    rd_rst_busy         => randomScanXReadIsReset,
    wr_en 		        => randomScanXWriteEnable,
    rd_en               => randomScanXReadEnable,
    din                 => randomScanXWriteData,
    dout                => randomScanXReadData,
    full                => randomScanXFull,
    empty               => randomScanXEmpty
);
scanRandomPositionsY : readFromRamFIFO
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_scan,
    rst                 => fifoReset,
    wr_rst_busy         => randomScanYWriteIsReset,
    rd_rst_busy         => randomScanYReadIsReset,
    wr_en 		        => randomScanYWriteEnable,
    rd_en               => randomScanYReadEnable,
    din                 => randomScanYWriteData,
    dout                => randomScanYReadData,
    full                => randomScanYFull,
    empty               => randomScanYEmpty
);

--FIFOs used to transmit image data from the image generation process over to be written into RAM
scanImage0 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan0FifoWriteIsReset,
    rd_rst_busy         => scan0FifoReadIsReset,
    wr_en 		        => scan0FifoWriteEnable,
    rd_en               => scan0FifoReadEnable,
    din                 => scan0FifoWriteData,
    dout                => scan0FifoReadData,
    full                => scan0FifoFull,
    empty               => scan0FifoEmpty
);
scanImage1 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan1FifoWriteIsReset,
    rd_rst_busy         => scan1FifoReadIsReset,
    wr_en 		        => scan1FifoWriteEnable,
    rd_en               => scan1FifoReadEnable,
    din                 => scan1FifoWriteData,
    dout                => scan1FifoReadData,
    full                => scan1FifoFull,
    empty               => scan1FifoEmpty
);
scanImage2 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan2FifoWriteIsReset,
    rd_rst_busy         => scan2FifoReadIsReset,
    wr_en 		        => scan2FifoWriteEnable,
    rd_en               => scan2FifoReadEnable,
    din                 => scan2FifoWriteData,
    dout                => scan2FifoReadData,
    full                => scan2FifoFull,
    empty               => scan2FifoEmpty
);
scanImage3 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan3FifoWriteIsReset,
    rd_rst_busy         => scan3FifoReadIsReset,
    wr_en 		        => scan3FifoWriteEnable,
    rd_en               => scan3FifoReadEnable,
    din                 => scan3FifoWriteData,
    dout                => scan3FifoReadData,
    full                => scan3FifoFull,
    empty               => scan3FifoEmpty
);
scanImage4 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan4FifoWriteIsReset,
    rd_rst_busy         => scan4FifoReadIsReset,
    wr_en 		        => scan4FifoWriteEnable,
    rd_en               => scan4FifoReadEnable,
    din                 => scan4FifoWriteData,
    dout                => scan4FifoReadData,
    full                => scan4FifoFull,
    empty               => scan4FifoEmpty
);
scanImage5 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan5FifoWriteIsReset,
    rd_rst_busy         => scan5FifoReadIsReset,
    wr_en 		        => scan5FifoWriteEnable,
    rd_en               => scan5FifoReadEnable,
    din                 => scan5FifoWriteData,
    dout                => scan5FifoReadData,
    full                => scan5FifoFull,
    empty               => scan5FifoEmpty
);
scanImage6 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan6FifoWriteIsReset,
    rd_rst_busy         => scan6FifoReadIsReset,
    wr_en 		        => scan6FifoWriteEnable,
    rd_en               => scan6FifoReadEnable,
    din                 => scan6FifoWriteData,
    dout                => scan6FifoReadData,
    full                => scan6FifoFull,
    empty               => scan6FifoEmpty
);
scanImage7 : writeTowardsRamFIFO 
port map (
    wr_clk              => clk_scan,
    rd_clk              => ui_clk,
    rst                 => fifoReset,
    wr_rst_busy         => scan7FifoWriteIsReset,
    rd_rst_busy         => scan7FifoReadIsReset,
    wr_en 		        => scan7FifoWriteEnable,
    rd_en               => scan7FifoReadEnable,
    din                 => scan7FifoWriteData,
    dout                => scan7FifoReadData,
    full                => scan7FifoFull,
    empty               => scan7FifoEmpty
);

--FIFOs used to pass image data from RAM storage into the communications process
usbImage0 : readFromRamFIFOAlmostEmpty 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb0FifoWriteIsReset,
    rd_rst_busy         => usb0FifoReadIsReset,
    wr_en 		        => usb0FifoWriteEnable,
    rd_en               => usb0FifoReadEnable,
    din                 => usb0FifoWriteData,
    dout                => usb0FifoReadData,
    full                => usb0FifoFull,
    empty               => usb0FifoEmpty,
    almost_empty        => usb0FifoAlmostEmpty,
    prog_full           => usb0FifoAlmostFull
);
usbImage1 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb1FifoWriteIsReset,
    rd_rst_busy         => usb1FifoReadIsReset,
    wr_en 		        => usb1FifoWriteEnable,
    rd_en               => usb1FifoReadEnable,
    din                 => usb1FifoWriteData,
    dout                => usb1FifoReadData,
    full                => usb1FifoFull,
    empty               => usb1FifoEmpty
);
usbImage2 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb2FifoWriteIsReset,
    rd_rst_busy         => usb2FifoReadIsReset,
    wr_en 		        => usb2FifoWriteEnable,
    rd_en               => usb2FifoReadEnable,
    din                 => usb2FifoWriteData,
    dout                => usb2FifoReadData,
    full                => usb2FifoFull,
    empty               => usb2FifoEmpty
);
usbImage3 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb3FifoWriteIsReset,
    rd_rst_busy         => usb3FifoReadIsReset,
    wr_en 		        => usb3FifoWriteEnable,
    rd_en               => usb3FifoReadEnable,
    din                 => usb3FifoWriteData,
    dout                => usb3FifoReadData,
    full                => usb3FifoFull,
    empty               => usb3FifoEmpty
);
usbImage4 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb4FifoWriteIsReset,
    rd_rst_busy         => usb4FifoReadIsReset,
    wr_en 		        => usb4FifoWriteEnable,
    rd_en               => usb4FifoReadEnable,
    din                 => usb4FifoWriteData,
    dout                => usb4FifoReadData,
    full                => usb4FifoFull,
    empty               => usb4FifoEmpty
);
usbImage5 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb5FifoWriteIsReset,
    rd_rst_busy         => usb5FifoReadIsReset,
    wr_en 		        => usb5FifoWriteEnable,
    rd_en               => usb5FifoReadEnable,
    din                 => usb5FifoWriteData,
    dout                => usb5FifoReadData,
    full                => usb5FifoFull,
    empty               => usb5FifoEmpty
);
usbImage6 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb6FifoWriteIsReset,
    rd_rst_busy         => usb6FifoReadIsReset,
    wr_en 		        => usb6FifoWriteEnable,
    rd_en               => usb6FifoReadEnable,
    din                 => usb6FifoWriteData,
    dout                => usb6FifoReadData,
    full                => usb6FifoFull,
    empty               => usb6FifoEmpty
);
usbImage7 : readFromRamFIFO 
port map (
    wr_clk              => ui_clk,
    rd_clk              => clk_comms,
    rst                 => fifoReset,
    wr_rst_busy         => usb7FifoWriteIsReset,
    rd_rst_busy         => usb7FifoReadIsReset,
    wr_en 		        => usb7FifoWriteEnable,
    rd_en               => usb7FifoReadEnable,
    din                 => usb7FifoWriteData,
    dout                => usb7FifoReadData,
    full                => usb7FifoFull,
    empty               => usb7FifoEmpty
);

--ADC BIT CLOCK ENTERS IBUFDS -> BUFR -> IDDR (x8) in Analog_input module
IBUFDS_bit_clk : IBUFDS
generic map (
    DIFF_TERM           => TRUE,      -- Differential Termination
    IBUF_LOW_PWR        => FALSE,  -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
    IOSTANDARD          => "LVDS_25")
port map (
    O                   => bit_clk,           -- Buffer output
    I                   => adc_bit_clk_p,     -- Diff_p buffer input (connect directly to top-level port)
    IB                  => adc_bit_clk_n     -- Diff_n buffer input (connect directly to top-level port)
);
BUFR_bit_clk : BUFR
generic map (
   BUFR_DIVIDE          => "BYPASS", -- Values: "BYPASS, 1, 2, 3, 4, 5, 6, 7, 8"
   SIM_DEVICE           => "7SERIES"  -- Must be set to "7SERIES"
)
port map (
   O                    => bit_clkr,           -- 1-bit output: Clock output port
   CE                   => '1',               -- 1-bit input: Active high, clock enable (Divided modes only)
   CLR                  => '0',              -- 1-bit input: Active high, asynchronous clear (Divided modes only)
   I                    => bit_clk             -- 1-bit input: Clock buffer input driven by an IBUF, MMCM or local interconnect
);

--ADC FRAME CLOCK ENTERS IBUFDS AND GOES TO ANALOG INPUT MODULES
IBUFDS_frame : IBUFDS
generic map (
    DIFF_TERM           => TRUE,      -- Differential Termination
    IBUF_LOW_PWR        => FALSE,  -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
    IOSTANDARD          => "LVDS_25")
port map (
    O                   => frame,         -- Buffer output
    I                   => adc_frame_p,   -- Diff_p buffer input (connect directly to top-level port)
    IB                  => adc_frame_n   -- Diff_n buffer input (connect directly to top-level port)
);

--Analog input module used to simultaneously read from all 8 analog inputs every 40 nanoseconds
Analog_Inputs_Instantation : Analog_Inputs
port map (
    frame               => frame,
    bit_clk             => bit_clkr,
    scan_clk            => clk_scan,
    clk_RAM             => clk_RAM,
    data_p0             => adc_data_p_0,
    data_n0             => adc_data_n_0,
    data_p1             => adc_data_p_1,
    data_n1             => adc_data_n_1,
    data_p2             => adc_data_p_2,
    data_n2             => adc_data_n_2,
    data_p3             => adc_data_p_3,
    data_n3             => adc_data_n_3,
    data_p4             => adc_data_p_4,
    data_n4             => adc_data_n_4,
    data_p5             => adc_data_p_5,
    data_n5             => adc_data_n_5,
    data_p6             => adc_data_p_6,
    data_n6             => adc_data_n_6,
    data_p7             => adc_data_p_7,
    data_n7             => adc_data_n_7,
    adc_out_0           => AIN0,
    adc_out_1           => AIN1,
    adc_out_2           => AIN2,
    adc_out_3           => AIN3,
    adc_out_4           => AIN4,
    adc_out_5           => AIN5,
    adc_out_6           => AIN6,
    adc_out_7           => AIN7
);

--CLOCKING WIZARD TO TAKE INPUT 100MHz CLOCK AND OUTPUT REFERENCE 200MHz CLOCK AND SCAN 25MHz CLOCK
clkGenerator : clocking_wizard
port map ( 
    clk_RAM             => clk_RAM,
    clk_100MHz          => clk_100MHz,
    clk_scan            => clk_scan,
    clk_comms           => clk_comms
);

--MEMORY INTERFACE GENERATION (MIG) FOR DDR3 RAM ON-BOARD
u_mig_7series_0 : mig_7series_0
port map (
    -- Memory interface ports
    ddr3_addr           => ddr3_addr,
    ddr3_ba             => ddr3_ba,
    ddr3_cas_n          => ddr3_cas_n,
    ddr3_ck_n           => ddr3_ck_n,
    ddr3_ck_p           => ddr3_ck_p,
    ddr3_cke            => ddr3_cke,
    ddr3_ras_n          => ddr3_ras_n,
    ddr3_reset_n        => ddr3_reset_n,
    ddr3_we_n           => ddr3_we_n,
    ddr3_dq             => ddr3_dq,
    ddr3_dqs_n          => ddr3_dqs_n,
    ddr3_dqs_p          => ddr3_dqs_p,
    init_calib_complete => init_calib_complete,
    ddr3_cs_n           => ddr3_cs_n,
    ddr3_dm             => ddr3_dm,
    ddr3_odt            => ddr3_odt,
    -- Application interface ports
    app_addr            => app_addr,
    app_cmd             => app_cmd,
    app_en              => app_en,
    app_wdf_data        => app_wdf_data,
    app_wdf_end         => app_wdf_end,
    app_wdf_wren        => app_wdf_wren,
    app_rd_data         => app_rd_data,
    app_rd_data_end     => app_rd_data_end,
    app_rd_data_valid   => app_rd_data_valid,
    app_rdy             => app_rdy,
    app_wdf_rdy         => app_wdf_rdy,
    app_sr_req          => app_sr_req,
    app_ref_req         => app_ref_req,
    app_zq_req          => app_zq_req,
    app_sr_active       => app_sr_active,
    app_ref_ack         => app_ref_ack,
    app_zq_ack          => app_zq_ack,
    ui_clk              => ui_clk,
    ui_clk_sync_rst     => ui_clk_sync_rst,
    app_wdf_mask        => app_wdf_mask,
    -- System Clock Ports
    sys_clk_i           => clk_100MHz,
    -- Reference Clock Ports
    clk_ref_i           => clk_RAM,
    sys_rst             => sys_rst
);

--single data point to cross clock domains safely without metastability
usingRandoms_CDC : xpm_cdc_single
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SRC_INPUT_REG => 1)                     -- DECIMAL; 0=do not register input, 1=register input
port map (
    dest_out => usingRandomScan_dest,       -- 1-bit output: src_in synchronized to the destination clock domain. This output is registered
    dest_clk => ui_clk,                     -- 1-bit input: Clock signal for the destination clock domain.
    src_clk => clk_scan,                   -- 1-bit input: optional; required when SRC_INPUT_REG = 1
    src_in => usingRandomScan_src);         -- 1-bit input: Input signal to be synchronized to dest_clk domain.
    
--Begin code here

    usb_siwu <= '1';

    --power-down line for the ADC - never touch this, really, leave it on
    adc_pdwn <= '0';

    --various communications here (UART/USB to PC, SPI to analog chip)
    communications: process(clk_comms) is
    begin
        if rising_edge(clk_comms) then
            
            bank14_led <= run;
            bank15_led <= pause;
--            bank16_led <= txPause;
            bank16_led <= usb_txe;
            bank35_led <= txEnable;
            
            --this handles the reset of all FIFOs used in this code. Resets must be asserted for at least 4 clock cycles.
            if beenReset = '0' and run = '0' and resetCounter > 0 then
                resetCounter <= resetCounter - 1;
            elsif beenReset = '0' and run = '0' and resetCounter = 0 then
--                fifoReset <= '1'; beenReset <= '1'; txPixelCounter <= 0;
                fifoReset <= '1'; beenReset <= '1';
            elsif beenReset = '1' and resetCounter < 7 then
                resetCounter <= resetCounter + 1;
            elsif beenReset = '1' and resetCounter = 7 then
                fifoReset <= '0';
            end if;
            
            --finite state machine for communications starts here
            case communicationState is
            
            --after finishing any previous state it will usually come back to idle
            when IDLE =>
            
                --reset all flags and counters that need to be reset while idle
                if pauseReset = '1' and pause = '0' then    pauseReset <= '0';                              end if;
--                if run = '0' then                           transmitX <= 0; transmitY <= 0; txPause <= '0'; end if;
                if run = '0' then                           transmitX <= 0; transmitY <= 0;                 end if;
                
                --ensure no write/read enables were left high by accident, which would continue to read out/write in when the data is garbage
                randomUartXWriteEnable <= '0'; randomUartYWriteEnable <= '0';
                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
                
                --default state for write commands is asserted - will deassert when writing
                usb_wr <= '1';
                
                -------------------------------------------------------------------------------------------------------------------
                --if rxf goes low, data will be available on the next clock cycle. This has highest priority!
                --  reception data comes in 4-byte chunks from the computer
                if usb_rxf = '0' then
                    usb_rd <= '0';                  --deassert the read output to say "put the data on the bus"
                    usb_data <= (others => 'Z');    --put the bus into tri-state mode so that it can be written to
                    rxEnable <= '1';                --used to mimic the usb_rd output so we know what state we're in while in RX - we stay in RX until we get all 4 bytes of data
                    rxByteIndex <= 0;
                    communicationState <= RX;
                    
                -------------------------------------------------------------------------------------------------------------------
                --if txe goes low and we have been asked to send image data to the computer, we can write the data on the next clock cycle
                --  transmission data going to the computer is sent in 7-byte chunks
--                elsif txPause = '0' and usb_txe = '0' and (usb0FifoReadIsReset = '0' and usb0FifoEmpty = '0' and (not (set_mode = 3 or set_mode = 4) or (usb6FifoReadIsReset = '0' and usb6FifoEmpty = '0' and usb7FifoReadIsReset = '0' and usb7FifoEmpty = '0')) ) then
                elsif usb_txe = '0' and (usb0FifoReadIsReset = '0' and usb0FifoEmpty = '0' and (not (set_mode = 3 or set_mode = 4) or (usb6FifoReadIsReset = '0' and usb6FifoEmpty = '0' and usb7FifoReadIsReset = '0' and usb7FifoEmpty = '0')) ) then
                    usb_rd <= '1';              --assert the read output because we are not reading here
                    txByteIndex <= 0;
                    txImage <= '1';
                    txEnable <= '0';
                    --"F0" means you're initiating a pixel data transmission from FPGA to PC, so set that data up now for transmission
                    txData(55 downto 48) <= x"F0";                                                             --mask, 1 byte, i.e. "F0" byte
                    if set_mode = 3 or set_mode = 4 then 
                        txData(47 downto 32) <= usb6FifoReadData; usb6FifoReadEnable <= '1';                   --X value, 2 bytes in counts     (0 <-> 65535)
                        txData(31 downto 16) <= usb7FifoReadData; usb7FifoReadEnable <= '1';                   --Y value, 2 bytes in counts     (0 <-> 65535)
                    else
                        txData(47 downto 32) <= std_logic_vector(to_unsigned(transmitX * pixelStepSize,16));   --X value, 2 bytes in counts     (0 <-> 65535)
                        txData(31 downto 16) <= std_logic_vector(to_unsigned(transmitY * pixelStepSize,16));   --Y value, 2 bytes in counts     (0 <-> 65535)
                    end if;
                    txData(15 downto 0) <= usb0FifoReadData; usb0FifoReadEnable <= '1';                        --data value, 2 bytes in counts  (0 <-> 65535)
                    communicationState <= TX;
                    
                -------------------------------------------------------------------------------------------------------------------
                --otherwise do nothing - deassert read because we are not doing that, stay in IDLE
                else
                    usb_rd <= '1';
                    communicationState <= IDLE;
                    
                end if;
            
            --we enter this state when data is ready to be read in, and we stay here until we read in all four bytes of data. rxEnable flag will help us to manage states in this case
            when RX =>
                
                --if the flag is on, we are ready to read in data, so do that based on the current byte index
                if rxEnable = '1' then
                    case rxByteIndex is
                    when 0 =>       reg <= usb_data;                    rxByteIndex <= 1;
                    when 1 =>       setValue(23 downto 16) <= usb_data; rxByteIndex <= 2;
                    when 2 =>       setValue(15 downto  8) <= usb_data; rxByteIndex <= 3;
                    when 3 =>       setValue( 7 downto  0) <= usb_data;
                    when others =>  NULL;
                    end case;
                    usb_rd <= '1';              --reassert rd so we don't keep reading and the value can update eventually
                    rxEnable <= '0';            --deassert the flag so we wait for rxf to go low again
                    --if we have the last byte index, process the data; otherwise stay in this loop until we get a signal that more data is ready
                    if rxByteIndex = 3 then
                        communicationState <= RX_PROCESSING;
                    else
                        communicationState <= RX;
                    end if;
                else        --if the flag is off, we are waiting for more data via the usb_rxf signal deasserting
                    if usb_rxf = '0' then
                        usb_rd <= '0';          --deassert the read flag so the usb chip updates the data
                        rxEnable <= '1';        --assert the flag so we know to read the data in now
                    end if;
                end if;
                
                --if the rxf pin is high for 2 ms continuously we aren't sending any signals, so reset ALL counters and go back to IDLE just in case there was an issue
                if usb_rxf = '1' then
                    if rxOffCheck + 1 = 50000 then
                        rxByteIndex <= 0;
                        rxOffCheck <= 0;
                        communicationState <= IDLE;
                    else
                        rxOffCheck <= rxOffCheck + 1;
                    end if;
                else
                    rxOffCheck <= 0;
                end if;
                
                --unset the read enables to make sure the FIFOs aren't spewing out data, just in case
                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
                
            -- here we receive data from the PC, and either set values or give the PC information
            when RX_PROCESSING =>
                
                case reg is
                
                --"C_" means set a value from the PC to the FPGA
                when x"C0" => run                   <= setValue(0); if setValue(0) = '1' then beenReset <= '0'; end if; communicationState <= IDLE;
                when x"C1" => set_mode              <= to_integer(unsigned(setValue));                                  communicationState <= IDLE;
                when x"C2" => dwell_time            <= to_integer(unsigned(setValue));                                  communicationState <= IDLE;
                when x"C3" => line_end_time         <= to_integer(unsigned(setValue));                                  communicationState <= IDLE;
                when x"C5" => imageSideLengthPixels <= to_integer(unsigned(setValue));                                  communicationState <= IDLE;
                when x"C7" => set_x_voltage         <= setValue(15 downto 0);                                           communicationState <= IDLE;
                when x"C8" => set_y_voltage         <= setValue(15 downto 0);                                           communicationState <= IDLE;
                when x"C9" => pixel_move_time       <= to_integer(unsigned(setValue));                                  communicationState <= IDLE;
                --CD means we have computed a randomized image in python and are passing the x coordinates into image space 6 in RAM
                when x"CD" => 
                    if randomUartXWriteIsReset = '0' then randomUartXWriteData <= setValue(15 downto 0); randomUartXWriteEnable <= '1'; end if;
                                                                                                                        communicationState <= IDLE;
                    
                --CE means we have computed a randomized image in python and are passing the y coordinates into image space 7 in RAM
                when x"CE" =>
                    if randomUartYWriteIsReset = '0' then randomUartYWriteData <= setValue(15 downto 0); randomUartYWriteEnable <= '1'; end if;
                                                                                                                        communicationState <= IDLE;
                
                --"D0" means we're going into SPI mode for the analog input chip - this is external to the state machine as it does not use UART
                when x"D0" => adcTestMode       <= setValue(15 downto 0);                                               communicationState <= IDLE;
                
                --"E_" means request a value from the FPGA to the PC, so set that data up now
                when x"E1" => txData <= x"E1000000" & std_logic_vector(to_unsigned(set_mode,24));                       communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E2" => txData <= x"E2000000" & std_logic_vector(to_unsigned(dwell_time,24));                     communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E3" => txData <= x"E3000000" & std_logic_vector(to_unsigned(line_end_time,24));                  communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E5" => txData <= x"E5000000" & std_logic_vector(to_unsigned(imageSideLengthPixels,24));          communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E7" => txData <= x"E700000000" & set_x_voltage;                                                  communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E8" => txData <= x"E800000000" & set_y_voltage;                                                  communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                when x"E9" => txData <= x"E9000000" & std_logic_vector(to_unsigned(pixel_move_time,24));                communicationState <= TX; txEnable <= '0'; txByteIndex <= 0;
                
                --"F_" means we're sending data out from imaging; F2 means we are in continuous imaging mode and we're being asked to continue
                when x"F2" => pauseReset <= '1';                                                                        communicationState <= IDLE;
--                when x"F4" => txPause    <= '0';                                                                        communicationState <= IDLE;
                when others =>                                                                                          communicationState <= IDLE;
                end case;
                
                reg <= x"00"; setValue <= x"000000";        --reset the register and setValue, and the next case has been chosen in the case statement 
                
                --unset the read enables to make sure the FIFOs aren't spewing out data, just in case
                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
                
            --here we have been triggered to send data to the computer
            when TX =>
                --unset the read enables to make sure the FIFOs aren't spewing out data while we're processing the data we got
                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
                
                --when txEnable is 0, put the data on the bus
                if txEnable = '0' then
                    usb_wr <= '1';                              --assert the usb write bit so we stop triggering a send
                    if usb_txe = '0' then                       --if usb chip can be written to safely, this will be deasserted
                        txEnable <= '1';                        -- toggle the enable bit to send the data on the next clock cycle
                        case txByteIndex is                     --based on the current byte being transmitted, change what data is going out
                        when 0 =>
                            usb_data <=     txData(55 downto 48);
                            txTestData <=   txData(55 downto 48);
                            txByteIndex <=  1;
                        when 1 =>
                            usb_data <=     txData(47 downto 40);
                            txTestData <=   txData(47 downto 40);
                            txByteIndex <=  2;
                        when 2 =>
                            usb_data <=     txData(39 downto 32);
                            txTestData <=   txData(39 downto 32);
                            txByteIndex <=  3;
                        when 3 =>
                            usb_data <=     txData(31 downto 24);
                            txTestData <=   txData(31 downto 24);
                            txByteIndex <=  4;
                        when 4 =>
                            usb_data <=     txData(23 downto 16);
                            txTestData <=   txData(23 downto 16);
                            txByteIndex <=  5;
                        when 5 =>
                            usb_data <=     txData(15 downto  8);
                            txTestData <=   txData(15 downto  8);
                            txByteIndex <=  6;
                        when 6 | 7 =>
                            usb_data <=     txData( 7 downto  0);
                            txTestData <=   txData( 7 downto  0);
                            txByteIndex <=  0;
                        when others =>
                            communicationState <= IDLE;
                        end case;
                        communicationState <= TX;
                    else
                        communicationState <= TX;               --the usb chip cannot be written to, so just stay here until it is ready
                    end if;
                    
                --when txEnable is 1, trigger the data to send via usb_wr
                else
                    if usb_txe = '0' then
                        usb_wr <= '0';      --deassert the write bit to trigger the data to go out on the USB
                        if ((commsCounter+1) * commsPeriod) > pulseWidth then
                            commsCounter <= 0;
                            txEnable <= '0';    --reset the TX state--if the byte index is 0, then we have completed sending all seven bytes, so break the loop
                            --we reach byte index 0 only if we've sent all seven bytes, so tidy things up and proceed to next case
                            if txByteIndex = 0 then
                                --increment the sent values of x and y if we were sending an image
                                if txImage = '1' then
                                    txImage <= '0';
    --                                txPixelCounter <= txPixelCounter + 1;
                                    if transmitX+1 = imageSideLengthPixels then
                                        if transmitY+1 < imageSideLengthPixels then
                                            transmitY <= transmitY + 1;
                                            transmitX <= 0;
                                        end if;
                                    else
                                        transmitX <= transmitX + 1;
                                    end if;
                                    --almost empty turns on when we have one proper data value left in the image FIFO which will be read out when the fifo read enable toggles, so this is effectively the last data
                                    if ( (usb0FifoAlmostEmpty = '1') and (transmitY+1 = imageSideLengthPixels) and (transmitX+1 = imageSideLengthPixels) ) then
                                        communicationState <= TX_IMAGE_END;     --if the last pixels in an image, go to the image end transmission
                                    --if the buffer is in danger of being overrun (4kB buffer size, seven bytes per pixel) before the PC can keep up, pause transmission until the PC sends an ACK
    --                                elsif txPixelCounter >= 9000 then
    --                                    txPause <= '1';
    --                                    txPixelCounter <= 0;
    --                                    communicationState <= TX_PAUSE;
                                    else
                                        communicationState <= IDLE;             --if a normal set of pixels, go back to idle in case there is more incoming data
                                    end if;
                                --if we weren't sending an image, then we don't need to do anything else fancy, return to idle
                                else
                                    communicationState <= IDLE;
                                end if;
                            --if the byte index is NOT 0, then we are not done sending all seven bytes, so return to TX to continue
                            else
                                communicationState <= TX;
                            end if;                    
                        else
                            commsCounter <= commsCounter + 1;
                            communicationState <= TX;
                        end if;
                    else
                        communicationState <= TX;
                    end if;
                    
                end if;
            
--            when TX_PAUSE =>
--                --reset all FIFO enables 
--                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
--                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
--                usb_wr <= '1';
--                txData <= x"F3000000000000"; txEnable <= '0';
--                communicationState <= TX;
            
            --here, we have reached the end of the image, so send a "F1000000000000" string to signify this. Doing so enables synchronization of image data, and pauses the acquisition so that the PC input buffer is not overrun.
            when TX_IMAGE_END =>
                --reset all FIFO enables 
                usb0FifoReadEnable <= '0'; usb1FifoReadEnable <= '0'; usb2FifoReadEnable <= '0'; usb3FifoReadEnable <= '0';
                usb4FifoReadEnable <= '0'; usb5FifoReadEnable <= '0'; usb6FifoReadEnable <= '0'; usb7FifoReadEnable <= '0';
                transmitX <= 0; transmitY <= 0; usb_wr <= '1';
                txData <= x"F1000000000000"; txEnable <= '0';
                communicationState <= TX;
            end case;
            
        --serial peripheral interface (SPI) communications to analog input chip, used for testing only
            if not(adcTestMode = x"0000") then
                case adcSpiCounter is
                --chip select going low enables communication, keep low for all 20 bits of each transmission
                when 0|208 => adc_cs <= '0'; adc_sdata <= '0'; adc_sclk <= '0';
                --data from transmitted word from PC
                when 66|74|82|90|98|106|114|122|130|138|146|154|162|170|178|186 => adc_sdata <= adcTestMode(15 - (adcSpiCounter-66)/8);
                --rising edge of the clock every eight clock cycles (~80ns per period, 12.5MHz)
                when 4|12|20|28|36|44|52|60|68|76|84|92|100|108|116|124|132|140|148|156|164|172|180|188|212|220|228|236|244|252|260|268|276|284|292|300|308|316|324|332|340|348|356|364|372|380|388|396 => adc_sclk <= '1';
                --falling edge of the clock every eight clock cycles (~80ns per period, 12.5MHz)
                when 8|16|24|32|40|48|56|64|72|80|88|96|104|112|120|128|136|144|152|160|168|176|184|192|216|224|232|240|248|256|264|272|280|288|296|304|312|320|328|336|344|352|360|368|376|384|392|400 => adc_sclk <= '0';
                -- transmitting 1's of 0x0FF01 to update the device and first nibble of zeros for the address
                when 274|282|290|298|306|314|322|330 | 394 => adc_sdata <= '1';
                -- transmitting the 0's of the data to update the device (0x00XXXX <CS high gap> 0x00FF01)
                when 2|10|18|26|34|42|50|58 | 210|218|226|234|242|250|258|266 | 338|346|354|362|370|378|386 => adc_sdata <= '0';
                --finish transmission of first command, lift chip select, wait a bit then send the 0x0FF01 bits
                when 194 => adc_cs <= '1';
                --finish transmission, lift chip select, clear adcTestMode so we don't do this again
                when 404 => adc_cs <= '1'; adcTestMode <= x"0000"; adc_sdata <= '0'; adc_sclk <= '0';
                --when other cases, do nothing - leave the clock and data where they are to meet frequency requirements
                when others =>
                end case;
                adcSpiCounter <= adcSpiCounter + 1;
            elsif adcTestMode = x"0000" then
                adc_sdata <= '0';
                adc_sclk <= '0';
                adc_cs <= '1';
                adcSpiCounter <= 0;
            end if;
        end if;
        
    end process communications;
    
    --DAC Control will be performed here, and not in a sub-file, because we will need to clearly link the analog output drive to the analog input reads
    --sample scanning (raster or random) and data acquisition (with integration times) will happen here
    image_generation: process(clk_scan) is                         
    begin

    if rising_edge(clk_scan) then
        --set the outputs via the intermediate variables
        x_analog_out <= x_DAC_output;
        y_analog_out <= y_DAC_output;
        
        --don't implement step size as a shift register because it is actually division by the total pixels less one, so it is not at all clean. Look-up-table / case structure like this is better.
        --  step_size = 65536 / (total_pixels - 1)
        case imageSideLengthPixels is
        when    8 =>    pixelStepSize <= 9362;
        when   16 =>    pixelStepSize <= 4369;
        when   32 =>    pixelStepSize <= 2114;
        when   64 =>    pixelStepSize <= 1040;
        when  128 =>    pixelStepSize <=  516;
        when  256 =>    pixelStepSize <=  257;
        when  512 =>    pixelStepSize <=  128;
        when 1024 =>    pixelStepSize <=   64;
        when 2048 =>    pixelStepSize <=   32;
        when 4096 =>    pixelStepSize <=   16;
        when 4728 =>    pixelStepSize <=   13;
        when others =>  pixelStepSize <= 9362;
        end case;
            
        --shift the sample delay register one to the left every clock cycle. Bit #0 on the right will be set somewhere in the below case statements
        adcShifter(7 downto 1) <= adcShifter(6 downto 0); 
        
        --interpret the mode...
        --Raster scan will take an image line-by-line.
        --Random scan will grab random xy coordinates from python, store them in RAM, and then use them as positional coordinates.
        --Continuous imaging (1 or 3) will continue taking images until the user presses stop on the interface.
        --Single image (2 or 4) will take a single image and stop all acquisition at that point.
        if      set_mode = 0 then                   AcquisitionMode <= idling;          usingRandomScan_src <= '0';
        elsif   set_mode = 1 or set_mode = 2 then   AcquisitionMode <= raster_scan;     usingRandomScan_src <= '0';
        elsif   set_mode = 3 or set_mode = 4 then   AcquisitionMode <= random_scan;     usingRandomScan_src <= '1';
        elsif   set_mode = 5 then                   AcquisitionMode <= fixed_voltage;   usingRandomScan_src <= '0';
        elsif   set_mode = 6 then                   AcquisitionMode <= testing;         usingRandomScan_src <= '0';
        else                                        AcquisitionMode <= idling;          usingRandomScan_src <= '0';
        end if;
        
        --the ADC outputs data from the current clock cycle a total of 8 clock cycles later. We need to delay, so adcShifter is an 8-bit counter that
        --shifts 1's and 0's to the left in the main case statement, and when a 1 happens at the leftmost bit, acquire data
        if adcShifter(7) = '1' then
            if sampleCounter + 1 < dwellCycles then
                --if we need to integrate more samples to get the dwell time correct, add the analog data to the data sum and increment the counter
                sampleCounter <= sampleCounter + 1;
                dataSum0 <= std_logic_vector(unsigned(dataSum0) + unsigned(AIN0));
                dataSum1 <= std_logic_vector(unsigned(dataSum1) + unsigned(AIN1));
                dataSum2 <= std_logic_vector(unsigned(dataSum2) + unsigned(AIN2));
                dataSum3 <= std_logic_vector(unsigned(dataSum3) + unsigned(AIN3));
                dataSum4 <= std_logic_vector(unsigned(dataSum4) + unsigned(AIN4));
                dataSum5 <= std_logic_vector(unsigned(dataSum5) + unsigned(AIN5));
                dataSum6 <= std_logic_vector(unsigned(dataSum6) + unsigned(AIN6));
                dataSum7 <= std_logic_vector(unsigned(dataSum7) + unsigned(AIN7));
                
                --ensure we aren't writing to the FIFO just yet
                scan0FifoWriteEnable <= '0'; scan1FifoWriteEnable <= '0'; scan2FifoWriteEnable <= '0'; scan3FifoWriteEnable <= '0';
                scan4FifoWriteEnable <= '0'; scan5FifoWriteEnable <= '0'; scan6FifoWriteEnable <= '0'; scan7FifoWriteEnable <= '0';
                
            --if sampling is complete, send the data into the FIFO to be put into RAM. Ensure we are not overflowing a 16-bit value
            elsif sampleCounter + 1 = dwellCycles then
            
                --Analog input 0
                if to_integer(unsigned(dataSum0) + unsigned(AIN0)) < 65536 then
                    scan0FifoWriteData <= std_logic_vector(unsigned(dataSum0(15 downto 0)) + unsigned(AIN0));
                else
                    scan0FifoWriteData <= (others => '1');
                end if;
                scan0FifoWriteEnable <= '1';
                
                --Analog input 1
                if to_integer(unsigned(dataSum1) + unsigned(AIN1)) < 65536 then
                    scan1FifoWriteData <= std_logic_vector(unsigned(dataSum1(15 downto 0)) + unsigned(AIN1));
                else
                    scan1FifoWriteData <= (others => '1');
                end if;
                scan1FifoWriteEnable <= '1';
                
                --Analog input 2
                if to_integer(unsigned(dataSum2) + unsigned(AIN2)) < 65536 then
                    scan2FifoWriteData <= std_logic_vector(unsigned(dataSum2(15 downto 0)) + unsigned(AIN2));
                else
                    scan2FifoWriteData <= (others => '1');
                end if;
                scan2FifoWriteEnable <= '1';
                
                --Analog input 3
                if to_integer(unsigned(dataSum3) + unsigned(AIN3)) < 65536 then
                    scan3FifoWriteData <= std_logic_vector(unsigned(dataSum3(15 downto 0)) + unsigned(AIN3));
                else
                    scan3FifoWriteData <= (others => '1');
                end if;
                scan3FifoWriteEnable <= '1';
                
                --Analog input 4
                if to_integer(unsigned(dataSum4) + unsigned(AIN4)) < 65536 then
                    scan4FifoWriteData <= std_logic_vector(unsigned(dataSum4(15 downto 0)) + unsigned(AIN4));
                else
                    scan4FifoWriteData <= (others => '1');
                end if;
                scan4FifoWriteEnable <= '1';
                
                --Analog input 5
                if to_integer(unsigned(dataSum5) + unsigned(AIN5)) < 65536 then
                    scan5FifoWriteData <= std_logic_vector(unsigned(dataSum5(15 downto 0)) + unsigned(AIN5));
                else
                    scan5FifoWriteData <= (others => '1');
                end if;
                scan5FifoWriteEnable <= '1';
                
                --in random scan mode (3 or 4) random positional data for X and Y is stored in image 6 and 7. Don't overwrite it, so skip this
                if not (set_mode = 3 or set_mode = 4) then
                
                    --Analog input 6
                    if to_integer(unsigned(dataSum6) + unsigned(AIN6)) < 65536 then
                        scan6FifoWriteData <= std_logic_vector(unsigned(dataSum6(15 downto 0)) + unsigned(AIN6));
                    else
                        scan6FifoWriteData <= (others => '1');
                    end if;
                    scan6FifoWriteEnable <= '1';
                    
                    --Analog input 7
                    if to_integer(unsigned(dataSum7) + unsigned(AIN7)) < 65536 then
                        scan7FifoWriteData <= std_logic_vector(unsigned(dataSum7(15 downto 0)) + unsigned(AIN7));
                    else
                        scan7FifoWriteData <= (others => '1');
                    end if;
                    scan7FifoWriteEnable <= '1';
                    
                end if;
            end if;
        --if the current value of adcShifter is 0 and not 1, do nothing
        else
            sampleCounter <= 0;
            dataSum0 <= (others => '0');
            dataSum1 <= (others => '0');
            dataSum2 <= (others => '0');
            dataSum3 <= (others => '0');
            dataSum4 <= (others => '0');
            dataSum5 <= (others => '0');
            dataSum6 <= (others => '0');
            dataSum7 <= (others => '0');
                
            --ensure we aren't writing to the FIFO just yet
            scan0FifoWriteEnable <= '0'; scan1FifoWriteEnable <= '0'; scan2FifoWriteEnable <= '0'; scan3FifoWriteEnable <= '0';
            scan4FifoWriteEnable <= '0'; scan5FifoWriteEnable <= '0'; scan6FifoWriteEnable <= '0'; scan7FifoWriteEnable <= '0';
        end if;
        
        mode_case : case AcquisitionMode is
         
        when raster_scan =>  -- will only run if raster_scan selected as mode
             
            if run = '0' then -- stop scanning if stop command sent
                Raster_Scan_State <= IDLING;
            end if;
            
            if (set_mode = 1 and pauseReset = '1') or run = '0' then
                pause <= '0';
            end if;
            
            case Raster_Scan_State is
                
                when IDLING => -- wait here until UART_RX process receives start command
                    x_location   <= 0;
                    y_location   <= 0;
                    x_DAC_output <= x"0000";
                    y_DAC_output <= x"0000";
                    dwellCycles <= to_integer(shift_left(baseDwell, dwell_time));
                    
                    --this clock cycle, we did not sample here
                    adcShifter(0) <= '0';
                    
                    --if run set on and we aren't paused by an end-of-image wait, continue with the raster scan
                    if run = '1' and pause = '0' then
                        Raster_Scan_State <= MEASURE_AND_MOVE;
                    else
                        Raster_Scan_State <= IDLING;
                    end if;
                    
                when MEASURE_AND_MOVE => -- line scan: acquire data during integration time, then increment x and/or y position and update DAC signals
                    if dwellCounter = dwellCycles then
                        dwellCounter <= 0;
                        --this clock cycle, we did not sample here - we passed the data on to one of the storage pixels
                        adcShifter(0) <= '0';
                        if x_location + 1 = imageSideLengthPixels and y_location + 1 = imageSideLengthPixels then     -- reached end of image
                            x_DAC_output <= x"0000";
                            y_DAC_output <= x"0000";
                            x_location <= 0;
                            y_location <= 0;
                            Raster_Scan_State <= SCAN_END_OF_FRAME;
                        elsif x_location + 1 = imageSideLengthPixels then                                      -- reached end of line
                            x_DAC_output <= x"0000";
                            x_location <= 0;
                            y_DAC_output <= std_logic_vector(to_unsigned(to_integer(unsigned( y_DAC_output )) + pixelStepSize , 16));
                            y_location <= y_location + 1;
                            Raster_Scan_State <= SCAN_END_OF_LINE;
                        else                                                                            -- move to next pixel
                            x_DAC_output <= std_logic_vector(to_unsigned(to_integer(unsigned( x_DAC_output )) + pixelStepSize , 16));
                            x_location <= x_location + 1;
                            Raster_Scan_State <= SCAN_WAIT_FOR_PIXEL;
                        end if;
                    else                                                                                -- still in sampling mode for this pixel, increment and add to rolling sum
                        --this clock cycle, we DID sample here! In 8 clock cycles, we need to read from the analog inputs, and that will happen in the code above
                        adcShifter(0) <= '1';
                        dwellCounter <= dwellCounter + 1;
                    end if;
                    
                when SCAN_WAIT_FOR_PIXEL => --time to delay the next reads so that the analog ouptut chip can drive the beam and have time for it to keep up
                    --this clock cycle, we did not sample here, we were moving the beam around a bit
                    adcShifter(0) <= '0';
                    if waitCounter = pixel_move_time then
                        waitCounter <= 0;
                        Raster_Scan_State <= MEASURE_AND_MOVE;
                    else
                        waitCounter <= waitCounter + 1;
                    end if;
                    
                when SCAN_END_OF_LINE => -- end of line reached, wait for line_end_time, then increment y position and reset x position
                    --this clock cycle, we did not sample here, we moved the beam to the next line
                    adcShifter(0) <= '0';
                    if lineCounter + 1 = line_end_time then
                        lineCounter <= 0;
                        Raster_Scan_State <= MEASURE_AND_MOVE;
                    else
                        lineCounter <= lineCounter + 1;
                    end if;
                 
                when SCAN_END_OF_FRAME => -- end of frame reached, wait for line_end_time for beam to get back and then pause for continuation from PC or stop scan command
                    --this clock cycle, we did not sample here, as we finished the image
                    adcShifter(0) <= '0';
                    if frameCounter + 1 = line_end_time then
                        Raster_Scan_State <= IDLING;
                        frameCounter <= 0;
                        pause <= '1';
                    else
                        frameCounter <= frameCounter + 1;
                        Raster_Scan_State <= SCAN_END_OF_FRAME;
                    end if;
                
                when others => 
                    --this clock cycle, we did not sample here
                    adcShifter(0) <= '0';
                    Raster_Scan_State <= IDLING;
            
            end case;
        
        --if random scan selected, we will get position pairs from RAM image 6 and 7, move to those, and take data
        when random_scan => 
             
            if run = '0' then -- stop scanning if stop command sent
                Random_Scan_State <= IDLING;
            end if;
            
            --if continuous mode selected and continue received from computer, continue
            if (set_mode = 3 and pauseReset = '1') or run = '0' then
                pause <= '0';
            end if;
            
            case Random_Scan_State is
                
                when IDLING => -- wait here until UART_RX process receives start command
                    x_location   <= 0;
                    y_location   <= 0;
                    x_DAC_output <= x"0000";
                    y_DAC_output <= x"0000";
                    dwellCycles <= to_integer(shift_left(baseDwell, dwell_time));
                    
                    --this clock cycle, we did not sample here
                    adcShifter(0) <= '0';
                    
                    --if run set on and not paused, start the random scan by reading in positions from RAM FIFO
                    if run = '1' and pause = '0' then
                        Random_Scan_State <= READ_POSITIONS;
                    else
                        Random_Scan_State <= IDLING;
                    end if;
                    
                when READ_POSITIONS =>      --here we will read from the RAM FIFOs for X and Y random data and move to those locations
                    adcShifter(0) <= '0';
                    if not (randomScanXReadIsReset = '1' or randomScanYReadIsReset = '1' or randomScanXEmpty = '1' or randomScanYEmpty = '1') then
                        x_DAC_output <= randomScanXReadData;
                        y_DAC_output <= randomScanYReadData;
                        randomScanXReadEnable <= '1';
                        randomScanYReadEnable <= '1';
                        Random_Scan_State <= SCAN_WAIT_FOR_PIXEL;
                    else
                        Random_Scan_State <= READ_POSITIONS;
                    end if;
                    
                    --this was attempted but not fully tested. Saved in case needed in future so not starting from nothing
--                when HYSTERESIS =>      --we usually want to approach pixels from the same direction to eliminate hysteresis, so we will come from the top-left by a bit every time (if we can)
--                    adcShifter(0) <= '0';
--                    if lineCounter >= line_end_time then        --here use the pixel line delay value as the majority of random moves will likely be large. UI label should shift to accomodate this
--                        case randomPositionCount is
--                        when 0 =>
--                            x_DAC_output <= std_logic_vector(shift_right(unsigned(randomScanXReadData), 4));
--                            y_DAC_output <= std_logic_vector(shift_right(unsigned(randomScanYReadData), 4));
--                        lineCounter <= 0;
--                        Random_Scan_State <= SCAN_WAIT_FOR_PIXEL;
--                    else
--                        lineCounter <= lineCounter + 1;
--                        Random_Scan_State <= HYSTERESIS;
--                    end if;
                
                when SCAN_WAIT_FOR_PIXEL => --we will now move to the actual position and wait for the beam to arrive
                    --this clock cycle, we did not sample here, we were moving the beam around a bit
                    adcShifter(0) <= '0';
                    randomScanXReadEnable <= '0';
                    randomScanYReadEnable <= '0';
                    if waitCounter = pixel_move_time then
                        waitCounter <= 0;
                        Random_Scan_State <= MEASURE_AND_MOVE;
                    else
                        waitCounter <= waitCounter + 1;
                        Random_Scan_State <= SCAN_WAIT_FOR_PIXEL;
                    end if;
                
                when MEASURE_AND_MOVE => -- acquire data during integration time, and increment pixel count
                
                    if dwellCounter = dwellCycles then
                        dwellCounter <= 0;
                        --this clock cycle, we did not sample here - we passed the data on to one of the storage pixels
                        adcShifter(0) <= '0';
                        if x_location + 1 = imageSideLengthPixels and y_location + 1 = imageSideLengthPixels then     -- reached end of image
                            x_location <= 0; y_location <= 0;
                            x_DAC_output <= (others => '0');
                            y_DAC_output <= (others => '0');
                            Random_Scan_State <= SCAN_END_OF_FRAME;
                        elsif x_location + 1 = imageSideLengthPixels then                                      -- move to next pixel
                            x_location <= 0; y_location <= y_location + 1;
                            Random_Scan_State <= READ_POSITIONS;
                        else                                                                            -- move to next pixel
                            x_location <= x_location + 1;
                            Random_Scan_State <= READ_POSITIONS;
                        end if;
                    else                                                                                -- still in sampling mode for this pixel, increment and add to rolling sum
                        --this clock cycle, we DID sample here! In 8 clock cycles, we need to read from the analog inputs
                        adcShifter(0) <= '1';
                        dwellCounter <= dwellCounter + 1;
                    end if;
                 
                when SCAN_END_OF_FRAME => -- end of frame reached, move to 0,0, wait for move to complete, and then return to idle with pause on
                    --this clock cycle, we did not sample here, as we finished the image
                    adcShifter(0) <= '0';
                    if frameCounter + 1 = line_end_time then
                        Random_Scan_State <= IDLING;
                        frameCounter <= 0;
                        pause <= '1';
                    else
                        x_DAC_output <= (others => '0');
                        y_DAC_output <= (others => '0');
                        frameCounter <= frameCounter + 1;
                        Random_Scan_State <= SCAN_END_OF_FRAME;
                    end if;
                
                when others => 
                    --this clock cycle, we did not sample here
                    adcShifter(0) <= '0';
                    Random_Scan_State <= IDLING;
            
            end case;
        
        when fixed_voltage => --for setting a fixed voltage on the deflectors
            x_analog_out <= set_x_voltage;
            y_analog_out <= set_y_voltage;
            --set_x_voltage and set_y_voltage received from PC
        
        when testing => --analog outputs will mirror analog input 0
            x_analog_out <= "1000000000000000";  --x analog output will mirror the first analog input
--            y_analog_out <= adc_data_1 & "00";  --y analog output will mirror the second analog input
--            y_analog_out <= std_logic_vector(unsigned(AIN0)/2) & "00";  --y analog output will mirror half the value of the first analog input
            y_analog_out <= "1111111111111111";
        
        when others => NULL;--do nothing   
        
        end case mode_case;
    end if;
    end process image_generation;
    
    --this process runs at the ui_clk frequency which is generated by the memory interface generator (MIG) that interfaces with the RAM. It controls RAM reads and writes.
    RAM : process(ui_clk) is
    begin
 
    if rising_edge(ui_clk) then
        if (ui_clk_sync_rst = '1') then 
            stateRam <= IDLE;
            app_en <= '0';
            app_wdf_wren <= '0';
        end if;
    
        if (ui_clk_sync_rst = '0') then
            
            --if any FIFOs are currently being reset, put the memory pointers back to their starting positions
            if randomUartXReadIsReset = '1' or randomUartYReadIsReset = '1' then
                writeAddressX <= x"6000000"; readAddressX <= x"6000000";
            end if;
            if randomScanXWriteIsReset = '1' or randomScanYWriteIsReset = '1' then
                writeAddressY <= x"7000000"; readAddressY <= x"7000000";
            end if;
            if usb0FifoWriteIsReset = '1' or scan0FifoReadIsReset = '1' then
                writeAddress0 <= x"0000000"; readAddress0 <= x"0000000";
            end if;
            if usb1FifoWriteIsReset = '1' or scan1FifoReadIsReset = '1' then
                writeAddress1 <= x"1000000"; readAddress1 <= x"1000000"; 
            end if;
            if usb2FifoWriteIsReset = '1' or scan2FifoReadIsReset = '1' then
                writeAddress2 <= x"2000000"; readAddress2 <= x"2000000";
            end if;
            if usb3FifoWriteIsReset = '1' or scan3FifoReadIsReset = '1' then
                writeAddress3 <= x"3000000"; readAddress3 <= x"3000000";
            end if; 
            if usb4FifoWriteIsReset = '1' or scan4FifoReadIsReset = '1' then
                writeAddress4 <= x"4000000"; readAddress4 <= x"4000000";
            end if;
            if usb5FifoWriteIsReset = '1' or scan5FifoReadIsReset = '1' then
                writeAddress5 <= x"5000000"; readAddress5 <= x"5000000";
            end if;
            if usb6FifoWriteIsReset = '1' or scan6FifoReadIsReset = '1' then
                writeAddress6 <= x"6000000"; readAddress6 <= x"6000000";
            end if;
            if usb7FifoWriteIsReset = '1' or scan7FifoReadIsReset = '1' then
                writeAddress7 <= x"7000000"; readAddress7 <= x"7000000";
            end if;
            
            case stateRam is
            --the idle case handles when nothing is actually happening; it resets all read/write enable flags for FIFOs and checks to see what can be done next
            when IDLE =>
                
                --ensure we are not accidentally reading or writing FIFOs in the IDLE state
                randomScanXWriteEnable <= '0'; randomScanYWriteEnable <= '0';
                usb0FifoWriteEnable <= '0'; usb1FifoWriteEnable <= '0'; usb2FifoWriteEnable <= '0'; usb3FifoWriteEnable <= '0';
                usb4FifoWriteEnable <= '0'; usb5FifoWriteEnable <= '0'; usb6FifoWriteEnable <= '0'; usb7FifoWriteEnable <= '0';
                
                --if RAM calibration incomplete, do nothing
                if init_calib_complete = '0' then
                    stateRam <= IDLE;
                else
                    --pixels are stored in the RAM that have not been sent, READ them into the UART FIFO to be punted to the PC
                    if ( not (writeAddress0 = readAddress0) and not (writeAddress7 = readAddress7) and (usb0FifoWriteIsReset = '0') and usb0FifoAlmostFull = '0' ) then
--                    if ( not (writeAddress0 = readAddress0) and not (writeAddress7 = readAddress7) and (usb0FifoWriteIsReset = '0') and usb0FifoFull = '0' ) then
                        reader <= 0;
                        stateRam <= READ;
                    
                    --a set of 8 pixels is ready to WRITE into RAM from the scan FIFO
                    elsif scan0FifoEmpty = '0' and scan0FifoReadIsReset = '0' then
                        writer <= 0;
                        stateRam <= WRITE;
                    
                    --if random X positions have come in from the random UART FIFOs to be put into RAM, do that now
                    elsif randomUartXEmpty = '0' and randomUartXReadIsReset = '0' then
                        stateRam <= WRITE_RANDOM_X;
                        
                    --if random Y positions have come in from the random UART FIFOs to be put into RAM, do that now
                    elsif randomUartYEmpty = '0' and randomUartYReadIsReset = '0' then
                        stateRam <= WRITE_RANDOM_Y;
                        
                    --if unsent random XY positions are in memory and need to be sent out to the scan loop via the random FIFOs, do that now
                    elsif not(writeAddressX = readAddressX) and not(writeAddressY = readAddressY) and randomScanXWriteIsReset = '0' and randomScanYWriteIsReset = '0' and randomScanXFull = '0' and randomScanYFull = '0' then 
                        stateRam <= READ_RANDOMS;
                    
                    --otherwise the RAM will put it's feet up as there is nothing to do.
                    else
                        stateRam <= IDLE;
                    end if;
                end if;
            
            --this case handles when data comes in from the image generation process and needs to be written to RAM.
            when WRITE =>
                if (app_rdy = '1' and app_wdf_rdy = '1') then
                    case writer is
                    --"analog input x" makes "image x"
                    when 0 =>
                        app_wdf_data <= scan0FifoReadData; scan0FifoReadEnable <= '1';
                        app_addr <= writeAddress0;
                        writeAddress0 <= std_logic_vector(unsigned(writeAddress0) + 8);
                        writer <= 1;
                    when 1 =>
                        app_wdf_data <= scan1FifoReadData; scan1FifoReadEnable <= '1';
                        app_addr <= writeAddress1;
                        writeAddress1 <= std_logic_vector(unsigned(writeAddress1) + 8);
                        writer <= 2;
                    when 2 =>
                        app_wdf_data <= scan2FifoReadData; scan2FifoReadEnable <= '1';
                        app_addr <= writeAddress2;
                        writeAddress2 <= std_logic_vector(unsigned(writeAddress2) + 8);
                        writer <= 3;
                    when 3 =>
                        app_wdf_data <= scan3FifoReadData; scan3FifoReadEnable <= '1';
                        app_addr <= writeAddress3;
                        writeAddress3 <= std_logic_vector(unsigned(writeAddress3) + 8);
                        writer <= 4;
                    when 4 =>
                        app_wdf_data <= scan4FifoReadData; scan4FifoReadEnable <= '1';
                        app_addr <= writeAddress4;
                        writeAddress4 <= std_logic_vector(unsigned(writeAddress4) + 8);
                        writer <= 5;
                    when 5 =>
                        app_wdf_data <= scan5FifoReadData; scan5FifoReadEnable <= '1';
                        app_addr <= writeAddress5;
                        writeAddress5 <= std_logic_vector(unsigned(writeAddress5) + 8);
                        --if using a random pattern, the X and Y coordinates for the pattern are stored in image 6 and 7 respectively so don't overwrite those
                        if usingRandomScan_dest = '1' then      
                            writer <= 0;
                            writeAddress6 <= std_logic_vector(unsigned(writeAddress6) + 8);
                            writeAddress7 <= std_logic_vector(unsigned(writeAddress7) + 8);
                        else
                            writer <= 6;
                        end if;
                    when 6 =>
                        app_wdf_data <= scan6FifoReadData; scan6FifoReadEnable <= '1';
                        app_addr <= writeAddress6;
                        writeAddress6 <= std_logic_vector(unsigned(writeAddress6) + 8);
                        writer <= 7;
                    when 7 =>
                        app_wdf_data <= scan7FifoReadData; scan7FifoReadEnable <= '1';
                        app_addr <= writeAddress7;
                        writeAddress7 <= std_logic_vector(unsigned(writeAddress7) + 8);
                        writer <= 0;
                    end case;
                    app_en <= '1';
                    app_wdf_wren <= '1';        --app_wdf_wren enables the write to RAM at the specified address app_addr with data app_wdf_data
                    app_cmd <= "000";           --app_cmd = "000" means you're going to write to RAM
                    stateRam <= WRITE_WAIT;
                end if;
            
            --this case handles the delay while data is written to RAM. Once done, it will check to see if there is more data to write or if it can go back to IDLE
            when WRITE_WAIT =>
                scan0FifoReadEnable <= '0'; scan1FifoReadEnable <= '0'; scan2FifoReadEnable <= '0'; scan3FifoReadEnable <= '0'; 
                scan4FifoReadEnable <= '0'; scan5FifoReadEnable <= '0'; scan6FifoReadEnable <= '0'; scan7FifoReadEnable <= '0'; 
                if (app_rdy = '1' and app_en = '1') then
                    app_en <= '0';
                end if;
                if (app_wdf_rdy = '1' and app_wdf_wren = '1') then
                    app_wdf_wren <= '0';
                end if;
                if (app_en = '0' and app_wdf_wren = '0') then
                    if writer = 0 then
                        stateRam <= IDLE;
                    else
                        stateRam <= WRITE;
                    end if;
                end if;
            
            --this case handles sending intensity information for all 8 images to the communications process so the data can be sent to the computer for display
            when READ =>
                usb0FifoWriteEnable <= '0'; usb1FifoWriteEnable <= '0'; usb2FifoWriteEnable <= '0'; usb3FifoWriteEnable <= '0';
                usb4FifoWriteEnable <= '0'; usb5FifoWriteEnable <= '0'; usb6FifoWriteEnable <= '0'; usb7FifoWriteEnable <= '0';
                if app_rdy = '1' then
                    app_en <= '1';      --app_en enables the read from RAM at the specified address app_addr with data app_rd_data
                    app_cmd <= "001";   --app_cmd = "001" means you're going to read from RAM
                    case reader is
                    when 0 => app_addr <= readAddress0;
                    when 1 => app_addr <= readAddress1;
                    when 2 => app_addr <= readAddress2;
                    when 3 => app_addr <= readAddress3;
                    when 4 => app_addr <= readAddress4;
                    when 5 => app_addr <= readAddress5;
                    when 6 => app_addr <= readAddress6;
                    when 7 => app_addr <= readAddress7;
                    end case;
                    stateRam <= READ_WAIT;
                end if;
            
            --this case handles the delay while the data is retrieved from RAM. If more data is to be sent, it will loop back to READ otherwise it will go to IDLE
            when READ_WAIT =>
                if (app_rdy = '1' and app_en = '1') then
                    app_en <= '0';
                end if;
                if (app_rd_data_valid = '1') then
                    case reader is
                    when 0 =>
                        usb0FifoWriteData <= app_rd_data; usb0FifoWriteEnable <= '1';
                        readAddress0 <= std_logic_vector(unsigned(readAddress0) + 8);
                        reader <= 1;
                        stateRam <= READ;
                    when 1 =>
                        usb1FifoWriteData <= app_rd_data; usb1FifoWriteEnable <= '1';
                        readAddress1 <= std_logic_vector(unsigned(readAddress1) + 8);
                        reader <= 2;
                        stateRam <= READ;
                    when 2 =>
                        usb2FifoWriteData <= app_rd_data; usb2FifoWriteEnable <= '1';
                        readAddress2 <= std_logic_vector(unsigned(readAddress2) + 8);
                        reader <= 3;
                        stateRam <= READ;
                    when 3 =>
                        usb3FifoWriteData <= app_rd_data; usb3FifoWriteEnable <= '1';
                        readAddress3 <= std_logic_vector(unsigned(readAddress3) + 8);
                        reader <= 4;
                        stateRam <= READ;
                    when 4 =>
                        usb4FifoWriteData <= app_rd_data; usb4FifoWriteEnable <= '1';
                        readAddress4 <= std_logic_vector(unsigned(readAddress4) + 8);
                        reader <= 5;
                        stateRam <= READ;
                    when 5 =>
                        usb5FifoWriteData <= app_rd_data; usb5FifoWriteEnable <= '1';
                        readAddress5 <= std_logic_vector(unsigned(readAddress5) + 8);
                        reader <= 6;
                        stateRam <= READ;
                    when 6 =>
                        usb6FifoWriteData <= app_rd_data; usb6FifoWriteEnable <= '1';
                        readAddress6 <= std_logic_vector(unsigned(readAddress6) + 8);
                        reader <= 7;
                        stateRam <= READ;
                    when 7 =>
                        usb7FifoWriteData <= app_rd_data; usb7FifoWriteEnable <= '1';
                        readAddress7 <= std_logic_vector(unsigned(readAddress7) + 8);
                        reader <= 0;
                        stateRam <= IDLE;
                    end case;
                end if;
            
            --this case handles when random X data positions comes in from the UART FIFO, and writes it to image 6 locations
            when WRITE_RANDOM_X =>
                app_wdf_data <= randomUartXReadData; randomUartXReadEnable <= '1';
                app_addr <= writeAddressX;
                writeAddressX <= std_logic_vector(unsigned(writeAddressX) + 8);
                app_en <= '1';
                app_wdf_wren <= '1';
                app_cmd <= "000";           --app_cmd = "000" means you're going to write
                stateRam <= RANDOM_WRITE_WAIT;
            
            --this case handles when random Y data positions comes in from the UART FIFO, and writes it to image 7 locations
            when WRITE_RANDOM_Y =>
                app_wdf_data <= randomUartYReadData; randomUartYReadEnable <= '1';
                app_addr <= writeAddressY;
                writeAddressY <= std_logic_vector(unsigned(writeAddressY) + 8);
                app_en <= '1';
                app_wdf_wren <= '1';
                app_cmd <= "000";           --app_cmd = "000" means you're going to write
                stateRam <= RANDOM_WRITE_WAIT;
            
            --this case handles the delay while waiting for the RAM to be written to
            when RANDOM_WRITE_WAIT =>
                randomUartXReadEnable <= '0'; randomUartYReadEnable <= '0';
                if (app_rdy = '1' and app_en = '1') then
                    app_en <= '0';
                end if;
                if (app_wdf_rdy = '1' and app_wdf_wren = '1') then
                    app_wdf_wren <= '0';
                end if;
                if (app_en = '0' and app_wdf_wren = '0') then
                    stateRam <= IDLE;
                end if;
            
            --this case handles the reading of random positions out to the image generation process, starting with reading X positions to the random X FIFO
            when READ_RANDOMS =>
                if app_rdy = '1' then
                    app_en <= '1';
                    app_cmd <= "001";
                    app_addr <= readAddressX;
                    stateRam <= READ_RANDOMS_WAIT;
                end if;
            
            --this case handles the delay while waiting for information to be read from RAM
            when READ_RANDOMS_WAIT =>
                if (app_rdy = '1' and app_en = '1') then
                    app_en <= '0';
                end if;
                if (app_rd_data_valid = '1') then
                    randomScanXWriteData <= app_rd_data; randomScanXWriteEnable <= '1';
                    readAddressX <= std_logic_vector(unsigned(readAddressX) + 8);
                    stateRam <= READ_RANDOMS_2;
                end if;
            
            --this case handles the reading of random positions out to the image generation process, following with reading Y positions to the random Y FIFO
            when READ_RANDOMS_2 =>
                randomScanXWriteEnable <= '0';
                if app_rdy = '1' then
                    app_en <= '1';
                    app_cmd <= "001";
                    app_addr <= readAddressY;
                    stateRam <= READ_RANDOMS_WAIT_2;
                end if;
            
            --this case handles the delay while waiting for information to be read from RAM
            when READ_RANDOMS_WAIT_2 =>
                if (app_rdy = '1' and app_en = '1') then
                    app_en <= '0';
                end if;
                if (app_rd_data_valid = '1') then
                    randomScanYWriteData <= app_rd_data; randomScanYWriteEnable <= '1';
                    readAddressY <= std_logic_vector(unsigned(readAddressY) + 8);
                    stateRam <= IDLE;
                end if;
              
            end case;
        end if;
    end if;
    end process RAM;

end Behavioral;