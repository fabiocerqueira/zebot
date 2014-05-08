#!/usr/bin/env python
#-*- coding: utf-8 -*-
from Yowsup.connectionmanager import YowsupConnectionManager

import os
import time
import base64
import random
from datetime import datetime


JID_BASE = "%s@s.whatsapp.net"

CHALLENGES = [
    'Tire uma selfie e envie agora no grupo, não vale se arrumar!',
    'Envie um vídeo de 10 segundos cantando uma música escolhida pelo grupo!',
    'Compartilhe aqui a última conversa com alguém do grupo, a sua escolha!(Print Screen)',
]

class ZeClient(object):

    def __init__(self, admin_phone, keep_alive=False, send_receipts=False):
        self.send_receipts = send_receipts
        self.keep_alive = keep_alive
        self.admin_phone = admin_phone
        self.admin_jid = JID_BASE % admin_phone
        # Configure connection manager
        connection_manager = YowsupConnectionManager()
        connection_manager.setAutoPong(keep_alive)
        self.signals = connection_manager.getSignalsInterface()
        self.methods = connection_manager.getMethodsInterface()
        # Configure callbacks
        self.signals.registerListener("auth_success", self.on_auth_success)
        self.signals.registerListener("auth_fail", self.on_auth_failed)
        self.signals.registerListener("disconnected", self.on_disconnected)
        self.signals.registerListener("message_received", self.on_message_received)
        self.signals.registerListener("group_messageReceived", self.on_group_message_received)

        self.players = {}

        self.done = False

    def login(self, bot_phone, password):
        self.bot_phone = bot_phone
        self.bot_jid = JID_BASE % bot_phone
        self.password = base64.b64decode(bytes(password.encode('utf-8')))
        self.methods.call("auth_login", (self.bot_phone, self.password))
        while not self.done:
            time.sleep(0.5)

    def on_auth_success(self, bot_phone):
        print("Authed %s" % bot_phone)
        self.methods.call("ready")

    def on_auth_failed(self, bot_phone, err):
        print("Auth Failed!")

    def on_disconnected(self, reason):
        print("Disconnected because %s" % reason)

    def on_message_received(self, message_id, jid, message, timestamp, wants_receipt, push_name, is_broadcast):
        if self.admin_jid != jid:
            return
        timestamp = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
        print("%s [%s]:%s" % (jid, timestamp, message))
        if wants_receipt and self.send_receipts:
            self.methods.call("message_ack", (jid, message_id))

    def on_group_message_received(self, message_id, group_jid, author, message, timestamp, wants_receipt, push_name):
        if '!rodar' == message:
            self.methods.call("message_send", (group_jid, 'rodando a chinela...'))
            try:
                ask, answer = random.sample(self.players[group_jid], 2)
            except:
                self.methods.call("message_send", (group_jid, "Vamos jogar galera! Digite !jogar"))
            else:
                msg = "%s -> %s" % (ask, answer)
                self.methods.call("message_send", (group_jid, msg))
        elif '!jogar' == message:
            if group_jid not in self.players:
                self.players[group_jid] = []
            if push_name not in self.players[group_jid]:
                self.players[group_jid].append(push_name)
                self.methods.call("message_send", (group_jid, ('%s entrou no jogo...' % push_name)))
            else:
                self.methods.call("message_send", (group_jid, ('%s já está jogando!' % push_name)))
        elif '!sair' == message:
            if group_jid not in self.players or not self.players[group_jid]:
                self.methods.call("message_send", (group_jid, 'Ninguém está jogando.'))
            else:
                if push_name in self.players[group_jid]:
                    self.players[group_jid].remove(push_name)
                    self.methods.call("message_send", (group_jid, '%s saiu do jogo.' % push_name))
                else:
                    self.methods.call("message_send", (group_jid, '%s não está no jogo.' % push_name))
        elif '!lancar' == message:
            msg = "Mentira"
            if random.randrange(100) > 55:
                msg = "Verdade"
            self.methods.call("message_send", (group_jid, msg))
        elif '!listar' == message:
            if group_jid in self.players and self.players[group_jid]:
                self.methods.call("message_send", (group_jid, ('No jogo agora: %s' % ','.join(self.players[group_jid]))))
            else:
                self.methods.call("message_send", (group_jid, 'Ninguém está jogando.'))
        elif '!desafio' == message:
            self.methods.call("message_send", (group_jid, random.choice(CHALLENGES)))
        if wants_receipt and self.send_receipts:
            self.methods.call("message_ack", (group_jid, message_id))


if __name__ == '__main__':
    bot_phone = os.environ.get("BOT_PHONE", "")
    password = os.environ.get("BOT_PASSWORD", "")
    admin_phone = os.environ.get("BOT_ADMIN", "")
    wa = ZeClient(admin_phone, True, True)
    wa.login(bot_phone, password)
