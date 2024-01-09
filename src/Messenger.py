#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 24.10.2018
@author: MrFlamez
'''

from collections import namedtuple
import re, i18n
from src.HTTPCommunication import HTTPConnection

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

class Messenger():
    __inbox = []
    __outbox = []
    __system = []
    __sent = []

    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection

    def __getMessageIDFromNewMessageResult(self, result):
        """Extrahiert aus content die ID der neu angelegten Nachricht"""
        #BG- Извлича ID на новосъздаденото съобщение от съдържанието.
        res = re.search(r'name="hpc" value="(.*)" id="hpc"', result)
        if res is None:
            raise MessengerError()
        else:
            return res.group(1)

    def __wasDeliverySuccessful(self, result) -> bool:
        """Prüft, ob der Versand der Nachricht erfolgreich war."""
        #BG-Проверява дали изпращането на съобщението е било успешно.
        res = re.search(r'Deine Nachricht wurde an.*verschickt.', result)
        return res is not None

    def __didTheMessageRecipientExist(self, result) -> bool:
        """Prüft, ob der Empfänger der Nachricht vorhanden war."""
        #BG-Проверява дали получателят на съобщението съществува.
        res = re.search(r'Der Empfänger existiert nicht.', result)
        return res is None

    def __didTheMessageHadASubject(self, result) -> bool:
        """Prüft, ob die Nachricht einen Betreff hatte."""
        #BG-Проверява дали съобщението има тема.
        res = re.search(r'Es wurde kein Betreff angegeben.', result)
        return res is None

    def __didTheMessageHadAText(self, result) -> bool:
        """Prüft, ob die Nachricht einen Text hatte."""
        #BG-Проверява дали съобщението има текст.
        res = re.search(r'Es wurde keine Nachricht eingegeben.', result)
        return res is None

    def __didTheMessageHadARecipient(self, result) -> bool:
        """Prüft, ob die Nachricht einen Empfänger hatte."""
        #BG-Проверява дали съобщението има получател.
        res = re.search(r'Es wurde kein Empfänger angegeben.', result)
        return res is None

    def __blockedFromMessageRecipient(self, result) -> bool:
        """Prüft, ob der Empfänger den Empfang von Nachrichten des Senders blockiert hat."""
        #BG-Проверява дали получателят е блокирал получаването на съобщения от изпращача.
        res = re.search(r'Der Empfänger hat dich auf die Blockliste gesetzt.', result)
        return res is not None

    def __getMessageDeliveryState(self, result):
        """Gibt den Status der gesendeten Nachricht zurück."""
        #BG-Връща статуса на изпратеното съобщение.
        state = 0
        if (self.__wasDeliverySuccessful(result) is True):
            state |= MSG_STATE_SENT_NO_ERR
        else:
            if (self.__didTheMessageRecipientExist(result) is False):
                state |= MSG_STATE_SENT_ERR_RECIPIENT_DOESNT_EXIST

            if (self.__didTheMessageHadASubject(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_SUBJECT

            if (self.__didTheMessageHadAText(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_TEXT

            if (self.__didTheMessageHadARecipient(result) is False):
                state |= MSG_STATE_SENT_ERR_NO_RECIPIENT

            if (self.__blockedFromMessageRecipient(result) is True):
                state |= MSG_STATE_SENT_ERR_BLOCKED

        if (state == 0):
            state = state or MSG_STATE_UNKNOWN

        return state

    def __getNewMessageID(self):
        """"Fordert mit der HTTP Connection eine neue Nachricht an und ermittelt die ID zum späteren Senden."""
        #BG-Изисква ново съобщение чрез HTTP връзка и определя ID за по-късно изпращане.
        try:
            result = self.__httpConn.createNewMessageAndReturnResult()
            return self.__getMessageIDFromNewMessageResult(result)
        except:
            raise

    def __getMessageByState(self):
        pass

    def getMessagesWithFailedState(self):
        pass

    def getMessagesWithUnknownState(self):
        pass

    def clearSentList(self):
        """Löscht die Liste der gesendeten Nachrichten."""
        #BG-Изтрива списъка с изпратени съобщения.
        self.__sent = []

    def getSummaryOfMessageDeliveryStates(self):
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

    def writeMessage(self, sender, recipients, subject, body):
        """Verschickt eine Nachricht und fügt diese der Liste der gesendeten Nachrichten hinzu."""
        #BG-Изпраща съобщение и го добавя към списъка с изпратени съобщения.
        if not type(recipients) is list:
            raise MessengerError()

        n = len(recipients)
        i = 0
        for recipient in recipients:

            try:
                newMessageID = self.__getNewMessageID()
                resultOfSentMessage = self.__httpConn.sendMessageAndReturnResult(newMessageID, recipient, subject, body)
                messageDeliveryState = self.__getMessageDeliveryState(resultOfSentMessage)
                tmp_Msg = Message(sender, recipient, subject, body, messageDeliveryState)
                self.__sent.append(tmp_Msg)
            except:
                print(f'Exception {recipient}')
                raise
            else:
                i += 1
                print(f'{i} von {n}')


class MessengerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
