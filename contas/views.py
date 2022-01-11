from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth import get_user_model


User = get_user_model()

def login(request):
    """ Caso esteja logado redireciona a dashboard """
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')

    """ Realiza login do usuario """
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if email == "" or password == "":
            messages.error(request, "Campos email e senha não podem ficar em branco!")
            return redirect('login')
        user = auth.authenticate(request, username=email, password=password)

        if user is not None:
            auth.login(request, user)
            proxima_pagina = request.POST.get('next')
            if proxima_pagina:
                return redirect(proxima_pagina)
            return redirect('dashboard')
        else:
            messages.error(request, "Email/Senha estão incorretos")
            return render(request, 'contas/login.html')

    return render(request, 'contas/login.html')


def logout(request):
    """ Realiza logout do usuário """
    auth.logout(request)
    return redirect('login')
