#!/usr/bin/env python
#-*- coding: utf-8 -*-
from Yowsup.connectionmanager import YowsupConnectionManager

import os
import time
import base64
from datetime import datetime

from game import TruthOrDare

JID_BASE = "%s@s.whatsapp.net"


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

        self.groups = {}

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

    def get_send_msg(self, dst_jid=None):
        if dst_jid:
            def send_msg(msg):
                self.methods.call('message_send', (dst_jid, msg))
        else:
            def send_msg(jid, msg):
                self.methods.call('message_send', (jid, msg))
        return send_msg

    def on_message_received(self, message_id, jid, message, timestamp, wants_receipt, push_name, is_broadcast):
        print "y"*50
        if message.startswith('!'):
            try:
                operation, params = message.split(' ', 1)
            except ValueError:
                operation, params = message, None
            send_msg = self.get_send_msg(jid)
            TruthOrDare.private_command(operation, params, send_msg, user_jid=jid)
        # reply ack
        if wants_receipt and self.send_receipts:
            self.methods.call("message_ack", (jid, message_id))

    def on_group_message_received(self, message_id, group_jid, author, message, timestamp, wants_receipt, push_name):
        if group_jid not in self.groups:
            send_msg = self.get_send_msg()
            game_group = TruthOrDare(group_jid, send_msg)
            self.groups[group_jid] = game_group
        if message.startswith('!'):
            try:
                operation, params = message.split(' ', 1)
            except ValueError:
                operation, params = message, None
            command = self.groups[group_jid].commands.get(operation)
            if command:
                command(push_name=push_name, author=author, message=message, params=params)
        # reply ack
        if wants_receipt and self.send_receipts:
            self.methods.call("message_ack", (group_jid, message_id))



if __name__ == '__main__':
    bot_phone = os.environ.get("BOT_PHONE", "")
    password = os.environ.get("BOT_PASSWORD", "")
    admin_phone = os.environ.get("BOT_ADMIN", "")
    wa = ZeClient(admin_phone, True, True)
    wa.login(bot_phone, password)
