from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.http import HttpResponse



# rooms=[{'id':1, 'name':' Frontend Developers'},
#        {'id':2, 'name':' Backend Developers'},
#        {'id':3, 'name':' Hello Developers'}]



def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home') # this is used when user is already loged in but manually go to login url to login automattically he come to home page no need to login again


    if request.method=='POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request, "User Not Exit.")

        user=authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Username Or Password doesn't Exit.")

    context={'page':page}
    return render(request,'login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form=MyUserCreationForm()

    if request.method == 'POST':
        form=MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)# commit here to avoid storing data to database before modifying user and then we can store it by using save method again
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
    else:
        messages.error(request,'An error occured during registration')
    return render(request,'login_register.html', {'form':form})

def home(request):
    q= request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms= Room.objects.filter(Q(topic__name__icontains=q) |
                               Q(name__icontains=q)  |
                               Q(description__icontains=q))  # if u want to search by topic or room or user we can  use Q from django

    topics=Topic.objects.all()[0:5]
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request,'home.html', context)

def room(request,pk):
    room=None
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all()
    participants=room.participants.all()
    # unique_participants = list({message.user for message in room_messages})
    # unique_participants_count = room_messages.values('user').distinct().count()
    count=len(Message.objects.all())


    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        room.participants.add(request.user)
        return redirect('room', pk=room.id) # here pk used in redirect to avoid reload error

    return render(request,'room.html',{'room':room, 'room_messages':room_messages, 'participants':participants, 'count':count})

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'profile.html', context)



@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    topics =Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context={'form': form, 'topics':topics}
    return render(request, 'room_form.html', context)

# def home(request):
#     context={'rooms':rooms}
#     return render(request,'home.html',context)


@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics =Topic.objects.all()
    if request.user != room.host:
            return HttpResponse('You are not allowed here!!')
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get('name')
        room.topic=topic
        room.desrciption=request.POST.get('desrciption')
        room.save()
        return redirect('home')
    context={'form':form, 'topics':topics, 'room':room}
    return render(request,'room_form.html',context)



@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)

    if request.user!=room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'delete.html',{'obj':room})



@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)


    if request.user!=message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'delete.html',{'obj':message.body})



@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'update-user.html', {'form': form})

def topicsPage(request):
    q= request.GET.get('q') if request.GET.get('q') !=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'topics.html', {'topics' : topics})


def activityPage(request):
    room_messages=Message.objects.all()
    return render(request,'activity.html',{'room_messages':room_messages})