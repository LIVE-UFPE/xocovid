import json
import random
from django.shortcuts import render
from django.http import HttpResponse

"""
! Funcionamento das views

Views nada mais é que um módulo python que agrupa um conjunto de ações.
views em django são divididas em dois tipos: views baseadas em FUNCTION e views baseadas em CLASS

* Function based View
views baseadas em funções sao feitas usando uma função em python:
    1. função recebe como argumento um objeto HttpRequest
    2. função retorna um objeto HttpResponse

são divididas em 4 estratégias básicas (CRUD):
? Create // Retrieve // Update // Delete
CRUD é a base de qualquer framework

! Só que tem mais um detalhe!!!
para acessar essa função, devemos especificar uma rota através do sistema de rotas do Django.
"""


# ? index é uma function view. uma função que retorna a view requisitada
def index(request): # ? request é um HttpResponse
    # return HttpResponse("teste complexo")

    names = ("bob", "dan", "jack", "lizzy", "susan")

    items = []
    for i in range(100):
        items.append({
            "name": random.choice(names),
            "age": random.randint(20,80),
            "url": "https://example.com",
        })


    context = {}
    context["items_json"] = json.dumps(items)

    # ? toda function view retorna um HttpResponse
    return render(request, 'index.html', context)
    """ Por hora, ele passa dados por um items_json, mas só foram usados no exemplo de integração 
        com Vue """