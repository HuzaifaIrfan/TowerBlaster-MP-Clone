
##############################################################################################################
##############################################################################################################
##############################################################################################################
##########          ###          ####  ##  ##  ##         ###         ########################################
##############  #######  ######  ####  ##  ##  ##  ##########  #####  ########################################
##############  #######  ######  ####  ##  ##  ##         ###         ########################################
##############  #######  ######  ####  ##  ##  ##  ##########  ##   ##########################################
##############  #######          #####        ###         ###  ####   ########################################
##############################################################################################################
##############################################################################################################
##############################################################################################################

##############################################################################################################
##############################################################################################################
##############################################################################################################
###########       ####  ########       ##       ##        ##         ###         #############################
###########  ####  ###  ########  ###  ##  ##########  #####  ##########  #####  #############################
###########      #####  ########       ##       #####  #####         ###         #############################
###########  ####  ###  ########  ###  #######  #####  #####  ##########  ##   ###############################
###########       ####        ##  ###  ##       #####  #####         ###  ####   #############################
##############################################################################################################
##############################################################################################################
##############################################################################################################





print("Tower Blaster Multiplayer Clone Server Made By Huzaifa Irfan")




##############################################################################################################
#########################################  Server Configuration importing  ###################################
##############################################################################################################

from conf import difficulties,port










##############################################################################################################
#########################################  Importing Flask and Socket Confs ##################################
##############################################################################################################


#Importing

import time
import random


from flask import Flask, render_template, session, request,jsonify, send_from_directory, \
copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect



#disabling Logger

async_mode = None
app = Flask(__name__, static_url_path='')
import logging
logss = logging.getLogger('werkzeug')
logss.disabled = True


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)






@app.route('/public/<path:path>')
def send_file(path):
    return send_from_directory('web-client', path)


#starting Route
@app.route('/')
def index():
    return send_from_directory('web-client', "index.html")




##############################################################################################################
############################  User and Games dictionary lists Configurations  ################################
##############################################################################################################


users={}

games={}




##############################################################################################################
#########################################  Used Custom Functions #############################################
##############################################################################################################


####################
# new game generator
####################

def makegame(gotgameid):
    global games
    #generate game
    print("Generating New Game")

    difficulty=games[gotgameid]["difficulty"]

    gen=list(range(difficulty["low"],difficulty["high"]+1))

    each=difficulty["towerheight"]

    #gen for player 1

    p1game=[]

    for i in range(0,each):
        num=random.choice(gen)
        p1game.append(num)
        gen.remove(num)

    games[gotgameid]["game"]["player1"]["game"]=p1game

    games[gotgameid]["game"]["player1"]["getagain"]=difficulty["getagain"]


    #gen for player 2
    p2game=[]

    for i in range(0,each):
        num=random.choice(gen)
        p2game.append(num)
        gen.remove(num)

    games[gotgameid]["game"]["player2"]["game"]=p2game

    games[gotgameid]["game"]["player2"]["getagain"]=difficulty["getagain"]


    games[gotgameid]["game"]["remaining"]=gen

    #print(games[gotgameid])



###############
#####getting random number from list to start game or change running
###############

def getarandom(gotgameid):
    gen=games[gotgameid]["game"]["remaining"]
    num=random.choice(gen)
    gen.remove(num)
    games[gotgameid]["game"]["remaining"]=gen
    return num




##############################
##### To check winner of game
##############################


def chkwinner(gamecont):
    win=1


    for i in range(1,len(gamecont)):
        if(gamecont[i]<gamecont[i-1]):
            win=0


    return win




##############################################################################################################
#########################################  Socket IO  Socket End Points ######################################
##############################################################################################################





####################
##### New User Connection to send username
####################

@socketio.on('Connection')
def Connection(username):
    global users
    userobj={"userid":request.sid,"username":username,"connected":True,"opponent":None,"gameid":None}
    users[request.sid]=userobj
    print(username,"Connected")


####################
##### Send Difficulty list to create Game
####################

@socketio.on('getdifficulties')
def getdifficulties():
    global difficulties
    emit("senddifficulties",difficulties)



####################
##### Creating New Game with difficulty
####################

@socketio.on('creategame')
def creategame(diffid):
    global users
    global games
    global difficulties

    #generate random Game ID
    gameid=str(random.getrandbits(32))

    if (diffid>0 and diffid<=len(difficulties)):
        difficulty=difficulties[diffid-1]
    else:
        difficulty=difficulties[0]

    try:

        users[request.sid]["gameid"]=gameid

        gameobj={"gameid":gameid,"creator":users[request.sid]["username"],"player1":request.sid,"p1again":None,"player2":None,"p2again":None,"game":None,"difficulty":difficulty}
        games[gameid]=gameobj
        print("New Game Created")
        #print(gameobj)
        emit("gamecreated")

    except:
        print("UserName Not created before creating game")



####################
##### Fetch Game list
####################

@socketio.on('fetchgames')
def fetchgames():
    global games
    global users
    freegames=[]
    for game in games.values():
        if users[game["player1"]]["gameid"]==game["gameid"]:
            if game["player2"]==None:
                freegames.append(game)

    emit("showgames",freegames)


####################
##### User Doesn't want to Play again or go to main menu
####################

@socketio.on('noplay')
def noplay():
    global games
    global users

    senderid=request.sid
    opponentid=users[request.sid]["opponent"]
    gotgameid=users[request.sid]["gameid"]

    if not(opponentid ==None):
        users[opponentid]["gameid"]=None
        users[opponentid]["opponent"]=None
        emit("opponentleft",users[request.sid]["username"],room=opponentid)

    users[senderid]["gameid"]=None
    users[senderid]["opponent"]=None

    

    emit("tomainmenu",room=senderid)

    
    # if games[gotgameid]["player1"]==senderid:
    #     games[gotgameid]["p1again"]=False

    # if games[gotgameid]["player2"]==senderid:
    #     games[gotgameid]["p2again"]=False


####################
##### User want to Play again
####################


@socketio.on('playagain')
def playagain():
    global games
    global users
    
    senderid=request.sid
    opponentid=users[request.sid]["opponent"]
    if not (users[request.sid]["gameid"]==None):
        gotgameid=users[request.sid]["gameid"]


        
        if games[gotgameid]["player1"]==senderid:
            games[gotgameid]["p1again"]=True

        if games[gotgameid]["player2"]==senderid:
            games[gotgameid]["p2again"]=True

        # print(games[gotgameid])
        if ((games[gotgameid]["p1again"]==True) and (games[gotgameid]["p2again"]==True)):
            games[gotgameid]["p1again"]=None
            games[gotgameid]["p2again"]=None



            #refresh gameplay
            makegame(gotgameid)
            
            games[gotgameid]["running"]=getarandom(gotgameid)

            #send their own game to players
            #checking users turn

            if(games[gotgameid]["game"]["player1"]["turn"]==True):

                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
            else:
                emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
            


            if(games[gotgameid]["game"]["player2"]["turn"]==True):
        
                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])

            else:

                emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])




####################
##### Get Another Random Number from List 
####################


@socketio.on('getquestion')
def getquestion():
    global games
    global users
    senderid=request.sid
    gotgameid=users[senderid]["gameid"]

    #check senders
    
    if games[gotgameid]["player1"]==senderid:
        #sender is player1
        if games[gotgameid]["game"]["player1"]["turn"]==True:
        
            if games[gotgameid]["game"]["player1"]["getagain"]>0:

                temprunning=games[gotgameid]["running"]
                games[gotgameid]["running"]=getarandom(gotgameid)
                remaining=games[gotgameid]["game"]["remaining"]
                remaining.append(temprunning)
                games[gotgameid]["game"]["remaining"]=remaining

                games[gotgameid]["game"]["player1"]["getagain"]=games[gotgameid]["game"]["player1"]["getagain"]-1

                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])

    
    if games[gotgameid]["player2"]==senderid:
        #sender is player2
        if games[gotgameid]["game"]["player2"]["turn"]==True:
        
            if games[gotgameid]["game"]["player2"]["getagain"]>0:

                temprunning=games[gotgameid]["running"]
                games[gotgameid]["running"]=getarandom(gotgameid)
                remaining=games[gotgameid]["game"]["remaining"]
                remaining.append(temprunning)
                games[gotgameid]["game"]["remaining"]=remaining

                games[gotgameid]["game"]["player2"]["getagain"]=games[gotgameid]["game"]["player2"]["getagain"]-1

                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])










###################################
##### Change The tower Block with Running and change turns and running chk winner
###################################

@socketio.on('changetower')
def changetower(gottowerheight):
    global games
    global users
    senderid=request.sid
    gotgameid=users[senderid]["gameid"]
    

    if games[gotgameid]["player1"]==senderid:
        #sender is player1
        if games[gotgameid]["game"]["player1"]["turn"]==True:
             #change turns
            games[gotgameid]["game"]["player1"]["turn"] = not games[gotgameid]["game"]["player1"]["turn"]
            games[gotgameid]["game"]["player2"]["turn"] = not games[gotgameid]["game"]["player2"]["turn"]

            if( ( gottowerheight>0 ) and ( gottowerheight <= len(games[gotgameid]["game"]["player1"]["game"]) ) ):
                tempitem=games[gotgameid]["game"]["player1"]["game"][gottowerheight-1]
                games[gotgameid]["game"]["player1"]["game"][gottowerheight-1]=games[gotgameid]["running"]
                games[gotgameid]["running"]=tempitem

                #check winner
                win=chkwinner(games[gotgameid]["game"]["player1"]["game"])

                    
                if win==1:
                    games[gotgameid]["game"]["player1"]["score"]=games[gotgameid]["game"]["player1"]["score"]+1
                    emit("winner",{"yourname":games[gotgameid]["game"]["player1"]["username"],"yourgame":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentgame":games[gotgameid]["game"]["player2"]["game"]} ,room=games[gotgameid]["player1"])
                    emit("looser",{"yourname":games[gotgameid]["game"]["player2"]["username"],"yourgame":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentgame":games[gotgameid]["game"]["player1"]["game"]} ,room=games[gotgameid]["player2"])



                else:

                    #emit next turn

                        #checking users turn

                    if(games[gotgameid]["game"]["player1"]["turn"]==True):

                        emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
                    else:
                        emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
                    


                    if(games[gotgameid]["game"]["player2"]["turn"]==True):
                
                        emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])

                    else:

                        emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])





    if games[gotgameid]["player2"]==senderid:
        #sender is player1
        if games[gotgameid]["game"]["player2"]["turn"]==True:
             #change turns
            games[gotgameid]["game"]["player1"]["turn"] = not games[gotgameid]["game"]["player1"]["turn"]
            games[gotgameid]["game"]["player2"]["turn"] = not games[gotgameid]["game"]["player2"]["turn"]

            if( ( gottowerheight>0 ) and ( gottowerheight <= len(games[gotgameid]["game"]["player2"]["game"]) ) ):
                tempitem=games[gotgameid]["game"]["player2"]["game"][gottowerheight-1]
                games[gotgameid]["game"]["player2"]["game"][gottowerheight-1]=games[gotgameid]["running"]
                games[gotgameid]["running"]=tempitem

                #check winner
                win=chkwinner(games[gotgameid]["game"]["player2"]["game"])

                    
                if win==1:
                    games[gotgameid]["game"]["player2"]["score"]=games[gotgameid]["game"]["player2"]["score"]+1
                    emit("winner",{"yourname":games[gotgameid]["game"]["player2"]["username"],"yourgame":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentgame":games[gotgameid]["game"]["player1"]["game"]} ,room=games[gotgameid]["player2"])
                    emit("looser",{"yourname":games[gotgameid]["game"]["player1"]["username"],"yourgame":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentgame":games[gotgameid]["game"]["player2"]["game"]} ,room=games[gotgameid]["player1"])



                else:

                    #emit next turn

                        #checking users turn

                    if(games[gotgameid]["game"]["player1"]["turn"]==True):

                        emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
                    else:
                        emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
                    


                    if(games[gotgameid]["game"]["player2"]["turn"]==True):
                
                        emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])

                    else:

                        emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])







############################################
##### Other User Joining the created game by the game id
############################################

@socketio.on('joingame')
def joingame(gotgameid):
    global games
    global users
    gotgameid=str(gotgameid)
    # print(gotgameid)
    try:

        if games[gotgameid]["player2"]==None:
            games[gotgameid]["player2"]=request.sid
            users[request.sid]["gameid"]=gotgameid
            users[request.sid]["opponent"]=games[gotgameid]["player1"]
            users[games[gotgameid]["player1"]]["opponent"]=games[gotgameid]["player2"]


            # game creation
            games[gotgameid]["game"]={"gameid":gotgameid,"player1":{"username":users[games[gotgameid]["player1"]]["username"],"score":0,"turn":False,"game":[]},"player2":{"username":users[games[gotgameid]["player2"]]["username"],"score":0,"turn":True,"game":[]}}
            makegame(gotgameid)

            games[gotgameid]["running"]=getarandom(gotgameid)

            #send their own game to players


            #checking users turn

            if(games[gotgameid]["game"]["player1"]["turn"]==True):

                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
            else:
                emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player1"]["username"],"yourscore":games[gotgameid]["game"]["player1"]["score"],"game":games[gotgameid]["game"]["player1"]["game"],"opponentname":games[gotgameid]["game"]["player2"]["username"],"opponentscore":games[gotgameid]["game"]["player2"]["score"],"turn":games[gotgameid]["game"]["player1"]["turn"],"getagain":games[gotgameid]["game"]["player1"]["getagain"]}  ,room=games[gotgameid]["player1"])
            


            if(games[gotgameid]["game"]["player2"]["turn"]==True):
        
                emit("loadinggame",{"running":games[gotgameid]["running"],"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])

            else:

                emit("loadinggame",{"running":None,"yourname":games[gotgameid]["game"]["player2"]["username"],"yourscore":games[gotgameid]["game"]["player2"]["score"],"game":games[gotgameid]["game"]["player2"]["game"],"opponentname":games[gotgameid]["game"]["player1"]["username"],"opponentscore":games[gotgameid]["game"]["player1"]["score"],"turn":games[gotgameid]["game"]["player2"]["turn"],"getagain":games[gotgameid]["game"]["player2"]["getagain"]}  ,room=games[gotgameid]["player2"])



        

        else:
            emit("notfree",games[gotgameid]["creator"])
        
    except:
        print("Got Wrong Game ID from Joining User")





####################
#####  User Disconnection
####################


@socketio.on('disconnect')
def disconnected():
    global users
    global games

    try:
        users[request.sid]["connected"]=False
        print(users[request.sid]["username"],"Disconnected")

        opponentid=users[request.sid]["opponent"]
        gameid=users[request.sid]["gameid"]

        if not(gameid == None):
            games[gameid]["player2"]="noone"
        if not(opponentid == None):
            users[opponentid]["gameid"]=None
            users[opponentid]["opponent"]=None
            emit("opponentleft",users[request.sid]["username"],room=opponentid)

    except:
        print("UserName ID not created before Disconnecting")



##############################################################################################################
######################################### Starting Socket IO Server ##########################################
##############################################################################################################

if __name__ == '__main__':
    print("Server started on port "+f"{port}")
    print("Waiting for Players to Connect")
    socketio.run(app,host='0.0.0.0', port=port, debug=False)