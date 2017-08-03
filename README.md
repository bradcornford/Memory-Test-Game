# Raspberry Pi Python memory test game

A project to create a memory test game on a Raspberry Pi using GPIO / I2C.

## Requirements

This package requires the following system packages to be installed:

- python-dev
- build-essential
- python-pip
- python-smbus

## Installation

Begin by installing this packages requirements:

    pip install -e .
    
Finally copy the example configuration file `example.config.py`, and save it as `config.py`

    cp memorytestgame/example.config.py memorytestgame/config.py

## Configuration

You can now configure Memory-Test-Game in a few simple steps. Open `memorytestgame/config.py` and update the options as needed.

- `leds` - An array of LEDs using GPIO pin as the key.
- `switches` - An array of Switches using GPIO pin as the key.
- `countdown` - The game countdown in seconds.
- `game_time` - The game play time in seconds.
- `score_increment` - The number to increment score by in game.
    
## Usage

It's really as simple as using the Mapper class

    sudo python memorytestgame/main.py
    
### License

Memory-Test-Game is open-sourced software licensed under the [MIT license](http://opensource.org/licenses/MIT)