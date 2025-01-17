from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password')
        else:
            messages.error(request, 'User does not exist')
    
    context = {'page': page}
    return render(request, 'base/login_registration.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = form.save(commit=False)
                user.username = username
                user.save()
                login(request, user)
                return redirect('login')
        else:
            messages.error(request, 'Form is not valid')
    
    context = {'form': form}
    return render(request, 'base/login_registration.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()[:5]
    total_rooms = Room.objects.all().count()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'total_rooms': total_rooms,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = room.message_set.create(
            user=request.user,
            body=request.POST.get('body')
        )
        message.save()
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    total_rooms = Room.objects.all().count()
    
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'total_rooms': total_rooms,
        'room_messages': room_messages
    }
    return render(request, 'base/user_profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == 'POST':
        topic_name = request.POST.get('room_topic')
        topic, created_at = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('Permission denied!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('room_topic')
        topic, created_at = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        
        return redirect('home')
    
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('Permission denied!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('Permission denied!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=message.room.id)
    
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, 'Form is not valid')
        
        return redirect('user-profile', pk=request.user.id)
    
    context = {'form': form, 'user': user}
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    total_rooms = Room.objects.all().count()
    
    q = request.POST.get('q') if request.POST.get('q') is not None else ''
    topics = Topic.objects.filter(
        Q(name__icontains=q)
    )
    
    context = {'topics': topics, 'total_rooms': total_rooms}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()
    
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)
