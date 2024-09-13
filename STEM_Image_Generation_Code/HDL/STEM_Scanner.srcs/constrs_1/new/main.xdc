#configure bank 0 voltage
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

set_property -dict {PACKAGE_PIN R2 IOSTANDARD SSTL135} [get_ports clk_100MHz]
create_clock -period 10.000 -name clk_100MHz -waveform {0.000 5.000} -add [get_ports clk_100MHz]
create_clock -period 5.714 -name adc_bit_clk_p -waveform {0.000 2.857} -add [get_ports adc_bit_clk_p]

set_property -dict {PACKAGE_PIN T14 IOSTANDARD LVCMOS33} [get_ports bank14_led]
set_property -dict {PACKAGE_PIN K14 IOSTANDARD LVCMOS33} [get_ports bank15_led]
set_property -dict {PACKAGE_PIN A11 IOSTANDARD LVCMOS18} [get_ports bank16_led]
set_property -dict {PACKAGE_PIN H5 IOSTANDARD LVCMOS25} [get_ports bank35_led]

set_property -dict {PACKAGE_PIN A13 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[15]}]
set_property -dict {PACKAGE_PIN B13 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[14]}]
set_property -dict {PACKAGE_PIN C13 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[13]}]
set_property -dict {PACKAGE_PIN A14 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[12]}]
set_property -dict {PACKAGE_PIN B14 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[11]}]
set_property -dict {PACKAGE_PIN C14 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[10]}]
set_property -dict {PACKAGE_PIN D14 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[9]}]
set_property -dict {PACKAGE_PIN A15 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[8]}]
set_property -dict {PACKAGE_PIN B15 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[7]}]
set_property -dict {PACKAGE_PIN D15 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[6]}]
set_property -dict {PACKAGE_PIN A16 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[5]}]
set_property -dict {PACKAGE_PIN B16 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[4]}]
set_property -dict {PACKAGE_PIN D16 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[3]}]
set_property -dict {PACKAGE_PIN A17 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[2]}]
set_property -dict {PACKAGE_PIN B17 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[1]}]
set_property -dict {PACKAGE_PIN B18 IOSTANDARD LVCMOS33} [get_ports {x_analog_out[0]}]

set_property -dict {PACKAGE_PIN C17 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[15]}]
set_property -dict {PACKAGE_PIN C18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[14]}]
set_property -dict {PACKAGE_PIN D17 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[13]}]
set_property -dict {PACKAGE_PIN D18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[12]}]
set_property -dict {PACKAGE_PIN E15 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[11]}]
set_property -dict {PACKAGE_PIN E16 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[10]}]
set_property -dict {PACKAGE_PIN E17 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[9]}]
set_property -dict {PACKAGE_PIN E18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[8]}]
set_property -dict {PACKAGE_PIN F15 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[7]}]
set_property -dict {PACKAGE_PIN F18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[6]}]
set_property -dict {PACKAGE_PIN G16 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[5]}]
set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[4]}]
set_property -dict {PACKAGE_PIN G18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[3]}]
set_property -dict {PACKAGE_PIN H16 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[2]}]
set_property -dict {PACKAGE_PIN H17 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[1]}]
set_property -dict {PACKAGE_PIN H18 IOSTANDARD LVCMOS33} [get_ports {y_analog_out[0]}]

#set_property -dict {PACKAGE_PIN L17 IOSTANDARD LVCMOS33} [get_ports tx_pin]
#set_property -dict {PACKAGE_PIN L16 IOSTANDARD LVCMOS33} [get_ports rx_pin]

#USB CHIP PORT "A" - ONLY ENABLE "A" OR "B" AT A TIME
set_property -dict {PACKAGE_PIN L16 IOSTANDARD LVCMOS33} [get_ports {usb_data[0]}]
set_property -dict {PACKAGE_PIN L17 IOSTANDARD LVCMOS33} [get_ports {usb_data[1]}]
set_property -dict {PACKAGE_PIN L18 IOSTANDARD LVCMOS33} [get_ports {usb_data[2]}]
set_property -dict {PACKAGE_PIN M16 IOSTANDARD LVCMOS33} [get_ports {usb_data[3]}]
set_property -dict {PACKAGE_PIN M17 IOSTANDARD LVCMOS33} [get_ports {usb_data[4]}]
set_property -dict {PACKAGE_PIN M18 IOSTANDARD LVCMOS33} [get_ports {usb_data[5]}]
set_property -dict {PACKAGE_PIN N18 IOSTANDARD LVCMOS33} [get_ports {usb_data[6]}]
set_property -dict {PACKAGE_PIN P18 IOSTANDARD LVCMOS33} [get_ports {usb_data[7]}]
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS33} [get_ports usb_rxf]
set_property -dict {PACKAGE_PIN N14 IOSTANDARD LVCMOS33} [get_ports usb_txe]
set_property -dict {PACKAGE_PIN N15 IOSTANDARD LVCMOS33} [get_ports usb_rd]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports usb_wr]
set_property -dict {PACKAGE_PIN P15 IOSTANDARD LVCMOS33} [get_ports usb_siwu]

#USB CHIP PORT "B" - ONLY ENABLE "A" OR "B" AT A TIME (CANNOT USE ON V1.0 BECAUSE TWO PINS ARE NOT CONNECTED FOR THIS)
#set_property -dict {PACKAGE_PIN R15 IOSTANDARD LVCMOS33} [get_ports {usb_data[0]}]
#set_property -dict {PACKAGE_PIN R16 IOSTANDARD LVCMOS33} [get_ports {usb_data[1]}]
#set_property -dict {PACKAGE_PIN R17 IOSTANDARD LVCMOS33} [get_ports {usb_data[2]}]
#set_property -dict {PACKAGE_PIN R18 IOSTANDARD LVCMOS33} [get_ports {usb_data[3]}]
#set_property -dict {PACKAGE_PIN T15 IOSTANDARD LVCMOS33} [get_ports {usb_data[4]}]
#set_property -dict {PACKAGE_PIN T18 IOSTANDARD LVCMOS33} [get_ports {usb_data[5]}]
#set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVCMOS33} [get_ports {usb_data[6]}]
#set_property -dict {PACKAGE_PIN U17 IOSTANDARD LVCMOS33} [get_ports {usb_data[7]}]
#set_property -dict {PACKAGE_PIN U16 IOSTANDARD LVCMOS33} [get_ports usb_rxf]
#set_property -dict {PACKAGE_PIN V17 IOSTANDARD LVCMOS33} [get_ports usb_txe]
#set_property -dict {PACKAGE_PIN V16 IOSTANDARD LVCMOS33} [get_ports usb_rd]
#set_property -dict {PACKAGE_PIN --- IOSTANDARD LVCMOS33} [get_ports usb_wr]
#set_property -dict {PACKAGE_PIN --- IOSTANDARD LVCMOS33} [get_ports usb_siwu]

set_property -dict {PACKAGE_PIN D11 IOSTANDARD LVCMOS18} [get_ports adc_cs]
set_property -dict {PACKAGE_PIN C9 IOSTANDARD LVCMOS18} [get_ports adc_sclk]
set_property -dict {PACKAGE_PIN C10 IOSTANDARD LVCMOS18} [get_ports adc_sdata]
set_property -dict {PACKAGE_PIN A9 IOSTANDARD LVCMOS18} [get_ports adc_pdwn]

# LVDS_25 data lines from ADC - these are serialized 14-bit data streams
set_property -dict {PACKAGE_PIN A8 IOSTANDARD LVDS_25} [get_ports adc_data_p_0]
set_property -dict {PACKAGE_PIN A7 IOSTANDARD LVDS_25} [get_ports adc_data_n_0]

set_property -dict {PACKAGE_PIN B7 IOSTANDARD LVDS_25} [get_ports adc_data_p_1]
set_property -dict {PACKAGE_PIN A6 IOSTANDARD LVDS_25} [get_ports adc_data_n_1]

set_property -dict {PACKAGE_PIN A5 IOSTANDARD LVDS_25} [get_ports adc_data_p_2]
set_property -dict {PACKAGE_PIN A4 IOSTANDARD LVDS_25} [get_ports adc_data_n_2]

set_property -dict {PACKAGE_PIN A3 IOSTANDARD LVDS_25} [get_ports adc_data_p_3]
set_property -dict {PACKAGE_PIN A2 IOSTANDARD LVDS_25} [get_ports adc_data_n_3]

set_property -dict {PACKAGE_PIN C2 IOSTANDARD LVDS_25} [get_ports adc_data_p_4]
set_property -dict {PACKAGE_PIN B2 IOSTANDARD LVDS_25} [get_ports adc_data_n_4]

set_property -dict {PACKAGE_PIN E1 IOSTANDARD LVDS_25} [get_ports adc_data_p_5]
set_property -dict {PACKAGE_PIN D1 IOSTANDARD LVDS_25} [get_ports adc_data_n_5]

set_property -dict {PACKAGE_PIN E2 IOSTANDARD LVDS_25} [get_ports adc_data_p_6]
set_property -dict {PACKAGE_PIN D2 IOSTANDARD LVDS_25} [get_ports adc_data_n_6]

set_property -dict {PACKAGE_PIN F2 IOSTANDARD LVDS_25} [get_ports adc_data_p_7]
set_property -dict {PACKAGE_PIN F1 IOSTANDARD LVDS_25} [get_ports adc_data_n_7]


# LVDS_25 clock lines from ADC - these are shared for all analog inputs
set_property -dict {PACKAGE_PIN F4 IOSTANDARD LVDS_25} [get_ports adc_bit_clk_p]
set_property -dict {PACKAGE_PIN E4 IOSTANDARD LVDS_25} [get_ports adc_bit_clk_n]
set_property -dict {PACKAGE_PIN C1 IOSTANDARD LVDS_25} [get_ports adc_frame_p]
set_property -dict {PACKAGE_PIN B1 IOSTANDARD LVDS_25} [get_ports adc_frame_n]

# enable the 100 ohm termination resistors on the LVDS_25 clock lines
set_property DIFF_TERM TRUE [get_ports adc_bit_clk_p]
set_property DIFF_TERM TRUE [get_ports adc_bit_clk_n]
set_property DIFF_TERM TRUE [get_ports adc_frame_p]
set_property DIFF_TERM TRUE [get_ports adc_frame_n]

#Flash memory configuration - SPIx4
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property CONFIG_MODE SPIx4 [current_design]

#input delays for frame clock input, adc data inputs
set_input_delay -clock [get_clocks adc_bit_clk_p] -min 0.000 [get_ports {adc_frame_n adc_frame_p}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -max 0.100 [get_ports {adc_frame_n adc_frame_p}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -min -add_delay 1.279 [get_ports {adc_data_p_0 adc_data_p_1 adc_data_p_2 adc_data_p_3 adc_data_p_4 adc_data_p_5 adc_data_p_6 adc_data_p_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -max -add_delay 1.579 [get_ports {adc_data_p_0 adc_data_p_1 adc_data_p_2 adc_data_p_3 adc_data_p_4 adc_data_p_5 adc_data_p_6 adc_data_p_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -clock_fall -min -add_delay 1.279 [get_ports {adc_data_p_0 adc_data_p_1 adc_data_p_2 adc_data_p_3 adc_data_p_4 adc_data_p_5 adc_data_p_6 adc_data_p_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -clock_fall -max -add_delay 1.579 [get_ports {adc_data_p_0 adc_data_p_1 adc_data_p_2 adc_data_p_3 adc_data_p_4 adc_data_p_5 adc_data_p_6 adc_data_p_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -min -add_delay 1.279 [get_ports {adc_data_n_0 adc_data_n_1 adc_data_n_2 adc_data_n_3 adc_data_n_4 adc_data_n_5 adc_data_n_6 adc_data_n_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -max -add_delay 1.579 [get_ports {adc_data_n_0 adc_data_n_1 adc_data_n_2 adc_data_n_3 adc_data_n_4 adc_data_n_5 adc_data_n_6 adc_data_n_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -clock_fall -min -add_delay 1.279 [get_ports {adc_data_n_0 adc_data_n_1 adc_data_n_2 adc_data_n_3 adc_data_n_4 adc_data_n_5 adc_data_n_6 adc_data_n_7}]
set_input_delay -clock [get_clocks adc_bit_clk_p] -clock_fall -max -add_delay 1.579 [get_ports {adc_data_n_0 adc_data_n_1 adc_data_n_2 adc_data_n_3 adc_data_n_4 adc_data_n_5 adc_data_n_6 adc_data_n_7}]

#input/output delays for USB pins
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports usb_rxf]
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.300 [get_ports usb_rxf]
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports usb_txe]
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.300 [get_ports usb_txe]
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports {usb_data[*]}]
set_input_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.300 [get_ports {usb_data[*]}]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] 10.000 [get_ports {usb_data[*]}]
#set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 5.000 [get_ports {usb_data[*]}]
#set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min -5.000 [get_ports {usb_data[*]}]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] 0.000 [get_ports usb_rd]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] 0.000 [get_ports usb_wr]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] 0.000 [get_ports usb_siwu]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports adc_cs]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.600 [get_ports adc_cs]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports adc_sclk]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.600 [get_ports adc_sclk]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -min 0.000 [get_ports adc_sdata]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT2]] -max 0.600 [get_ports adc_sdata]

#output delays for analog outputs X and Y
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT1]] -min 0.000 [get_ports -filter { NAME =~  "*x_analog_out*" && DIRECTION == "OUT" }]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT1]] -max 0.100 [get_ports -filter { NAME =~  "*x_analog_out*" && DIRECTION == "OUT" }]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT1]] -min 0.000 [get_ports -filter { NAME =~  "*y_analog_out*" && DIRECTION == "OUT" }]
set_output_delay -clock [get_clocks -of_objects [get_pins clkGenerator/inst/mmcm_adv_inst/CLKOUT1]] -max 0.100 [get_ports -filter { NAME =~  "*y_analog_out*" && DIRECTION == "OUT" }]

set_false_path -from [list [get_ports adc_frame_p] [get_ports adc_frame_n]] -to [list [get_pins Analog_Inputs_Instantation/reportValues_reg/D] [get_pins Analog_Inputs_Instantation/frame_last_reg/D]]