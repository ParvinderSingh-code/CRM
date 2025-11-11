from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 

# functions
def login_view(request):
    if request.user.is_authenticated:  
        return redirect('contact:student')
    if request.method == "POST":
        #getting Username and password from my login.html
        username = request.POST.get('username')
        password = request.POST.get('password')
        #cross checking if username enter in login page does exist or not in my user DB
        if not User.objects.filter(username=username).exists():
            messages.warning(request, 'Username does not exist')
            return redirect('accounts:login')
        #if username or password does not match raise error
        user = authenticate(username=username, password=password)
        if user is None:
            messages.warning(request, 'Invalid password')
            return redirect('accounts:login')
        # If all good then proceeding and connecting with contact student navbar
        else:
            login(request, user)
            return redirect("contact:student")
    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    return redirect('accounts:login')
