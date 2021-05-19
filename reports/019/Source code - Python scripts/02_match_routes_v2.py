import numpy as np
import requests
from geojson import Point, LineString, Feature, FeatureCollection, dump, load

def route_list_to_string(ref_route_list):
	ref_route_string = ""
	for c in range(0,len(ref_route_list[:-1])):
		this_c = ref_route_list[c]
		next_c = ref_route_list[c+1]
		loc = "{},{};{},{}".format(this_c[0], this_c[1], next_c[0], next_c[1])
		ref_route_string = ref_route_string + loc + ";"
	return ref_route_string[:-1]
	
def match_route(coord_string, year):
	y = year + 3000
	url = "http://127.0.0.1:" + str(y) + "/match/v1/driving/" + coord_string + "?overview=full&geometries=geojson"	# define your OSRM server address here
	r = requests.get(url)
	if r.status_code!= 200:
		print(r.text)
		return {}
	res = r.json()
	geometry = res['matchings'][0]['geometry']
	distance = res['matchings'][0]['distance']
	duration = res['matchings'][0]['duration']
	confidence = res['matchings'][0]['confidence']
	try:
		start_point = [res['tracepoints'][0]['location'][1], res['tracepoints'][0]['location'][0]]
	except:
		start_point = [0,0]
	try:
		end_point = [res['tracepoints'][-1]['location'][1], res['tracepoints'][-1]['location'][0]]
	except:
		end_point = [0,0]
	out = {
		'geometry':geometry,
		'distance':distance,
		'duration':duration,
		'confidence':confidence,
		'start_point':start_point,
		'end_point':end_point
		}
	return out

number_array = range(1001,1501) # insert IDs to match (001_fastest for example)
for number in number_array:	
	number_str = str(number)
	file_string1 = number_str[1:] + '_fastest.geojson'
	features = []
	with open(file_string1) as read_file:
		gj1 = load(read_file)
	fastest_list = []
	#import pdb; pdb.set_trace()
	for i in range(0,6):
		fastest_geometry = gj1['features'][i]['geometry']
		fastest_route = route_list_to_string(gj1['features'][i]['geometry']['coordinates'])
		fastest_time = gj1['features'][i]['properties']['duration']
		fastest_distance = gj1['features'][i]['properties']['distance']
		fastest_list.append(fastest_route)
		features.append(Feature(geometry=fastest_geometry, properties={"year": i+2014, "duration": fastest_time, "distance": fastest_distance}))
	
	year = 2014.2020
	for fastest in fastest_list:
		if year == 2020.2020:
			break
		req_year = match_route(fastest, 2020)
		if req_year == {}:
			continue
		#import pdb; pdb.set_trace()
		year_route_json = req_year['geometry']
		year_route_time = req_year['duration']
		year_route_dist = req_year['distance']
		features.append(Feature(geometry=year_route_json, properties={"year": str(year)+"0", "duration": year_route_time, "distance": year_route_dist}))
		year = year + 1
		
	feature_collection = FeatureCollection(features)
	file_string2 = number_str[1:] + '_routes.geojson'
	with open(file_string2, 'w') as write_file:
		dump(feature_collection, write_file)
	print("File " + number_str[1:] + ' done!')
