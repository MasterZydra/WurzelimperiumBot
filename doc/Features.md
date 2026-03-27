# Features

This page lists all features currently supported by the bot.

For an overview of **ongoing and planned features**, see the tracking issue:  
➡️ https://github.com/MasterZydra/WurzelimperiumBot/issues/84

## 🌐 General Automation

- **Headless login**  
  Allows logging in without needing a browser.

- **Automatic daily login bonus**  
  Claims the daily bonus automatically.

- **Automatic planting and harvesting**  
  Plants and harvests crops as soon as possible.  
  **Config:** Use account notes to restrict crops:  
  `growOnly: Sonnenblume, Apfel` or `growOnly: Kaffee`

- **Automatic watering**  
  Waters both normal gardens and water gardens.

- **Automated Wimp handling**  
  Serves Wimps based on available stock.  
  **Config:** Set minimum stock levels in account notes:  
  `minStock: 100` or `minStock(Apple): 200`

- **Bot disable switch**  
  Add `stopWIB` in account notes to disable the bot.

## 🌿 Special Gardens

- **Recreation garden**  
  Collects available points automatically.

- **Megafruit garden**  
  Harvests and processes Megafruits.

- **Ivyhouse**  
  Handles all Ivyhouse-related actions.

- **Birdhouse**  
  Collects and processes bird-related resources.

- **Biogas plant**  
  Automates biogas production and resource collection.

## 🎮 Mini Games / Event

### 📅 Calendars
- **Advent calendar**  
  Opens the daily calendar door.

- **Birthday calendar**  
  Opens the daily birthday calendar door.

- **Easter calendar**  
  Opens the daily Easter door.

- **Summer calendar**  
  Opens the daily summer event door.

### ⛏️ Digging Games
- **Autumn Dig Game**  
  Performs five randomized digs.

- **Easter Dig Game**  
  Performs five randomized digs.

### 🎡 Other Events
- **Fair**  
  Crafts tickets and plays:
  - Thimble game  
  - Wet gnome game  

- **Summer memory**  
  Plays the memory game automatically.
