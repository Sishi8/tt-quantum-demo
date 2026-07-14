# Schrodinger's Seven-Segment

Schrodinger's Seven-Segment is a small educational ASIC project that demonstrates selected ideas from single-qubit quantum computing using ordinary digital logic and one seven-segment display.

The project does not contain a physical qubit and is not a real quantum computer. Instead, it classically models a small set of qubit states and applies simplified gate-transition rules.

## How it works

The first three input switches select an operation:

- `000` — Idle
- `001` — X gate, or bit flip
- `010` — H gate, or Hadamard
- `011` — Measure
- `100` — Reset to zero
- `101` — Z gate, or phase flip
- `110` — Reserved
- `111` — Reserved

Each press of the manual step-clock button executes the selected operation once.

Internally, the design stores one of four simulated qubit states:

- `|0>` — definite zero
- `|1>` — definite one
- `|+>` — positive-phase superposition
- `|->` — negative-phase superposition

The X, H, and Z operations update the stored state according to simplified single-qubit gate rules.

Measurement behaves as follows:

- Measuring `|0>` produces `0`
- Measuring `|1>` produces `1`
- Measuring `|+>` or `|->` produces a pseudo-random `0` or `1`

After measurement, the stored state collapses to the displayed result.

A small linear-feedback shift register, or LFSR, is used to create pseudo-random measurement outcomes. This is deterministic digital logic, not true quantum randomness.

The seven-segment display shows either the current state or the selected operation.

State display conventions:

- `0` — state `|0>`
- `1` — state `|1>`
- `S` — state `|+>`
- `S.` — state `|->`

Operation display conventions:

- `-` — Idle
- `F` — Flip, representing X
- `H` — Hadamard
- `r` — Read, representing measurement
- `C` — Clear, representing reset
- `P` — Phase, representing Z

One input switch selects whether the display shows the current qubit state or the selected operation.

## How to test

Use the first three input switches to select an operation.

Use the display-mode switch to choose between:

- Current state view
- Selected operation view

Use the manual step-clock button to execute the selected operation.

Suggested tests:

### Test 1: Reset

1. Select Reset: `100`
2. Press the step clock
3. Switch to state view
4. The display should show `0`

### Test 2: X gate

1. Reset to `0`
2. Select X: `001`
3. Press the step clock
4. The display should show `1`

### Test 3: Superposition and measurement

1. Reset to `0`
2. Select H: `010`
3. Press the step clock
4. The state display should show `S`
5. Select Measure: `011`
6. Press the step clock
7. The display should show either `0` or `1`

### Test 4: Two Hadamard gates

1. Reset to `0`
2. Apply H
3. Apply H again
4. Measure
5. The result should be `0`

This demonstrates that two Hadamard operations cancel each other.

### Test 5: Phase and interference

1. Reset to `0`
2. Apply H
3. Apply Z
4. Apply H
5. Measure
6. The result should be `1`

This demonstrates that relative phase can affect the final measurement result.

## External hardware

No additional external hardware is required.

The project uses the standard Tiny Tapeout demo-board resources:

- Eight input switches
- Manual step-clock button
- Reset button
- One seven-segment display

## Limitations

This project is a classical educational model.

It does not:

- Contain a physical qubit
- Simulate arbitrary quantum amplitudes
- Model decoherence or noise
- Produce true quantum randomness
- Support multi-qubit entanglement

It is intended to demonstrate the basic ideas of state preparation, gate sequencing, superposition, phase, interference, measurement, and collapse.
