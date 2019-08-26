from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.safestring import mark_safe
from django.db import transaction

from random import randint
from drawbud.forms import *
from drawbud.models import *

import re
import base64
from django.core.files.base import ContentFile


def login_action(request):
	context = {}

	if request.method == 'GET':
		context['form'] = LoginForm(initial={'username':''})
		return render(request, 'drawbud/login.html', context)
	
	# get the field from request.POST
	form = LoginForm(request.POST)
	context['form'] = form

	# validate
	if not form.is_valid():
		return render(request, 'drawbud/login.html', context)
	
	# get the user object
	# using the cleaned_data (validated)
	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])
	
	# save the user in the session
	login(request, user)
	# using reverse to get the url based on the tag
	# redirect to the url with name global
	return redirect(reverse('lobby'))

def register_action(request):
	context = {}

	if request.method == 'GET':
		context['form'] = RegisterForm()
		return render(request, 'drawbud/register.html', context)

	form = RegisterForm(request.POST)
	context['form'] = form

	if not form.is_valid():
		return render(request, 'drawbud/register.html', context)

	# create a new user object and login
	# using the cleaned_data (validated)
	new_user = User.objects.create_user(username=form.cleaned_data['username'],
										password=form.cleaned_data['password'],
										email=form.cleaned_data['email'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
	# save the change
	profile = Profile.objects.create(user=new_user)
	new_user.save()
	profile.save()
	
	# get the user object from database
	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	login(request, new_user)
	return redirect(reverse('lobby'))

@login_required
def lobby(request):
	context = {}
	rooms = Room.objects.filter(start_game=False)
	context['rooms'] = rooms
	return render(request, 'drawbud/home.html',context)
	
@login_required
def tutorial(request):
	return render(request, "drawbud/tutorial.html", {})

@login_required
def save_image(request):
	print("*************")
	print(request)
	return HttpResponse()


@login_required
def myprofile_action(request):

	context = {}
	if request.method == 'GET':
		
		context['form'] = ItemForm()
		context['items'] = Profile.objects.filter(user=request.user)
		context['drawings'] = Drawing.objects.filter(owner=request.user)
		return render(request, 'drawbud/myprofile.html', context)

	
	new_item = request.user.profile
	
	form = ItemForm(request.POST, request.FILES, instance=new_item)
	
	if not form.is_valid():
		context['form'] = form
	else:
		try:
			new_item.content_type = form.cleaned_data['profile_picture'].content_type
		except AttributeError:
			pass

		form.save()
		context['message'] = 'Item #{0} saved.'.format(new_item.id)
		context['form'] = ItemForm()
	
	if Profile.objects.filter(user=request.user).exists():
		context['items'] = Profile.objects.filter(user=request.user)

	if Drawing.objects.filter(owner=request.user).exists():
		context['drawings'] = Drawing.objects.filter(owner=request.user)
	return render(request, 'drawbud/myprofile.html', context)


@login_required
def getphoto_action(request, id):
	item = get_object_or_404(Profile, id=id)

	if not item.profile_picture:
		raise Http404
	return HttpResponse(item.profile_picture, content_type=item.content_type)

@login_required
def getdrawing_action(request, id):
	item = get_object_or_404(Drawing, id=id)

	if not item.image:
		raise Http404
	return HttpResponse(item.image, content_type=item.content_type)

@login_required 
def logout_action(request):
	logout(request)
	return redirect(reverse('login'))

@login_required
def room_action(request):
    context = {}
    form = RoomForm(request.POST)
    context['form'] = form

    
    if not form.is_valid():
        context['rooms'] = Room.objects.filter(start_game=False)
        context['error_message'] = "Room name already taken" 
        return render(request, 'drawbud/home.html', context)
        
        
    # check if the object already exist   
    if not Room.objects.filter(owner=request.user).exists():
        new_room = Room.objects.create(owner = request.user,
                                       room_name=form.cleaned_data['room_name'],
                                       max_player_number=form.cleaned_data['max_player_number'],
                                       curr_player_number=1,
                                       description=form.cleaned_data['description'],
                                       start_game=False,
                                       word='')
        new_room.save()
    else:
        context['rooms'] = Room.objects.filter(start_game=False)
        context['error_message'] = "Room already exists" 
        return render(request, 'drawbud/home.html', context)
        

    if not Player.objects.filter(username=request.user.username).exists():
        new_player = Player.objects.create(username=request.user.username,
                                           room_name=form.cleaned_data['room_name'])
        new_player.save()
    else:
        context['rooms'] = Room.objects.filter(start_game=False)
        context['error_message'] = "Player already exists" 
        return render(request, 'drawbud/home.html', context)
        

    return HttpResponseRedirect('/get_room/%s' % new_room.room_name)

@login_required
def getroom_action(request, room_name):

    context = {}
    
    # new players join
    if request.method == 'POST':
        # the user is not in other room currently
        if not Player.objects.filter(username=request.user.username).exists(): 
            with transaction.atomic():
                selected_room = Room.objects.select_for_update().filter(room_name=room_name)
                if selected_room.exists():
                    selected_room = selected_room[0]
                    if (selected_room.curr_player_number + 1) > selected_room.max_player_number:
                        context['rooms'] = Room.objects.filter(start_game=False)
                        context['error_message'] = "Player exceeds maximum number of players" 
                        return render(request, 'drawbud/home.html', context)
                        
                    # cannot join a already start game
                    elif selected_room.start_game:
                        context['rooms'] = Room.objects.filter(start_game=False)
                        context['error_message'] = "The game has already started" 
                        return render(request, 'drawbud/home.html', context)
                        
                    else:
                        selected_room.curr_player_number = selected_room.curr_player_number + 1
                        selected_room.save()
            new_player = Player.objects.create(username=request.user.username,
                                           room_name=room_name)
            new_player.save()

        else:
            
            context['error_message'] = "You are already in a Room" 
            rooms = Room.objects.filter(start_game=False)
            context['rooms'] = rooms
            return render(request, 'drawbud/home.html', context)
            
    #need to check whether the room exist
    if not Room.objects.filter(room_name=room_name).exists():
        
        context['error_message'] = "Room doesn't exists" 
        rooms = Room.objects.filter(start_game=False)
        context['rooms'] = rooms
        return render(request, 'drawbud/home.html', context)
        
    context['items'] = Room.objects.get(room_name=room_name)
    context['players'] = Player.objects.filter(room_name=room_name)
    curr_user = Player.objects.filter(username=request.user.username)
    if not context['players'].exists() or not curr_user.exists():
        
        context['error_message'] = "Player doesn't exist"
        rooms = Room.objects.filter(start_game=False)
        context['rooms'] = rooms
        return render(request, 'drawbud/home.html', context)
        
    return render(request, 'drawbud/room.html', context)

    
@login_required
def remove(request, delete_user):
    if request.method == 'POST':
        player = Player.objects.filter(username=delete_user)
        if player.exists():
            player = player[0]
            # decrease the number of players in the room
            with transaction.atomic():
                room_to_leave = Room.objects.select_for_update().filter(room_name=player.room_name)
                if room_to_leave.exists():
                    room_to_leave = room_to_leave[0]
                    room_to_leave.curr_player_number = room_to_leave.curr_player_number - 1
                    if room_to_leave.curr_player_number <= 0 or delete_user == room_to_leave.owner.username:
                        room_to_leave.delete()
                    elif room_to_leave.start_game and room_to_leave.curr_player_number == 1:
                        room_to_leave.delete()
                    else:
                        room_to_leave.save()

            # delete user
            player.delete()
    return HttpResponse()

@login_required
def leave_to_lobby(request, delete_user):
    # wait until the player objects has been deleted
    while(Player.objects.filter(username=delete_user).exists()):
        continue
    return redirect(reverse('lobby'))

@login_required
def startRoom(request, room_name):
    if request.method == 'POST':
        with transaction.atomic():
            room = Room.objects.select_for_update().filter(room_name=room_name)
            if room.exists():
                room = room[0]
                room.start_game = True
                room.save()
    return HttpResponse()

@login_required
def getVoc(request, room_name):
    if request.method == 'POST':
        with transaction.atomic():
            room = Room.objects.select_for_update().filter(room_name=room_name)
            if room.exists():
                room = room[0] 
                room.word = getWord()
                room.save()
                return HttpResponse(room.word)
    return Http404

def getWord():
	wordlist = ['dog', 'cat', 'flower', 'apple', 'grape', 'whale', 'elephant', 
                'lion', 'book', 'piano', 'violin', 'guitar']
	randomIndex = randint(0, len(wordlist) - 1)
	return wordlist[randomIndex]

@login_required
def checkAns(request):
    if request.method == 'GET' and 'room_name' in request.GET:
        correct = False
        with transaction.atomic():
            room = Room.objects.select_for_update().filter(room_name=request.GET['room_name'])
            if room.exists():
                room = room[0]
                if 'ans' in request.GET and request.GET['ans'].lower() == room.word:
                    room.word = 'needsanewvocabulary'
                    room.save()
                    correct = True
        if correct:
            player_profile = Profile.objects.get(user=request.user)
            player_profile.score += 3
            player_profile.save()
            return HttpResponse('correct')

    return HttpResponse('wrong')



@login_required
def uploadImage(request):
	if request.method == 'POST':
		
		format, imgstr = request.POST['imgBase64'].split(';base64,')
		ext = format.split('/')[-1]
		data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
		new_image = Drawing.objects.create(owner=request.user, 
										image=data, text=request.POST['word'])

		try:
			new_image.content_type = 'image/*'
		except AttributeError:
			pass

		return HttpResponse('saved')
	return HttpResponse('ERROR')
	
