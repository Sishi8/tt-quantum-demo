/*
 * Copyright (c) 2026 Sishi
 * SPDX-License-Identifier: Apache-2.0
 *
 * Project: TinyMind AI Accelerator
 *
 * TinyMind is an eight-input, three-class, fixed-weight neural-network
 * inference accelerator.
 *
 * All eight input switches are binary features.
 *
 * Three artificial neurons calculate scores in parallel:
 *
 *   A = AI-oriented
 *   H = Hardware-oriented
 *   C = Creative-oriented
 *
 * The class with the highest score becomes the prediction.
 *
 * The step clock changes what the seven-segment display shows:
 *
 *   First view  : predicted class, A/H/C
 *   Second view : confidence margin, 0-9
 *
 * Each additional clock press switches between these two views.
 *
 * This design performs inference only. The ternary weights are fixed in
 * hardware and do not change while the chip is operating.
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Eight binary AI features
    output wire [7:0] uo_out,   // Seven-segment display
    input  wire [7:0] uio_in,   // Unused bidirectional inputs
    output wire [7:0] uio_out,  // Unused bidirectional outputs
    output wire [7:0] uio_oe,   // Bidirectional output enables
    input  wire       ena,      // Design enable
    input  wire       clk,      // Step clock toggles the display view
    input  wire       rst_n     // Active-low reset
);

  /*
   * -----------------------------------------------------------------------
   * INPUT FEATURES
   * -----------------------------------------------------------------------
   *
   * Suggested meanings:
   *
   *   ui_in[0] = Likes mathematics
   *   ui_in[1] = Likes programming
   *   ui_in[2] = Likes electronics
   *   ui_in[3] = Likes physics
   *   ui_in[4] = Likes data and patterns
   *   ui_in[5] = Likes building things
   *   ui_in[6] = Likes design and creativity
   *   ui_in[7] = Likes experimentation and research
   *
   * Every feature is binary:
   *
   *   0 = No
   *   1 = Yes
   */

  /*
   * Convert each one-bit input into an explicitly signed six-bit number.
   *
   * Explicit sizing avoids accidental signed-arithmetic or overflow
   * differences between RTL simulation and synthesized hardware.
   */

  wire signed [5:0] x0;
  wire signed [5:0] x1;
  wire signed [5:0] x2;
  wire signed [5:0] x3;
  wire signed [5:0] x4;
  wire signed [5:0] x5;
  wire signed [5:0] x6;
  wire signed [5:0] x7;

  assign x0 = ui_in[0] ? 6'sd1 : 6'sd0;
  assign x1 = ui_in[1] ? 6'sd1 : 6'sd0;
  assign x2 = ui_in[2] ? 6'sd1 : 6'sd0;
  assign x3 = ui_in[3] ? 6'sd1 : 6'sd0;
  assign x4 = ui_in[4] ? 6'sd1 : 6'sd0;
  assign x5 = ui_in[5] ? 6'sd1 : 6'sd0;
  assign x6 = ui_in[6] ? 6'sd1 : 6'sd0;
  assign x7 = ui_in[7] ? 6'sd1 : 6'sd0;


  /*
   * -----------------------------------------------------------------------
   * FIXED TERNARY-WEIGHT NEURONS
   * -----------------------------------------------------------------------
   *
   * Every weight is one of:
   *
   *   +1 = feature supports this class
   *    0 = feature is ignored
   *   -1 = feature works against this class
   *
   * These are demonstration weights. In a later learning exercise, the
   * weights could be trained in Python and then exported into this RTL.
   */


  /*
   * AI-oriented neuron
   *
   * Feature             Weight
   * --------------------------
   * Mathematics           +1
   * Programming           +1
   * Electronics            0
   * Physics                0
   * Data and patterns     +1
   * Building things       -1
   * Creativity             0
   * Research              +1
   * Bias                  +1
   */

  wire signed [5:0] score_ai;

  assign score_ai =
      x0 +
      x1 +
      x4 -
      x5 +
      x7 +
      6'sd1;


  /*
   * Hardware-oriented neuron
   *
   * Feature             Weight
   * --------------------------
   * Mathematics           +1
   * Programming            0
   * Electronics           +1
   * Physics               +1
   * Data and patterns      0
   * Building things       +1
   * Creativity            -1
   * Research               0
   * Bias                   0
   */

  wire signed [5:0] score_hardware;

  assign score_hardware =
      x0 +
      x2 +
      x3 +
      x5 -
      x6;


  /*
   * Creative-oriented neuron
   *
   * Feature             Weight
   * --------------------------
   * Mathematics            0
   * Programming           -1
   * Electronics           -1
   * Physics                0
   * Data and patterns      0
   * Building things       +1
   * Creativity            +1
   * Research              +1
   * Bias                  +1
   */

  wire signed [5:0] score_creative;

  assign score_creative =
      -x1 -
      x2 +
      x5 +
      x6 +
      x7 +
      6'sd1;


  /*
   * -----------------------------------------------------------------------
   * WINNER AND RUNNER-UP SELECTION
   * -----------------------------------------------------------------------
   *
   * The class with the largest score wins.
   *
   * In an exact tie, the deterministic priority is:
   *
   *   AI, then Hardware, then Creative
   */

  localparam [1:0] CLASS_AI       = 2'b00;
  localparam [1:0] CLASS_HARDWARE = 2'b01;
  localparam [1:0] CLASS_CREATIVE = 2'b10;

  reg [1:0] predicted_class;

  reg signed [5:0] winning_score;
  reg signed [5:0] second_score;

  always @(*) begin
    if ((score_ai >= score_hardware) &&
        (score_ai >= score_creative)) begin

      predicted_class = CLASS_AI;
      winning_score   = score_ai;

      if (score_hardware >= score_creative)
        second_score = score_hardware;
      else
        second_score = score_creative;

    end else if (score_hardware >= score_creative) begin

      predicted_class = CLASS_HARDWARE;
      winning_score   = score_hardware;

      if (score_ai >= score_creative)
        second_score = score_ai;
      else
        second_score = score_creative;

    end else begin

      predicted_class = CLASS_CREATIVE;
      winning_score   = score_creative;

      if (score_ai >= score_hardware)
        second_score = score_ai;
      else
        second_score = score_hardware;
    end
  end


  /*
   * -----------------------------------------------------------------------
   * CONFIDENCE MARGIN
   * -----------------------------------------------------------------------
   *
   * Confidence margin:
   *
   *   winning score - second-highest score
   *
   * This is not a percentage. It shows how far the winning neuron finished
   * ahead of the runner-up.
   */

  wire signed [5:0] raw_margin;
  wire [3:0] confidence_digit;

  assign raw_margin = winning_score - second_score;

  /*
   * The seven-segment display can show only one decimal digit.
   */

  assign confidence_digit =
      (raw_margin > 6'sd9) ? 4'd9 : raw_margin[3:0];

  /*
   * A margin of zero or one is considered a close prediction.
   */

  wire close_prediction;

  assign close_prediction = (raw_margin <= 6'sd1);


  /*
   * -----------------------------------------------------------------------
   * DISPLAY-VIEW REGISTER
   * -----------------------------------------------------------------------
   *
   * show_confidence = 0:
   *   Display the predicted class.
   *
   * show_confidence = 1:
   *   Display the confidence margin.
   *
   * Each rising clock edge toggles between the two views.
   * Reset returns the display to class view.
   */

  reg show_confidence;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      show_confidence <= 1'b0;
    else
      show_confidence <= ~show_confidence;
  end


  /*
   * -----------------------------------------------------------------------
   * SEVEN-SEGMENT PATTERNS
   * -----------------------------------------------------------------------
   *
   * Assumed segment order:
   *
   *          a
   *        -----
   *     f |     | b
   *       |  g  |
   *        -----
   *     e |     | c
   *       |     |
   *        -----
   *          d
   *
   * segments[6:0] = {a, b, c, d, e, f, g}
   * uo_out[7]     = decimal point
   *
   * This version assumes logic 1 turns a segment on.
   */

  localparam [6:0] SEG_0 = 7'b1111110;
  localparam [6:0] SEG_1 = 7'b0110000;
  localparam [6:0] SEG_2 = 7'b1101101;
  localparam [6:0] SEG_3 = 7'b1111001;
  localparam [6:0] SEG_4 = 7'b0110011;
  localparam [6:0] SEG_5 = 7'b1011011;
  localparam [6:0] SEG_6 = 7'b1011111;
  localparam [6:0] SEG_7 = 7'b1110000;
  localparam [6:0] SEG_8 = 7'b1111111;
  localparam [6:0] SEG_9 = 7'b1111011;

  localparam [6:0] SEG_A = 7'b1110111;
  localparam [6:0] SEG_H = 7'b0110111;
  localparam [6:0] SEG_C = 7'b1001110;


  /*
   * Select the seven-segment letter for the predicted class.
   */

  reg [6:0] class_segments;

  always @(*) begin
    case (predicted_class)
      CLASS_AI:
        class_segments = SEG_A;

      CLASS_HARDWARE:
        class_segments = SEG_H;

      CLASS_CREATIVE:
        class_segments = SEG_C;

      default:
        class_segments = SEG_0;
    endcase
  end


  /*
   * Convert the confidence margin into a decimal digit.
   */

  reg [6:0] confidence_segments;

  always @(*) begin
    case (confidence_digit)
      4'd0: confidence_segments = SEG_0;
      4'd1: confidence_segments = SEG_1;
      4'd2: confidence_segments = SEG_2;
      4'd3: confidence_segments = SEG_3;
      4'd4: confidence_segments = SEG_4;
      4'd5: confidence_segments = SEG_5;
      4'd6: confidence_segments = SEG_6;
      4'd7: confidence_segments = SEG_7;
      4'd8: confidence_segments = SEG_8;
      4'd9: confidence_segments = SEG_9;

      default:
        confidence_segments = SEG_0;
    endcase
  end


  /*
   * -----------------------------------------------------------------------
   * FINAL DISPLAY OUTPUT
   * -----------------------------------------------------------------------
   *
   * Class view:
   *   A, H, or C
   *   Decimal point means the prediction is close.
   *
   * Confidence view:
   *   Margin from 0 through 9
   *   Decimal point remains off.
   */

  wire [6:0] displayed_segments;
  wire       displayed_decimal_point;

  assign displayed_segments =
      show_confidence ? confidence_segments : class_segments;

  assign displayed_decimal_point =
      show_confidence ? 1'b0 : close_prediction;

  assign uo_out = {
      displayed_decimal_point,
      displayed_segments
  };


  /*
   * Bidirectional pins are unused.
   */

  assign uio_out = 8'b0000_0000;
  assign uio_oe  = 8'b0000_0000;


  /*
   * Mark intentionally unused inputs.
   */

  wire _unused = &{
      ena,
      uio_in,
      1'b0
  };

endmodule

`default_nettype wire
