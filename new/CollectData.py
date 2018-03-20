import youtube_dl, random, nltk, json, urllib2, urllib, pycountry, sys, datetime, pytz, os, dateutil.relativedelta, cPickle as pickle

now = datetime.datetime.utcnow()
LIMIT = datetime.datetime(now.year, now.month, now.day) + dateutil.relativedelta.relativedelta(months=-1)
LOWER_TEMP = (LIMIT + dateutil.relativedelta.relativedelta(days=-4)).replace(tzinfo=pytz.UTC).isoformat("T")
UPPER_TEMP = (LIMIT + dateutil.relativedelta.relativedelta(days=4)).replace(tzinfo=pytz.UTC).isoformat("T")
LOWER = LOWER_TEMP[:LOWER_TEMP.find("+")]+"Z"
UPPER = UPPER_TEMP[:UPPER_TEMP.find("+")]+"Z"
keys, apiCounter, VIDEOLANGUAGE, SIZE = [], 0, "en", 3000 #ADD YOUR API KEY(S) TO THE keys LIST
Lexicons, sample, countryCodes, total, sampleRates = list(set(nltk.corpus.words.words())-set(nltk.corpus.stopwords.words())), list(), list(), 0, dict()
good = ['News & Politics', 'Pets & Animals', 'Film & Animation', 'Science & Technology', 'Music', 'Nonprofits & Activism', 'Travel & Events', 'Comedy', 'Howto & Style', 'People & Blogs', 'Sports', 'Entertainment', 'Gaming', 'Education', 'Autos & Vehicles']

def API_KEY():
	global apiCounter
	apiCounter += 1
	return keys[abs(apiCounter-1)%len(keys)]

def getVideo(videoId):
	global sampelRates
	ydl = youtube_dl.YoutubeDL({'format': 'bestvideo'})
	result = dict()
	with ydl:
		result = ydl.extract_info("https://www.youtube.com/watch?v={0}".format(videoId.encode("ascii")), download=False)

	result['DataAPI'] = json.load(urllib2.urlopen("https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics%2CrecordingDetails%2CtopicDetails&id={0}&key={1}".format(videoId, API_KEY())))
	return result

def search(query, categoryID, numResults, language):
	response = json.load(urllib2.urlopen("https://www.googleapis.com/youtube/v3/search?part=snippet&q={0}&relevanceLanguage={1}&safeSearch=none&maxResults={2}&type=video&videoCategoryId={3}&order=viewCount&publishedBefore={4}&publishedAfter={5}&key={6}".format(str(query), str(language), str(numResults), str(categoryID), str(UPPER), str(LOWER), str(API_KEY()))))
	return response

def allCategories():
	Categories, i = dict(), 1

	for country in countryCodes:

		while country not in Categories:
			try:
				url = "https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode={0}&key={1}".format(country, API_KEY())
				Categories[country] = json.load(urllib2.urlopen(url))
			except:
				print("***CATEGORIES ERROR: " + str(sys.exc_info()[0]) + "***")

		print("RETRIEVED: " + str(i) + "/"+ str(len(countryCodes)) + ", witch Country Code: " + str(country))
		i += 1

	cats = set()
	for key, values in Categories.items():
		if ('items' in values):
			for category in values['items']:
				if (('id' in category) and ('snippet' in category) and ('title' in category['snippet'])):
					cats.add((int(category['id'].encode('utf-8')), category['snippet']['title'].encode('utf-8')))

	return sorted(list(cats), key=lambda x: x[0])

def retrieveCategories():
	global good

	print('***GETTING COUNTRY CODES***')
	for country in list(pycountry.countries):
		countryCodes.append(country.alpha_2.encode('utf-8'))

	print('***GET ALL CATEGORIES***')
	return filter(lambda x: x[1] in good, allCategories())

def collectData():
	totalAttempts, IDcount, names, categories = 1, 1, list(), retrieveCategories()

	print('***QUERYING VIDEOS***')
	for ID, NAME in categories:
		print("***Category: " + str(NAME) + "(" + str(IDcount) + "/" + str(len(categories)) + ")***")
		videosForThisCategory, seen, videos = 1, list(), {NAME:dict()}

		while (len(videos[NAME]) < SIZE):
			try:
				query, searchResults  = Lexicons[random.randint(0, len(Lexicons))].encode('utf-8'), 1

				while (query in seen):
					query = Lexicons[random.randint(0, len(Lexicons))].encode('utf-8')

				seen.append(query)
				result = search(query=query, categoryID=ID, numResults=searchResults, language=VIDEOLANGUAGE)

				if (('items' in result) and (len(result['items']) > 0) and ('id' in result['items'][0]) and ('videoId' in result['items'][0]['id'])):
					if (result['items'][0]['id']['videoId'] not in names):

						print("***# Videos Found for " + str(NAME) + ": (" + str(videosForThisCategory)+"/"+str(SIZE)+ ")***")
						videoID = result['items'][0]['id']['videoId'].encode('utf-8')
						videos[NAME][videoID] = [result, getVideo(videoID)]
						videosForThisCategory += 1
						names.append(videoID)

					else:
						print("***STATUS: Already Exists, TOTAL ATTEMPTS: " + str(totalAttempts) + ", CATEGORY: " + str(NAME) + ", CATEGORY PROGRESS: (" + str(IDcount) + "/" + str(len(categories)) + "), VIDEOS COLLECTED: (" + str(videosForThisCategory)+"/"+str(SIZE)+ ")***")

				else:
					print("***STATUS: Empty Result, TOTAL ATTEMPTS: " + str(totalAttempts) + ", CATEGORY: " + str(NAME) + ", CATEGORY PROGRESS: (" + str(IDcount) + "/" + str(len(categories)) + "), VIDEOS COLLECTED: (" + str(videosForThisCategory)+"/"+str(SIZE)+ ")***")

			except:
				print("***MAIN ERROR: " + str(sys.exc_info()[0]) + ", CATEGORY: " + str(NAME) + ", CATEGORY PROGRESS: (" + str(IDcount) + "/" + str(len(categories)) + "), VIDEOS COLLECTED: (" + str(videosForThisCategory)+"/"+str(SIZE)+ ")***")

			totalAttempts += 1

		IDcount += 1
		print('***SAVING DATA :: {0}.txt***'.format(str(NAME)))
		with open('{0}.txt'.format(str(NAME)), 'wb') as file:
			pickle.dump(videos, file)

	with open('names.txt', 'wb') as file:
		pickle.dump(names, file)

def distillData():
	files = map(lambda x: x+'.txt', good)

	for file in files:
		with open(f, 'rb') as f:
			videos.update(pickle.loads(f.read()))

	with open('videos.txt', 'wb') as f:
		pickle.dump(videos, f)

collectData()
distillData()
