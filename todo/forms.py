from django.forms import ModelForm   #собственная форма для создания записей
from .models import Todo

class TodoForm(ModelForm):
    class Meta():
        model=Todo
        fields=['title','memo','important']
