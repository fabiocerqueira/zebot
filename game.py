#-*- coding: utf-8 -*-
import random

CHALLENGES = [
    'Tire uma selfie e envie agora no grupo, não vale se arrumar!',
    'Envie um vídeo de 10 segundos cantando uma música escolhida pelo grupo!',
    'Compartilhe aqui a última conversa com alguém do grupo, a sua escolha!(Print Screen)',
]

class TruthOrDare(object):

    def __init__(self, group_jid, msg_callback = None):
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
        self.send_msg(self.group_jid, random.choice(CHALLENGES))
