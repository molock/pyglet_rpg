#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.engine_lib import *
from game_lib.math_lib import Point
from game_lib.protocol_lib import *
from game_lib.server_lib import *
from game_lib.gui_lib import AskHostname

from random import randrange

from config import PROFILE, TILESIZE, HOSTNAME, BLOCKTILES

class GameServer(SocketServer, TimerCallable, Game, AskHostname):
    hostname = None
    client_requestes = {}
    client_responses = {}
    def __init__(self):
        AskHostname.__init__(self)
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        Game.__init__(self)
    
    def timer_handler(self):
        self.process_action()
        look =  self.process_look()
        for name, messages in look.items():
            self.client_responses[name].append(messages)
        

    def accept(self, client):
        "вызывается при подключении клиента"
        print 'accept'
        self.client_requestes[client] = []
        self.client_responses[client] = []
        message = ('accept', self.create_player(client))
        self.client_responses[client] = [message]
        print 'acepting complete'


    def write(self, client):
        if self.client_responses[client]:
            try:
                for action, response in self.client_responses[client]:
                    data = pack(response, action)
                    self.put_message(client, data)
            except Exception, excp:
                print 'server.writ eror %s \n %s' % (excp, str(self.client_responses[client][0]))
                raise excp
            finally:
                self.client_responses[client] = []
    
    def read(self, client, messages):
        for message in messages:
            request = unpack(message)
            self.client_requestes[client].append(request)

    
    def close(self, client):
        print 'server close %s' % str(client)
        self.close_player(client)
        del self.client_requestes[client]
        del self.client_responses[client]

    def start(self):
        self.start_timer()
        self.run()
    



        

def main():
    server = GameServer()
    server.start()

if __name__ == '__main__':
    PROFILE = 1
    if PROFILE:
        print 'profile'
        import cProfile
        cProfile.run('main()', '/tmp/game_server.stat')
        

    else:
        main()

