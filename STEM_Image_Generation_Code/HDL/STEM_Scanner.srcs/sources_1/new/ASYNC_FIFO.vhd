----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 03/07/2024 02:13:46 PM
-- Design Name: 
-- Module Name: ASYNC_FIFO - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity ASYNC_FIFO is
    Port (
    clk             : in std_logic;                         -- 25MHz clock system runs on
    data            : inout std_logic_vector (7 downto 0);  -- the bidirectional data bus, 8 bits wide
    rxf             : in std_logic;                         -- goes low when data is available from the computer (on next clock cycle)
    txe             : in std_logic;                         -- goes low when data can be sent to the computer safely, we aren't reading
    rd              : out std_logic;                        -- trigger to say "read the data from the computer now"
    wr              : out std_logic;                        -- trigger to say "I've got data for the computer on the bus so write it"
    siwu            : out std_logic;                        -- send-immediately / wake-up signal, can be left asserted if not used
    tx_enable       : in std_logic;                         -- to enable sending data
    tx_data_out     : in std_logic_vector(55 downto 0);     -- requested data to send
    rx_data_in      : out std_logic_vector(31 downto 0);    -- received data
    rx_data_ready   : out std_logic;                        -- indicates when data received
    rx_data_ack     : in std_logic;                         -- feedback to say we've read the data
    tx_running      : out std_logic                         -- to say we are sending data, don't give us more to send yet
    );
end ASYNC_FIFO;

architecture Behavioral of ASYNC_FIFO is

    signal rxByteIndex  : integer range 0 to 3 := 0;
    signal rxOffCheck   : integer range 0 to 50000 := 0;
    
    signal txByteIndex  : integer range 0 to 7 := 0;
    signal txData       : std_logic_vector(55 downto 0) := (others => '0');
    signal txEnabled    : std_logic := '0';
    signal tx_done      : std_logic := '0';
    
    type usbStateList is (IDLE, READ, WRITE);
    signal usbState     : usbStateList := IDLE;
    
    attribute mark_debug : string;    
    attribute mark_debug of txe : signal is "true";
    attribute mark_debug of wr : signal is "true";
    attribute mark_debug of tx_enable : signal is "true";
    attribute mark_debug of tx_running : signal is "true";
    attribute mark_debug of usbState : signal is "true";
    attribute mark_debug of txByteIndex : signal is "true";
    
begin

siwu <= '1';

--process for data transmission and reception. Has to be in the same process because we can either read or write every clock cycle, NOT both.
usb : process(clk) is
begin
if rising_edge(clk) then
    
    --this is the finite state machine that handles reading and writing to the computer
    case usbState is
    
    -----------------------------------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------------
    -- state falls back to IDLE when reads or writes are complete
    when IDLE =>
    
        --if external data acknowledgement has been given, clear the ready signal and the data in bus
        if rx_data_ack = '1' then
            rx_data_ready <= '0';
            rx_data_in <= (others => '0');
        end if;
        
        --default state for write commands is asserted - will deassert when writing
        wr <= '1'; tx_done <= '0';
        
        --if the rxf pin is high for 2 ms continuously we aren't sending any signals, so reset ALL counters just in case there was an issue
        if rxf = '1' then
            if rxOffCheck + 1 = 50000 then
                rxByteIndex <= 0;
                rxOffCheck <= 0;
            else
                rxOffCheck <= rxOffCheck + 1;
            end if;
        else
            rxOffCheck <= 0;
        end if;
        
        --latch the tx enabled status, as the external process will only hold enabled high for one clock cycle
        if tx_enable = '1' then
            txEnabled <= '1';
        end if;
        
        --unlatch the enabled status when transmission is complete
        if tx_done = '1' then
            txEnabled <= '0';
            tx_done <= '0';
            tx_running <= '0';
            txByteIndex <= 0;
        end if;
        
        -------------------------------------------------------------------------------------------------------------------
        --if rxf goes low, data will be available on the next clock cycle. This has highest priority!
        --  reception data comes in 4-byte chunks from the computer
        if rxf = '0' then
            rd <= '0';                  --deassert the read output to say "put the data on the bus"
            data <= (others => 'Z');    --put the bus into tri-state mode so that it can be written to
            usbState <= READ;
            
        -------------------------------------------------------------------------------------------------------------------
        --if txe goes low and we have been asked to send data to the computer, we can write the data on the next clock cycle
        --  transmission data going to the computer is sent in 7-byte chunks
        elsif txe = '0' and (txEnabled = '1') then
            tx_running <= '1';          --trigger the outside world that we are now sending data
            rd <= '1';                  --assert the read output because we are not reading here
            usbState <= WRITE;
            
            case txByteIndex is         --based on the current byte being transmitted, change what data is going out
            when 0 =>
                data <= tx_data_out(55 downto 48);
            when 1 =>
                data <= tx_data_out(47 downto 40);
            when 2 =>
                data <= tx_data_out(39 downto 32);
            when 3 =>
                data <= tx_data_out(31 downto 24);
            when 4 =>
                data <= tx_data_out(23 downto 16);
            when 5 =>
                data <= tx_data_out(15 downto  8);
            when 6 =>
                data <= tx_data_out( 7 downto  0);
            when others =>
                usbState <=  IDLE;
            end case;
            
        -------------------------------------------------------------------------------------------------------------------
        --otherwise do nothing - deassert read because we are not doing that, stay in IDLE
        else
            rd <= '1';
            usbState <= IDLE;
            
        end if;
    
    -----------------------------------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------------
    -- state enters READ when rxf input has deasserted, and on this clock cycle data will be on the bus
    -- data will appear 14ns after rxf deasserts, and our system clock has a 40ns period, so "next clock cycle" is good
    when READ =>
        case rxByteIndex is
        when 0 =>       rx_data_in(31 downto 24) <= data; rxByteIndex <= 1;
        when 1 =>       rx_data_in(23 downto 16) <= data; rxByteIndex <= 2;
        when 2 =>       rx_data_in(15 downto  8) <= data; rxByteIndex <= 3;
        when 3 =>       rx_data_in( 7 downto  0) <= data; rxByteIndex <= 0; rx_data_ready <= '1';
        when others =>  NULL;
        end case;
        rd <= '1';      --reassert rd
        usbState <= IDLE;
    
    -----------------------------------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------------
    -- state enters WRITE when txe input has deasserted saying "it's ok to write now" and there is data to write on the bus
    when WRITE =>
        if txByteIndex = 6 then
            tx_done <= '1';
        else
            txByteIndex <= txByteIndex + 1;
        end if;
        wr <= '0';
        usbState <= IDLE;
        
    -----------------------------------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------------
    when OTHERS => usbState <= IDLE;
    end case;
    
end if; 
end process usb;
end Behavioral;
