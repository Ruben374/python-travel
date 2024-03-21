# Grupo:P11G05
import requests
from requests.structures import CaseInsensitiveDict
from math import radians, sin, cos, sqrt, atan2
import time
import os
from datetime import datetime

from pprint import pprint
API_KEY = "36c11bb1277b4a1c8fffd8ae9acb9997"

# retorna a moeda no local


def _getCountryCurrency(country):
    currencies = []
    country = country.lower()
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = "https://restcountries.com/v3.1/name/{}".format(
        country)
    try:
        resp = requests.get(url, headers=headers)
        result = resp.json()
        for currency in result[0]["currencies"]:
            currencies.append(currency)
        return currencies
    except Exception as error:
        return False

# retorna a categoria mais comum


def _mostCommunCategories(places):
    categoriesCount = {}
    for place in places:
        categories = place.get('categories', [])
        for categorie in categories:
            if categorie in categoriesCount:
                categoriesCount[categorie] += 1
            else:
                categoriesCount[categorie] = 1

    return max(categoriesCount, key=categoriesCount.get)

# formata a data


def _dateFormatted(_datetime):
    # Converter a string para um objeto datetime
    date_obj = datetime.strptime(_datetime, "%Y-%m-%dT%H:%M:%S.%f%z")
    # Obter hora e minuto
    hours = date_obj.hour
    min = date_obj.minute
    # Formatar a data no formato dd/mm/aa
    date = date_obj.strftime("%d/%m/%y")
    date = str(hours)+":"+str(min)+" "+str(date)
    return date

# ordena as categorias


def _sortCategories(data):
    os.system('cls' if os.name == 'nt' else 'clear')
    end = False
    while not end:

        print("PRETENDE ORDENAR AS ATRAÇÕES?")
        print("1-Por distância")
        print("2-Por país")
        print("3-Não")
        op = input("Escolha a sua opção:")
        if op == "1":
            data['places'] = sorted(data['places'], key=lambda x: x['dist'])
            end = True
        elif op == "2":
            data['places'] = sorted(data['places'], key=lambda x: x['country'])
            end = True
        elif op == "3":
            return data
        else:
            print("Opção invalida, retona ao menu dentro de 3 segundos")
            time.sleep(3)
            os.system('cls' if os.name == 'nt' else 'clear')
    return data

# escreve os dados no ficheiro csv


def _writeOnFile(data):
    data['places'] = sorted(data['places'], key=lambda x: x['dist'])
    with open("data.csv", "w", encoding='utf-8') as file:
        file.write("----------PONTO DE PARTIDA-----------------\n")
        file.write("Nome: {}\n".format(data["info"]["name"]))
        
        file.write("----------ESTATISTICAS-----------------\n")
        file.write("Número de atrações: {}\n".format(
            data["stat"]["attractions"]))
        file.write("Distância média do ponto de partida: {}".format(
            data["stat"]["average_distance"])+" Km\n")
        file.write("Categoria mais comum: {}\n".format(
            data["stat"]["mostCommunCategorie"]))

        i = 1
        for place in data["places"]:
            file.write("----------ATRAÇÃO {}-----------------\n".format(i))
            i += 1
            file.write("Nome: {}\n".format(place["name"]))
            file.write("País: {}\n".format(place["country"]))
            file.write("Localização: {}\n".format(place["location"]))
            file.write("Categorias: {}\n".format(place["categories"]))
            file.write("Distância do ponto de partida: {}".format(
                place["dist"])+" Km\n")
            file.write("Endereço: {}\n".format(place["adress"]))
            file.write("Fuso Horario: {}\n".format(place["timezone"]))
            file.write("Horario atual: {}\n".format(place["time"]))
            file.write("Moedas: {}\n".format( place["currency"]))
    print("Dados exportados no ficheiro data.csv")


# calcula a distancia entre dois pontos, recebendo latitude e longitude de ambos


def _haversine(lat1, lon1, lat2, lon2):
    # Raio médio da Terra em metros
    R = 6371000.0
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Diferença de coordenadas
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # Distância em metros
    distance = R * c
    return distance/100

# faz o levantamento de algumas estatisticas


def _getStat(placeList):
    stat = {}
    sum = 0
    stat["attractions"] = len(placeList)
    for place in placeList:
        sum += place["dist"]
    if len(placeList) > 0:
        stat["average_distance"] = sum/len(placeList)
    stat["mostCommunCategorie"] = _mostCommunCategories(placeList)
    return stat

# retorna o horario atual do ponto de partida


def _getCountryCurrentDatetime(countryCode):
    time = ""
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = "http://worldtimeapi.org/api/timezone/{}".format(
        countryCode)
    try:
        resp = requests.get(url, headers=headers)
        result = resp.json()
        time = result["datetime"]
        return _dateFormatted(time)
    except Exception as error:
        return " "


# Verifica se as categorias inseridas pelo usuario estão dentro do ficheiro de categorias
def _verifyCategories(_categories):
    _categories = _categories.split(",")
    list_categories = []
    _count = 0
    with open("categories.txt") as file:
        for line in file:
            list_categories.append(line.strip())
    for cat in _categories:
        if cat in list_categories:
            _count += 1
    if _count == len(_categories):
        return True
    else:
        return False


# retorna informações sobre o ponto de partida
def _getPlaceDetails(lon, lat):
    headers = CaseInsensitiveDict()
    details = {}
    headers["Accept"] = "application/json"
    url = "https://api.geoapify.com/v1/geocode/reverse?lat={}&lon={}&apiKey={}".format(
        lat, lon, API_KEY)

    resp = requests.get(url, headers=headers)
    result = resp.json()

    details["name"] = result["features"][0]["properties"]["formatted"]

    details["time"] = _getCountryCurrentDatetime(
        result["features"][0]["properties"]["timezone"]["name"])

    details["timezone"] = result["features"][0]["properties"]["timezone"]["name"]

    details["currency"] = _getCountryCurrency(
        result["features"][0]["properties"]["country"])
    return details

# retorna as atrações


def _getPlaces(categories, lon, lat, radius,limit):
    # Configurar cabeçalho
    places = []
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = "https://api.geoapify.com/v2/places?categories={}&filter=circle:{},{},{}&limit={}&apiKey={}".format(
        categories, lon, lat, radius, limit, API_KEY)
    try:
        resp = requests.get(url, headers=headers)
        result = resp.json()
        places = []
        # print(result)
        for place in result["features"]:
            properties = place.get("properties", {})
            nome = properties.get("name")
            if nome:
                dic = {}
                dic["name"] = place["properties"]["name"]
                dic["country"] = place["properties"]["country"]
                dic["location"] = str(
                    place["properties"]["lat"])+" | "+str(place["properties"]["lon"])
                dic["dist"] = _haversine(lat, lon, place["properties"]
                                         ["lat"], place["properties"]["lon"])
                dic["categories"] = place["properties"]["categories"]
                dic["adress"] = place["properties"]["formatted"]
                detail = _getPlaceDetails(lon, lat)
                #print(detail)
                dic["time"] = detail["time"]
                dic["timezone"] = detail["timezone"]
                dic["currency"] = detail["currency"]
                places.append(dic)
        return places
    except Exception as error:
        return []


# retorna um dicionario com as informações que serão apresentadas


def getData(categories, lon, lat, radius,limit):
    print("Carregando os dados...")
    data = {}
    # country details,
    country_Details = _getPlaceDetails(lon, lat)
    # places[]
    places = _getPlaces(categories, lon, lat, radius,limit)
    # stat
    # print(places)
    #print(country_Details)
    if len(places) > 0 and len(country_Details) > 0:
        stat = _getStat(places)
        data["info"] = country_Details
        data["places"] = places
        data["stat"] = stat
        return data
    else:
        return 0
    #os.system('cls' if os.name == 'nt' else 'clear')


def main():
    end = False
    while not end:
        # -----------------Bloco de inputs do usuario---------------------
        location = input(
            "Digite a latitude e a longitude de partida separadas por virgulas: ")
        radius = input("Digite o raio do circulo de busca em Km: ")
        radius = float(radius)*1000
        categories = input("Digite a(as) categorias separadas por virgulas: ")
        limit=input("Degite o limite de atrações que podem ser mostradas: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        location = location.split(",")
        lat = float(location[0])
        lon = float(location[1])
        limit=int(limit)
        categories = categories.strip()
        # ----------------A busca é realizada e os dados são apresentados se as categorias forem validas--------------------
        if _verifyCategories(categories):
            # retorna um dicionario com as informações do ponto de partida, estatisticas e as atrações
            data = getData(categories, lon, lat, radius,limit)
            # Apresenta um menu ao usuario com a possiilidade de ordenar os dados

            if data != 0:
                data = _sortCategories(data)
                os.system('cls' if os.name == 'nt' else 'clear')  # limpa tela
                print("----------PONTO DE PARTIDA-----------------\n")
                print("Nome: ", data["info"]["name"])

                print("\n----------ESTATISTICAS-----------------\n")
                print("Número de atrações: ", data["stat"]["attractions"])
                print("Distância média do ponto de partida: ",
                      data["stat"]["average_distance"], "Km")
                print("Categoria mais comum: ",
                      data["stat"]["mostCommunCategorie"])
                i = 1
                for place in data["places"]:
                    print("\n----------ATRAÇÃO {}-----------------\n".format(i))
                    i += 1
                    print("Nome: ", place["name"])
                    print("País: ", place["country"])
                    print("Localização: ", place["location"])
                    print("Categorias: ", place["categories"])
                    print("Distância do ponto de partida: ",
                          place["dist"], "Km")
                    print("Endereço: ", place["adress"])
                    print("Fuso Horario: ", place["timezone"])
                    print("Horario atual: ", place["time"])
                    print("Moedas: ", place["currency"])
                # exportar os dados para um ficheiro externo
                _writeOnFile(data)
                end = True
            else:
                print("latitude e longitude invalidas, tente novamente em 3 segundos")
                time.sleep(3)
                os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Nada encontrado,verifique a latitude e longitude de partida, tente novamente dentro de 3 segundos")
            time.sleep(3)
            os.system('cls' if os.name == 'nt' else 'clear')


main()
