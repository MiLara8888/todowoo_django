from django.db import IntegrityError  # импортированиие ошибки
from django.shortcuts import render, redirect, get_object_or_404  # redirect для перенаправление
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # форма регистрации,форма входа
from django.contrib.auth.models import User  # модель пользователя
from django.contrib.auth import login, logout, authenticate  # аунтефикация
from .forms import TodoForm  # импортировали собственную форму для создания записей
from django.utils import timezone
from .models import Todo
from django.contrib.auth.decorators import login_required  #декоратор доступа только регистрированым пользователям


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'],
                    password=request.POST['password1'])  # создание пользователя(встроенная функция)
                user.save()  # сохранение пользователя в бд
                login(request, user)  # пользователь заходит под своими данными
                return redirect('currenttodoo')

            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': 'Пользователь с таким именем уже существует, пожалуйста задайте другое имя'})

        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Пароли не совпадают'})

@login_required
def createuser(request):
    if request.method == 'GET':
        return render(request, 'todo/create.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)  # создаем пост форму
            newtodo = form.save(commit=False)  # сохраняем данные в бд
            newtodo.user = request.user  # привязка к пользователю
            newtodo.save()  # сохраняем записть пользователя
            return redirect('currenttodoo')  # перенапрявляем
        except ValueError:
            return render(request, 'todo/create.html', {'form': TodoForm(), 'error': 'Переданы неверные данные'})

@login_required
def currenttodoo(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodoo.html', {'todos': todos})

@login_required
def logoutuser(request):  # выход пользователя
    if request.method == 'POST':  # только пост запрос, потому что браузеры прогружают страницы в фоновом режиме обязательно проверяеим
        logout(request)
        return redirect('home')


def loginuser(request):  # вход пользователя
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Неправильно введены данные пользователя'})
        else:
            login(request, user)  # пользователь заходит под своими данными
            return redirect('currenttodoo')

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)  # создаем пост форму
            form.save()
            return redirect('currenttodoo')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'form': TodoForm(), 'error': 'Переданы неверные данные'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodoo')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodoo')

@login_required
def completedtodos(request):         #выполненные функции
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completed.html', {'todos': todos})



