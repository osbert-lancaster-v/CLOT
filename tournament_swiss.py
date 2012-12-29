
import logging
import random
from copy import deepcopy

from mwmatching import maxWeightMatching
import new_utility_functions

import main
#from players import Player
import players


def seeIfTourneyCanStart():
	
	ppp = players.Player.all()
	count = 0
	for p in ppp:
		if p.isParticipating:
			count += 1
	
	if count >= main.getMinimumNumberOfPlayers():
		if (not main.isTourneyInPlay()) and (not main.hasTourneyFinished()):
			if main.areWePastStarttime():
				main.startTourney()
				logging.info('tourney starting')
				return True
	else:
		logging.info('tourney doesnt yet have enough players to start.  num active players = '+str(count)+' num needed players = '+str(main.getMinimumNumberOfPlayers()))
		return False


def getMatchedList_Swiss():

	#head_to_head_biggermat
	head_to_head_biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable()

	num_players = len(head_to_head_biggermat)-1
	assert(num_players>=2)

	#in this function, we use ids from 0 to num_players.
	#here, we create a mapping from these ids to the database's player_ids, 
	#randomly shuffled to try and avoid paterns in the matching
	temp = deepcopy(head_to_head_biggermat[0][1:])
	playersidlocal_playerids = [temp[i] for i in range(0,num_players)]
	logging.info('playersidlocal_playerids')
	logging.info(playersidlocal_playerids)

	num_wins = []
	num_games = []
	for i in range(0,num_players):
		num_wins.append(0)
		num_games.append(0)
		for j  in range(0,num_players):
			num_wins[i] += head_to_head_2d[i][j][0]
			num_games[i] += (head_to_head_2d[i][j][0]+head_to_head_2d[i][j][0])/2

	#deal with odd num_players
	player_who_sits_out = -1
	if num_players%2 == 1:
		tmp = zip(num_games,range(0,num_players))
		tmp.sort()
		logging.info('tmp')
		logging.info(tmp)
		player_who_sits_out = tmp[-1][1] #this player is one who has highest number of games
		logging.info('player_who_sits_out')
		logging.info(player_who_sits_out)

	#make edges
	edges=[]
	for i in range(0,num_players):
		for j  in range(i+1,num_players):
			if (head_to_head_2d[i][j][0]==0) and (head_to_head_2d[i][j][1]==0):
				if (player_who_sits_out!=i) and (player_who_sits_out!=j):
					# i,j have not played yet
					abs_win_diff = abs(num_wins[i]-num_wins[j])
					edges.append((i,j,-abs_win_diff+0.1*random.random())) #note the - sign.  the 0.1*random.random() is to randomise things WITHOUT changing the ranking of num wins etc. 
				else:
					edges.append((i,j,-1000000)) #a big number, to ensure we never make this match
	logging.info('edges')
	logging.info(edges)

	#call the clever matching algorithm
	matchups = maxWeightMatching(edges,True)
	logging.info('matchups')
	logging.info(matchups)
	if not matchups:
		return [] #we havent got any matchups.  likely that the tournament is over. 

	#package matchups into right format
	doneq = [False] * num_players
	new_match_list = []
	for i in range(0,num_players):
		if not doneq[i]:
			doneq[i]=True
			j = matchups[i]
			if j != -1:
				doneq[j]=True
			
				i_id = playersidlocal_playerids[i]
				j_id = playersidlocal_playerids[j]
			
				new_match_list.append(str(i_id))
				new_match_list.append(str(j_id))
	if player_who_sits_out >= 0:
		new_match_list.append(str(playersidlocal_playerids[player_who_sits_out])) #he wont get a game though, because of the odd number

	logging.info('new_match_list')
	logging.info(new_match_list)
	
	return new_match_list


