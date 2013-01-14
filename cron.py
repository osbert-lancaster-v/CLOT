import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import datetime
from django import shortcuts
from django.utils import simplejson as json
import logging
import random


import clot
import main
import games
import players


#this function is called at set time intervals by the appengine
def go(request):
	logging.info("Starting cron...")
	
	for tourney in main.ClotConfig.all():
		cron_one_tourney(tourney.tourney_id,tourney)
	
	logging.info("Cron done")
	return shortcuts.render_to_response('cron.html')


def cron_one_tourney(tourney_id, tourney_clotconfig):
	tourney_id = int(tourney_id)
	logging.info( 'in cron_one_tourney(' +str(tourney_id)+' )' )

	if (not main.isTourneyInPlay(tourney_id, tourney_clotconfig)) and main.seeIfTourneyCanStart(tourney_id, tourney_clotconfig):
		main.startTourney(tourney_id, tourney_clotconfig)
		logging.info('******STARTED TOURNEY ' +str(tourney_id)+ '*****')
		logging.info(main.getTourneyType(tourney_id, tourney_clotconfig))
		logging.info('main.isTourneyInPlay() ' +str(main.isTourneyInPlay(tourney_id, tourney_clotconfig)))

	if main.isTourneyInPlay(tourney_id, tourney_clotconfig):
		checkInProgressGames(tourney_id, tourney_clotconfig)
		setResultsOfAllFinishedGames(tourney_id)
		main.createGames(tourney_id, tourney_clotconfig)
		clot.setRanks(tourney_id)

	logging.info( 'cron_one_tourney(' +str(tourney_id)+' ) done' )


def checkInProgressGames(tourney_id, tourney_clotconfig):
	"""This is called periodically to look for games that are finished.  If we find
	a finished game, we record the winner"""

	#Find all games that we think aren't finished
	activeGames = games.Game.all().filter("winner =", None).filter("tourney_id =", tourney_id)#.run(batch_size=1000)

	for g in activeGames:
		#call WarLight's GameFeed API so that it can tell us if it's finished or not
		apiret = main.hitapi('/API/GameFeed?GameID=' + str(g.wlnetGameID), {})
		data = json.loads(apiret)
		state = data.get('state', 'err')
		
		#logging.info('+++++++++++++++++++++++++++++++++++++++++++')
		#logging.info('data: ' + str(data) + ' ')
		#logging.info('+++++++++++++++++++++++++++++++++++++++++++')
		
		player_data = data.get('players')
		
		#logging.info('player_data: ' + str(player_data) + ' ')
		#logging.info('+++++++++++++++++++++++++++++++++++++++++++')

		if state == 'err': raise Exception("GameFeed API failed.  Message = " + data.get('error', apiret))

		if state == 'Finished':
			#It's finished. Record the winner and save it back.
			winner = findWinner(data,tourney_id)
			logging.info('Identified the winner of game ' + str(g.wlnetGameID) + ' is ' + str(winner))
			loser = findLoser(data,tourney_id)
			logging.info('Identified the loser of game ' + str(g.wlnetGameID) + ' is ' + str(loser))
			g.winner = winner.key().id()
			g.loser = loser.key().id()
			g.dateEnded = datetime.datetime.now()
			g.save()
		else:
			#It's still going.
			logging.info('Game ' + str(g.wlnetGameID) + ' is not finished, state=' + state + ', numTurns=' + data['numberOfTurns']+' ----------------------------------------------------------------------------')
			
			#terminate games that have not started for a long time. 
			if state == 'WaitingForPlayers':
				latest_joining_time = g.dateCreated +datetime.timedelta(0,60*main.getHowLongYouHaveToJoinGames(tourney_id, tourney_clotconfig)) 
				if datetime.datetime.now() > latest_joining_time:
					logging.info('game ' + str(g.wlnetGameID) + ' has taken too long to start')
					logging.info('data: ' + str(data) + ' ')

					#find who Joined and who did not.
					good_player_wlids = []
					bad_player_wlids = []
					logging.info('')
					logging.info('players are:')
					for p in player_data:
						logging.info(p)
						if p['state']=='Playing':                  #only 'Playing' is the acceptable status - anything else means you did not join (ie ignored, or declined). 
							good_player_wlids.append(int(p['id']))
						else:
							bad_player_wlids.append(int(p['id']))
					
					#shuffle randomly in case we need to select winner at random
					random.shuffle(good_player_wlids)
					random.shuffle(bad_player_wlids)
					
					#set the winner and loser
					if len(good_player_wlids)==1 and len(bad_player_wlids)==1:
						logging.info('1 player Joined, the other did not ')
						g.winner = findPlayerID_FromWarlightID(good_player_wlids[0],tourney_id)
						g.loser = findPlayerID_FromWarlightID(bad_player_wlids[0],tourney_id)
					elif len(bad_player_wlids)==2:
						logging.info('neither player Joined, winner/loser will be selected randomly')
						g.winner = findPlayerID_FromWarlightID(bad_player_wlids[0],tourney_id)
						g.loser = findPlayerID_FromWarlightID(bad_player_wlids[1],tourney_id)
					else:
						assert False   #must not occur
					g.dateEnded = datetime.datetime.now()
					
					logging.info('player ' + str(g.winner) + ' won')
					logging.info('player ' + str(g.loser) + ' lost')
					g.save()


#must have called checkInProgressGames() recently !!!!!!
def setResultsOfAllFinishedGames(tourney_id):
	logging.info('')
	logging.info('in setResultsOfAllFinishedGames(tourney_id)')
	
	the_players = players.Player.all().filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	playersDict = dict([(p.key().id(),p) for p in the_players])
	
	finished_games = games.Game.all().filter("winner !=", None).filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	for game in finished_games:
		logging.info('finished game: '+str(game))
		logging.info('game.winner: '+str(game.winner))
		game.winningTeamName = str(playersDict[game.winner])
		logging.info('game.winningTeamName = '+str(game.winningTeamName))
		game.save()

	logging.info('leaving setResultsOfAllFinishedGames()')
	logging.info('')

def findWinner(data,tourney_id):
	"""Simple helper function to return the Player who won the game.  This takes json data returned by the GameFeed 
	API.  We just look for a player with the "won" state and then retrieve their Player instance from the database"""
	winnerInviteToken = filter(lambda p: p['state'] == 'Won', data['players'])[0]["id"]
	return players.Player.all().filter("tourney_id =", tourney_id).filter('inviteToken =', winnerInviteToken)[0]#.run(batch_size=1000)[0]

def findLoser(data,tourney_id):
	"""Simple helper function to return the Player who lost the game.  This takes json data returned by the GameFeed 
	API.  We just look for a player with the "won" state and then retrieve their Player instance from the database"""
	loserInviteToken = filter(lambda p: p['state'] != 'Won', data['players'])[0]["id"]
	return players.Player.all().filter("tourney_id =", tourney_id).filter('inviteToken =', loserInviteToken)[0]#.run(batch_size=1000)[0]

def findPlayerID_FromWarlightID(player_wlid,tourney_id):
	"""Simple helper function"""
	the_player = players.Player.all().filter("tourney_id =", tourney_id).filter('inviteToken =', str(player_wlid)).get()  #using get() because there is only one object
	return the_player.key().id()




