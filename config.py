#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
from os.path import join

TMP = tempfile.gettempdir()
TMP = "/tmp"

#имя хоста по-умолчанию
HOSTNAME = '127.0.0.1'
IN_PORT = 8888
OUT_PORT = 8889
SERIALISATION = 'json'
# SERIALISATION = 'marshal'
ZLIB = False


TILESIZE = 60
CHUNK_SIZE = 6
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1
PLAYER_LOOK_RADIUS = 9
SQUARE_FOV = True

###
WORLD_PATH = 'data/worldmaps/%s/'
WORLD_PERSISTENCE = True
SAVE_WORLD = True
WORLD_FILE = 'world.marshal.zlib'
MAP_FILE = 'map.marshal.zlib'
MAP_IMAGE = 'map.png'
MAP_DICT = 'tiledict.py'
WORLD_MUL = 1



PROFILE_SERVER = 1
SOCKET_SERVER_PROFILE = 1

SERVER_PROFILE_FILE = join(TMP,'/tmp/game_server.stat')
SOCKET_SERVER_PROFILE_FILE = join(TMP,'/tmp/socket_server.stat')

