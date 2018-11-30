#!/usr/bin/python
# -*- coding: utf-8 -*-
import _thread
import time
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.http import JsonResponse

tokenList = []
a = [1, -1, 0, 0]
b = [0, 0, 1, -1]
status = {}
game = {}
scores = {}
playing = {}
timer = {}
cnt = 0

dr = [
    0,
    -1,
    -1,
    -1,
    0,
    1,
    1,
    1,
    ]
dc = [
    -1,
    -1,
    0,
    1,
    1,
    1,
    0,
    -1,
    ]


def Timer(token):
	while(True):
		timer[token]-=1
		time.sleep(1)

def home(request):
    return render(request, 'userInput.html')


def getToken(request):
	return JsonResponse({'list':tokenList})


def passChance(request):

	token = request.GET['token']
	player = request.GET['player']
	if player == '1':
		status[token] = 5
	else:
		status[token] = 4
	
	return JsonResponse({'token':token})
	
def scoreUpdate(token):
	scores[token] = 0
	global cnt
	cnt = 0
	for i in range(0,8):
		for j in range(0,8):
			if game[token][i*8+j] == '0':
				scores[token]+=1
			if game[token][i*8+j] == '1':
				cnt+=1

def request(request):
	token = request.GET['token']
	chance = request.GET['player'] 
	print(tokenList)
	scoreUpdate(token)
	global cnt
	if status[token] == 6 or status[token] == 7:
		playing[token]-=1
		tokenList.remove(token)
	if playing[token] == 0:
		tokenList.remove(x)
	if (scores[token]+cnt) == 64:
		if chance == '1':
			if scores[token] > cnt:
				status[token] = 6
			else:
				status[token] = 7
		else:
			if scores[token] > cnt:
				status[token] = 7
			else:
				status[token] = 6
	
	if status[token]==2:
		status[token] = 4
		timer[token] = 60
	if scores[token]==0 or timer[token] <= 0 or cnt==0 or status[token] >= 6:
		if status[token] == 4:
			status[token] = 7
		elif status[token] == 5:
			status[token] = 6
		#tokenList.remove(token)
		
	if status[token] == 4:
	    return JsonResponse({'token':token,'table':game[token],'player':chance,'score1':scores[token],'score2':cnt,'status':status[token],'timer1':timer[token],'timer2':'60'})
	elif status[token] == 5:
	    return JsonResponse({'token':token,'table':game[token],'player':chance,'score1':scores[token],'score2':cnt,'status':status[token],'timer1':'60','timer2':timer[token]})
	else:
	    return JsonResponse({'token':token,'table':game[token],'player':chance,'score1':scores[token],'score2':cnt,'status':status[token],'timer1':'60','timer2':'60'})

def newGame(request):
    unique_id = get_random_string(length=5)
    tokenList.append(unique_id)
    board = ""
    for i in range(0,8):
    	for j in range(0,8):
    		if (i==j) and (i==3 or j == 4):
    			board += '0'
    		elif (i==3 and j==4) or (i==4 and j==3):
    			board += '1'
    		else:
    			board += '2'
    game[unique_id] = board
    id = '1'
    token = unique_id
    player = '1'
    playing[token] = 1
    status[token] = 1
    timer[token] = 60
    return  render(request, 'newGame.html', {'token': unique_id,'table':board,'player':"1"})


def verify(request, token):

	if str(token) in tokenList:
		if playing[token] == 2:
			return render(request, 'userInput.html')
		status[token] = 2
		playing[token] = 2
		timer[token] = 60
		_thread.start_new_thread(Timer,(token,))
		return render(request, 'newGame.html', {'token': token,'table':game[token],'player':"2"})
	else:
		return render(request, 'userInput.html')


def update(request):
    global chance
    row = int(request.GET['row'])
    col = int(request.GET['col'])
    token = request.GET['token']
    player = request.GET['player']
    table = list(game[token])
    flip = int(player) - 1
    table[row * 8 + col] = flip
    timer[token] = 60
    
    for i in range(0, 8):
        x = dr[i]
        y = dc[i]
        l = row+x
        r = col+y
        cnt = 0
        while(l>=0 and l<8 and r>=0 and r<8):
        	#print(table[l*8+r])
        	if table[l*8+r] == '2':
        		break
        	if table[l*8+r] == str(flip):
        	    break
        	cnt+=1
        	l+=x
        	r+=y	
        if cnt >= 1 and l>=0 and l<8 and r>=0 and r < 8 and table[l*8+r] == str(flip):
            l = row+x
            r = col+y
            while(l>=0 and l<8 and r>=0 and r<8):
            	if table[l*8+r] == '2':
            		break
            	if table[l*8+r] == str(flip):
            	    break
            	table[l*8+r] = str(flip)
            	l+=x
            	r+=y
                                    
    
    game[token] ="".join([str(i) for i in table])
    status[token]^=1
    scoreUpdate(token)
    global cnt
    if scores[token] == 0 or timer[token] == 0:
    	status[token]+=2
    if cnt == 0:
    	status[token] +=2
    if player == '1':
        return JsonResponse({'table': "".join([str(i) for i in table]), 'player': player,'timer1':timer[token],'timer2':'60','score1':scores[token],'score2':cnt,'status':status[token]})
    else:
        return JsonResponse({'table': "".join([str(i) for i in table]), 'player': player,'timer1':'60','timer2':timer[token],'score1':cnt,'score2':scores[token],'status':status[token]})
	
