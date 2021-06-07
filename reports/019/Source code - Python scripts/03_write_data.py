import geojson
import csv

with open('route_data.csv', mode='w', newline='') as write_file:
	csv_writer = csv.writer(write_file, delimiter=',')
	csv_writer.writerow(['route_id', 'time20', 'time14', 'time15', 'time16', 'time17', 'time18', 'time19', 'dist20', 'dist14', 'dist15', 'dist16', 'dist17', 'dist18', 'dist19'])
	for number in range(1001,1501):
		number_str = str(number)
		file_string1 = './routes/' + number_str[1:] + '_routes.geojson'
		with open(file_string1) as read_file:
			gj1 = geojson.load(read_file)
		time20 = gj1['features'][6]['properties']['duration']
		time14 = gj1['features'][7]['properties']['duration']
		time15 = gj1['features'][8]['properties']['duration']
		time16 = gj1['features'][9]['properties']['duration']
		time17 = gj1['features'][10]['properties']['duration']
		time18 = gj1['features'][11]['properties']['duration']
		time19 = gj1['features'][12]['properties']['duration']
		dist20 = gj1['features'][6]['properties']['distance']
		dist14 = gj1['features'][7]['properties']['distance']
		dist15 = gj1['features'][8]['properties']['distance']
		dist16 = gj1['features'][9]['properties']['distance']
		dist17 = gj1['features'][10]['properties']['distance']
		dist18 = gj1['features'][11]['properties']['distance']
		dist19 = gj1['features'][12]['properties']['distance']
		print(number_str[1:] + " done")
		csv_writer.writerow([number_str[1:], time20, time14, time15, time16, time17, time18, time19, dist20, dist14, dist15, dist16, dist17, dist18, dist19])