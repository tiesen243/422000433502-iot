# 422000433502 - IoT

This repository contains Internet of Things (IoT) experiments and learning materials developed for the **Raspberry Pi 4**.

The project is organized as a collection of independent activities. Each activity has its own directory and README file containing the relevant description, hardware requirements, setup instructions, and usage details.

## Platform

- Raspberry Pi 4
- Raspberry Pi OS
- Python
- GPIO-based electronics and sensors

## Using this project

Clone the repository on your Raspberry Pi 4:

```bash
git clone https://github.com/tiesen243/422000433502-iot.git
cd 422000433502-iot
```

Install the project dependencies with [`uv`](https://docs.astral.sh/uv/):

```bash
uv sync
```

Open the README inside an activity directory to find its specific wiring, dependencies, and run command. Run Python programs from the repository root with:

```bash
uv run python path/to/activity/main.py
```

Make sure the required circuit is connected correctly before running any GPIO program. Use appropriate resistors and never connect components in a way that could damage the Raspberry Pi.

## Adding activities

Additional activities can be added in their own directories. Each directory should include a README with the activity description and instructions, along with its source code and any required circuit or design files.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
