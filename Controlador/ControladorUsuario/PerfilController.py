from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method =='GET':
        return render(request, 'signup.html',{
        'formUser':UserCreationForm,
    })
    else:
        if request.POST['password1']==request.POST['password2']:
            try:
                user=User.objects.create_user(username=request.POST['username'], password=request.POST['password1'], alergias=request.POST['alergia'])
                user.save()

                login(request, user)
                return redirect('perfiles')
            except IntegrityError                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     : 
                return render(request, 'signup.html',{
                        'formUser':UserCreationForm,
                        "error":'usuario ya existe'
                    })        
        else:
            return render(request, 'signup.html',{
                'formUser':UserCreationForm,
                "error":'contraseñas no coinciden'
                })

def perfiles(request):
    users= User.objects.all()
    return render(request,'perfiles.html', {'users': users})

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method=='GET':
        return render(request, 'signin.html',{
        'form':AuthenticationForm
    })
    else:
        user= authenticate(request, username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            return render(request, 'signin.html',{
                'form':AuthenticationForm,
                "error": 'Usuario o contraseña incorrectas'})
        else:
            login(request,user)
            return redirect('perfiles')