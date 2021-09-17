#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 24.10.2018
@author: MrFlamez
'''

from collections import namedtuple
import re
from types import ListType

# Message States
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

    def __init__(self, httpConnection):
        self.__httpConn = httpConnection

    def __getMessageIDFromNewMessageResult(self, result):
        """
        Extrahiert aus content die ID der neu angelegten Nachricht
        """

        res = re.search(r'name="hpc" value="(.*)" id="hpc"', result)
        if res is None:
            raise MessengerError()
        else:
            return res.group(1)

    def __wasDeliverySuccessful(self, result):
        """
        Prüft, ob der Versand der Nachricht erfolgreich war.
        """
        res = re.search(r'Deine Nachricht wurde an.*verschickt.', result)
        if (res is not None):
            return True
        else:
            return False

    def __didTheMessageRecipientExist(self, result):
        """
        Prüft, ob der Empfänger der Nachricht vorhanden war.
        """
        res = re.search(r'Der Empfänger existiert nicht.', result)
        if (res is not None):
            return False
        else:
            return True

    def __didTheMessageHadASubject(self, result):
        """
        Prüft, ob die Nachricht einen Betreff hatte.
        """
        res = re.search(r'Es wurde kein Betreff angegeben.', result)
        if (res is not None):
            return False
        else:
            return True

    def __didTheMessageHadAText(self, result):
        """
        Prüft, ob die Nachricht einen Text hatte.
        """
        res = re.search(r'Es wurde keine Nachricht eingegeben.', result)
        if (res is not None):
            return False
        else:
            return True

    def __didTheMessageHadARecipient(self, result):
        """
        Prüft, ob die Nachricht einen Empfänger hatte.
        """
        res = re.search(r'Es wurde kein Empfänger angegeben.', result)
        if (res is not None):
            return False
        else:
            return True

    def __blockedFromMessageRecipient(self, result):
        """
        Prüft, ob der Empfänger den Empfang von Nachrichten des Senders blockiert hat.
        """
        res = re.search(r'Der Empfänger hat dich auf die Blockliste gesetzt.', result)
        if (res is not None):
            return True
        else:
            return False

    def __getMessageDeliveryState(self, result):
        """
        Gibt den Status der gesendeten Nachricht zurück.
        """
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
        """"
        Fordert mit der HTTP Connection eine neue Nachricht an und ermittelt die ID zum späteren Senden.
        """

        try:
            result = self.__httpConn.createNewMessageAndReturnResult()
            id = self.__getMessageIDFromNewMessageResult(result)
        except:
            raise
        else:
            return id

    def __getMessageByState(self):
        """
        """
        pass

    def getMessagesWithFailedState(self):
        """
        """
        pass

    def getMessagesWithUnknownState(self):
        """
        """
        pass

    def clearSentList(self):
        """
        Löscht die Liste der gesendeten Nachrichten.
        """
        self.__sent = []

    def getSummaryOfMessageDeliveryStates(self):
        """
        Gibt eine Zusammenfassung über die Stati aller gesendeten Nachrichten zurück.
        """
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
        """
        Verschickt eine Nachricht und fügt diese der Liste der gesendeten Nachrichten hinzu.
        """
        if not type(recipients) is ListType:
            raise MessengerError()
            return

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
                print 'Exception ' + recipient
                raise
            else:
                i += 1
                print str(i) + ' von ' + str(n)


class MessengerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
