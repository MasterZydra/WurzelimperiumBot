#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 24.10.2018
@author: MrFlamez
'''

from collections import namedtuple
import re, i18n
from src.message.Http import Http
from src.core.User import User
from src.logger.Logger import Logger

i18n.load_path.append('lang')

# Message States
#BG-Статус на съобщенията
MSG_STATE_UNKNOWN = 1
MSG_STATE_SENT_NO_ERR = 2
MSG_STATE_SENT_ERR_NO_RECIPIENT = 4
MSG_STATE_SENT_ERR_NO_SUBJECT = 8
MSG_STATE_SENT_ERR_NO_TEXT = 16
MSG_STATE_SENT_ERR_BLOCKED = 32
MSG_STATE_SENT_ERR_RECIPIENT_DOESNT_EXIST = 64

Message = namedtuple('Message', ['sender', 'to', 'subject', 'text', 'state'])

class Messenger:
    __inbox = []
    __outbox = []
    __system = []
    __sent = []

    def __init__(self):
        self.__http = Http()
        self.__user = User()

    def __get_message_id_from_new_message_result(self, result):
        """Extrahiert aus content die ID der neu angelegten Nachricht"""
        #BG- Извлича ID на новосъздаденото съобщение от съдържанието.
        res = re.search(r'name="hpc" value="(.*)" id="hpc"', result)
        if res is None:
            raise MessengerError()
        else:
            return res.group(1)

    def __was_delivery_successful(self, result) -> bool:
        """Prüft, ob der Versand der Nachricht erfolgreich war."""
        #BG-Проверява дали изпращането на съобщението е било успешно.
        res = re.search(r'Deine Nachricht wurde an.*verschickt.', result)
        return res is not None

    def __did_message_recipient_exist(self, result) -> bool:
        """Prüft, ob der Empfänger der Nachricht vorhanden war."""
        #BG-Проверява дали получателят на съобщението съществува.
        res = re.search(r'Der Empfänger existiert nicht.', result)
        return res is None

    def __did_message_had_subject(self, result) -> bool:
        """Prüft, ob die Nachricht einen Betreff hatte."""
        #BG-Проверява дали съобщението има тема.
        res = re.search(r'Es wurde kein Betreff angegeben.', result)
        return res is None

    def __did_message_had_text(self, result) -> bool:
        """Prüft, ob die Nachricht einen Text hatte."""
        #BG-Проверява дали съобщението има текст.
        res = re.search(r'Es wurde keine Nachricht eingegeben.', result)
        return res is None

    def __did_message_had_recipient(self, result) -> bool:
        """Prüft, ob die Nachricht einen Empfänger hatte."""
        #BG-Проверява дали съобщението има получател.
        res = re.search(r'Es wurde kein Empfänger angegeben.', result)
        return res is None

    def __blocked_from_message_recipient(self, result) -> bool:
        """Prüft, ob der Empfänger den Empfang von Nachrichten des Senders blockiert hat."""
        #BG-Проверява дали получателят е блокирал получаването на съобщения от изпращача.
        res = re.search(r'Der Empfänger hat dich auf die Blockliste gesetzt.', result)
        return res is not None

    def __get_message_delivery_state(self, result):
        """Gibt den Status der gesendeten Nachricht zurück."""
        #BG-Връща статуса на изпратеното съобщение.
        state = 0
        if (self.__was_delivery_successful(result) is True):
            state |= MSG_STATE_SENT_NO_ERR
        else:
            if (self.__did_message_recipient_exist(result) is False):
                state |= MSG_STATE_SENT_ERR_RECIPIENT_DOESNT_EXIST

            if (self.__did_message_had_subject(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_SUBJECT

            if (self.__did_message_had_text(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_TEXT

            if (self.__did_message_had_recipient(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_RECIPIENT

            if (self.__blocked_from_message_recipient(result) is True):
                state |= MSG_STATE_SENT_ERR_BLOCKED

        if (state == 0):
            state = state or MSG_STATE_UNKNOWN

        return state

    def __get_new_message_id(self):
        """"Fordert mit der HTTP Connection eine neue Nachricht an und ermittelt die ID zum späteren Senden."""
        #BG-Изисква ново съобщение чрез HTTP връзка и определя ID за по-късно изпращане.
        try:
            result = self.__http.create_new_message_and_return_result()
            if result is None:
                return None
            return self.__get_message_id_from_new_message_result(result)
        except Exception:
            Logger().print_exception("Failed to get new message id")
            return None

    def clear_sent_list(self):
        """Löscht die Liste der gesendeten Nachrichten."""
        #BG-Изтрива списъка с изпратени съобщения.
        self.__sent = []

    def get_summary_message_delivery_states(self):
        """Gibt eine Zusammenfassung über die Stati aller gesendeten Nachrichten zurück."""
        #BG-Връща обобщение на статусите на всички изпратени съобщения.
        numberOfAllSentMessages = len(self.__sent)
        numberOfsuccessfulMessages = 0
        numberOfFailedMessages = 0
        numberOfUnknownMessages = 0

        errorMask = MSG_STATE_SENT_ERR_BLOCKED | \
                    MSG_STATE_SENT_ERR_NO_RECIPIENT | \
                    MSG_STATE_SENT_ERR_NO_SUBJECT | \
                    MSG_STATE_SENT_ERR_NO_TEXT | \
                    MSG_STATE_SENT_ERR_RECIPIENT_DOESNT_EXIST

        for msg in self.__sent:
            if (msg.state & MSG_STATE_SENT_NO_ERR != 0):
                numberOfsuccessfulMessages += 1

            elif (msg.state & MSG_STATE_UNKNOWN != 0):
                numberOfUnknownMessages += 1

            elif (msg.state & errorMask != 0):
                numberOfFailedMessages += 1

        summary = {'sent': numberOfAllSentMessages, \
                   'fail': numberOfFailedMessages, \
                   'success': numberOfsuccessfulMessages, \
                   'unknown': numberOfUnknownMessages}

        return summary

    def write(self, recipients, subject, body) -> bool:
        """Verschickt eine Nachricht und fügt diese der Liste der gesendeten Nachrichten hinzu."""
        #BG-Изпраща съобщение и го добавя към списъка с изпратени съобщения.
        if not type(recipients) is list:
            raise MessengerError()

        n = len(recipients)
        i = 0
        for recipient in recipients:
            try:
                newMessageID = self.__get_new_message_id()
                if newMessageID is None:
                    return False
                resultOfSentMessage = self.__http.send_message_and_return_result(newMessageID, recipient, subject, body)
                if resultOfSentMessage is None:
                    return False
                messageDeliveryState = self.__get_message_delivery_state(resultOfSentMessage)
                tmp_Msg = Message(self.__user.get_username(), recipient, subject, body, messageDeliveryState)
                self.__sent.append(tmp_Msg)
                i += 1
                Logger().debug(f'{i} von {n}')
            except Exception:
                Logger().print_exception(f'Failed to write message to {recipient}')
                return False

        return True


class MessengerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
