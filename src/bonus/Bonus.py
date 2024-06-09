from src.bonus.Http import Http
import time

class Bonus:
    def __init__(self):
        self.__http = Http()

    def get_daily_login_bonus(self):
        bonus_data = self.__http.read_user_data()
        for day, bonus in bonus_data['data']['rewards'].items():
            if 'done' in bonus:
                continue

            if any(_ in bonus for _ in ('money', 'products')):
                self.__http.get_daily_login_bonus(day)
                time.sleep(3)

