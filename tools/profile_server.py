#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path; path.append('../')
from config import SERVER_PROFILE_FILE

import pstats
stats = pstats.Stats(SERVER_PROFILE_FILE)
stats.sort_stats('cumulative')
stats.print_stats()
