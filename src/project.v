/*
 * Temporary seven-segment output mapping test
 *
 * Purpose:
 *   Turn on one uo_out bit at a time so we can discover
 *   which output controls each seven-segment LED.
 *
 * How to use:
 *
 *   Set switches ui_in[2:0] to:
 *
 *     000 -> uo_out[0]
 *     001 -> uo_out[1]
 *     010 -> uo_out[2]
 *     011 -> uo_out[3]
 *     100 -> uo_out[4]
 *     101 -> uo_out[5]
 *     110 -> uo_out[6]
 *     111 -> uo_out[7]
 *
 * Change the three switches and observe which display segment lights.
 *
 * This is only a temporary test.
 * After we identify the mapping, we will replace this file with the
 * full Schrodinger's Seven-Segment design.
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated input switches
    output wire [7:0] uo_out,   // Dedicated outputs connected to display
    input  wire [7:0] uio_in,   // Bidirectional input path
    output wire [7:0] uio_out,  // Bidirectional output path
    output wire [7:0] uio_oe,   // Bidirectional output-enable path
    input  wire       ena,      // Design enable
    input  wire       clk,      // Clock, unused in this test
    input  wire       rst_n     // Reset, unused in this test
);

  /*
   * selected_bit chooses which output line is turned on.
   *
   * ui_in[2:0] is a 3-bit binary number from 0 to 7.
   */
  wire [2:0] selected_bit;

  assign selected_bit = ui_in[2:0];


  /*
   * output_pattern contains exactly one logic 1.
   *
   * Examples:
   *
   * selected_bit = 0 -> 0000_0001
   * selected_bit = 1 -> 0000_0010
   * selected_bit = 2 -> 0000_0100
   * selected_bit = 7 -> 1000_0000
   */
  reg [7:0] output_pattern;

  always @(*) begin
    case (selected_bit)
      3'b000: output_pattern = 8'b0000_0001;
      3'b001: output_pattern = 8'b0000_0010;
      3'b010: output_pattern = 8'b0000_0100;
      3'b011: output_pattern = 8'b0000_1000;
      3'b100: output_pattern = 8'b0001_0000;
      3'b101: output_pattern = 8'b0010_0000;
      3'b110: output_pattern = 8'b0100_0000;
      3'b111: output_pattern = 8'b1000_0000;

      default: output_pattern = 8'b0000_0000;
    endcase
  end


  /*
   * Send the selected one-hot pattern to the display outputs.
   */
  assign uo_out = output_pattern;


  /*
   * Bidirectional pins are not used.
   *
   * uio_oe = 0 configures all bidirectional pins as inputs.
   */
  assign uio_out = 8'b0000_0000;
  assign uio_oe  = 8'b0000_0000;


  /*
   * Mark unused inputs so linting does not complain.
   */
  wire _unused = &{
      ena,
      clk,
      rst_n,
      ui_in[7:3],
      uio_in,
      1'b0
  };

endmodule

`default_nettype wire
