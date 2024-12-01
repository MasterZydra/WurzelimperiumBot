[![WurzelimperiumBot Runner](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml)
[![WurzelimperiumBot Binary Compile and Release](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
![GitHub](https://img.shields.io/github/license/MasterZydra/WurzelimperiumBot)

A forked from [MrFlamez/Wurzelimperium-Bot](https://github.com/MrFlamez/Wurzelimperium-Bot)

*Read this in other languages: [English](README.md), [German](README.de.md), [Bulgarian](README.bg.md)*

# Wurzelimperium-Bot
A Bot for the browsergame Wurzelimperium from Upjers. Enjoy free premium features in the game thanks to this bot!

**Inhaltsverzeichnis**
- [Usage](#usage)
- [Features](#features)
- [Installation](#installation)
- [Installation script für Linux](#installation-script-für-linux)

## Usage
Usage of this bot is possible in various situations:

### Script
Like in [example.py](./example.py) tasks can be created as script or automatically run on your pc.

### Automated
This script automates a lot of garden work and can be run by GitHub actions.  
Learn more [automated_script.py](./automated_script.py)

The fully automated script only allows passing your login credentials as arguments:  
e.g. `python3 ./automated_script.py 12 FooBar password1337 en`

```
usage: automated_script.py [-h] [-p] [-l] server user password [lang]

positional arguments:
  server        server number
  user          username for login
  password      password for login
  lang          Set Language and Region for the Game and Bot

options:
  -h, --help    show this help message and exit
  -p, --portal  If -p or --portal Argument is passed, Portal Account Login will be used.
  -l, --log     If -l or --log Argument is passed, logging will be enabled.
```

### Interactive
With the program [console.py](./console.py) you can run actions by using an interactive console.

The following commands are supported by the console:
```
bee          Send bees
bonus        Get the daily login bonus
details      Show details to the products
             Opt. argument: "all", "water"
buy          Buy a given plant
exit         Close connection and exit bot
games        Play the minigames
grow         Grow a given plant
grow-water   Grow a given water plant
harvest      Harvest all gardens
help         Show all available commands
lowest       Show the plant with the lowest stock (unequal zero)
             Opt. argument: "single", "water"
stock        Show all plants in stock
             Opt. argument: "sort"
user         Show details to the current user
water        Water all plants
weed         Remove all weed
wimp         Process Wimp Customers in Gardens
```

You have two options to pass your credentials:  
1. Pass them as arguments:  
  e.g. `python3 console.py --server 1 --user MyUserName  --password AVerySecurePassword`
2. Set them in the file itself:  
    You can set your credentials in the area `# Login data`

```
usage: console.py [-h] [--server SERVER] [--user USER] [--password PASSWORD] [--lang LANG] [-p] [-l]

options:
  -h, --help           show this help message and exit
  --server SERVER      server number
  --user USER          username for login
  --password PASSWORD  password for login
  --lang LANG          Set Language and Region for the Game and Bot
  -p, --portal         If -p or --portal Argument is passed, Portal Account Login will be used.
  -l, --log            If -l or --log Argument is passed, logging will be enabled.
```

### Standalone
There is also a standalone executable file for windows. [Win32-CLI-Standalone](https://github.com/MasterZydra/WurzelimperiumBot/releases/)

## Features
- Headless login without need of a browser.
- Completely automated watering of gardens.
- Automated planting and harvesting.  
  You can set the focus to grow only given plants in the account notes:  
  e.g. `growOnly: Sonnenblume, Apfel` or `growOnly: Kaffee`
- Automated processing of Wimps in gardens.  
  You can set the minimum stock in the account notes:  
  e.g. `minStock: 100` or `minStock(Apple): 200`
- You can disable the Bot by adding `stopWIB` in your notes
- Automatically claiming of daily login bonus.

## Installation
**Using venv**  <small>[askUbuntu](https://askubuntu.com/questions/1465218/pip-error-on-ubuntu-externally-managed-environment-%C3%97-this-environment-is-extern)</small>  
1. Install venv: `sudo apt install python3-venv`  
2. Create a new virtual environment in directory named env: `python3 -m venv env`
3. Activate virtual environment: `source env/bin/activate`  
4. Installation of requirements: `pip install -r ./requirements.txt`

**Requirements:** [Python 3](https://www.python.org/download/releases/3.0/)  
Installation of the dependencies: `pip install -r ./requirements.txt`

## Installation script for Linux
The installation script for linux is located in branch [`unix`](https://github.com/MasterZydra/WurzelimperiumBot/tree/unix).  
Thanks to [xRuffKez](https://github.com/xRuffKez) for developing the script.
