import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import re
from wordcloud import WordCloud

rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False


start_time = time.time()

# 웹툰 정보 가져오기

new_naver_title_ids = []
old_naver_title_ids = []
new_kakao_genre = []
old_kakao_genre = []
def verticalize_labels(labels):
    return ["\n".join(label) for label in labels]

def naver_data_crawl(days):
    url = f'https://korea-webtoon-api.herokuapp.com/?service=naver&updateDay={days}&perPage=1500'
    response = requests.get(url)
    parsed_data = json.loads(response.text)
    webtoon_list = parsed_data['webtoons']
    for i in webtoon_list:
        url = i['url']
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        title_id = query_params.get('titleId', [None])[0]
        if days == 'finished':
            old_naver_title_ids.append(title_id)
        else:
            new_naver_title_ids.append(title_id)
        

def kakao_data_crawl(parsed_data,i):
    cnt = 0
    try :
        while True:
            new_kakao_genre.append(parsed_data[cnt]['content']['seoKeywords'])
            print("Tag : ",parsed_data[cnt]['content']['seoKeywords'])
            cnt += 1
    except:
        pass

def kakao_genre_completed(parsed_data):
    cnt = 0
    try :
        while True:
            old_kakao_genre.append(parsed_data[cnt]['content']['seoKeywords'])
            print("Tag : ",parsed_data[cnt]['content']['seoKeywords'])
            cnt += 1
    except:
        pass


weekdays = ['mon','tue','wed','thu','fri','sat','sun','finished']
executor = ThreadPoolExecutor()
for days in weekdays:
    executor.submit(naver_data_crawl, days)
executor.shutdown(wait=True)

url = 'https://gateway-kw.kakao.com/section/v1/pages/general-weekdays'
response = requests.get(url)
parsed_data = json.loads(response.text)
for i in range(0,7):
    kakao_data_crawl(parsed_data['data']['sections'][i]['cardGroups'][0]['cards'],i)
    
url = 'https://gateway-kw.kakao.com/section/v1/sections?placement=channel_completed'
response = requests.get(url)
parsed_data = json.loads(response.text)
kakao_genre_completed(parsed_data['data'][0]['cardGroups'][0]['cards'])


# 웹툰 장르 가져오기


new_naver_tags_list = []
old_naver_tags_list = []
def new_naver_bring_info(webtoon_links):
    url = f"https://comic.naver.com/api/article/list/info?titleId={webtoon_links}"
    response = requests.get(url)
    if response.status_code == 404:
        exit(1)
    parsed_data = json.loads(response.text)
    tags = parsed_data['gfpAdCustomParam']['tags']
    print("Tag : ",end='',sep='')
    for tag in tags:
        new_naver_tags_list.append(tag)
        print(f"{tag} ",end='',sep='')
    print()
    
def old_naver_bring_info(webtoon_links):
    url = f"https://comic.naver.com/api/article/list/info?titleId={webtoon_links}"
    response = requests.get(url)
    if response.status_code == 404:
        exit(1)
    parsed_data = json.loads(response.text)
    tags = parsed_data['gfpAdCustomParam']['tags']
    for tag in tags:
        old_naver_tags_list.append(tag)
    print("Naver Old Tags : ", tags)
    print()

def crawl_new_naver_best_webtoons():
    pass



executor = ThreadPoolExecutor()
for webtoon_links in new_naver_title_ids:
    executor.submit(new_naver_bring_info,webtoon_links)
executor.shutdown(wait=True)

executor = ThreadPoolExecutor()
for webtoon_links in old_naver_title_ids:
    executor.submit(old_naver_bring_info,webtoon_links)
executor.shutdown(wait=True)



    
    
    
# # 결과 출력

new_naver_genre_set = {}
old_naver_genre_set = {}

# 현재 연재 중인 네이버 웹툰 데이터 정리
for genre in new_naver_tags_list:
    genre = genre.replace('완결','')
    if re.search(r'20\d{2}|공모전|최강자전', genre):
        continue  # 단어 감지시 다음으로 넘어감
    if genre and genre in new_naver_genre_set:
        new_naver_genre_set[genre] += 1
    elif genre:
        new_naver_genre_set[genre] = 1

for genre in list(new_naver_genre_set.keys()):
    if new_naver_genre_set[genre] <= 15:
        del new_naver_genre_set[genre]

# 완결된 네이버 웹툰 데이터 정리
for genre in old_naver_tags_list:
    genre = genre.replace('완결','')
    if re.search(r'20\d{2}|공모전|최강자전', genre):
        continue
    if genre and genre in old_naver_genre_set:
        old_naver_genre_set[genre] += 1
    elif genre:
        old_naver_genre_set[genre] = 1

for genre in list(old_naver_genre_set.keys()):
    if old_naver_genre_set[genre] <= 15:
        del old_naver_genre_set[genre]

new_kakao_genre_set = {}
old_kakao_genre_set = {}

# 현재 연재 중인 카카오 웹툰 데이터 정리
for genre_list in new_kakao_genre:
    genre = genre.replace('완결','').replace('#','')
    for genre in genre_list:
        if genre and genre in new_kakao_genre_set:
            new_kakao_genre_set[genre] += 1
        elif genre:
            new_kakao_genre_set[genre] = 1

for genre in list(new_kakao_genre_set.keys()):
    if new_kakao_genre_set[genre] <= 25:
        del new_kakao_genre_set[genre]

# 완결된 카카오 웹툰 데이터 정리
for genre_list in old_kakao_genre:
    genre = genre.replace('완결','').replace('#','')
    for genre in genre_list:
        if genre and genre in old_kakao_genre_set:
            old_kakao_genre_set[genre] += 1
        elif genre:
            old_kakao_genre_set[genre] = 1

for genre in list(old_kakao_genre_set.keys()):
    if old_kakao_genre_set[genre] <= 25:
        del old_kakao_genre_set[genre]
    
    
# 시각화

end_time = time.time() - start_time
print("소요 시간 : %s" % end_time)

print(new_naver_genre_set)
print(old_naver_genre_set)
print(new_kakao_genre_set)
print(old_kakao_genre_set)


final_genre_set = {'액션,판타지,무협':0,'드라마,로맨스,감성':0,'일상,개그':0,'스릴러,공포,아포칼립스':0}

sorted_genres = sorted(new_naver_genre_set.items(), key=lambda x: x[1])
genres, counts = zip(*sorted_genres)
plt.figure(figsize=(20, 10))
plt.barh(genres, counts, color='skyblue')
plt.xlabel('작품 수')
plt.title('현재 연재 중인 네이버 웹툰 장르')
plt.show()

top_5_genres, top_5_counts = zip(*sorted_genres[-1:-6:-1])

plt.figure(figsize=(20, 10))
plt.barh(top_5_genres, top_5_counts, color='skyblue')
plt.xlabel('작품 수')
plt.title('현재 연재 중인 네이버 웹툰 장르 중 인기 장르')
plt.show()

# 워드 클라우드
wordcloud = WordCloud(width=1600, height=1200, background_color='white', font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc').generate_from_frequencies(new_naver_genre_set)
plt.figure(figsize=(20, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()



sorted_old_naver_genres = sorted(old_naver_genre_set.items(), key=lambda x: x[1])
old_naver_genres, old_naver_counts = zip(*sorted_old_naver_genres)
plt.figure(figsize=(20, 10))
plt.barh(old_naver_genres, old_naver_counts, color='skyblue')
plt.xlabel('작품 수')
plt.title('현재 완결된 네이버 웹툰 장르')
plt.show()


sorted_new_kakao_genres = sorted(new_kakao_genre_set.items(), key=lambda x: x[1])
new_kakao_genres, new_kakao_counts = zip(*sorted_new_kakao_genres)
plt.figure(figsize=(20, 10))
plt.barh(new_kakao_genres, new_kakao_counts, color='lightgreen')
plt.xlabel('작품 수')
plt.title('현재 연재 중인 카카오 웹툰 장르')
plt.show()

top_5_genres, top_5_counts = zip(*sorted_new_kakao_genres[-1:-6:-1])

plt.figure(figsize=(20, 10))
plt.barh(top_5_genres, top_5_counts, color='skyblue')
plt.xlabel('작품 수')
plt.title('현재 연재 중인 카카오 웹툰 장르 중 인기 장르')
plt.show()


# 워드 클라우드
wordcloud = WordCloud(width=1600, height=1200, background_color='white', font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc').generate_from_frequencies(new_kakao_genre_set)
plt.figure(figsize=(20, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()



sorted_old_kakao_genres = sorted(old_kakao_genre_set.items(), key=lambda x: x[1])
old_kakao_genres, old_kakao_counts = zip(*sorted_old_kakao_genres)
plt.figure(figsize=(20, 10))
plt.barh(old_kakao_genres, old_kakao_counts, color='lightgreen')
plt.xlabel('작품 수')
plt.title('현재 완결된 카카오 웹툰 장르')
plt.show()

for genre in list(new_naver_genre_set.keys()):
    if genre in r'\b(로맨스|로판|하렘|폭스|연애|사랑|결혼|연인|러블리|로판|남친|여친|걸크러시|설레는)\b':
        final_genre_set['드라마,로맨스,감성'] += new_naver_genre_set[genre]
        
    elif genre in r'\b(능력|배틀|왕도물|액션|판도|판타지|헌터|회귀|인외|학원|서사|이세계|먼치킨|무협|압도|사극|복수극)\b':
        final_genre_set['액션,판타지,무협'] += new_naver_genre_set[genre]
        
    elif genre in r'\b(일상|개그|4차원|힐링|재미|코믹|평온|힐링|발랄|)\b':
        final_genre_set['일상,개그'] += new_naver_genre_set[genre]
        
    elif genre in r'\b(스릴러|범죄|공포|아포칼립스|빙의|좀비|괴물|몬스터|등골|오싹|긴장|미스테리|처절)\b':
        final_genre_set['스릴러,공포,아포칼립스'] += new_naver_genre_set[genre]

for genre in list(new_kakao_genre_set.keys()):
    if genre in r'\b(로맨스|로판|하렘|폭스|연애|사랑|결혼|연인|러블리|로판|남친|여친|걸크러시|설레는)\b':
        final_genre_set['드라마,로맨스,감성'] += new_kakao_genre_set[genre]
        
    elif genre in r'\b(능력|배틀|왕도물|액션|판도|판타지|헌터|회귀|인외|학원|서사|이세계|먼치킨|무협|압도|사극|복수극)\b':
        final_genre_set['액션,판타지,무협'] += new_kakao_genre_set[genre]
        
    elif genre in r'\b(일상|개그|4차원|힐링|재미|코믹|평온|힐링|발랄|)\b':
        final_genre_set['일상,개그'] += new_kakao_genre_set[genre]
        
    elif genre in r'\b(스릴러|범죄|공포|아포칼립스|빙의|좀비|괴물|몬스터|등골|오싹|긴장|미스테리|처절)\b':
        final_genre_set['스릴러,공포,아포칼립스'] += new_kakao_genre_set[genre]

old_final_genre_set = {'액션,판타지,무협':0,'드라마,로맨스,감성':0,'일상,개그':0,'스릴러,공포,아포칼립스':0}

for genre in list(old_naver_genre_set.keys()):
    if genre in r'\b(로맨스|로판|하렘|폭스|연애|사랑|결혼|연인|러블리|로판|남친|여친|걸크러시|설레는)\b':
        old_final_genre_set['드라마,로맨스,감성'] += old_naver_genre_set[genre]
        
    elif genre in r'\b(능력|배틀|왕도물|액션|판도|판타지|헌터|회귀|인외|학원|서사|이세계|먼치킨|무협|압도|사극|복수극)\b':
        old_final_genre_set['액션,판타지,무협'] += old_naver_genre_set[genre]
        
    elif genre in r'\b(일상|개그|4차원|힐링|재미|코믹|평온|힐링|발랄|)\b':
        old_final_genre_set['일상,개그'] += old_naver_genre_set[genre]
        
    elif genre in r'\b(스릴러|범죄|공포|아포칼립스|빙의|좀비|괴물|몬스터|등골|오싹|긴장|미스테리|처절)\b':
        old_final_genre_set['스릴러,공포,아포칼립스'] += old_naver_genre_set[genre]

for genre in list(old_kakao_genre_set.keys()):
    if genre in r'\b(로맨스|로판|하렘|폭스|연애|사랑|결혼|연인|러블리|로판|남친|여친|걸크러시|설레는)\b':
        old_final_genre_set['드라마,로맨스,감성'] += old_kakao_genre_set[genre]
        
    elif genre in r'\b(능력|배틀|왕도물|액션|판도|판타지|헌터|회귀|인외|학원|서사|이세계|먼치킨|무협|압도|사극|복수극)\b':
        old_final_genre_set['액션,판타지,무협'] += old_kakao_genre_set[genre]
        
    elif genre in r'\b(일상|개그|4차원|힐링|재미|코믹|평온|힐링|발랄|)\b':
        old_final_genre_set['일상,개그'] += old_kakao_genre_set[genre]
        
    elif genre in r'\b(스릴러|범죄|공포|아포칼립스|빙의|좀비|괴물|몬스터|등골|오싹|긴장|미스테리|처절)\b':
        old_final_genre_set['스릴러,공포,아포칼립스'] += old_kakao_genre_set[genre]

plt.figure(figsize=(20, 10))
plt.pie(final_genre_set.values(), labels=final_genre_set.keys(), autopct='%1.1f%%', startangle=140)
plt.suptitle('메이저 장르와 마이너 장르 (현재 연재중인 웹툰)')
plt.show()

plt.figure(figsize=(20, 10))
plt.pie(old_final_genre_set.values(), labels=old_final_genre_set.keys(), autopct='%1.1f%%', startangle=140)
plt.suptitle('메이저 장르와 마이너 장르 (완결 웹툰)')
plt.show()
