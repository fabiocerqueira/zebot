#-*- coding: utf-8 -*-
import unittest

from game import TruthOrDare, CHALLENGES, HELP_TEXT

MESSAGE = ('', '')

def send_msg(jid, msg):
    global MESSAGE
    MESSAGE = (jid, msg)

class TruthOrDareTestCase(unittest.TestCase):

    def setUp(self):
        self.game = TruthOrDare('group', send_msg)

    def test_play(self):
        self.game.players = ['player1', 'player2']
        self.game.play()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertTrue('player1' in msg)
        self.assertTrue('pergunta para' in msg)
        self.assertTrue('player2' in msg)

    def test_play_without_players(self):
        self.game.play()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'Vamos jogar galera! Digite !jogar')

    def test_join(self):
        self.game.join(push_name='player1')
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'player1 entrou no jogo...')
        self.assertTrue('player1' in self.game.players)

    def test_join_with_player_in_game(self):
        self.game.players = ['player1']
        self.game.join(push_name='player1')
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'player1 já está jogando!')

    def test_left(self):
        self.game.players = ['player1']
        self.game.left(push_name='player1')
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'player1 saiu do jogo.')
        self.assertTrue('player1' not in self.game.players)

    def test_left_without_in_the_game(self):
        self.game.left(push_name='player1')
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'player1 não está no jogo.')
        self.assertTrue('player1' not in self.game.players)

    def test_list(self):
        self.game.players = ['player1', 'player2']
        self.game.list_players()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertTrue('No jogo agora: ' in msg)
        self.assertTrue('player1' in msg)
        self.assertTrue('player2' in msg)

    def test_list_players_without_players(self):
        self.game.list_players()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, 'Ninguém está jogando.')

    def test_throw(self):
        self.game.throw()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertTrue(msg in ['Mentira', 'Verdade'])

    def test_challenge(self):
        self.game.challenge()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertTrue(msg in CHALLENGES)

    def test_help(self):
        self.game.game_help()
        jid, msg = MESSAGE
        self.assertEquals(jid, 'group')
        self.assertEquals(msg, HELP_TEXT)

    def tearDown(self):
        self.game = None

if __name__ == '__main__':
    unittest.main()
