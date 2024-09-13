library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.NUMERIC_STD.ALL;

Library UNISIM;
use UNISIM.vcomponents.all; 

Library xpm;
use xpm.vcomponents.all;

entity Analog_Inputs is
    Port (
        frame           : in std_logic;
        bit_clk         : in std_logic;
        scan_clk        : in std_logic;
        clk_RAM         : in std_logic;
        data_p0         : in std_logic;
        data_n0         : in std_logic;
        data_p1         : in std_logic;
        data_n1         : in std_logic;
        data_p2         : in std_logic;
        data_n2         : in std_logic;
        data_p3         : in std_logic;
        data_n3         : in std_logic;
        data_p4         : in std_logic;
        data_n4         : in std_logic;
        data_p5         : in std_logic;
        data_n5         : in std_logic;
        data_p6         : in std_logic;
        data_n6         : in std_logic;
        data_p7         : in std_logic;
        data_n7         : in std_logic;
        adc_out_0       : out std_logic_vector(13 downto 0);
        adc_out_1       : out std_logic_vector(13 downto 0);
        adc_out_2       : out std_logic_vector(13 downto 0);
        adc_out_3       : out std_logic_vector(13 downto 0);
        adc_out_4       : out std_logic_vector(13 downto 0);
        adc_out_5       : out std_logic_vector(13 downto 0);
        adc_out_6       : out std_logic_vector(13 downto 0);
        adc_out_7       : out std_logic_vector(13 downto 0)
    );
end Analog_Inputs;

architecture Behavioral of Analog_Inputs is
    
signal deserialized_value_0 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_1 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_2 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_3 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_4 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_5 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_6 : std_logic_vector(13 downto 0) := (others => '0');
signal deserialized_value_7 : std_logic_vector(13 downto 0) := (others => '0');
signal reportValues          : std_logic := '0';
signal frame_last           : std_logic := '0';
signal data0                : std_logic := '0';
signal data1                : std_logic := '0';
signal data2                : std_logic := '0';
signal data3                : std_logic := '0';
signal data4                : std_logic := '0';
signal data5                : std_logic := '0';
signal data6                : std_logic := '0';
signal data7                : std_logic := '0';
signal data0Delayed         : std_logic := '0';
signal data1Delayed         : std_logic := '0';
signal data2Delayed         : std_logic := '0';
signal data3Delayed         : std_logic := '0';
signal data4Delayed         : std_logic := '0';
signal data5Delayed         : std_logic := '0';
signal data6Delayed         : std_logic := '0';
signal data7Delayed         : std_logic := '0';
signal Q1_0                 : std_logic := '0';
signal Q2_0                 : std_logic := '0';
signal Q1_1                 : std_logic := '0';
signal Q2_1                 : std_logic := '0';
signal Q1_2                 : std_logic := '0';
signal Q2_2                 : std_logic := '0';
signal Q1_3                 : std_logic := '0';
signal Q2_3                 : std_logic := '0';
signal Q1_4                 : std_logic := '0';
signal Q2_4                 : std_logic := '0';
signal Q1_5                 : std_logic := '0';
signal Q2_5                 : std_logic := '0';
signal Q1_6                 : std_logic := '0';
signal Q2_6                 : std_logic := '0';
signal Q1_7                 : std_logic := '0';
signal Q2_7                 : std_logic := '0';
signal cntOut0              : std_logic_vector(4 downto 0);
signal cntOut1              : std_logic_vector(4 downto 0);
signal cntOut2              : std_logic_vector(4 downto 0);
signal cntOut3              : std_logic_vector(4 downto 0);
signal cntOut4              : std_logic_vector(4 downto 0);
signal cntOut5              : std_logic_vector(4 downto 0);
signal cntOut6              : std_logic_vector(4 downto 0);
signal cntOut7              : std_logic_vector(4 downto 0);
signal adc_out_0_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_1_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_2_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_3_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_4_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_5_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_6_bit_clk    : std_logic_vector(13 downto 0);
signal adc_out_7_bit_clk    : std_logic_vector(13 downto 0);
signal controlReady         : std_logic;
signal controlReset         : std_logic;
signal initCounter          : integer range 0 to 3 := 0;

--attribute mark_debug : string;
--attribute mark_debug of adc_out_0 : signal is "true";
--attribute mark_debug of adc_out_0_bit_clk : signal is "true";

begin

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 0 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data0 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data0,                              -- Buffer output
   I => data_p0,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n0                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_0_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut0,                  -- 5-bit output: Counter value output
   DATAOUT => data0Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data0,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_0 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",         -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_0,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_0,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data0Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN0_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_0,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_0_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 1 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data1 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data1,                              -- Buffer output
   I => data_p1,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n1                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_1_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut1,                  -- 5-bit output: Counter value output
   DATAOUT => data1Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data1,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_1 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_1,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_1,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data1Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN1_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_1,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_1_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 2 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data2 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data2,                              -- Buffer output
   I => data_p2,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n2                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_2_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut2,                  -- 5-bit output: Counter value output
   DATAOUT => data2Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data2,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_2 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_2,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_2,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data2Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN2_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_2,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_2_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 3 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data3 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data3,                              -- Buffer output
   I => data_p3,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n3                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_3_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut3,                  -- 5-bit output: Counter value output
   DATAOUT => data3Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data3,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_3 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_3,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_3,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data3Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN3_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_3,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_3_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 4 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data4 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data4,                              -- Buffer output
   I => data_p4,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n4                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_4_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut4,                  -- 5-bit output: Counter value output
   DATAOUT => data4Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data4,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_4 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_4,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_4,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data4Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN4_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_4,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_4_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 5 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data5 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data5,                              -- Buffer output
   I => data_p5,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n5                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_5_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut5,                  -- 5-bit output: Counter value output
   DATAOUT => data5Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data5,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_5 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_5,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_5,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data5Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN5_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_5,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_5_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 6 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data6 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data6,                              -- Buffer output
   I => data_p6,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n6                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_6_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut6,                  -- 5-bit output: Counter value output
   DATAOUT => data6Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data6,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_6 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_6,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_6,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data6Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN6_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_6,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_6_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

--------------------------------------------------------------------------------------------------------------
--ANALOG INPUT 7 ENTERS IBUFDS -> IDELAYE2 -> IDDR -> FABRIC LOGIC -> CLOCK DOMAIN CROSSING TO SCAN 25MHz AREA
--------------------------------------------------------------------------------------------------------------
IBUFDS_data7 : IBUFDS
generic map (
   DIFF_TERM => TRUE,                       -- Differential Termination
   IBUF_LOW_PWR => FALSE,                   -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
   IOSTANDARD => "LVDS_25")
port map (
   O => data7,                              -- Buffer output
   I => data_p7,                            -- Diff_p buffer input (connect directly to top-level port)
   IB => data_n7                            -- Diff_n buffer input (connect directly to top-level port)
);
adc_data_7_delay : IDELAYE2
generic map (
   CINVCTRL_SEL => "FALSE",                 -- Enable dynamic clock inversion (FALSE, TRUE)
   DELAY_SRC => "IDATAIN",                  -- Delay input (IDATAIN, DATAIN)
   HIGH_PERFORMANCE_MODE => "TRUE",         -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
   IDELAY_TYPE => "FIXED",                  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   IDELAY_VALUE => 10,                      -- Input delay tap setting (0-31)
   PIPE_SEL => "FALSE",                     -- Select pipelined mode, FALSE, TRUE
   REFCLK_FREQUENCY => 200.0,               -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   SIGNAL_PATTERN => "DATA"                 -- DATA, CLOCK input signal
)
port map (
   CNTVALUEOUT => cntOut7,                  -- 5-bit output: Counter value output
   DATAOUT => data7Delayed,                 -- 1-bit output: Delayed data output
   C => '0',                                -- 1-bit input: Clock input
   CE => '0',                               -- 1-bit input: Active high enable increment/decrement input
   CINVCTRL => '0',                         -- 1-bit input: Dynamic clock inversion input
   CNTVALUEIN => "00000",                   -- 5-bit input: Counter value input
   DATAIN => '0',                           -- 1-bit input: Internal delay data input
   IDATAIN => data7,                        -- 1-bit input: Data input from the I/O
   INC => '0',                              -- 1-bit input: Increment / Decrement tap delay input
   LD => '0',                               -- 1-bit input: Load IDELAY_VALUE input
   LDPIPEEN => '0',                         -- 1-bit input: Enable PIPELINE register to load data input
   REGRST => '0'                            -- 1-bit input: Active-high reset tap-delay input
);
--IDDR module will pull two bits out of the serial stream per bit clock cycle, Q1 and Q2
IDDR_data_7 : IDDR
generic map (
   DDR_CLK_EDGE => "OPPOSITE_EDGE",   -- "OPPOSITE_EDGE", "SAME_EDGE" or "SAME_EDGE_PIPELINED"
   INIT_Q1 => '0',                          -- Initial value of Q1: '0' or '1'
   INIT_Q2 => '0',                          -- Initial value of Q2: '0' or '1'
   SRTYPE => "SYNC")                        -- Set/Reset type: "SYNC" or "ASYNC"
port map (
   Q1 => Q1_7,                              -- 1-bit output for positive edge of clock
   Q2 => Q2_7,                              -- 1-bit output for negative edge of clock
   C => bit_clk,                            -- 1-bit clock input
   CE => '1',                               -- 1-bit clock enable input
   D => data7Delayed,                       -- 1-bit DDR data input
   R => '0',                                -- 1-bit reset
   S => '0'                                 -- 1-bit set
);
AIN7_CDC : xpm_cdc_gray
generic map (
    DEST_SYNC_FF => 2,                      -- DECIMAL; range: 2-10
    INIT_SYNC_FF => 0,                      -- DECIMAL; 0=disable simulation init values, 1=enable simulation init values
    REG_OUTPUT => 0,                        -- DECIMAL; 0=disable registered output, 1=enable registered output
    SIM_ASSERT_CHK => 0,                    -- DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    SIM_LOSSLESS_GRAY_CHK => 0,             -- DECIMAL; 0=disable lossless check, 1=enable lossless check
    WIDTH => 14                             -- DECIMAL; range: 2-32
)
port map (
    dest_out_bin => adc_out_7,              -- WIDTH-bit output: Binary input bus (src_in_bin) synchronized to destination clock domain. This output is combinatorial unless REG_OUTPUT is set to 1.
    dest_clk => scan_clk,                   -- 1-bit input: Destination clock.
    src_clk => bit_clk,                     -- 1-bit input: Source clock.
    src_in_bin => adc_out_7_bit_clk         -- WIDTH-bit input: Binary input bus that will be synchronized to the destination clock domain.
);

-----------------------------------------------------------------------
--IDELAYCTRL IS A SINGLE CONTROL USED TO DELAY ALL OTHER IDELAY MODULES
-----------------------------------------------------------------------
IDELAYCTRL_inst : IDELAYCTRL
port map (
   RDY => controlReady,                     -- 1-bit output: Ready output
   REFCLK => clk_RAM,                       -- 1-bit input: Reference clock input
   RST => controlReset                      -- 1-bit input: Active high reset input
);


dataStream : process(bit_clk) is
begin
if rising_edge(bit_clk) then
    if controlReady = '1' then
        controlReset <= '0';
        --record the previous framing input state so we know when we've gone high
        frame_last <= frame;
        --if the frame bit goes high, trigger a report of the values
        if frame = '1' and frame_last = '0' then
            reportValues <= '1';
        else
            reportValues <= '0';
        end if;
        --separate the reporting by one clock cycle because when the signal comes to say "this is the data start" we are still recording, so delay 1 clock cycle
        if reportValues = '1' then
            adc_out_0_bit_clk <= deserialized_value_0;
            adc_out_1_bit_clk <= deserialized_value_1;
            adc_out_2_bit_clk <= deserialized_value_2;
            adc_out_3_bit_clk <= deserialized_value_3;
            adc_out_4_bit_clk <= deserialized_value_4;
            adc_out_5_bit_clk <= deserialized_value_5;
            adc_out_6_bit_clk <= deserialized_value_6;
            adc_out_7_bit_clk <= deserialized_value_7;
        end if;
        --shift the rightmost 12 bits to the left, and add new bits on the right
        deserialized_value_0 <= deserialized_value_0(11 downto 0) & Q1_0 & Q2_0;
        deserialized_value_1 <= deserialized_value_1(11 downto 0) & Q1_1 & Q2_1;
        deserialized_value_2 <= deserialized_value_2(11 downto 0) & Q1_2 & Q2_2;
        deserialized_value_3 <= deserialized_value_3(11 downto 0) & Q1_3 & Q2_3;
        deserialized_value_4 <= deserialized_value_4(11 downto 0) & Q1_4 & Q2_4;
        deserialized_value_5 <= deserialized_value_5(11 downto 0) & Q1_5 & Q2_5;
        deserialized_value_6 <= deserialized_value_6(11 downto 0) & Q1_6 & Q2_6;
        deserialized_value_7 <= deserialized_value_7(11 downto 0) & Q1_7 & Q2_7;
    else
        -- the idelaycontrol needs to be reset on power-up for proper function - this will do it
        if initCounter < 3 then
            controlReset <= '1';
            initCounter <= initCounter + 1;
        else
            controlReset <= '0';
        end if;
    end if;
end if;
end process dataStream;
end Behavioral;