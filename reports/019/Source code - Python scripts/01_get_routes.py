import numpy as np
import requests
from geojson import Point, LineString, Feature, FeatureCollection, dump

def nearest_road_point(lon, lat, year):
	loc = "{},{}".format(lon, lat)
	y = year + 3000
	url = "http://127.0.0.1:" + str(y) + "/nearest/v1/driving/"	# define your OSRM server address here
	r = requests.get(url + loc)
	if r.status_code!= 200:
		return {}
	res = r.json()
	nearest_point = res['waypoints'][0]['location']
	return nearest_point

def get_route(start_lon, start_lat, end_lon, end_lat, year):
	loc = "{},{};{},{}".format(start_lon, start_lat, end_lon, end_lat)
	y = year + 3000
	url = "http://127.0.0.1:" + str(y) + "/route/v1/driving/"	# define your OSRM server address here
	url2 = "?overview=full&geometries=geojson"
	r = requests.get(url + loc + url2)
	if r.status_code!= 200:
		return {}
	res = r.json()
	geometry = res['routes'][0]['geometry']
	coords = res['routes'][0]['geometry']['coordinates']
	distance = res['routes'][0]['distance']
	duration = res['routes'][0]['duration']
	start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
	end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
	out = {
		'geometry':geometry,
		'coords':coords,
		'distance':distance,
		'duration':duration,
		'start_point':start_point,
		'end_point':end_point
		}
	return out
	
	
# random coords
lons = np.random.uniform(16.22,16.53,2).round(6)
lats = np.random.uniform(48.14,48.28,2).round(6)

start_point = nearest_road_point(lons[0], lats[0], 2020)
end_point = nearest_road_point(lons[1], lats[1], 2020)

features2 = []

for year in range(2014,2021):
	req = get_route(start_point[0], start_point[1], end_point[0], end_point[1], year)
	route_json = req['geometry']
	route_time = req['duration']
	route_dist = req['distance']
	features2.append(Feature(geometry=route_json, properties={"year": year, "duration": route_time, "distance": route_dist}))

feature_collection2 = FeatureCollection(features2)
with open('id_fastest.geojson', 'w') as file:
   dump(feature_collection2, file)