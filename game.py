#-*- coding: utf-8 -*-
import os
import random

BASE_DIR = os.path.dirname(__file__)

HELP_TEXT = """!jogar -> Para entrar no jogo
!sair -> Para sair do jogo
!rodar -> Quem pergunta para quem?
!listar -> Para listar os jogadores
!lancar -> A resposta é verdade ou mentira?
!desafio -> Para escolher um desafio
!ajuda -> Para informação de ajuda"""

class TruthOrDare(object):

    def __init__(self, group_jid, msg_callback):
        self.send_msg = msg_callback
        self.players = []
        self.group_jid = group_jid
        self.commands = {
            '!rodar': self.play,
            '!jogar': self.join,
            '!sair': self.left,
            '!listar': self.list_players,
            '!lancar': self.throw,
            '!desafio': self.challenge,
            '!ajuda': self.game_help,
        }

    def play(self, **kwargs):
        try:
            ask, answer = random.sample(self.players, 2)
        except ValueError:
            self.send_msg(self.group_jid, 'Vamos jogar galera! Digite !jogar')
        else:
            self.send_msg(self.group_jid, 'Rodando a chinela...')
            msg = "%s pergunta para %s!" % (ask, answer)
            self.send_msg(self.group_jid, msg)

    def join(self, **kwargs):
        push_name = kwargs['push_name']
        if push_name not in self.players:
            self.players.append(push_name)
            self.send_msg(self.group_jid, '%s entrou no jogo...' % push_name)
        else:
            self.send_msg(self.group_jid, '%s já está jogando!' % push_name)

    def left(self, **kwargs):
        push_name = kwargs['push_name']
        if push_name not in self.players:
            self.send_msg(self.group_jid, '%s não está no jogo.' % push_name)
        else:
            self.players.remove(push_name)
            self.send_msg(self.group_jid, '%s saiu do jogo.' % push_name)

    def list_players(self, **kwargs):
        if not self.players:
            self.send_msg(self.group_jid, 'Ninguém está jogando.')
        else:
            self.send_msg(self.group_jid,
                          'No jogo agora: %s' % ','.join(self.players))

    def throw(self, **kwargs):
        msg = "Mentira"
        if random.randrange(100) > 55:
            msg = "Verdade"
        self.send_msg(self.group_jid, msg)

    def challenge(self, **kwargs):
        err_msg = "Não há desafios cadastrados!"
        challenges = []
        try:
            challenges = open(os.path.join(BASE_DIR, 'challenges.txt')).readlines()
        except IOError:
            self.send_msg(self.group_jid, err_msg)
            return
        if challenges:
            self.send_msg(self.group_jid, random.choice(challenges))
        else:
            self.send_msg(self.group_jid, err_msg)

    def game_help(self, **kwargs):
        self.send_msg(self.group_jid, HELP_TEXT)

    # Admin methods
    @classmethod
    def admin_command(cls, operation, params, send_msg_callback, **kwargs):
        cls.send_msg = staticmethod(send_msg_callback)
        commands = {
            '!add': cls.add_challenge,
        }
        cmd = commands.get(operation)
        if cmd:
            return cmd(params, **kwargs)
        else:
            return None

    @classmethod
    def add_challenge(cls, new_challenge, **kwargs):
        try:
            challenges = open(os.path.join(BASE_DIR, 'challenges.txt'), 'a+')
            challenges.write(new_challenge + '\n')
            resp_message = "Desafio registrado com sucesso!"
        except:
            resp_message = "Problema ao registrar o desafio!"
        cls.send_msg(resp_message)
