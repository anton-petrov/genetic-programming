# Evolve + game with human

import gp

winner = gp.evolve(5, 100, gp.tournament, maxgen=50)
gp.gridgame([winner, gp.humanplayer()])
