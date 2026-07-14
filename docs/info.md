# TinyMind – A Tiny AI Inference Accelerator

## Motivation

Modern Artificial Intelligence (AI) systems such as image classifiers, speech recognizers, and large language models are built from millions—or even billions—of artificial neurons. During **training**, these neurons learn numerical parameters called **weights** from large datasets. Once training is complete, the learned weights are deployed to specialized hardware where they are repeatedly used to make predictions. This process is called **inference**.

TinyMind is a miniature educational ASIC that demonstrates this exact principle on a much smaller scale.

Instead of billions of neurons, TinyMind contains three.

Instead of millions of weights, TinyMind uses a handful of fixed **ternary weights** (`+1`, `0`, and `−1`) implemented directly in digital logic.

Although intentionally simple, the chip illustrates the same high-level inference pipeline found in modern AI accelerators.

---

# Project Goal

The goal of TinyMind is to demonstrate how AI inference can be implemented directly in digital hardware.

Rather than executing software instructions on a CPU, TinyMind performs its classification entirely using combinational logic synthesized into silicon.

This project was developed as part of the Tiny Tapeout educational ASIC program to help explain the relationship between:

- Machine Learning
- Digital Logic Design
- ASIC Implementation
- Hardware AI Accelerators

---

# AI Vocabulary

## Artificial Neuron

An artificial neuron is a small mathematical function that combines several inputs to produce a score.

Each neuron evaluates the same inputs but uses a different set of weights.

The neuron with the highest score becomes the prediction.

---

## Feature

A feature is one piece of information given to the AI.

TinyMind uses the eight input switches as binary features.

Each feature is either

```
0 = OFF
1 = ON
```

---

## Weight

A weight tells the neuron how important a feature is.

TinyMind uses **ternary weights**, meaning every weight can only be

| Weight | Meaning |
|---------|---------|
| +1 | Supports this class |
| 0 | Ignore this feature |
| -1 | Works against this class |

Using ternary weights removes the need for hardware multipliers, making the circuit much smaller while still demonstrating neural-network inference.

---

## Training

Training is the process of determining the best weights.

Training normally happens on powerful computers or GPUs using many example datasets.

TinyMind **does not perform training**.

Its weights are permanently built into the hardware.

---

## Inference

Inference is the process of making predictions using previously learned weights.

Every time the switches change, TinyMind immediately performs a new inference.

---

# Hardware Architecture

TinyMind contains three independent artificial neurons.

Each neuron evaluates the same eight input features.

```
                 Eight Input Features

                        │
                        ▼

          ┌─────────────────────────┐
          │     AI Neuron           │
          └─────────────────────────┘

          ┌─────────────────────────┐
          │  Hardware Neuron        │
          └─────────────────────────┘

          ┌─────────────────────────┐
          │  Creative Neuron        │
          └─────────────────────────┘

                        │
                        ▼

             Winner-Takes-All Logic

                        │
                        ▼

             Seven-Segment Display
```

All three neurons operate simultaneously.

This parallel computation is one of the defining characteristics of AI accelerators.

---

# Hardware Dataflow

The complete inference pipeline is shown below.

```
        Binary Input Features

                │

                ▼

      Fixed Ternary Weights

                │

                ▼

     Three Parallel Neurons

                │

                ▼

       Score Calculation

                │

                ▼

    Winner-Takes-All Selection

                │

                ▼

 Seven-Segment Display Output
```

Unlike a CPU, TinyMind does not execute instructions.

The hardware itself performs the neural-network computation.

---

# Example Inference

Suppose the eight switches are set to

```
10110010
```

Each neuron independently calculates a score.

| Neuron | Score |
|---------|------:|
| AI | **5** |
| Hardware | 2 |
| Creative | 1 |

The AI neuron has the highest score.

The display therefore shows

```
A
```

Pressing the step clock changes the display to

```
3
```

The value **3** is the confidence margin:

```
Winning Score − Second Highest Score
```

A larger value indicates a stronger prediction.

---

# Using the Demo Board

The Tiny Tapeout demonstration board provides

- Eight input switches
- One seven-segment display
- One step clock

Operation is simple:

1. Set the eight input switches.
2. Observe the predicted class.
3. Press the step clock.
4. Observe the confidence margin.
5. Press the clock again to return to the class display.

Try changing only one switch at a time and observe how the prediction changes.

---

# Why This Is an AI Accelerator

Modern AI accelerators contain dedicated hardware for neural-network inference.

TinyMind demonstrates the same architectural idea on a much smaller scale.

Instead of software repeatedly executing arithmetic instructions, the inference logic is permanently implemented in hardware.

Although TinyMind contains only three neurons, the overall processing flow is conceptually similar to larger commercial inference accelerators.

---

# Educational Takeaways

TinyMind demonstrates several important concepts in modern AI hardware:

- Binary feature vectors
- Artificial neurons
- Fixed ternary weights
- Parallel inference
- Winner-takes-all classification
- Confidence estimation
- Hardware implementation of neural networks

These same principles appear in much larger AI accelerators used in data centers, edge devices, and embedded systems.

---

# Future Improvements

Future versions of TinyMind could include:

- Training the weights using Python before hardware generation
- Automatically exporting trained weights into Verilog
- Larger neural networks with hidden layers
- Additional output classes
- Interactive learning demonstrations

---

# External Hardware

TinyMind requires only the standard Tiny Tapeout demonstration board.

No additional external hardware is required.

---

# About Tiny Tapeout

TinyMind was created as part of the Tiny Tapeout educational ASIC program (Virtual 2026)

The project explores how machine-learning inference can be represented directly in digital logic, synthesized into standard cells, placed and routed into a manufacturable layout, and ultimately fabricated as a real integrated circuit.
