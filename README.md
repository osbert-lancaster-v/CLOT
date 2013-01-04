CLOT stands for Custom Ladder Or Tournament.  It is an extension to the game WarLight located at http://warlight.net. CLOT allows developers to host their own ladders or tournaments in any way they please.

For the official CLOT documentation, see http://wiki.warlight.net/index.php/CLOT

For a guide on how to get started making your own CLOT, see http://wiki.warlight.net/index.php/Getting_Started_with_CLOT


*** info for running the code ***

you can run on google app engine.
you can also run locally (eg for testing).

http://wiki.warlight.net/index.php/CLOT  and 
http://wiki.warlight.net/index.php/Getting_Started_with_CLOT
  has links on how to get this stuff set up.

the site_password is stored in site_password.py  
(you should change it to some other password for your own site)

if you have debug etc on, then the error/debug messages might give info away to users,
eg your site password.  
bear this in mind (though i dont think a CLOT site is a primary target for crackers :)


*** info for understanding/modifying the CLOT code ***

code uses django website stuff and runs on google app engine.
http://www.djangobook.com  is quite good, but very long.


---- code layout ----
main.py contains the ClotConfig class.  this class stores the information about a tournament.
also in main.py are functions to read and modify the ClotConfig objects.

players.py  contains the Player class.  players are specific to any given tourney.  
(ie the same warlight player, if he/she/it is in 3 tourneys here, will have 3 objects, one for each tourney)

games.py  contains the Game class.  also the GamePlayer class.

cron.py contains the function cron.go(), which is called periodically by the appserver.
this function and the ones it calls do 'real things' tothe database - i.e. they creat games, record finished games, etc.



there are 3 tourney types at present.  swiss.   roundrobin.   randommatchup.
i have tried to modularise the code  -  there are only a few places where 
you see the words swiss/roundrobin/randommatchup apart from in their own files
(tournament_swiss.py,  tournament_roundrobin.py, tournament_randommatchup.py).
if you want to create your own tourney type, i suggest that you use these as templates/examples.
create your file tournament_MYTOURNEYTYPE.py and put your new tourney-specific logic in there.
then link into it in the few places elsewhere in the code that you need to (do a search for the word 'swiss' 
and you will see where those places are).


the .html templates are in templates/...

urls.py lists the urls and the associated functions that are called.  
note that the regexps (if any) in the url will be passed to the functions as function arguments.


NOTE   - the code does NOT know/understand games other than 1v1.
if you want to add these, please go ahead  :)  (mainly, you need to modify Game and the code that uses Game)


---- things that confused me ----
(so maybe they might confuse you also)

you are using python PLUS django (for the web stuff) PLUS google apps
IT IS NOT JUST NICE SIMPLE PYTHON.
IT IS NOT JUST NICE SIMPLE DJANGO either (googleapps changes some things from normal django).
if you are making small changes, then just modifying my code will be fairly easy - you can work just in python (almost).

you are using the database, db.
each time someone loads one of your pages, your code is called.  
BUT it is a new instance of your code (this is obvious, i guess :/) so it has to re-load things from the database.
 - so when you modify database stuff, make sure you call save(), else other instances of your code will not know about it.

some/most error messages are nice and clear :)  (particularly, most run-time errors)
others are not (eg 'compile/load-time errors are often unclear)
and others give no error message at all :/  (so tough to find and fix :(
good luck.


---- running code in testing etc ----

i have added extra pages that call the cron fn (also, fizzer added the /testing page)
go to  ..../testcron  to run the function  testcron() that is in testcron.py
go to  ....tourneys/[[tourney id]]/testcron to run the function  testcron_one_tourney() that is in testcron.py
these save you waiting for the cron job to run.  (btw, on my local instance, the cron job never runs for some reason :/)

also, the webpages  /myadmin_tourneys   and    /myadmin_players   give you some info on your code objects.

using logging.info('a logging message')
and also logging.debug('another logging message')
will pass the measages to the terminal (or to the logs files) and so help with debugging.
at the moment, my code has rather too many .info messages, 
but that is because i expect to keep making changes in the future, and so i might still need them.


when you have made big changes to your code, maybe you need to reset the appengine.
locally, you include  --clear_datastore
whilst for the google appengine, you go to eg https://appengine.google.com/dashboard
and go to datastore-admin and reset your database objects there.


---- known issues ----

in the clotconfig form, the default start time is meant to be the current time.
BUT this function only gets evaluated once.  
so later on, your default start time is a long way in the past :(
the correct methods mentioned on eg stackoverflow website do NOT work for us - differences 
of 'pure' django vs googleapps django :(
not a big deal, but annoying.

the swiss tourney for odd number of players (3 players in fact) 
does NOT show the special swiss list of games correctly - the last round is not shown.
i think this is not too big a deal as i *think* it ~only happens for 3 players and 3 rounds.
i will keep an eye on it though.

BIG!!
no way to decide who won by default in cases where games do not start.  fizzer will 
be updating the API to allow me to fix this, in his next warlight release.
currently a winner is nominated at random in these cases. 






