import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import logging
from django import http
from django import shortcuts


from copy import deepcopy

import clot
import main
import players


###########################################

def seeIfTourneyCanStart(tourney_id, tourney_clotconfig):
	"""this is the default function, if no special one is specified for the tourney type chosen"""
	
	ppp = players.Player.all().filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	count = 0
	for p in ppp:
		if p.isParticipating:
			count += 1
	
	if count >= main.getMinimumNumberOfPlayers(tourney_id, tourney_clotconfig):
		if (not main.isTourneyInPlay(tourney_id, tourney_clotconfig)) and (not main.hasTourneyFinished(tourney_id, tourney_clotconfig)):
			if main.areWePastStarttime(tourney_id, tourney_clotconfig):
				main.startTourney(tourney_id, tourney_clotconfig)
				logging.info('tourney starting')
				return True
	else:
		logging.info('tourney doesnt yet have enough players to start.  num active players = '+str(count)+' num needed players = '+str(main.getMinimumNumberOfPlayers(tourney_id, tourney_clotconfig)))
		return False


def getHeadToHeadTable(tourney_id):
	"""returns a table of the player's head to head results.
	see end of the function for exactly what is returned"""

	#Load all finished games
	finishedGames = clot.getFinishedGames(tourney_id)
	#logging.info("finishedGames:")
	#logging.info(finishedGames)

	#get player_id : name   dict
	players_id_name_dict = clot.getPlayersIDNameDict(tourney_id)
	#logging.info('players_id_name_dict')
	#logging.info(players_id_name_dict)

	#get list of players, sorted by currentRank, highest First.
	players_sorted_by_rank = [[p.player_id, p.currentRank] for p in players.Player.all().filter("tourney_id =", tourney_id)] ###.run(batch_size=1000)]
	players_sorted_by_rank.sort(key=lambda x: x[1])
	players_ids_sorted_by_rank = [int(p[0]) for p in players_sorted_by_rank]
	##logging.info('players_ids_sorted_by_rank')
	##logging.info(players_ids_sorted_by_rank)

	#Group finished games by who won
	finishedGamesGroupedByWinner = main.group(finishedGames, lambda g: g.winner)
	#logging.info("finishedGamesGroupedByWinner:")
	#logging.info(finishedGamesGroupedByWinner)

	#make the head-to-head table
	head_to_head_2d = [[getHeadToHead(p,o,finishedGamesGroupedByWinner) for o in players_ids_sorted_by_rank] for p in players_ids_sorted_by_rank]
	players_for_h2h = [p for p in players_ids_sorted_by_rank]
	#logging.info('head_to_head_2d:')
	#logging.info(head_to_head_2d)

	#now package it up for the html
	biggermat = deepcopy(head_to_head_2d)
	biggermat.insert(0,players_for_h2h)
	players_for_h2h_padded = deepcopy(players_for_h2h)
	players_for_h2h_padded_22 = [str(player) + '::'+str(players_id_name_dict[player]) for player in players_for_h2h_padded]
	#logging.info(players_for_h2h_padded_22)

	players_for_h2h_padded_22.insert(0,'player_id')
	for i,j in zip(biggermat, players_for_h2h_padded_22):
		i.insert(0,j)
	#logging.info(biggermat)

	#biggermat [x][y] for x,y>0 is the number of games player x won against player y.  
	#biggermat [0][y] for y>0 is the player_id of player y.
	#biggermat [x][0] for x>0 is the player_id of player x.
	return biggermat, head_to_head_2d


def catcrp(x,y):
	return str(x)+'---'+str(y)


def getHeadToHead(team_a_id,team_b_id,finishedGamesGroupedByWinner):
	"""given 2 player_id s and the list of finished games, 
	calculate their head-to-head wins"""

	##logging.info('in getHeadToHead(....)')
	
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

	##logging.info([num_team_a_wins,num_team_b_wins])
	
	return [num_team_a_wins,num_team_b_wins]




