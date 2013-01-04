import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging
import random
from copy import deepcopy


import main
import new_utility_functions
import games
import players



def pairs(lst):
	"""Simple helper function that groups a list into pairs.  For example, [1,2,3,4,5] would return [1,2],[3,4]"""
	for i in range(1, len(lst), 2):
		yield lst[i-1], lst[i]

def setRanks_ByNumWinsOnly(tourney_id):
	"""This looks at what games everyone has won and sets their currentRank field.
	The current algorithm is very simple - just award ranks based on number of games won.
	You should replace this with your own ranking logic."""
	
	logging.info('in setRanks()')

	#Load all finished games
	finishedGames = games.Game.all().filter("winner !=", None).filter("tourney_id =", tourney_id)
	logging.info("finishedGames:")
	logging.info(finishedGames)

	players_id_name_dict = getPlayersIDNameDict(tourney_id)
	logging.info('players_id_name_dict')
	logging.info(players_id_name_dict)

	#Group them by who won
	finishedGamesGroupedByWinner = main.group(finishedGames, lambda g: g.winner)
	logging.info("finishedGamesGroupedByWinner:")
	logging.info(finishedGamesGroupedByWinner)
	for game in games.Game.all().filter("tourney_id =", tourney_id):
		logging.info('game:')
		logging.info(game)
		
		if game.winner != None:
			pass

	#Get rid of the game data, and replace it with the number of games each player won
	winCounts = dict(map(lambda (playerID,the_games): (playerID, len(the_games)), finishedGamesGroupedByWinner.items())) 

	#Map this from Player.all() to ensure we have an entry for every player, even those with no wins
	playersMappedToNumWins = [(p, winCounts.get(p.key().id(), 0)) for p in players.Player.all().filter("tourney_id =", tourney_id)] 

	#sort by the number of wins each player has.
	playersMappedToNumWins.sort(key=lambda (player,numWins): numWins, reverse=True)

	#Now that it's sorted, we can just loop through each player and set their currentRank
	for index,(player,numWins) in enumerate(playersMappedToNumWins):
		player.currentRank = index + 1 #index is 0-based, and we want our top player to be ranked #1, so we add one.
		player.numWins = numWins #added by unkn
		player.save()
		logging.info('player:')
		logging.info(player)

	logging.info('setRanks finished')


def setRanks(tourney_id):
	setRanks_WithTiebreaks(tourney_id)


def setRanks_WithTiebreaks(tourney_id):
	"""this function ranks players by number of wins.  
	then, players who tie on number of wins are separated 
	by how many wins their beaten opponets have.  
	i.e. beating someone who won lots of games is better 
	for your ranking than beating someone with few wins. """
	
	logging.info('in setRanks_WithTiebreaks()')
	
	head_to_head_biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable(tourney_id)
	
	the_ids = deepcopy(head_to_head_biggermat[0][1:])
	logging.info('the_ids:')
	logging.info(the_ids)
	
	the_players = players.Player.all().filter("tourney_id =", tourney_id)
	num_players = len(list(the_players))
	assert(num_players==len(the_ids))
	
	num_wins = [0]*num_players
	for i in range(0,num_players):
		logging.info(i)
		for j in range(0,num_players):
			num_wins[i] += head_to_head_2d[i][j][0]
	
	logging.info('num_wins = '+str(num_wins))
	
	sum_of_wins_of_players_you_beat = [0]*num_players
	for i in range(0,num_players):
		logging.info(i)
		for j in range(0,num_players):
			sum_of_wins_of_players_you_beat[i] += head_to_head_2d[i][j][0]*num_wins[j]

	logging.info('sum_of_wins_of_players_you_beat = '+str(sum_of_wins_of_players_you_beat))

	points_and_playerid=[]
	for i in range(0,num_players):
		points_and_playerid.append(
				[ num_wins[i] +0.0001*sum_of_wins_of_players_you_beat[i] , the_ids[i] ]
				)
	logging.info('points_and_playerid:')
	logging.info(points_and_playerid)
	
	points_and_playerid.sort(reverse=True)
	
	logging.info('points_and_playerid:')
	logging.info(points_and_playerid)
	
	for p in the_players:
		player_id = int(p.player_id)
		rank = -1
		points = -1.0
		for i in range(0,len(points_and_playerid)):
			if points_and_playerid[i][1]==player_id:
				rank = i+1
				points = points_and_playerid[i][0]
		p.currentRank = rank
		p.numWins = int(round(points))
		p.save()
	
	logging.info('leaving setRanks_WithTiebreaks()')



def getFinishedGames(tourney_id):
	return games.Game.all().filter("winner !=", None).filter("tourney_id =", tourney_id)


def getPlayersIDNameDict(tourney_id):
	return dict([[p.key().id() , p] for p in players.Player.all().filter("tourney_id =", tourney_id)])


