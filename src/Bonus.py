import time


class Bonus:
    def __init__(self, httpConnection, spieler):
        self.__httpConn = httpConnection
        self.__spieler = spieler

    def getDailyLoginBonus(self):
        bonus_data = self.__httpConn.readUserDataFromServer(data_type="dailyloginbonus")['dailyloginbonus']
        for day, bonus in bonus_data['data']['rewards'].items():
            if 'done' not in bonus:
                if any(_ in bonus for _ in ('money', 'products')):
                    self.__httpConn.getDailyLoginBonus(day)
                    time.sleep(3)