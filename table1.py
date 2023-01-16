import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import csv
import chromedriver_autoinstaller

# chromedriver_autoinstaller.install()

from datetime import datetime
from selenium import webdriver
import re
from urllib.request import urlopen
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

df = pd.read_csv('은평구.csv') # 서울시 구별 기본 정보(출처: 비플페이)
def get_phone():
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    try:
        phone = soup.find("span",{"class":"dry01"}).get_text()
    except:#전화번호 없는 경우
        phone = ''
        return phone
    
    phone_li = soup.find("li",{"class":"SF_Mq SjF5j"})
    #print(phone_li)
    
    check_info = phone_li.find('a', class_='zkI3M') #업체전화번호인지 확인
    #print(check_info)
    if check_info is not None:
        phone = '업체전화번호 ' + phone
    
    return phone

def get_address_post():
    post_num = new_address = old_address = ''
        #주소 및 우편번호
    address_flag = 1
    try: #도로명주소 더보기 버튼 있으면 클릭
        wait(driver, 500).until(EC.element_to_be_clickable((By.CLASS_NAME, 'IH7VW'))).click()
        try:
            wait(driver, 500).until(EC.visibility_of_element_located((By.CLASS_NAME, 'dIrDd')))
        except:
            address_flag = 0
    except:
        address_flag = 0

    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")

        
    if address_flag: #주소 더보기 버튼 있는 경우
        driver.implicitly_wait(10)
        
        plus_button = driver.find_element(By.CLASS_NAME, 'dIrDd')
        address_post = plus_button.text

        address_post_list = address_post.split('\n')
        print(address_post_list)
        for i in address_post_list: #도로명, 지번주소 가져오는 코드
            if i.startswith('도로'):
                new_address = i[3:-2]
            elif i.startswith('지번'):
                if i[-3:] == '복사우':
                    old_address = i[2:-3]
                else:
                    old_address = i[2:-2]
                
        #우편번호 가져오는 코드
        try:
            int(address_post[-7:-2])
            post_num = address_post[-7:-2]
            if len(post_num) != 5:
                post_num = ''
        except: #우편번호가 아닌 경우
            post_num = ''
        post_num = str(post_num)
        return new_address, old_address, post_num
        
        #print(2, post_num)
    #더보기 버튼 없는 경우
    new_address = soup.find('span',{'class':'IH7VW'}).get_text()

    return new_address, old_address, post_num

def get_introduce():
    try: #가게설명 더보기 버튼 있는 경우
        wait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'rvCSr'))).click()
    except:
        pass
        
    #load_page() #더보기 버튼 클릭 후 html update
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    
    
    introduce_li = soup.find('li',{'class':'SF_Mq I5Ypx'})
    #print(introduce_li)
    if introduce_li is None: #가게설명 없는 경우
        introduce = ''
    else:
        introduce = introduce_li.find('span',{'class':'zPfVt'}).get_text()
    introduce = re.sub(r"[^가-힣0-9a-zA-Z.,\s]", "", introduce) #특수문자제거
    introduce = re.sub("[\u2009\n]", "", introduce) #괄호제거
    return introduce

def get_time():
    time = ''
    count = 0
    try: #운영시간 더보기 버튼 있는 경우
        wait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'X007O'))).click()
    except: #운영시간 없는 경우
        time = ''
        return time
        
    #스타벅스 -> class 명 다름..
    while count < 10: #html update 제대로 받아올때까지 loop
        try:
            time = time_li.findAll('div', {'class':'nNPOq'})
            break
        except:
            r = driver.page_source
            soup = BeautifulSoup(r, "html.parser")
            #check 필요  SF_Mq Sg7qM or SF_Mq Sg7qM oTbgr
            try:
                time_li = soup.find('li',{'class':'SF_Mq Sg7qM'})
            except:
                try:
                    time_li = soup.find('li',{'class':'SF_Mq Sg7qM oTbgr'})
                except:
                    return ''
        count += 1
            
    #print(time)
    time_sentence = ''
    for i in range(len(time)):
        if i == len(time) - 1: #맨 마지막 '접기' 제외
            #print(time[i].get_text()[:-2])
            temp = time[i].get_text()[:-2]
        else:
            #print(time[i].get_text())
            temp = time[i].get_text()
        temp += ' \n'
        #print('------------------------------------------------------')
        time_sentence += temp
    
    time_sentence = time_sentence.encode('CP949', 'ignore').decode('CP949')
    return time_sentence

def create_folder_if_not_exists(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

# 업체사진
def get_image():
    flag = 0
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    
    divs = soup.findAll('a',{'class':'tpj9w'})
    for index, div in enumerate(divs):
        check_image_tag = divs[index]
        if check_image_tag.get_text() == '사진': #사진 탭이 존재하는지 체크
            flag = 1
            try:
                element = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a['+ str(index+1) +']')
                element.click() #사진 탭 클릭
            except: #사진 탭이 화면 밖에 있는 경우 (일단 NULL 처리)
                return '',''
            #업체사진 클릭
            try:
                wait(driver, 1.25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-root"]/div/div/div/div[7]/div[2]/div/div/div/div/div[1]/a'))).click()
            except: #사진 탭 있는데 사진 없는 경우 처리
                return '',''

            #images = driver.find_elements(By.XPATH, '//*[starts-with(@id, "ibu")]')
            try: #CLASS 명 2가지 case 발견 
                section = driver.find_element(By.CLASS_NAME, 'ZHl8u')
            except:
                try:
                    section = driver.find_element(By.CLASS_NAME, 'DxoU4')
                except:
                    section = driver.find_element(By.CLASS_NAME, 'place_section_content')
            try:
                images = section.find_elements(By.XPATH, '//*[starts-with(@id, "ibu")]')
            except: #업체사진 아닌 경우
                return '',''
            index = 1
            # 가맹점 이미지 데이터 경로 설정
            save_path = "C:/Users/wngud/Desktop/crawling2/images/은평구/" + str(df['aflt_id'][i]) + '_img'
            create_folder_if_not_exists(save_path)
            
            file_names = ''
            for image in images:
                src =image.get_attribute('src')
                if src is not None:
                    t = urlopen(src).read()
                    temp = str(df['aflt_id'][i]) + '_' + str(index) + ".jpg"
                    file = open(os.path.join(save_path, temp), "wb")
                    file.write(t)
                    #print("img save " + str(df['aflt_id'][i]) + '_' + str(index) + ".jpg")
                    file_names += temp + ';'
                    index += 1
    if flag:
        path = str(df['aflt_id'][i]) + '_img'
        return file_names, path
    else:
        return '',''

def add_data_to_csv(query,file_path): #크롤링 결과 하나씩 csv파일에 추가하는 함수
    file_path = 'test.csv' #local path
    fieldnames = ['가맹점ID', '가맹점명', '업종','전화번호','운영시간','도로명주소','지번주소','우편번호','가게소개','업체사진_파일명','경로']
    #print(query)
    get_id = query[0]
    title = query[1]
    industry = query[2]
    phone = query[3]
    time = query[4]
    new_address = query[5]
    old_real_address = query[6]
    post_num = query[7]
    introduce = query[8]
    file_names = query[9]
    path = query[10]
    
    file_exists = os.path.isfile(file_path) #파일 존재 여부 확인
    with open('test.csv', 'a', newline = '') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:#파일 없는 경우
            wr.writeheader() #csv header 추가 (fieldnames)
        wr.writerow({ #
            '가맹점ID' :get_id,
            '가맹점명':title,
            '업종' : industry, 
            '전화번호' :phone, 
            '운영시간':time, 
            '도로명주소':new_address, 
            '지번주소':old_real_address, 
            '우편번호':post_num, 
            '가게소개': introduce, 
            '업체사진_파일명': file_names,
            '경로': path})

    crawl_df = pd.DataFrame()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--disable-dev-shm-usage')
dpath = '/usr/bin/chromedriver'

#####################################################
#####################################################
for i in range(len(df)): # 실행 for문
    file_path = 'test.csv' #정상입력 파일
    file_2_path = 'test2.csv' #timeoutexception 처리 파일
    flag = 1
    get_addr = df['addrs'][i] #주소 추출
    get_id = df['aflt_id'][i] #가맹점 id 추출
    temp_addr = get_addr
    search_name = df['aflt_nm'][i] + ' '+ temp_addr # 검색어 완성 (주소 + 상호명)
    driver = webdriver.Chrome('C:/Users/wngud/Desktop/crawling2/chromedriver.exe') #크롬드라이버 경로 및 속도 향상을 위한 옵션 설정
    driver.set_window_position(0, 0)
    driver.set_window_size(1000, 3000)
    
    #검색어에 특수 문자 포함되어있는 경우 제거해줘야 검색 가능
    search_name = re.sub('[=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','', search_name)
    driver.get("https://map.naver.com/v5/search/"+ search_name)
    
    #가맹점 검색 결과 case 구분 
    #검색 결과 없음, 검색 결과 있음, 바로 상세페이지 진입(단일 플레이스)

    driver.implicitly_wait(15)
    try:#바로 상세페이지로 넘어가는 경우
        driver.switch_to.frame('entryIframe')
    #driver.switch_to.frame('iframe')
    except Exception as error:#여러 검색 나오는 경우 or 검색결과 없는 경우
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="searchIframe"]')) #iframe 안에 검색 결과 목록이 속해있으므로 프레임 전환
        
        try: #검색 결과 없는 경우
            no_result = driver.find_element(By.CLASS_NAME, 'vEAWt')
            #파일에 크롤링 데이터 추가해서 자장
            query = [get_id, df['aflt_nm'][i], '','','','','','','','',''] #가맹점명 외 공란으로 작성
            add_data_to_csv(query,file_path)
            driver.quit()
            continue
        except: # 검색 결과 있는 경우
            pass
        
        #여러 검색 결과 중 맨 위 내용 선택
        try:#
            wait(driver, 1.25).until(EC.element_to_be_clickable((By.CLASS_NAME, 'place_bluelink'))).click()
        except:
            flag = 0 #검색 결과 없는 경우 판별
        driver.switch_to.default_content() #default로 frame 초기화
        if flag: 
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="entryIframe"]')) #entryframe으로 전환 (상세페이지 진입)
    
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    
    try:
        wait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'Fc1rA')))
    except:
        query = [get_id, df['aflt_nm'][i], '','','','','','','','','']
        add_data_to_csv(query,file_2_path)
        continue
    title = driver.find_element(By.CLASS_NAME, 'Fc1rA').text
    industry = driver.find_element(By.CLASS_NAME, 'DJJvD').text
    
    #함수 순서 중요 -> 클릭 miss 나기 쉬움
    #운영시간
    time = get_time()
    
    #주소 및 우편번호
    new_address, old_address,post_num = get_address_post()
    old_join_address=' '.join(get_addr)
    old_real_address = f"{old_join_address} {old_address}"
    
    # 전화번호
    phone = get_phone()

    #가게설명
    introduce = get_introduce()
    
    #print code
    file_names, path = get_image()
    print('업체사진: ',file_names)
    print('경로: ',path)
    print('가맹점ID: ', get_id)
    print('가맹점명: ', title)
    print('업종: ',industry)
    print('도로명주소: ', new_address)
    print('지번주소: ',old_real_address)
    print('우편번호: ',post_num)
    print('가게소개: ',introduce)
    print('전화번호: ',phone)
    print('운영시간: ',time)
    
    
    #파일에 크롤링 데이터 추가해서 자장
    query = [get_id, title, industry, phone, time, new_address, old_real_address, post_num, introduce, file_names, path]
    add_data_to_csv(query,file_path)
    driver.quit()