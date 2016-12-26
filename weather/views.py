from django.shortcuts import render
from django.contrib import messages

# Create your views here.
from datetime import timedelta, date , datetime
import json

try:
	import urllib.request as urllib2
except ImportError:
	import urllib2

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def getReading(single_date,place,parameter,timeinterval):
	x = []
	y = []
	place = urllib2.quote(place)

	dateformat = "".join(single_date.strftime("%Y-%m-%d").split("-"))
	api_key = '0af22b0fc86c18ec'
	makeurl = 'http://api.wunderground.com/api/'+api_key+'/history_'+dateformat+'/q/CA/'+place+'.json'
	print(makeurl)

	f = urllib2.urlopen(makeurl)
	json_string = f.read()
	parsed_json = json.loads(json_string.decode())
	if 'history' not in parsed_json:
		return x , y

	#print("coming here")
	observations = parsed_json['history']['observations']

	if timeinterval == '' and len(observations) > 1:
		t1 = observations[0]['date']['hour'] + ":" + observations[0]['date']['min']
		t2 = observations[1]['date']['hour'] + ":" + observations[1]['date']['min']
		FMT = '%H:%M'
		tdelta = datetime.strptime(t2, FMT) - datetime.strptime(t1, FMT)
		d = datetime(1,1,1) + tdelta 
		timeinterval =  str(d.day-1) + ":" + str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)

	for observation in observations:
		x.append(observation['date']['pretty'])
		y.append(observation[parameter])

	return x , y ,timeinterval

def homepage(request):
	x_axis = []
	y_axis = []
	unitscale = 'imperial'
	place = ''
	sdate = ''
	edate = ''
	timeinterval = ''
	parameter = 'dew'
	if request.method == "POST":
		cd = request.POST
		#print(cd["place"],cd["parameter"],cd["start_date"],cd["end_date"])
		sdate = cd["start_date"].split("/")
		start_date = date(int(sdate[2]),int(sdate[0]),int(sdate[1]))
		edate = cd["end_date"].split("/")
		end_date = date(int(edate[2]),int(edate[0]),int(edate[1]))

		place = cd['place'].split(",")[0]
		parameter = cd["parameter"]
		unitscale = cd['unitscale']
		for single_date in daterange(start_date, end_date):
			x , y , timeinterval = getReading(single_date,place,parameter,timeinterval)
			if not x or not y:
				messages.info(request, 'No data found for this city. Try a different name of your city.')
				break
			x_axis = x_axis + x
			y_axis = y_axis + y

		sdate = cd["start_date"]
		edate = cd["end_date"]
	z = zip(x_axis,y_axis)
	return render(request,'weather/home.html',{'x' : x_axis , 'y' : y_axis ,'z' :z , 'unitscale' : unitscale,'place' : place,'sdate' : sdate,'edate' :edate , 'parameter' : parameter , 'timeinterval' : timeinterval})
