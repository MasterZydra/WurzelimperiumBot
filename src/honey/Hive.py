#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Hive:
    def __init__(self, nr, attributes):
        self.__nr = nr
        self.__level = attributes.get('level')
        self.__time = attributes.get('time')
        self.__pid = attributes.get('pid')
        self.__pid_change_time = attributes.get('pid_change_time')
        self.__pid_change_duration= attributes.get('pid_change_duration')
        self.__pid_change_remain = attributes.get('pid_change_remain')
        self.__tour_start = attributes.get('tour_start')
        self.__tour_duration = attributes.get('tour_duration')
        self.__tour_remain = attributes.get('tour_remain', 0)

    def get_nr(self):
        return self.__nr

    def get_level(self):
        return self.__level

    def get_time(self):
        return self.__time

    def get_pid(self):
        return self.__pid
    
    def get_pid_change_time(self):
        return self.__pid_change_time

    def get_pid_change_duration(self):
        return self.__pid_change_duration

    def get_pid_change_remain(self):
        return self.__pid_change_remain

    def get_tour_start(self):
        return self.__tour_start

    def get_tour_duration(self):
        return self.__tour_duration

    def get_tour_remain(self):
        return self.__tour_remain
