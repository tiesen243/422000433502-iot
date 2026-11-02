# Lab 1 - LED GPIO Control

This lab demonstrates digital output control on a **Raspberry Pi 4** using Python. The program turns a sequence of LEDs on and off one at a time and prints each LED state to the terminal.

## Hardware requirements

- Raspberry Pi 4
- LEDs
- Current-limiting resistors
- Connecting wires
- The circuit described in [`lab-1.docx`](./lab-1.docx)
- The KiCad files in [`lab_1/`](./lab_1/)

> Use an appropriate resistor with every LED. Check all connections carefully before powering the circuit.

## GPIO pins

The program uses these Raspberry Pi GPIO pins:

```text
21, 26, 20, 19, 16, 13, 6, 12, 5, 7, 11, 8,
9, 25, 10, 24, 22, 23, 27, 17, 18, 15, 4, 14
```

## Software requirements

- Raspberry Pi OS
- Python 3.14 or newer
- [`uv`](https://docs.astral.sh/uv/)

The required Python packages are declared in the root [`pyproject.toml`](../pyproject.toml).

## Installation

From the repository root on the Raspberry Pi 4:

```bash
git clone https://github.com/tiesen243/422000433502-iot.git
cd 422000433502-iot
uv sync
```

## Run the lab

```bash
uv run python lab_1/main.py
```

Press `Ctrl+C` to stop the program. The program turns all LEDs off before exiting.

## Files

- [`main.py`](./main.py) - Python implementation
- [`lab-1.docx`](./lab-1.docx) - Lab documentation
- [`lab_1/`](./lab_1/) - KiCad schematic and project files
