import json
import requests
import string
import re
import urllib
import datetime

def hangulSyllableFinder(cho,jung,jong):
    return chr(0xAC00 + 21*28*cho + 28*jung+jong)

def crawler(event,context):
	hanSyl = []
	for cho in range(0, 19):
		for jung in range(0, 21):
			for jong in range(0, 28):
				hanSyl.append(hangulSyllableFinder(cho, jung, jong))
	today = datetime.date.today()
	client_id = "_xkzhN_KZRgp48B3EetB"
	client_secret = "qfkFS_0oVS"
	cleanr = re.compile('<.*?>')
	for delta in range(7, 0, -1):
		other = today - datetime.timedelta(delta)
		otherStr = '%04d%02d%02d' % (other.year, other.month, other.day)
		for ind, char in enumerate(hanSyl + [i for i in string.ascii_lowercase]):
			try:
				encText = urllib.parse.quote(char)
				encDate = urllib.parse.quote(otherStr)
				url = "https://openapi.naver.com/v1/search/book.json?query=" + encText + '&d_dafr=' + encDate + '&display=100'  # json 결과
				request = urllib.request.Request(url)
				request.add_header("X-Naver-Client-Id", client_id)
				request.add_header("X-Naver-Client-Secret", client_secret)
				response = urllib.request.urlopen(request)
				rescode = response.getcode()
				parsed = ''
				if (rescode == 200):
					response_body = response.read()
					parsed = response_body
				else:
					print("Error Code:" + rescode)
				parsedData = json.loads(parsed)
				for i in range(len(parsedData['items'])):
					item = parsedData['items'][i]
					item['title'] = re.sub(cleanr, '', item['title'])
					title = item['title']
					author = item['author']
					publisher = item['publisher']
					isbn = item['isbn']
					pubdate = item['pubdate']
					description = item['description']
					image = item['image']
					try:
						r = requests.post('http://3.16.58.104:5000/books/importData', data={
							'title': title,
							'author': author,
							'isbn': isbn,
							'description': description,
							'publisher': publisher,
							'image': image,
							'publishedAt': int(pubdate)
						})
					except ValueError:
						pass
			except ConnectionError:
				pass
			except TypeError:
				pass
			except ValueError:
				pass

	return {
		'statusCode': 200,
		'body': json.dumps('Updated DB with recent book data :D')
	}

