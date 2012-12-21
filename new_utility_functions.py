import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import logging
from django import http
from django import shortcuts
from players import Player
from games import Game
from games import GamePlayer
from main import group
from main import ClotConfig
from main import getClotConfig

from copy import deepcopy

from clot import getFinishedGames
from clot import getPlayersIDNameDict


###########################################

def getHeadToHeadTable():

	#Load all finished games
	finishedGames = getFinishedGames()
	logging.info("finishedGames:")
	logging.info(finishedGames)

	#get player_id : name   dict
	players_id_name_dict = getPlayersIDNameDict()
	logging.info('players_id_name_dict')
	logging.info(players_id_name_dict)

	#Group finished games by who won
	finishedGamesGroupedByWinner = group(finishedGames, lambda g: g.winner)
	logging.info("finishedGamesGroupedByWinner:")
	logging.info(finishedGamesGroupedByWinner)

	#make the head-to-head table
	head_to_head_2d = [[getHeadToHead(p,o,finishedGamesGroupedByWinner) for o in players_id_name_dict] for p in players_id_name_dict]
	players_for_h2h = [p for p in players_id_name_dict]
	logging.info('head_to_head_2d:')
	logging.info(head_to_head_2d)

	#now package it up for the html
	biggermat = deepcopy(head_to_head_2d)
	biggermat.insert(0,players_for_h2h)
	players_for_h2h_padded = deepcopy(players_for_h2h)
	players_for_h2h_padded_22 = [str(player) + '::'+str(players_id_name_dict[player]) for player in players_for_h2h_padded]
	logging.info(players_for_h2h_padded_22)

	players_for_h2h_padded_22.insert(0,'player_id')
	for i,j in zip(biggermat, players_for_h2h_padded_22):
		i.insert(0,j)
	logging.info(biggermat)

	#biggermat [x][y] for x,y>0 is the number of games player x won against player y.  
	#biggermat [0][y] for y>0 is the player_id of player y.
	#biggermat [x][0] for x>0 is the player_id of player x.
	return biggermat


def catcrp(x,y):
	return str(x)+'---'+str(y)


def getHeadToHead(team_a_id,team_b_id,finishedGamesGroupedByWinner):
	"""given 2 player_id s and the list of finished games, 
	calculate their head-to-head wins"""

	logging.info('in getHeadToHead(....)')
	
	num_team_a_wins = 0
	if team_a_id in finishedGamesGroupedByWinner.keys():
		team_a_wins = finishedGamesGroupedByWinner[team_a_id]
		for game in team_a_wins:
			if game.loser == team_b_id:
				num_team_a_wins+=1
	
	num_team_b_wins = 0
	if team_b_id in finishedGamesGroupedByWinner.keys():
		team_b_id = finishedGamesGroupedByWinner[team_b_id]
		for game in team_b_id:
			if game.loser == team_a_id:
				num_team_b_wins+=1

	logging.info([num_team_a_wins,num_team_b_wins])
	return [num_team_a_wins,num_team_b_wins]




