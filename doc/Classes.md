```mermaid
  classDiagram
    class Bonsai
    class Bonus
    class Garden
    class Honig
    class HTTPConnection
    class Storage
    class Marketplace
    class Messenger
    class Note
    class Product
    class ProductData
    class Quests
    class Session
    class User
    class Wimps
    class WurzelBot
    
    HTTPConnection *-- Session
    Bonsai *-- HTTPConnection
    Bonus *-- HTTPConnection
    Garden *-- HTTPConnection
    Honig *-- HTTPConnection
    Marketplace *-- HTTPConnection
    Messenger *-- HTTPConnection
    Note *-- HTTPConnection
    ProductData *-- HTTPConnection
    ProductData *-- Product
    Quests *-- HTTPConnection
    Quests *-- User
    Storage *-- HTTPConnection
    Wimps *-- HTTPConnection
    
    WurzelBot *-- Bonsai
    WurzelBot *-- Bonus
    WurzelBot *-- Garden
    WurzelBot *-- Honig
    WurzelBot *-- HTTPConnection
    WurzelBot *-- Marketplace
    WurzelBot *-- Messenger
    WurzelBot *-- Note
    WurzelBot *-- ProductData
    WurzelBot *-- Quest
    WurzelBot *-- User
    WurzelBot *-- Storage
    WurzelBot *-- Wimps
```
