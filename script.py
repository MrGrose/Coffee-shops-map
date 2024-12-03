import json
import random
from os import getenv

import folium
import requests
from dotenv import load_dotenv
from geopy import distance


def fetch_coordinates(apikey: str, address: str) -> tuple:
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()['response'][
        'GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lon, lat


def get_file_content() -> list:
    data = []
    with open('coffee.json', 'r', encoding='CP1251') as file_content:
        file_contents = json.load(file_content)
        for elem in file_contents:
            data.append({'title': elem['Name'],
                         'distance': get_distance(
                            elem['geoData']['coordinates'][1],
                            elem['geoData']['coordinates'][0]),
                         'latitude': elem['geoData']['coordinates'][0],
                         'longitude': elem['geoData']['coordinates'][1],
                         }
                        )
    return data


def get_distance(longitude: float, latitude: float) -> float:
    return distance.distance((coords[1], coords[0]), (longitude, latitude)).km


def get_user_posts(user: dict) -> float:
    return user['distance']


def save_map(data: list) -> None:
    m = folium.Map([coords[1], coords[0]], zoom_start=16)

    folium.Marker(
        location=[coords[1], coords[0]],
        popup="Your location",
        icon=folium.Icon(icon="info-sign", color='red'),
    ).add_to(m)

    for elem in sorted(data, key=get_user_posts)[:5]:
        folium.Marker(
            location=[elem['longitude'] + random.uniform(-0.0001, 0.0001),
                      elem['latitude'] + random.uniform(-0.0001, 0.0001)],
            tooltip=elem['title'],
            icon=folium.Icon(color='green'),
        ).add_to(m)

    m.save('index.html')


def main() -> None:
    load_dotenv()
    apikey = getenv('API_KEY')
    address = 'Красная площадь'
    global coords
    coords = fetch_coordinates(apikey, address)
    data = get_file_content()
    save_map(data)


if __name__ == '__main__':
    main()
