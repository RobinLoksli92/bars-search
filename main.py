import json
import requests
import os
import folium
from flask import Flask
from geopy import distance
from functools import partial

NEAREST_BARS_AMOUNT = 5

def open_map(name_of_save_file):
    with open(name_of_save_file) as map_to_watch:
        return map_to_watch.read()

def get_bars_distance(bar_info):
    return bar_info['distance']

def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat

def load_file(json_file):
    with open(json_file,"r", encoding="CP1251") as bars_of_moscow:
        bars_json = bars_of_moscow.read()
        bars = json.loads(bars_json)
    return bars

def compose_new_bars_info(bars):
    bars_info = []
    for bar in bars:
        bar_name = bar['Name']
        bar_geo_data = bar['geoData']
        bar_coordinates = bar_geo_data['coordinates']
        bar_latitude = bar_coordinates[1]
        bar_longitude = bar_coordinates[0]
        bar_coordinates = [bar_latitude, bar_longitude]
        distance_to_bar = (distance.distance(bar_coordinates,coordinates).km)
        bar_info = {
            'distance': distance_to_bar,
            'latitude':  bar_latitude,
            'longitude': bar_longitude,
            'title': bar_name} 
        bars_info.append(bar_info)
    return bars_info

def find_nearest_bars(bars_info):
    sort_for_distance = sorted(bars_info, key=get_bars_distance)
    nearest_bars = sort_for_distance[:NEAREST_BARS_AMOUNT]
    return nearest_bars

def make_markers_on_map(nearest_bars, name_of_save_file):
    my_start_location = folium.Map(
        location=coordinates,
        zoom_start=12,
        tiles='Stamen Terrain')
    tooltip = 'Click me!'
    folium.Marker(coordinates, popup="Me", tooltip=tooltip).add_to(my_start_location) 
    for nearest_bar in nearest_bars:
        nearest_bar_name = nearest_bar['title']
        nearest_bar_latitude = nearest_bar['latitude']
        nearest_bar_longitude = nearest_bar['longitude']
        folium.Marker([nearest_bar_latitude, nearest_bar_longitude], popup=nearest_bar_name, tooltip=tooltip).add_to(my_start_location) 
    my_start_location.save(name_of_save_file)

def show_map_on_site(name_of_save_file):
    app = Flask(__name__)
    app.add_url_rule('/', 'map', partial(open_map, name_of_save_file))
    app.run('0.0.0.0')


if __name__ == '__main__':
    apikey = os.getenv("APIKEY_FOR_GEO")
    coordinates = input('Где вы находитесь ? ')
    coordinates = fetch_coordinates(apikey, coordinates)
    coordinates = [coordinates[1], coordinates[0]]

    json_file = "bars.json"
    bars = load_file(json_file)

    bars_info = compose_new_bars_info(bars)
    nearest_bars = find_nearest_bars(bars_info)

    name_of_save_file = 'index.html'   
    my_start_location = make_markers_on_map(nearest_bars, name_of_save_file)

    show_map_on_site(name_of_save_file)  
