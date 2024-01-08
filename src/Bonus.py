import time
import logging
from src.HTTPCommunication import HTTPConnection

class Bonus:
    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection
        self._logBonus = logging.getLogger("bot.Bonus")
        self._logBonus.setLevel(logging.DEBUG)

    def getDailyLoginBonus(self):
        bonus_data = self.__httpConn.readUserDataFromServer(data_type="dailyloginbonus")['dailyloginbonus']
        for day, bonus in bonus_data['data']['rewards'].items():
            if 'done' not in bonus:
                if any(_ in bonus for _ in ('money', 'products')):
                    self.__httpConn.getDailyLoginBonus(day)
                    time.sleep(3)

    def collectBonusitemPoints(self):
        self.__httpConn.initGardenShed()
        self.__httpConn.openTrophyCase()
        jContent = self.__httpConn.collectBonusitems()
        claim_msg = jContent['msg']
        already_claimed_msg = jContent['message']
        self._logBonus.info(f"{claim_msg}{already_claimed_msg}")
