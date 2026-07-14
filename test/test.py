# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

"""
Tests for TinyMind, an 8-input, 3-class fixed-weight AI inference accelerator.

All eight input switches are binary features.

The design calculates three class scores:

    A = AI-oriented
    H = Hardware-oriented
    C = Creative-oriented

The seven-segment display has two views:

    show_confidence = 0 -> predicted class: A, H, or C
    show_confidence = 1 -> confidence margin: 0 through 9

The internal display-view register toggles on every rising clock edge.

Reset returns the display to class view.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


# ---------------------------------------------------------------------------
# Seven-segment patterns
# ---------------------------------------------------------------------------
#
# These values must match src/project.v.
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
    Software reference model matching the Verilog neuron equations.

    Parameters
    ----------
    features:
        Eight-bit integer containing x0 through x7.

    Returns
    -------
    tuple:
        predicted_class,
        score_ai,
        score_hardware,
        score_creative,
        confidence_margin
    """

    # Extract the eight input features.
    # Each feature is either 0 or 1.
    x0 = (features >> 0) & 1
    x1 = (features >> 1) & 1
    x2 = (features >> 2) & 1
    x3 = (features >> 3) & 1
    x4 = (features >> 4) & 1
    x5 = (features >> 5) & 1
    x6 = (features >> 6) & 1
    x7 = (features >> 7) & 1

    # -----------------------------------------------------------------------
    # AI-oriented neuron
    #
    # score_ai =
    #     +x0
    #     +x1
    #     +x4
    #     -x5
    #     +x7
    #     +1 bias
    # -----------------------------------------------------------------------

    score_ai = x0 + x1 + x4 - x5 + x7 + 1

    # -----------------------------------------------------------------------
    # Hardware-oriented neuron
    #
    # score_hardware =
    #     +x0
    #     +x2
    #     +x3
    #     +x5
    #     -x6
    # -----------------------------------------------------------------------

    score_hardware = x0 + x2 + x3 + x5 - x6

    # -----------------------------------------------------------------------
    # Creative-oriented neuron
    #
    # score_creative =
    #     -x1
    #     -x2
    #     +x5
    #     +x6
    #     +x7
    #     +1 bias
    # -----------------------------------------------------------------------

    score_creative = -x1 - x2 + x5 + x6 + x7 + 1

    # -----------------------------------------------------------------------
    # Winner selection
    #
    # Tie priority must match the Verilog:
    #
    #     A first
    #     H second
    #     C third
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

    # The hardware limits the display to one decimal digit.
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
    Build the expected 8-bit class-view output.

    uo_out[6:0] shows A, H, or C.

    uo_out[7] is the decimal point and turns on when the confidence
    margin is zero or one.
    """

    segments = CLASS_SEGMENTS[predicted_class]

    close_prediction = confidence_margin <= 1
    decimal_point = 1 if close_prediction else 0

    return (decimal_point << 7) | segments


def expected_confidence_output(confidence_margin: int) -> int:
    """
    Build the expected 8-bit confidence-view output.

    The decimal point is off in confidence mode.
    """

    return DIGIT_SEGMENTS[confidence_margin]


@cocotb.test()
async def test_project(dut):
    """
    Exhaustively test all 256 input combinations in both display views.
    """

    dut._log.info("Starting exhaustive TinyMind test")

    # Start the clock.
    #
    # The design toggles between class view and confidence view
    # on every rising edge.
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Put all inputs into known initial conditions.
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # -----------------------------------------------------------------------
    # Apply reset
    #
    # rst_n = 0 resets show_confidence to zero,
    # meaning the display starts in class view.
    # -----------------------------------------------------------------------

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)

    dut.rst_n.value = 1
    await Timer(1, unit="us")

    # -----------------------------------------------------------------------
    # Test every possible eight-feature input pattern.
    # -----------------------------------------------------------------------

    for features in range(256):

        dut.ui_in.value = features

        # Allow combinational score and display logic to settle.
        await Timer(1, unit="us")

        (
            predicted_class,
            score_ai,
            score_hardware,
            score_creative,
            confidence_margin,
        ) = calculate_prediction(features)

        expected_class = expected_class_output(
            predicted_class,
            confidence_margin,
        )

        expected_confidence = expected_confidence_output(
            confidence_margin
        )

        # -------------------------------------------------------------------
        # Return to class view before checking this input.
        #
        # Reset is used for every input combination so the test always starts
        # from a known display state.
        # -------------------------------------------------------------------

        dut.rst_n.value = 0
        await Timer(1, unit="us")

        dut.rst_n.value = 1
        await Timer(1, unit="us")

        # -------------------------------------------------------------------
        # Check class view.
        # -------------------------------------------------------------------

        actual_class = int(dut.uo_out.value)

        dut._log.info(
            f"features={features:08b} "
            f"scores(A,H,C)=("
            f"{score_ai},{score_hardware},{score_creative}) "
            f"class={predicted_class} "
            f"margin={confidence_margin} "
            f"class_expected={expected_class:08b} "
            f"class_actual={actual_class:08b}"
        )

        assert actual_class == expected_class, (
            f"Class view failed for features {features:08b}: "
            f"expected class {predicted_class}, "
            f"expected output {expected_class:08b}, "
            f"received {actual_class:08b}"
        )

        # -------------------------------------------------------------------
        # Press the step clock once.
        #
        # The rising edge changes show_confidence from 0 to 1.
        # -------------------------------------------------------------------

        await ClockCycles(dut.clk, 1)
        await Timer(1, unit="us")

        # -------------------------------------------------------------------
        # Check confidence view.
        # -------------------------------------------------------------------

        actual_confidence = int(dut.uo_out.value)

        dut._log.info(
            f"features={features:08b} "
            f"confidence={confidence_margin} "
            f"confidence_expected={expected_confidence:08b} "
            f"confidence_actual={actual_confidence:08b}"
        )

        assert actual_confidence == expected_confidence, (
            f"Confidence view failed for features {features:08b}: "
            f"expected confidence margin {confidence_margin}, "
            f"expected output {expected_confidence:08b}, "
            f"received {actual_confidence:08b}"
        )

        # -------------------------------------------------------------------
        # Press the step clock again.
        #
        # The display should return to class view.
        # -------------------------------------------------------------------

        await ClockCycles(dut.clk, 1)
        await Timer(1, unit="us")

        actual_class_again = int(dut.uo_out.value)

        assert actual_class_again == expected_class, (
            f"Second class view failed for features {features:08b}: "
            f"expected output {expected_class:08b}, "
            f"received {actual_class_again:08b}"
        )

        # Bidirectional pins must remain unused.
        assert int(dut.uio_out.value) == 0, (
            f"Expected uio_out=00000000, "
            f"received {int(dut.uio_out.value):08b}"
        )

        assert int(dut.uio_oe.value) == 0, (
            f"Expected uio_oe=00000000, "
            f"received {int(dut.uio_oe.value):08b}"
        )

    dut._log.info(
        "All 256 input combinations passed in class and confidence views"
    )
