# -*- coding: utf-8 -*-
from flask import Flask, request
import requests
import json
from threading import Thread
import random
import sys
import time

url = "http://172.17.3.193:8000/"
app = Flask(__name__)

liste = []


def renvoie(id):
    compteur = 0
    global liste
    while len(liste) - 10 > 0:
        data = {
            "command": "sorted",
            "data": liste[:10],
            "id": id,
            "order": compteur,
            "last": False,
            "length": 10
        }
        print("échantillon")
        print(liste[:10])
        requests.post(url, json=data)
        liste = liste[10:]  # on reinitialise les rang de la liste triée
        compteur = compteur + 1
    data = {
        "command": "sorted",
        "data": liste,
        "id": id,
        "order": compteur + 1,
        "last": True,
        "length": len(liste)
    }
    print("échantillon final")
    print(liste)
    requests.post(url, json=data)
    liste[:] = []


def partition(tab, little, big):
    i = (little - 1)  # index of smaller element
    pivot = tab[big]  # pivot

    for j in range(little, big):

        # Positionning for the sharding of the liste
        if tab[j] <= pivot:
            # increment index of smaller element
            i = i + 1
            tab[i], tab[j] = tab[j], tab[i]

    tab[i + 1], tab[big] = tab[big], tab[i + 1]
    return (i + 1)


def quicksort(tab, little, big, id, liste):
    if little < big:
        pi = partition(tab, little, big)
        thread1 = Thread(target=quicksortfils, args=(tab, little, pi - 1, id, liste), daemon=True)
        thread1.start()
        thread2 = Thread(target=quicksortfils, args=(tab, pi + 1, big, id, liste), daemon=True)
        thread2.start()
        thread2.join()
        thread1.join()
    renvoie(id)


def quicksortfils(tab, little, big, id, liste):
    if little < big:
        pi = partition(tab, little, big)
        thread1 = Thread(target=quicksortfils, args=(tab, little, pi - 1, id, liste), daemon=True)
        thread1.start()
        thread2 = Thread(target=quicksortfils, args=(tab, pi + 1, big, id, liste), daemon=True)
        thread2.start()
        thread2.join()
        thread1.join()


@app.route('/', methods=['GET', 'POST'])
def index():
    global liste
    d = request.json
    RESULT = dict(d)
    result = {'ping': 'pong'}

    # Partie pour le ping
    if RESULT['command'] == "ping":
        print("ping received")
        return (result)



    # Partie pour le sample
    elif RESULT['command'] == "sample":
        print("sample recieved")
        table = random.sample(range(RESULT['begin'], RESULT['end']), RESULT['size'])
        result = {'sample': table}
        return result




    # Partie pour le sort
    elif RESULT['command'] == "sort":
        print("sort received")
        if RESULT['last'] == True:
            liste = liste + RESULT['data']
            size = len(liste) - 1
            Thread(target=quicksort, args=(liste, 0, size, RESULT['id'], liste), daemon=True).start()
            # we start the thread here
        else:
            liste = liste + RESULT['data']
        return '', 200


if __name__ == "__main__":
    data = {"command": "connect",
            "name": "Frederic Chopin",
            "port": 5000}
    try:
        requests.post(url, json=data)
    except:
        print("le serveur est down")
    app.run(host='0.0.0.0', port='5000', debug='true')

###fin du main pour le thread
