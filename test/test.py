# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

"""
Tests for TinyMind, a fixed-weight ternary AI inference accelerator.

The design uses:

    ui_in[6:0] = seven binary input features
    ui_in[7]   = display mode

Display modes:

    ui_in[7] = 0 -> show predicted class: A, H, or C
    ui_in[7] = 1 -> show confidence margin: 0 through 9

The test checks all:

    128 feature combinations
    × 2 display modes
    = 256 total input combinations
"""

import cocotb
from cocotb.triggers import Timer


# ---------------------------------------------------------------------------
# Seven-segment patterns
# ---------------------------------------------------------------------------
#
# These constants must match the patterns in src/project.v.
#
# Segment order:
#
#     segments[6:0] = {a, b, c, d, e, f, g}
#
# uo_out[7] is the decimal point.
#

SEG_0 = 0b1111110
SEG_1 = 0b0110000
SEG_2 = 0b1101101
SEG_3 = 0b1111001
SEG_4 = 0b0110011
SEG_5 = 0b1011011
SEG_6 = 0b1011111
SEG_7 = 0b1110000
SEG_8 = 0b1111111
SEG_9 = 0b1111011

SEG_A = 0b1110111
SEG_H = 0b0110111
SEG_C = 0b1001110


DIGIT_SEGMENTS = {
    0: SEG_0,
    1: SEG_1,
    2: SEG_2,
    3: SEG_3,
    4: SEG_4,
    5: SEG_5,
    6: SEG_6,
    7: SEG_7,
    8: SEG_8,
    9: SEG_9,
}


CLASS_SEGMENTS = {
    "A": SEG_A,
    "H": SEG_H,
    "C": SEG_C,
}


def calculate_prediction(features: int) -> tuple[str, int, int, int, int]:
    """
    Software reference model of the three hardware neurons.

    Parameters
    ----------
    features:
        Seven-bit value containing feature inputs x0 through x6.

    Returns
    -------
    tuple:
        predicted class,
        AI score,
        hardware score,
        creative score,
        confidence margin
    """

    # Extract each feature bit as either integer 0 or 1.
    x0 = (features >> 0) & 1
    x1 = (features >> 1) & 1
    x2 = (features >> 2) & 1
    x3 = (features >> 3) & 1
    x4 = (features >> 4) & 1
    x5 = (features >> 5) & 1
    x6 = (features >> 6) & 1

    # -----------------------------------------------------------------------
    # AI-oriented neuron
    #
    # Weights:
    #
    #   x0 Math        +1
    #   x1 Programming +1
    #   x2 Electronics  0
    #   x3 Physics      0
    #   x4 Data        +1
    #   x5 Building    -1
    #   x6 Creativity   0
    #   Bias           +1
    # -----------------------------------------------------------------------

    score_ai = x0 + x1 + x4 - x5 + 1

    # -----------------------------------------------------------------------
    # Hardware-oriented neuron
    #
    # Weights:
    #
    #   x0 Math        +1
    #   x1 Programming  0
    #   x2 Electronics +1
    #   x3 Physics     +1
    #   x4 Data         0
    #   x5 Building    +1
    #   x6 Creativity  -1
    #   Bias            0
    # -----------------------------------------------------------------------

    score_hardware = x0 + x2 + x3 + x5 - x6

    # -----------------------------------------------------------------------
    # Creative-oriented neuron
    #
    # Weights:
    #
    #   x0 Math         0
    #   x1 Programming -1
    #   x2 Electronics -1
    #   x3 Physics      0
    #   x4 Data         0
    #   x5 Building    +1
    #   x6 Creativity  +1
    #   Bias           +1
    # -----------------------------------------------------------------------

    score_creative = -x1 - x2 + x5 + x6 + 1

    # -----------------------------------------------------------------------
    # Select the winning class.
    #
    # Tie priority must match the Verilog:
    #
    #   AI first
    #   Hardware second
    #   Creative third
    # -----------------------------------------------------------------------

    if score_ai >= score_hardware and score_ai >= score_creative:
        predicted_class = "A"
        winning_score = score_ai
        second_score = max(score_hardware, score_creative)

    elif score_hardware >= score_creative:
        predicted_class = "H"
        winning_score = score_hardware
        second_score = max(score_ai, score_creative)

    else:
        predicted_class = "C"
        winning_score = score_creative
        second_score = max(score_ai, score_hardware)

    confidence_margin = winning_score - second_score

    # The hardware limits the displayed margin to one decimal digit.
    confidence_margin = min(confidence_margin, 9)

    return (
        predicted_class,
        score_ai,
        score_hardware,
        score_creative,
        confidence_margin,
    )


def expected_class_output(
    predicted_class: str,
    confidence_margin: int,
) -> int:
    """
    Build the expected 8-bit output for class-display mode.

    uo_out[6:0] contains the class character.

    uo_out[7], the decimal point, turns on when the winning margin is
    zero or one, indicating that the prediction is close.
    """

    segments = CLASS_SEGMENTS[predicted_class]

    close_prediction = confidence_margin <= 1
    decimal_point = 1 if close_prediction else 0

    return (decimal_point << 7) | segments


def expected_confidence_output(confidence_margin: int) -> int:
    """
    Build the expected 8-bit output for confidence-display mode.

    The decimal point remains off in this mode.
    """

    segments = DIGIT_SEGMENTS[confidence_margin]

    return segments


@cocotb.test()
async def test_project(dut):
    """
    Exhaustively verify all feature patterns in both display modes.
    """

    dut._log.info("Starting exhaustive TinyMind test")

    # The current design is combinational, but all inputs should still be
    # placed into known states for reliable RTL and gate-level simulation.
    dut.ena.value = 1
    dut.clk.value = 0
    dut.rst_n.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0

    # Allow the circuit to settle before testing.
    await Timer(1, unit="us")

    # There are 128 possible combinations of seven feature switches.
    for features in range(128):

        (
            predicted_class,
            score_ai,
            score_hardware,
            score_creative,
            confidence_margin,
        ) = calculate_prediction(features)

        # -------------------------------------------------------------------
        # Test class-display mode: ui_in[7] = 0
        # -------------------------------------------------------------------

        class_mode_input = features
        dut.ui_in.value = class_mode_input

        await Timer(1, unit="us")

        expected_class = expected_class_output(
            predicted_class,
            confidence_margin,
        )

        actual_class = int(dut.uo_out.value)

        dut._log.info(
            f"features={features:07b} "
            f"scores(A,H,C)=("
            f"{score_ai},{score_hardware},{score_creative}) "
            f"class={predicted_class} "
            f"margin={confidence_margin} "
            f"class_expected={expected_class:08b} "
            f"class_actual={actual_class:08b}"
        )

        assert actual_class == expected_class, (
            f"Class mode failed for features {features:07b}: "
            f"expected class {predicted_class}, "
            f"expected output {expected_class:08b}, "
            f"received {actual_class:08b}"
        )

        # -------------------------------------------------------------------
        # Test confidence-display mode: ui_in[7] = 1
        # -------------------------------------------------------------------

        confidence_mode_input = features | 0b1000_0000
        dut.ui_in.value = confidence_mode_input

        await Timer(1, unit="us")

        expected_confidence = expected_confidence_output(
            confidence_margin
        )

        actual_confidence = int(dut.uo_out.value)

        dut._log.info(
            f"features={features:07b} "
            f"confidence={confidence_margin} "
            f"confidence_expected={expected_confidence:08b} "
            f"confidence_actual={actual_confidence:08b}"
        )

        assert actual_confidence == expected_confidence, (
            f"Confidence mode failed for features {features:07b}: "
            f"expected margin {confidence_margin}, "
            f"expected output {expected_confidence:08b}, "
            f"received {actual_confidence:08b}"
        )

        # The bidirectional pins are unused in every mode.
        assert int(dut.uio_out.value) == 0, (
            f"Expected uio_out=00000000, "
            f"received {int(dut.uio_out.value):08b}"
        )

        assert int(dut.uio_oe.value) == 0, (
            f"Expected uio_oe=00000000, "
            f"received {int(dut.uio_oe.value):08b}"
        )

    dut._log.info(
        "All 128 feature combinations passed in both display modes"
    )
