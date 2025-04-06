from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic
from .forms import RoomForm
# Create your views here.

rooms = [
    {'id': 1, 'name': 'Lets Learn Python'},
    {'id': 2, 'name': 'Competitive Programming is Fun'},
    {'id': 3, 'name': 'Lets Learn Python'}
]

def login_page(request):
    if (request.user.is_authenticated):
        return redirect('home')
    if (request.method == 'POST'):
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request, 'User does not exist')            
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is Incorrect')
    context = {'page': 'login'}
    return render(request, 'base/login_register.html', context)

def register_user(request):
    form = UserCreationForm()
    if (request.method == "POST"):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Access the user right away
            user.username = user.username.lower()
            user.save()
            
    context = {'page':'register', 'form': form}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all();
    context = {'rooms': rooms, 'topics': topics, 'room_count': rooms.count()}

    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room' : room}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    if (request.method == "POST"):
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    form = RoomForm()
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # prefilled form

    if (request.user != room.host):
        return HttpResponse("You are not allowed Here")

    if (request.method == "POST"):
        form = RoomForm(request.POST, instance=room)
        if (form.is_valid()):
            form.save() 
            return redirect('home')       

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if (request.method == "POST"):
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})
