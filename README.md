[![Python application](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
![GitHub](https://img.shields.io/github/license/MasterZydra/WurzelimperiumBot)

A forked from [MrFlamez/Wurzelimperium-Bot](https://github.com/MrFlamez/Wurzelimperium-Bot)

*Read this in other languages: [English](README.md), [German](README.de.md), [Russian](README.ru.md).*

# Wurzelimperium-Bot
A Bot for the browsergame Wurzelimperium from Upjers. Enjoy free premium features in the game thanks to this bot!

**Inhaltsverzeichnis**
- [Usage](#usage)
- [Features](#features)
- [Installation](#installation)
- [Installation script für Linux](#installation-script-für-linux)

## Usage
Usage of this bot is possible in various situations:
- **Script**:  
Like in [example.py](./example.py) tasks can be created as script or automatically run on your pc.
- **Automated**:  
Like using a script you can solve much more complex tasks, which can be run by GitHub actions for example.. Learn more [automated_script.py](./automated_script.py)
- **Interactive**:  
With program [console.py](./console.py) you can run actions by using an input `water` to water your whole garden.

By using [example.py](./example.py) and [console.py](./console.py) you have to edit and provide your login data and game region (language) in the files which you are running.

- **Standalone**:
There is also a standalone executable file for windows. [Win32-CLI-Standalone](https://github.com/MasterZydra/WurzelimperiumBot/releases/)

## Features
- Headless login without need of a browser.
- Completely automated watering of gardens.
- Automated planting and harvesting.
- Automated processing of Wimps in gardens.
- Automatically claiming of daily login bonus.

## Installation
**Requirements:** [Python 3](https://www.python.org/download/releases/3.0/)
1. Installation of requirements:  
`pip install -r ./requirements.txt`
2. Provide login data in scripts ([example.py](./example.py) and/or [console.py](./console.py)).  
   With fully automated script [automated_script.py](./automated_script.py) you need to pass your login credentials by adding them to the script as flag: </br>
   `python3 ./automated_script.py <server-nr> <username> <password> <lang>` </br>
   Example: python3 ./automated_script.py 12 FooBar password1337 en
3. Run the script.

## Installation script for Linux
The installation script for linux is located in branch [`unix`](https://github.com/MasterZydra/WurzelimperiumBot/tree/unix).  
Thanks to [xRuffKez](https://github.com/xRuffKez) for developing the script.
