import time
from src.core.HTTPCommunication import HTTPConnection

class Bonus:
    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection

    def getDailyLoginBonus(self):
        bonus_data = self.__httpConn.readUserDataFromServer(data_type="dailyloginbonus")['dailyloginbonus']
        bonuses_to_claim = [(day, bonus) for day, bonus in bonus_data['data']['rewards'].items()
                            if 'done' not in bonus and any(_ in bonus for _ in ('money', 'products'))]

        self.__claim_login_bonuses(bonuses_to_claim)

    def __claim_login_bonuses(self, bonuses_to_claim):
        for day, _ in bonuses_to_claim:
            self.__httpConn.getDailyLoginBonus(day)
            
        sleep_time = max(0, len(bonuses_to_claim) - 1) * 3
        time.sleep(sleep_time)

                    
