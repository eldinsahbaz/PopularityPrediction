import os, sys, glob2, json, time, datetime, os, math, nltk, string, random, librosa, re, scipy,urllib, urllib2, errno, httplib, ssl, youtube_dl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import KFold
from scipy.stats import binned_statistic
from socket import error as socket_error
from bs4 import BeautifulSoup, Comment
from nltk.corpus import stopwords
from sklearn.svm import LinearSVC
from sklearn import linear_model
from collections import Counter
from scipy import linalg as LA
from sklearn.ensemble import *
from dateutil import parser
from sklearn.svm import SVC
from sklearn.dummy import *
from socket import socket
from copy import deepcopy
from sklearn import tree
from ffmpy import FFmpeg
from scipy import signal
import cPickle as pickle
from sklearn import svm
from sys import maxint
from sklearn import *
import numpy as np
from nltk import *
import os.path

with open('Categories.txt', 'rb') as file:
    CategorySet = pickle.loads(file.read())

with open('urls.txt', 'rb') as file:
    URLSet = pickle.loads(file.read())

#http://help.dimsemenov.com/kb/wordpress-royalslider-tutorials/wp-how-to-get-youtube-api-key
API_KEY, regionCode = "****", "US"
maxint, minint = sys.maxint, -sys.maxint-1

#Gather channels
def sourceChannels():
    topChannels = open("topChannels.txt", "w")
    bottomChannels = open("bottomChannels.txt", "w")
    dict1 = dict()
    dict2 = dict()
    Bottom_html = BeautifulSoup(urllib2.urlopen(urllib2.Request("https://socialblade.com/youtube/top/bottom50030d/mostunviewed", headers={'User-Agent' : "Magic Browser"})).read())
    Top_html = BeautifulSoup(urllib2.urlopen(urllib2.Request("https://socialblade.com/youtube/top/5000/mostviewed", headers={'User-Agent' : "Magic Browser"})).read())

    print("-----TOP-----")
    for div in Top_html.findAll('div'):
        yt = div.find('a')
        if yt:
            print(yt)
            if ('youtube/user' in div.find('a')['href']):
                username = (re.sub('\/[a-z]*\/[a-z]*\/', '', div.find('a')['href'])).encode('utf-8')
                print(yt)
                if ' ' in username:
                    username = '+'.join(username.split(' '))
                try:
                    info = json.load(urllib2.urlopen("https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername={0}&key={1}".format(username, API_KEY)))
                    if ('items' in info) and (len(info['items']) > 0) and ('id' in info['items'][0]):
                        #topChannels.write("%s\n" % (info['items'][0]['id']).encode('utf-8'))
                        dict1[username] = (info['items'][0]['id']).encode('utf-8')
                except:
                    pass
            elif ('youtube/channel' in div.find('a')['href']):
                dict1[(div.find('a').contents[0]).encode('utf-8')] = (re.sub('\/[a-z]*\/[a-z]*\/', '', div.find('a')['href'])).encode('utf-8')
                #topChannels.write("%s\n" % ((re.sub('\/[a-z]*\/[a-z]*\/', '', div.find('a')['href'])).encode('utf-8')))

    pickle.dump(dict1, topChannels)
    topChannels.close()

    print("-----BOTTOM-----")
    for div in Bottom_html.findAll('div'):
        yt = div.find('a')
        if yt:
            if ('youtube/user' in div.find('a')['href']) or ('youtube/channel' in div.find('a')['href']):
                username = (re.sub('\/[a-z]*\/[a-z]*\/', '', div.find('a')['href'])).encode('utf-8')
                if not (isEnglish(username) and isEnglish(div.find('a').contents[0])):
                    continue
                print(yt)
                if ' ' in username:
                    username = '+'.join(username.split(' '))
                try:
                    info = json.load(urllib2.urlopen("https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername={0}&key={1}".format(username, API_KEY)))
                    if ('items' in info) and (len(info['items']) > 0) and ('id' in info['items'][0]):
                        dict2[username] = (info['items'][0]['id']).encode('utf-8')
                        #bottomChannels.write("%s\n" % (info['items'][0]['id']).encode('utf-8'))
                except:
                    pass

    pickle.dump(dict2, bottomChannels)

    bottomChannels.close()
    topChannels = dict1
    bottomChannels = dict2
    channels = list()

    for i in range(1,30):
        index = randint(0, len(topChannels))
        samples.append(topChannels[index][1])
        del topChannels[index]

    for i in range(1,60):
        index = randint(0, len(bottomChannels))
        samples.append(bottomChannels[index][1])
        del bottomChannels[index]

    f = open('samples.txt', 'w')
    pickle.dump(samples, f)
    f.close()

    return channels


#Source data from channels
def allCategories(regionCode):
    tags = dict()

    while not tags:
        try:
            url = "https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode={0}&key={1}".format(
                regionCode, API_KEY)
            tags = json.load(urllib2.urlopen(url))
        except urllib2.HTTPError as e:
            print(e)
            time.sleep(30)
        except socket_error as se:
            print(se)
            time.sleep(300)
        except urllib2.URLError, e:
            print(e)
            time.sleep(30)
        except httplib.HTTPException, e:
            print(e)
            time.sleep(30)
        except ssl.SSLError, e:
            print(e)
            time.sleep(30)
        except Exception, e:
            print(e)
            time.sleep(30)
        except:
            print("error")
            time.sleep(30)

    return tags

def getChannelStatistics(channelId):
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={0}&key={1}".format(
        channelId, API_KEY)
    return json.load(urllib2.urlopen(url))

def getVideoIDs(channelId):
    videos = list()

    url = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={0}&key={1}".format(channelId, API_KEY)
    response = json.load(urllib2.urlopen(url))

    if ('items' in response) and (len(response['items']) > 0) and ('contentDetails' in response['items'][0]) and (
        'relatedPlaylists' in response['items'][0]['contentDetails']) and (
        'uploads' in response['items'][0]['contentDetails']['relatedPlaylists']):
        playlistId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=3&playlistId={0}&key={1}".format(
            playlistId, API_KEY)

        response = json.load(urllib2.urlopen(url))

        while True:
            videos.extend(response['items'])

            if not ('nextPageToken' in response):
                break

            response = json.load(urllib2.urlopen(url + ("&pageToken={0}".format(response['nextPageToken']))))

    print("number of videos found: " + str(len(videos)))
    return videos

def getVideo(videoId):
    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.youtube.com/watch?v={0}".format(videoId.encode("ascii"))])

    ydl = youtube_dl.YoutubeDL({'format': 'bestvideo'})

    result = dict()
    with ydl:
        result = ydl.extract_info("https://www.youtube.com/watch?v={0}".format(videoId.encode("ascii")), download=False)

    return result

def getComments(video):
    comments = list()
    response = json.load(urllib2.urlopen("https://www.googleapis.com/youtube/v3/commentThreads?part=snippet%2Creplies&videoId={0}&key={1}".format(video, API_KEY)))

    while True:

        comments.extend(response['items'])

        if not ('nextPageToken' in response):
            break

        print("nextPageToken: " + response['nextPageToken'])
        response = json.load(urllib2.urlopen(
            "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet%2Creplies&pageToken={0}%3D%3D&videoId={1}&key={2}".format(
                response['nextPageToken'], video, API_KEY)))

    return comments

def getMetadata(channelIDs):
    data = dict()
    filePath = "C:/Users/esahbaz/PycharmProjects/getChannels"
    for channelId in channelIDs:
        data[channelId] = dict()
        print("channelId: {0}".format(channelId))

        print("getting channel statistics")
        statistics = dict()

        while not statistics:
            try:
                statistics = getChannelStatistics(channelId)
            except urllib2.HTTPError as e:
                print(e)
                time.sleep(30)
            except socket_error as se:
                print(se)
                time.sleep(300)
            except urllib2.URLError, e:
                print(e)
                time.sleep(30)
            except httplib.HTTPException, e:
                print(e)
                time.sleep(30)
            except ssl.SSLError, e:
                print(e)
                time.sleep(30)
            except Exception, e:
                print(e)
                time.sleep(30)
            except:
                print("error")
                time.sleep(30)

        data[channelId]['statistics'] = statistics
        channelDirectory = filePath + str(channelId) + "/"

        if not os.path.exists(channelDirectory):
            os.makedirs(channelDirectory)
        os.chdir(channelDirectory)

        f = open("statistics.txt", 'w')
        json.dump(data[channelId]['statistics'], f)
        f.close()

        print("getting all videoIds from channel")
        videos = list()

        while not videos:
            try:
                videos = getVideoIDs(channelId)
            except urllib2.HTTPError as e:
                print(e)
                time.sleep(30)
            except socket_error as se:
                print(se)
                time.sleep(300)
            except urllib2.URLError, e:
                print(e)
                time.sleep(30)
            except httplib.HTTPException, e:
                print(e)
                time.sleep(30)
            except ssl.SSLError, e:
                print(e)
                time.sleep(30)
            except Exception, e:
                print(e)
                time.sleep(30)
            except:
                print("error")
                time.sleep(30)

        for video in videos:
            if ('snippet' in video) and ('resourceId' in video['snippet']) and (
                'videoId' in video['snippet']['resourceId']):
                videoId = video['snippet']['resourceId']['videoId']  # video['id']['videoId']
                print("videoId: {0}".format(videoId))

                directory = channelDirectory + str(videoId) + "/"

                if not os.path.exists(directory):
                    os.makedirs(directory)
                os.chdir(directory)

                print("getting video")

                vidInfo = dict()
                times = 0

                while not vidInfo and times < 10:
                    try:
                        times += 1
                        vidInfo = getVideo(videoId)
                    except urllib2.HTTPError as e:
                        print(e)
                        time.sleep(30)
                    except socket_error as se:
                        print(se)
                        time.sleep(300)
                    except urllib2.URLError, e:
                        print(e)
                        time.sleep(30)
                    except httplib.HTTPException, e:
                        print(e)
                        time.sleep(30)
                    except ssl.SSLError, e:
                        print(e)
                        time.sleep(30)
                    except Exception, e:
                        print(e)
                        time.sleep(30)
                    except:
                        print("error")
                        time.sleep(30)

                if times == 10:
                    print("Skipping video: {0}".format(videoId))
                    continue

                data[channelId][videoId] = dict()
                data[channelId][videoId].update(vidInfo)
                print("getting video thumbnail")
                done = False

                while not done:
                    try:
                        if (('snippet' in video) and ('thumbnails' in video['snippet']) and (
                            'high' in video['snippet']['thumbnails']) and (
                            'url' in video['snippet']['thumbnails']['high'])):
                            urllib.urlretrieve(video['snippet']['thumbnails']['high']['url'], "0.jpg")
                        elif ('thumbnail' in vidInfo):
                            urllib.urlretrieve(vidInfo['thumbnail'], "0.jpg")
                        else:
                            break

                        done = True

                    except urllib2.HTTPError as e:
                        print(e)
                        time.sleep(30)
                    except socket_error as se:
                        print(se)
                        time.sleep(300)
                    except urllib2.URLError, e:
                        print(e)
                        time.sleep(30)
                    except httplib.HTTPException, e:
                        print(e)
                        time.sleep(30)
                    except ssl.SSLError, e:
                        print(e)
                        time.sleep(30)
                    except Exception, e:
                        print(e)
                        time.sleep(30)
                    except:
                        print("error")
                        time.sleep(30)

                f = open("data.txt", 'w')
                json.dump(data[channelId][videoId], f)
                f.close()

    return data

def storeToDisk(channelIDs, regionCode):
    print("getting all categories for {0}".format(regionCode))
    f = open("Categories.txt", "w")
    json.dump(allCategories(regionCode), f)
    f.close()

    for channelId in channelIDs:
        data = None

        while not data:
            try:
                data = getMetadata([channelId])
            except urllib2.HTTPError as e:
                print(e)
                time.sleep(30)
            except socket_error as se:
                print(se)
                time.sleep(30)
            except urllib2.URLError, e:
                print(e)
                time.sleep(30)
            except httplib.HTTPException, e:
                print(e)
                time.sleep(30)
            except ssl.SSLError, e:
                print(e)
                time.sleep(30)
            except Exception, e:
                print(e)
                time.sleep(30)
            except:
                print("error")
                time.sleep(30)


#Process sourced data
def compress():
    data, files = dict(), list()
    CollectedData = "/home/esahbaz/eldin/Documents/CollectedData"

    for dirpath, dirnames, filenames in os.walk(CollectedData):
        files.extend([os.path.join(dirpath, f) for f in filenames if f.endswith(".txt")])

    for i in range(len(files)):
        directories = files[i][len(CollectedData)+1:].split('/')
        print(files[i])

        if not (list(set(directories)) == ['']):
            os.chdir(os.path.join(CollectedData, '/'.join(directories[:-1])))

            print(os.path.join(CollectedData, files[i]))
            with open(os.path.join(CollectedData, files[i])) as file: 
                localData = json.loads((file.readlines())[0])
                
                if not (directories[0] in data):
                    data[directories[0]] = dict()

                print(directories)
                data[directories[0]].update({directories[1] : localData})

    file = open("data.txt", 'w')
    json.dump(data, file)
    file.close()

def convert(file):
    newFile = file.replace(os.path.splitext(file)[1], '.wav')
    FFmpeg(inputs={file: None}, outputs={newFile: '-ab 160k -ac 2 -ar 44100 -vn'}).run()
    return newFile

def discretize(numbers, numCuts=10):
    indices = [int(len(numbers)*(x/float(numCuts)))-1 for x in range(1, numCuts+1)]
    temp = sorted(numbers)
    cuts = list()
    cutPairs = list()

    for x in indices[:-1]:
        cuts.append(((temp[x] + temp[x+1])/2))

    for x in range(len(cuts)):
        if x == 0:
            cutPairs.append((minint, cuts[x]))
        elif x == (len(cuts)-1):
            cutPairs.append((cuts[x-1], cuts[x]))
            cutPairs.append((cuts[x], maxint))
        else:
            cutPairs.append((cuts[x-1], cuts[x]))

    return cutPairs

def discretize_train(data, labels, numCuts=10):
    final_cuts = dict()

    for label in labels:
        numbers = list()

        for x in data.keys():
            for y in data[x].keys():
                    numbers.append(data[x][y][label])

        indices = [int(len(numbers)*(x/float(numCuts)))-1 for x in range(1, numCuts+1)]
        numbers.sort()
        cuts = list()
        cutPairs = list()

        for x in indices[:-1]:
            cuts.append(((numbers[x] + numbers[x+1])/2))

        for x in range(len(cuts)):
            if x == 0:
                cutPairs.append((minint, cuts[x]))
            elif x == (len(cuts)-1):
                cutPairs.append((cuts[x-1], cuts[x]))
                cutPairs.append((cuts[x], maxint))
            else:
                cutPairs.append((cuts[x-1], cuts[x]))

        for x in data.keys():
            for y in data[x].keys():
                for z in range(len(cutPairs)):
                    if (data[x][y][label] >= cutPairs[z][0]) and (data[x][y][label] < cutPairs[z][1]):
                        data[x][y][label] = z
                        break

        final_cuts[label] = cutPairs
    return final_cuts

def discretize_test(data, labels, cut_dict):
    for label in labels:
        cutPairs = cut_dict[label]
        for x in data.keys():
            for y in data[x].keys():
                for z in range(len(cutPairs)):
                    if (data[x][y][label] >= cutPairs[z][0]) and (data[x][y][label] < cutPairs[z][1]):
                        data[x][y][label] = z
                        break

def trainSigmoidNorm(data, labels):
    global_data = dict()

    for label in labels:
        numbers = list()

        for x in data.keys():
            for y in data[x].keys():
                    numbers.append(data[x][y][label])

        avg = np.array(numbers).mean()
        std = np.array(numbers).std()
        V = lambda x: ((x-avg)/std)
        num = lambda x: (1-math.exp(-V(x)))
        denom = lambda x: (1+math.exp(-V(x)))

        for x in data.keys():
            for y in data[x].keys():
                data[x][y][label] = (num(data[x][y][label])/denom(data[x][y][label]))

        global_data[label] = (avg, std)
    return global_data

def equalInterval(data, labels):
    for label in labels:
        numbers = list()

        for x in data.keys():
            for y in data[x].keys():
                    numbers.append(data[x][y][label])

        numbers = np.array(numbers)
        hist, bin_edges = np.histogram(numbers, bins=10)
        cutPairs = list()

        for x in range(len(bin_edges)-1):
            cutPairs.append((bin_edges[x], bin_edges[x+1]))

        for x in data.keys():
            for y in data[x].keys():
                for z in range(len(cutPairs)):
                    if (data[x][y][label] >= cutPairs[z][0]) and (data[x][y][label] < cutPairs[z][1]):
                        data[x][y][label] = z
                        break

def compact(data):
    output = list()
    for x in data.keys():
        local = list()
        for y in data[x].keys():
            local.append([k for l,k in sorted(data[x][y].items())])

        output.extend(local)

    return output

def accuracy(output, testLabels):
    return (100*np.count_nonzero(np.array(output) == testLabels)/float(len(testLabels)))

def logTransform(number, base=10):
    if number == 0:
        return 0
    else:
        return math.log(number, base)

def extractURLS(text):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def SymbolTextRatio(text):
    if not text:
        return (0, 0)

    acceptable = list(string.uppercase+string.lowercase)
    characters = ''.join(map(lambda x: x if (x in acceptable) else '', text))
    symbols = ''.join(map(lambda y: y if (not (y in acceptable)) else '', filter(lambda x: not(x == ' '), text)))
    
    return (len(symbols), len(characters))

def LowerUpperRatio(text):
    if not text:
        return (0, 0)

    upper = len(filter(lambda x: x in string.uppercase, list(text)))
    lower = len(filter(lambda x: x in string.lowercase, list(text)))
    return (lower, upper)

def NumberWords(text):
    if not text:
        return 0

    acceptable = list(string.uppercase+string.lowercase)+[' ']
    return len(filter(lambda z: z, filter(lambda y: y in acceptable, ' '.join(filter(lambda x: x, text.split('\n')))).split()))

def filterData(data):
    channels, channelIDs = data.values(), data.keys()
    skipped, completed, total = 0, 0, 0
    filtered = dict()

    for i in range(len(channels)):

        channel = channels[i]
        channelID = channelIDs[i]
        videos = channel.values()
        videoIDs = channel.keys()
        maxDate = list()
        
        for j in range(len(videos)):
        
            video = videos[j]
            videoID = videoIDs[j]

            if not ('statistics.txt' in videoID):
                
                if not (channelID in filtered):
                    filtered[channelID] = dict()

                if not (videoID in filtered[channelID]):
                    if 'entries' in data[channelID][videoID]:

                        for i in range(len(data[channelID][videoID]['entries'])):
                            a = [data[channelID][videoID]['entries'][i]['upload_date'], data[channelID][videoID]['entries'][i]['height'], data[channelID][videoID]['entries'][i]['duration'], data[channelID][videoID]['entries'][i]['view_count'], data[channelID][videoID]['entries'][i]['title'], data[channelID][videoID]['entries'][i]['tags'], data[channelID][videoID]['entries'][i]['description'], data[channelID][videoID]['entries'][i]['categories']] 
                            if not(None in a):
                                try:
                                    uploadDate = data[channelID][videoID]['entries'][i]['upload_date']
                                    maxDate.append(time.mktime((datetime.datetime(year=int(uploadDate[:4]), month=int(uploadDate[4:6]), day=int(uploadDate[6:]))).timetuple()))
                                except:
                                    pass
                    else:
                        a = [data[channelID][videoID]['upload_date'], data[channelID][videoID]['height'], data[channelID][videoID]['duration'], data[channelID][videoID]['view_count'], data[channelID][videoID]['title'], data[channelID][videoID]['tags'], data[channelID][videoID]['description'], data[channelID][videoID]['categories']]
                        if not(None in a):
                            try:
                                uploadDate = data[channelID][videoID]['upload_date']
                                maxDate.append(time.mktime((datetime.datetime(year=int(uploadDate[:4]), month=int(uploadDate[4:6]), day=int(uploadDate[6:]))).timetuple()))
                            except:
                                pass
        maxDate = (max(maxDate) - (time.mktime((datetime.datetime(year=1, month=1, day=31)).timetuple()) - time.mktime((datetime.datetime(year=1, month=1, day=1)).timetuple())))
	
        for j in range(len(videos)):
        
            video = videos[j]
            videoID = videoIDs[j]

            if not ('statistics.txt' in videoID):
                
                if not (channelID in filtered):
                    filtered[channelID] = dict()

                if not (videoID in filtered[channelID]):
                    if 'entries' in data[channelID][videoID]:

                        for i in range(len(data[channelID][videoID]['entries'])):
                            a = [data[channelID][videoID]['entries'][i]['upload_date'], data[channelID][videoID]['entries'][i]['height'], data[channelID][videoID]['entries'][i]['duration'], data[channelID][videoID]['entries'][i]['view_count'], data[channelID][videoID]['entries'][i]['title'], data[channelID][videoID]['entries'][i]['tags'], data[channelID][videoID]['entries'][i]['description'], data[channelID][videoID]['entries'][i]['categories']]
                            uploadDate = data[channelID][videoID]['entries'][i]['upload_date']
                            
                            if not(None in a) and ((time.mktime((datetime.datetime(year=int(uploadDate[:4]), month=int(uploadDate[4:6]), day=int(uploadDate[6:]))).timetuple())) <= maxDate):
                                try:
                                    temp = dict()
                                    temp['duration'] = int(data[channelID][videoID]['entries'][i]['duration'])
                                    temp['video_view_count'] = int(data[channelID][videoID]['entries'][i]['view_count'])
                                    temp['resolution'] = str(data[channelID][videoID]['entries'][i]['height'])
                                    temp['video_title'] = data[channelID][videoID]['entries'][i]['title']
                                    temp['video_description'] = data[channelID][videoID]['entries'][i]['description']
                                    temp['categories'] = data[channelID][videoID]['entries'][i]['categories']
                                    temp['tags'] = data[channelID][videoID]['entries'][i]['tags']
                                    filtered[channelID][data[channelID][videoID]['entries'][i]['id']] = temp
                                    print(channelID + '/' + videoID + '...SAVED')
                                    completed += 1
                                    total += 1
                                except:
                                    skipped += 1
                                    total += 1
                            else:
                                skipped += 1
                                total += 1
                    else:
                        a = [data[channelID][videoID]['upload_date'], data[channelID][videoID]['height'], data[channelID][videoID]['duration'], data[channelID][videoID]['view_count'], data[channelID][videoID]['title'], data[channelID][videoID]['tags'], data[channelID][videoID]['description'], data[channelID][videoID]['categories']]
                        uploadDate = data[channelID][videoID]['upload_date']

                        if not(None in a) and ((time.mktime((datetime.datetime(year=int(uploadDate[:4]), month=int(uploadDate[4:6]), day=int(uploadDate[6:]))).timetuple())) <= maxDate):
                            try:
                                temp = dict()
                                temp['duration'] = int(data[channelID][videoID]['duration'])
                                temp['video_view_count'] = int(data[channelID][videoID]['view_count'])
                                temp['resolution'] = str(data[channelID][videoID]['height'])
                                temp['video_title'] = data[channelID][videoID]['title']
                                temp['video_description'] = data[channelID][videoID]['description']
                                temp['categories'] = data[channelID][videoID]['categories']
                                temp['tags'] = data[channelID][videoID]['tags']
                                filtered[channelID][videoID] = temp
                                print(channelID + '/' + videoID + '...SAVED')
                                completed += 1
                                total += 1
                            except:
                                skipped += 1
                                total += 1
                        else:
                            skipped += 1
                            total += 1

    print('STATISTICS')
    print('skipped: ' + str(skipped)+'/'+str(total))
    print('completed: ' + str(completed)+'/'+str(total) +'\n')

    print('***PROCESSING TEXT***')
    i = 1
    resolutions = list()
    tags = list()

    for x in filtered.keys():
        j=1
        for y in filtered[x].keys():
            print(str(i) + '/' + str(len(filtered.keys())) + ', ' + str(j) + '/' + str(len(filtered[x].keys())))
            resolutions.append(filtered[x][y]['resolution'])
            tags.append(len(filtered[x][y]['tags']))
            j += 1
        i += 1

    resolution_cuts = discretize(numbers=sorted(map(lambda x: int(x), resolutions)))
    tag_cuts = discretize(numbers=sorted(tags))

    i=1
    for x in filtered.keys():
        j=1
        for y in filtered[x].keys():
            print(str(i) + '/' + str(len(filtered.keys())) + ', ' + str(j) + '/' + str(len(filtered[x].keys())))

            for z in range(len(tag_cuts)):
                if (len(filtered[x][y]['tags']) >= tag_cuts[z][0]) and (len(filtered[x][y]['tags']) < tag_cuts[z][1]):
                    filtered[x][y]['tags'] = z
                    break

            for z in range(len(resolution_cuts)):
                if (int(filtered[x][y]['resolution']) >= resolution_cuts[z][0]) and (int(filtered[x][y]['resolution']) < resolution_cuts[z][1]):
                    filtered[x][y]['resolution'] = z
                    break
            
            bit_string = list("0"*len(CategorySet))
            presentCategories = filter(lambda z: z in CategorySet, filtered[x][y]['categories'])
            indices = map(lambda y: CategorySet.index(y), presentCategories)
            missing = map(lambda x: x.split(' '), list(set(filtered[x][y]['categories']) - set(presentCategories)))
            
            for missingSplit in missing:
                for components in missingSplit:
                    try:
                        indices.append(CategorySet.index(components))
                        break
                    except:
                        pass

            for z in indices:
                bit_string[z] = '1'

            filtered[x][y]['categories'] = int(''.join(bit_string), 2)

            bit_string = list("0"*len(URLSet))
            descriptionURLs = extractURLS(filtered[x][y]['video_description'])

            indices = list()
            for url in descriptionURLs:
                for setURL in range(len(URLSet)):
                    if URLSet[setURL] in url:
                        indices.append(setURL)
                        break
            
            for z in indices:
                bit_string[z] = '1'

            filtered[x][y]['URLs'] = int(''.join(bit_string), 2)
            filtered[x][y]['numberURLs'] = len(descriptionURLs)
            
            a = SymbolTextRatio(filtered[x][y]['video_description'])
            b = LowerUpperRatio(filtered[x][y]['video_description'])
            filtered[x][y]['description_symbol'], filtered[x][y]['description_text'] = a[0], a[1]
            filtered[x][y]['description_lower'], filtered[x][y]['description_upper'] = b[0], b[1]
            filtered[x][y]['description_length'] = NumberWords(filtered[x][y]['video_description'])

            a = SymbolTextRatio(filtered[x][y]['video_title'])
            b = LowerUpperRatio(filtered[x][y]['video_title'])
            filtered[x][y]['title_symbol'], filtered[x][y]['title_text'] = a[0], a[1]
            filtered[x][y]['title_lower'], filtered[x][y]['title_upper'] = b[0], b[1]
            filtered[x][y]['title_length'] = NumberWords(filtered[x][y]['video_title'])

            j += 1
        i += 1

    trainSigmoidNorm(data=filtered, labels=['video_view_count', 'description_symbol', 'description_text', 'description_lower', 'description_upper', 'title_symbol', 'title_text', 'title_lower', 'title_upper', 'categories', 'URLs', 'numberURLs', 'description_length', 'title_length', 'duration'])
    discretize_train(data=filtered, labels=['video_view_count', 'description_symbol', 'description_text', 'description_lower', 'description_upper', 'title_symbol', 'title_text', 'title_lower', 'title_upper', 'categories', 'URLs', 'numberURLs', 'description_length', 'title_length', 'duration'])

    for x in filtered.keys():
        for y in filtered[x].keys():
            if 'video_description' in filtered[x][y]:
                del filtered[x][y]['video_description']

            if 'video_title' in filtered[x][y]:
                del filtered[x][y]['video_title']
    '''
    videos = list()
    CollectedData = "/home/esahbaz/eldin/Documents/CollectedData"
    for dirpath, dirnames, filenames in os.walk(CollectedData):
        videos.extend([os.path.join(dirpath, f) for f in filenames if f.endswith(".webm")])
        videos.extend([os.path.join(dirpath, f) for f in filenames if f.endswith(".m4a")])

    for i in range(len(videos)):
        directories = videos[i][len(CollectedData)+1:].split('/')
        print(videos[i])

        if not (list(set(directories)) == ['']):
            try:
                os.chdir(os.path.join(CollectedData, '/'.join(directories[:-1])))
                newFile = convert(videos[i])
                y, sr = librosa.load(newFile)
                os.remove(newFile)
                b, a = signal.butter(4, [0, 44], 'bandpass', analog=True)
                w, h = signal.freqs(b, a)
                mfcc = librosa.feature.mfcc(w)
                eigVals, _ = LA.eig(mfcc)
                eigVals = sorted(eigVals.reshape((1, (eigVals.shape[0]*eigVals.shape[1]))).tolist()[0], reverse=True)            
                saved = [0,0,0,0,0,0,0,0,0,0]
                saved[:len(eigVals)] = eigVals[:10]

                try:
                    filtered[directories[0]][directories[1]]['mfcc'] = saved
                    print([directories[0], directories[1]], 'SUCCESS')
                except:
                    print([directories[0], directories[1]], 'FAIL')
            
                print(videos[i] + "...SUCCESS")
            except:
                print(videos[i] + "...Error: " + str(sys.exc_info()[0]))
        else:
            print(videos[i] + "...SKIPPED")


    print('***REMOVING CHANNELS WITHOUT MFCC DATA***')
    for x in filtered.keys():
        for y in filtered[x].keys():
            if not ('mfcc' in filtered[x][y]):
                del filtered[x][y]
            
            if len(filtered[x]) == 0:
                del filtered[x]
    '''

    print('***SAVING FILTERED DATA***')
    file = open('filtered.txt', 'w')
    json.dump(filtered, file)
    file.close()

    return filtered


#Train classifiers and save the best performing ones
def classify(data):
    accuracies = dict()
    labels = list()
    
    for x in data.keys():
        for y in data[x].keys():
            labels.append(data[x][y]['video_view_count'])
            del data[x][y]['video_view_count']

    data = compact(data)
    labels = np.array(labels)
    
    try:
        accuracies['RandomForest'] = cross_val_score(BaggingClassifier(RandomForestClassifier()), data, labels, cv=10)
    except:
        print('rf failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['LogisticRegression'] = cross_val_score(BaggingClassifier(linear_model.LogisticRegression(C=1e5)), data, labels, cv=10)
    except:
        print('lr failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['SupportVectorMachine'] = cross_val_score(BaggingClassifier(svm.SVC()), data, labels, cv=10)
    except:
        print('svc failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['NaiveBayes'] = cross_val_score(BaggingClassifier(GaussianNB()), data, labels, cv=10)
    except:
        print('nb failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['KNearestNeighbors'] = cross_val_score(BaggingClassifier(KNeighborsClassifier()), data, labels, cv=10)
    except:
        print('knn failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['NeuralNetwork'] = cross_val_score(BaggingClassifier(MLPClassifier()), data, labels, cv=10)
    except:
        print('ann failed: ' + str(sys.exc_info()[0]))

    try:
        accuracies['GradientBoost'] = cross_val_score(BaggingClassifier(GradientBoostingClassifier()), data, labels, cv=10)
    except:
        print('Gradient failed: ' + str(sys.exc_info()[0]))

    try:
        accuracies['AdaBoost'] = cross_val_score(BaggingClassifier(AdaBoostClassifier()), data, labels, cv=10)
    except:
        print('ada failed: ' + str(sys.exc_info()[0]))
    
    try:
        accuracies['Dummy'] = cross_val_score(DummyClassifier(), data, labels, cv=10)
    except:
        print('Dummy failed: ' + str(sys.exc_info()[0]))

    return accuracies, labels

def saveModels(accuracies, labels):
    file = open('distributions.txt', 'wb')
    pickle.dump(labels, file)
    file.close()

    file = open('allModels.txt', 'wb')
    pickle.dump(accuracies, file)
    file.close()

'''
channels = sourceChannels()
storeToDisk(list(set(channels.values())), regionCode)
compress()
'''

start = datetime.datetime.now()
print('READING DATA FROM FILE')
with open("data.txt") as file:
    data = json.loads((file.readlines())[0])

print('***FILTERING DATA***')
data = filterData(data)

print('***CLASSIFYING DATA***')
allModels, distributions = classify(deepcopy(data))

print('***SAVING MODELS***')
saveModels(allModels, distributions)

print('DURATION: ' + str(datetime.datetime.now()-start))
