import pandas as pd
import requests
from bs4 import BeautifulSoup

import csv
from datetime import datetime
import time
from selenium import webdriver
import re
from urllib.request import urlopen
import os


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys #안보이는 메뉴 탭 누를때 사용
from selenium.webdriver import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

df = pd.read_csv('은평구.csv') # 서울시 구별 가맹점 정보(출처: 비플페이)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

#table2 -> table2 data
def add_table2_to_csv(query,file_path): #크롤링 결과 하나씩 csv파일에 추가하는 함수
    file_path = 'table2.csv' #local path
    fieldnames = ['가맹점ID', '포장', '매장', '배달', '항목명', '가격', 'timestamp']
    #print(query)
    get_id = query[0]
    takeout = query[1]
    place = query[2]
    delivery = query[3]
    menu_str = query[4]
    price_str= query[5]
    timestamp = query[6]

    file_exists = os.path.isfile(file_path) #파일 존재 여부 확인
    with open('table2.csv', 'a') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:#파일 없는 경우
            wr.writeheader() #csv header 추가 (fieldnames)
        wr.writerow({ #
            '가맹점ID' :get_id,
            '포장':takeout,
            '매장' : place, 
            '배달' :delivery, 
            '항목명':menu_str, 
            '가격':price_str, 
            'timestamp':timestamp})

#table3 -> table3 data
def add_table3_to_csv(query,file_path): #크롤링 결과 하나씩 csv파일에 추가하는 함수
    file_path = 'table3.csv' #local path
    fieldnames = ['가맹점ID', '키워드통계', '리뷰_메뉴탭_5', '리뷰_특징탭_1', '리뷰_특징탭_2', '리뷰_특징탭_3', '리뷰_특징탭_4', '리뷰_특징탭_5']
    #print(query)
    
    get_id = query[0]
    keyword_str = query[1]
    tab_name_str = query[2]
    feature_str_0 = query[3]
    feature_str_1 = query[4]
    feature_str_2 = query[5]
    feature_str_3 = query[6]
    feature_str_4 = query[7]
    
    file_exists = os.path.isfile(file_path) #파일 존재 여부 확인
    with open('table3.csv', 'a') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:#파일 없는 경우
            wr.writeheader() #csv header 추가 (fieldnames)
        wr.writerow({ #
            '가맹점ID' :get_id,
            '키워드통계':keyword_str,
            '리뷰_메뉴탭_5' : tab_name_str, 
            '리뷰_특징탭_1' :feature_str_0, 
            '리뷰_특징탭_2':feature_str_1, 
            '리뷰_특징탭_3':feature_str_2, 
            '리뷰_특징탭_4':feature_str_3, 
            '리뷰_특징탭_5':feature_str_4 })



def add_error_to_csv(query,file_path): #크롤링 결과 하나씩 csv파일에 추가하는 함수
    file_path = 'test4.csv' #local path
    fieldnames = ['가맹점ID']
    #print(query)
    
    get_id = query[0]
    
    file_exists = os.path.isfile(file_path) #파일 존재 여부 확인
    with open('test4.csv', 'a') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:#파일 없는 경우
            wr.writeheader() #csv header 추가 (fieldnames)
        wr.writerow({ #
            '가맹점ID' :get_id,})



def get_menu():
    takeout_flag = place_flag = delivery_flag = None #takeout ->포장, place->매장, delivery->배달
    action = ActionChains(driver)
    menus = []
    menu_str = ''
    price_str = ''
    case_flag = 1
    menu_or_price_flag = -1 #메뉴, 가격, 선물하기 케이스 구분하기 위함

    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    
    divs = soup.findAll('a',{'class':'tpj9w'})
    for index, div in enumerate(divs):
        #print(index)
        check_image_tag = divs[index]
        print(1)
        if check_image_tag.get_text() == '메뉴' or check_image_tag.get_text() == '가격' or check_image_tag.get_text() == '선물하기' or check_image_tag.get_text() == '예매' or check_image_tag.get_text() == '객실': 
        #메뉴(가격, 선물하기) 탭이 존재하는지 체크    
            element = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a['+ str(index+1) +']')
            wait(driver, 3).until(EC.element_to_be_clickable(element)).send_keys(Keys.ENTER) #메뉴(가격, 선물하기) 탭 클릭
            if check_image_tag.get_text() == '메뉴':
                menu_or_price_flag = 0
            elif check_image_tag.get_text() == '가격': #가격은 한번더 눌러줌 (안 누르는 경우 방지용)
                menu_or_price_flag = 1
                element.click()
            elif check_image_tag.get_text() == '선물하기':
                menu_or_price_flag = 2
            elif check_image_tag.get_text() == '예매':
                menu_or_price_flag = 3
            else:
                menu_or_price_flag = 4
            break
    if menu_or_price_flag == 0: #메뉴 탭 크롤링 코드 부분 시작
        #분류 존재하는지 체크, 존재하면 크롤링
        try:
            cases = driver.find_element(By.CLASS_NAME, 'info_main_tab')
        except:
            case_flag = 0
        if case_flag: #분류 존재하는 경우
            #배달 -> sc_box startswith
            #매장 -> order_list startswith
            #포장 -> order_list startswith
            cases_split = cases.text.split('\n')
            for index, case in enumerate(cases_split):
                element = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div[2]/div/a['+ str(index+1) +']')
                
                if element.text in '포장할게요':
                    takeout_flag = 1
                elif element.text in ['매장', '먹고갈게요']:
                    place_flag = 1  
                elif element.text in '배달':
                    delivery_flag = 1 
                element.click() #분류 탭 클릭      
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                driver.implicitly_wait(5)
                #print(soup)

                items = driver.find_elements(By.CLASS_NAME, 'order_list_item')
                #print(len(items))
                #print(items)
                if len(items) > 0:
                    for item in items:
                        try:
                            name = item.find_element(By.CLASS_NAME, 'tit')
                            price = item.find_element(By.CLASS_NAME, 'price')
                            data = (name.text,price.text)
                            if data not in menus: #중복은 무시
                                menu_str += name.text + ';'
                                price_str += price.text + ';'
                                menus.append(data) 
                        except: #메뉴 없는 곳은 패스
                            pass
                      #각각 case 잘 들어가는지 확인할 때 사용하는 부분
#                     print(menus)
#                     menus = []
#                     print('-------------------------')


                else: #배달 분류 크롤링
                    #print('여기')
                    sections = driver.find_elements(By.XPATH, '//*[starts-with(@class, "sc_box")]')
                    for index,section in enumerate(sections):
                        #print(index)
                        open_flag = 0
                        action.move_to_element(section).perform() #섹션들 확인하며 아래로 스크롤
                        #이미 열려있는 섹션인지 체크 -> 열려있으면 클릭하지 않아야함
                        try:
                            check_active = section.find_element(By.CLASS_NAME, 'active')
                            #print('active 0')
                        except: 
                            open_flag = 1
                        if open_flag: #열려있지 않은 경우 -> 클릭
                            try:
                                temp = section.find_element(By.CLASS_NAME, 'list_tit')
                                wait(driver, 3).until(EC.element_to_be_clickable(temp)).click() #모든 섹션 클릭해서 열어줌

                            except: #클릭 불가능한 섹션 클릭 안하고 넘어감
                                pass
                        #더보기 버튼 눌러주는 부분
                        try: 
                            button = driver.find_element(By.CLASS_NAME, 'sc_extend_view')
                            while button.is_displayed: #displayed가 none될 때까지 클릭
                                try:
                                    wait(driver, 3).until(EC.element_to_be_clickable(button)).click() #모든 섹션 클릭해서 열어줌
                                except:
                                    break
                        except: #더보기 버튼 없는 경우
                            pass

                    #모든 섹션 다 연 후 메뉴 크롤링        
                    #menus = []
                    lis = driver.find_elements(By.CLASS_NAME, 'list_item')
                    for li in lis:
                        try:
                            name = li.find_element(By.CLASS_NAME, 'name')
                            price = li.find_element(By.CLASS_NAME, 'price')
                            data = (name.text,price.text)
                            if data not in menus: 
                                menu_str += name.text + ';'
                                price_str += price.text + ';'
                                menus.append(data)
                        except: #메뉴 없는 곳은 패스
                            pass
                    #print(menus)

        else: #분류 존재하지 않는 경우

            try: #업체명 존재하는지 체크
                delivery_name = driver.find_element(By.CLASS_NAME, 'btn_wrapper').text
                delivery_flag = 1
            except:
                pass
            
            #일반 -> ZUXK
            #배민 -> sc_box startswith
            sections = driver.find_elements(By.XPATH, '//*[starts-with(@class, "sc_box")]')
            if sections: #배민인 경우
                for index,section in enumerate(sections):
                    open_flag = 0
                    action.move_to_element(section).perform() #섹션들 확인하며 아래로 스크롤
                    #이미 열려있는 섹션인지 체크 -> 열려있으면 클릭하지 않아야함
                    try:
                        check_active = section.find_element(By.CLASS_NAME, 'active')
                        #print('active 0')
                    except: 
                        open_flag = 1
                    if open_flag: #열려있지 않은 경우 -> 클릭
                        try:
                            temp = section.find_element(By.CLASS_NAME, 'list_tit')
                            wait(driver, 3).until(EC.element_to_be_clickable(temp)).click() #모든 섹션 클릭해서 열어줌

                        except: #클릭 불가능한 섹션 클릭 안하고 넘어감
                            pass
                    #더보기 버튼 눌러주는 부분
                    try: 
                        button = driver.find_element(By.CLASS_NAME, 'sc_extend_view')
                        while button.is_displayed: #displayed가 none될 때까지 클릭
                            try:
                                wait(driver, 3).until(EC.element_to_be_clickable(button)).click() #모든 섹션 클릭해서 열어줌
                            except:
                                break
                    except: #더보기 버튼 없는 경우
                        pass

                #모든 섹션 다 연 후 메뉴 크롤링        
                menus = []
                lis = driver.find_elements(By.CLASS_NAME, 'list_item')
                for li in lis:
                    try:
                        name = li.find_element(By.CLASS_NAME, 'name')
                        price = li.find_element(By.CLASS_NAME, 'price')
                        menu_str += name.text + ';'
                        price_str += price.text + ';'
                        menus.append((name.text,price.text))  
                    except: #메뉴 없는 곳은 패스
                        pass
                #print(menus)

            else: #일반 case
                #더보기 버튼 눌러주는 부분
                try: 

                    button = driver.find_element(By.CLASS_NAME, 'fvwqf')
                    action.move_to_element(button).perform() #버튼까지 아래로 스크롤
                    while button.is_displayed: #displayed가 none될 때까지 클릭
                        try:
                            wait(driver, 3).until(EC.element_to_be_clickable(button)).click() #모든 섹션 클릭해서 열어줌
                        except:
                            break
                except: #더보기 버튼 없는 경우
                    pass            
                menus = []
                try:
                    ul_menus = driver.find_element(By.CLASS_NAME, 'ZUYk_')
                    lis = driver.find_elements(By.CLASS_NAME, 'P_Yxm')
                    for li in lis: #메뉴, 가격 크롤링
                        name = li.find_element(By.CLASS_NAME, 'Sqg65')
                        price = li.find_element(By.CLASS_NAME, 'SSaNE')
                        menu_str += name.text + ';'
                        price_str += price.text + ';'
                        menus.append((name.text,price.text))
                except: # ex> 서울 마포구 코하루야
                    #print('여기')
                    items = driver.find_elements(By.CLASS_NAME, 'order_list_item')
                #print(len(items))
                #print(items)
                    if len(items) > 0:
                        for item in items:
                            try:
                                name = item.find_element(By.CLASS_NAME, 'tit')
                                price = item.find_element(By.CLASS_NAME, 'price')
                                data = (name.text,price.text)
                                if data not in menus: #중복은 무시
                                    menu_str += name.text + ';'
                                    price_str += price.text + ';'
                                    menus.append(data) 
                            except: #메뉴 없는 곳은 패스
                                pass
                #print(menus)
        menu_str = menu_str.encode('CP949', 'ignore').decode('CP949')        
        return takeout_flag, place_flag, delivery_flag, menus, menu_str, price_str  
    
    elif menu_or_price_flag == 1: #가격 탭 크롤링 코드 부분 시작
    #주노헤어 당산역점 -> 가격탭 공란
        #print('가격')
        section = driver.find_elements(By.CLASS_NAME, 'place_section_content')
        divs = driver.find_elements(By.CLASS_NAME, 'LwJHx')
        for div in divs:
            name = div.find_element(By.CLASS_NAME, 'gqmxb')
            price = div.find_element(By.CLASS_NAME, 'dELze')
            menu_str += name.text + ';'
            price_str += price.text + ';'            
            menus.append((name.text,price.text))
        #print(menus)
    elif menu_or_price_flag == 2:
        #print('선물하기')
        divs = driver.find_elements(By.CLASS_NAME, 'XiiIo')
        for div in divs:
            name = div.find_element(By.CLASS_NAME, 'JhiJB')
            price = div.find_element(By.CLASS_NAME, 'XvicB')
            price = price.text.split('\n')[0]
            menu_str += name.text + ';'
            price_str += price + ';'
            menus.append((name.text,price))
        #print(menus)
    elif menu_or_price_flag == 3:
        #print('예매')
        divs = driver.find_elements(By.CLASS_NAME, 'tkK1g')
        for div in divs:
            name = div.find_element(By.CLASS_NAME, 'QTWaA')
            price = div.find_element(By.CLASS_NAME, 'CTesk')
            menu_str += name.text + ';'
            price_str += price.text + ';'
            menus.append((name.text,price))
        #print(menus)
    elif menu_or_price_flag == 4:
        #print('객실')
        divs = driver.find_elements(By.CLASS_NAME, 'vtGHh')
        for div in divs:
            name = div.find_element(By.CLASS_NAME, 'FtVpy')
            price = div.find_element(By.CLASS_NAME, 'QW7xr')
            menu_str += name.text + ';'
            price_str += price.text + ';'
            menus.append((name.text,price))
        #print(menus)
    else:
        pass
        #print('메뉴 탭 없음')
    menu_str = menu_str.encode('CP949', 'ignore').decode('CP949')  
    return takeout_flag, place_flag, delivery_flag, menus, menu_str, price_str  
            
def get_review():
    keyword_str = ''
    tab_name_str = ''
    feature_str_0 = feature_str_1 = feature_str_2 = feature_str_3 = feature_str_4 = ''
    review_flag = 0
    keyword_flag = 1
    action = ActionChains(driver)
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")
    divs = soup.findAll('a',{'class':'tpj9w'})
    for index, div in enumerate(divs):
        check_review_tag = divs[index]
        if check_review_tag.get_text() == '리뷰': 
        #리뷰 탭이 존재하는지 체크    
            review_flag = 1
            element = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a['+ str(index+1) +']')
            for _ in range(3): #엔터키 씹히는 경우 방지
                try:
                    element.send_keys(Keys.ENTER) #리뷰 탭 클릭
                except:
                    pass
            break
    if review_flag == 0: #리뷰 탭 없는 경우
        return keyword_str, tab_name_str, feature_str_0, feature_str_1, feature_str_2, feature_str_3, feature_str_4

    
    #이런 점이 좋았어요 크롤링 부분
    try:
        keywords = driver.find_element(By.CLASS_NAME, 'BBfpo')
    except: #키워드 통계 없는 가맹점
        keyword_flag = 0
        
    if keyword_flag: #키워드 통계 있는 경우
        try: 
            button = keywords.find_element(By.CLASS_NAME, 'Tvx37')
            while button.is_displayed: #displayed가 none될 때까지 더보기 버튼 클릭
                try:
                    wait(driver, 5).until(EC.element_to_be_clickable(button)).click() #모든 섹션 클릭해서 열어줌
                except:
                    break
        except: #더보기 버튼 없는 경우
            pass
        lis = keywords.find_elements(By.CLASS_NAME, 'nbD78')
        for li in lis: #키워드 통계 추출
            try:
                keyword = li.find_element(By.CLASS_NAME, 'nWiXa')
            except: #키워드 통계가 공개됩니다! (인원수 부족으로 키워드 통계 없는곳)
                break
            number = li.find_element(By.CLASS_NAME, 'TwM9q')
            number = re.sub(r'[^0-9]', '', number.text)
            
            temp = keyword.text + number + ';'
            keyword_str += temp

        #print(keyword_str)    
    
    #리뷰 하이라이트 부분 구하는 코드 섹션
    try:
        move_to = driver.find_element(By.CLASS_NAME, 'YeINN')
    except: #블로그 리뷰만 있는 곳 ex> 경상남도 거제시 MBODY STUDIO
        return keyword_str, tab_name_str, feature_str_0, feature_str_1, feature_str_2, feature_str_3, feature_str_4
    action.move_to_element(move_to).perform()
    
    #html reload
    r = driver.page_source
    soup = BeautifulSoup(r, "html.parser")

    sections = driver.find_elements(By.CLASS_NAME, 'PaWWQ')
    #sections = soup.findAll('div', {'class':'PaWWQ'})

    #메뉴, 특징 탭 있는 경우
    if len(sections) > 1:
        for i,section in enumerate(sections): #메뉴, 특징 -> 2번 반복, 메뉴 탭만 -> 1번 반복
            #name = section.find_element(By.CLASS_NAME, 'LeSFd')
            if i == 0: #메뉴
                camera = section.find_element(By.CLASS_NAME, 'flicking-camera')
                driver.execute_script("arguments[0].style.transform = 'none';", camera) #특징 탭 카메라 맨 왼쪽으로 이동
                tabs = section.find_elements(By.CLASS_NAME, 'cbqXB')
                for j,tab in enumerate(tabs):
                    if j > 4:   #5개 까지만 메뉴 탭 내용 추출
                        break
                    elif j == 2:
                        driver.execute_script("arguments[0].style.transform = 'translateX(-150px)';", camera) #카메라 중간 이동
                    driver.implicitly_wait(1.5)
                    tab_name = tab.text
                    hangul = re.compile('[^ ㄱ-ㅣ가-힣a-zA-Z+]') #리뷰개수(숫자) 제거 
                    tab_name = hangul.sub('', tab_name)
                    tab_name_str += tab_name + ';'
                    #print(tab_name)
            else: #특징탭
                #print('특징', i)
                #asdfasdf
                review_section = driver.find_element(By.CLASS_NAME,'lcndr')
                tabs = section.find_elements(By.CLASS_NAME, 'cbqXB')
                camera = section.find_element(By.CLASS_NAME, 'flicking-camera')
                driver.execute_script("arguments[0].style.transform = 'none';", camera) #특징 탭 카메라 맨 왼쪽으로 이동
                
                for j, tab in enumerate(tabs):
                    #print(j, camera.get_attribute("style"))
                    wait(driver, 5).until(EC.element_to_be_clickable(tab)).send_keys(Keys.ENTER)#리뷰 탭 클릭
                    try: 
                        button = review_section.find_element(By.CLASS_NAME, 'fvwqf')
                        for i in range(11): #11 -> 100개
                            #print(i)
                            driver.implicitly_wait(3)
                            action.move_to_element(button).perform()
                            driver.implicitly_wait(3)
                            wait(driver, 500).until(EC.element_to_be_clickable(button)).click() #클릭 미스 방지 대기시간 넉넉히                
                    except: #더보기 버튼 없는 경우
                        pass
                    driver.implicitly_wait(2)
                    tab_name = tab.text
                    hangul = re.compile('[^ ㄱ-ㅣ가-힣a-zA-Z+]') #리뷰개수(숫자) 제거 
                    tab_name = hangul.sub('', tab_name)
                    #tab_name_str += tab_name + ';' 

                    if j == 0:
                        feature_str_0 += tab_name + ';'
                    elif j == 1:
                        feature_str_1 += tab_name + ';'
                    elif j == 2:
                        driver.execute_script("arguments[0].style.transform = 'translateX(-150px)';", camera) #카메라 중간 이동
                        feature_str_2 += tab_name + ';'
                    elif j == 3:
                        feature_str_3 += tab_name + ';'
                    else:
                        feature_str_4 += tab_name + ';'
                    
            #모든 리뷰 누르지 않는 방식
                    driver.page_source #html reload
                    driver.implicitly_wait(5)
                    spans = driver.find_elements(By.CLASS_NAME, 'highlight')
                    driver.implicitly_wait(5)
                    #print(len(spans))
                    for span in spans:
                        feature = span.text
                        feature = feature.encode('CP949', 'ignore').decode('CP949')
                        if j == 0:
                            feature_str_0 += feature + ';'
                        elif j == 1:
                            feature_str_1 += feature + ';'
                        elif j == 2:
                            feature_str_2 += feature + ';'
                        elif j == 3:
                            feature_str_3 += feature + ';'
                        else:
                            feature_str_4 += feature + ';'
                            #print(span.text)
                        #print(len(spans)) 개수 check
                        #print('-------------------------------------------------------') 
                    driver.execute_script("scroll(100,0);") #맨 위로 스크롤링
                    try:
                        move_to = driver.find_element(By.CLASS_NAME, 'YeINN')
                    except:
                        move_to = driver.find_element(By.CLASS_NAME, 'vEAWt')
                    action.move_to_element(move_to).perform()
                
                    if j > 3: #특징 5개만 추출
                        break
                        
    else: #탭 없거나 하나만 있는 경우
        one_flag = 0
        try: #하나의 탭만 존재
            tab = driver.find_element(By.CLASS_NAME, 'YwgDA')
            one_flag = 1

        except: #탭 없음
            pass
        if one_flag:
            review_section = driver.find_element(By.CLASS_NAME,'lcndr')
            camera = tab.find_element(By.CLASS_NAME, 'flicking-camera')
            driver.execute_script("arguments[0].style.transform = 'none';", camera) #특징 탭 카메라 맨 왼쪽으로 이동
            #print('하나')
            tabs = driver.find_elements(By.CLASS_NAME, 'cbqXB')
            #print(tabs))
            for j, tab in enumerate(tabs):
                tab.send_keys(Keys.ENTER) #리뷰 탭 클릭
                #print(tab.text)
                try: 
                    button = review_section.find_element(By.CLASS_NAME, 'fvwqf')
                    for i in range(11): #11 -> 100개
                        #print(i)
                        driver.implicitly_wait(2)
                        #print(i) 
                        action.move_to_element(button).perform()
                        wait(driver, 5).until(EC.element_to_be_clickable(button)).click() #클릭 미스 방지 대기시간 넉넉히                
                    #print('----------------------------------------------------')
                except: #더보기 버튼 없는 경우
                    pass
                driver.implicitly_wait(2)
                tab_name = tab.text
                hangul = re.compile('[^ ㄱ-ㅣ가-힣a-zA-Z+]') #리뷰개수(숫자) 제거 
                tab_name = hangul.sub('', tab_name)
                #tab_name_str += tab_name + ';' 
                
                if j == 0:
                    feature_str_0 += tab_name + ';'
                elif j == 1:
                    feature_str_1 += tab_name + ';'
                elif j == 2:
                    driver.execute_script("arguments[0].style.transform = 'translateX(-150px)';", camera) #카메라 중간 이동
                    feature_str_2 += tab_name + ';'
                elif j == 3:
                    feature_str_3 += tab_name + ';'
                else:
                    feature_str_4 += tab_name + ';'

        #모든 리뷰 누르지 않는 방식
                driver.page_source #html reload
                driver.implicitly_wait(5)
                try:
                    spans = driver.find_elements(By.CLASS_NAME, 'highlight')
                except:
                    pass
                driver.implicitly_wait(5)
                #print(len(spans))
                for span in spans:
                    feature = span.text
                    feature = feature.encode('CP949', 'ignore').decode('CP949')
                    if j == 0:
                        feature_str_0 += feature + ';'
                    elif j == 1:
                        feature_str_1 += feature + ';'
                    elif j == 2:
                        feature_str_2 += feature + ';'
                    elif j == 3:
                        feature_str_3 += feature + ';'
                    else:
                        feature_str_4 += feature + ';'
                        #print(span.text)
                    #print(len(spans)) 개수 check
                    #print('-------------------------------------------------------')                    
                
                driver.execute_script("scroll(100,0);") #맨 위로 스크롤링
                try:
                    move_to = driver.find_element(By.CLASS_NAME, 'YeINN')
                except:
                    move_to = driver.find_element(By.CLASS_NAME, 'vEAWt')
                action.move_to_element(move_to).perform()
                if j > 3:
                    break


        
    return keyword_str, tab_name_str, feature_str_0, feature_str_1, feature_str_2, feature_str_3, feature_str_4            


#start = time.time()

##################################################
##################################################
for i in range(len(df)): # 실행 for문
    table2_path = 'table2.csv' #biz_menu
    table3_path = 'table3.csv' #biz_comment
    table4_path = 'test4.csv' #error
    errors = pd.DataFrame()
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

    driver.implicitly_wait(10)
    try:#바로 상세페이지로 넘어가는 경우
        driver.switch_to.frame('entryIframe')
    #driver.switch_to.frame('iframe')
    except Exception as error:#여러 검색 나오는 경우 or 검색결과 없는 경우
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="searchIframe"]')) #iframe 안에 검색 결과 목록이 속해있으므로 프레임 전환
        
        try: #검색 결과 없는 경우
            no_result = driver.find_element(By.CLASS_NAME, 'vEAWt')
            query_2 = [get_id, '','','','','',''] #가맹점명 외 공란으로 작성
            query_3 = [get_id, '','','','','','',''] #가맹점명 외 공란으로 작성
            add_table2_to_csv(query_2, table2_path)
            add_table3_to_csv(query_3, table3_path)

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
    
    #get timestamp
    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    francies_id = df['aflt_id'][i]
    try:
        takeout_flag, place_flag, delivery_flag, menus, menu_str, price_str = get_menu()
    except:
        print('menu')
        print('test4 저장')
        query = [get_id]
        add_error_to_csv(query, table4_path)
        continue
        
    try:
        #menu, review 사이 약간의 term
        driver.refresh() #default로 frame 초기화
        driver.implicitly_wait(10)
        driver.switch_to.frame('entryIframe') #iframe 다시 변경
        driver.implicitly_wait(5)
        keyword_str, tab_name_str, feature_str_0, feature_str_1, feature_str_2, feature_str_3, feature_str_4 = get_review()
    except:
        print('review')
        print('test4 저장')
        query = [get_id]
        add_error_to_csv(query, table4_path)
        continue
    print('가맹점ID', francies_id)
    print("포장: ", takeout_flag)
    print("매장: ", place_flag)
    print("배달: ", delivery_flag)
    #print('메뉴: ', menus)
    print('메뉴모음: ', menu_str)
    print('가격모음: ', price_str)

    print('\n키워드통계모음:', keyword_str)
    print('\n메뉴탭이름모음: ', tab_name_str)
    print('\n특징탭1: ', feature_str_0)
    print('\n특징탭2: ', feature_str_1)
    print('\n특징탭3: ', feature_str_2)
    print('\n특징탭4: ', feature_str_3)
    print('\n특징탭5: ', feature_str_4)
    print('\ntimestamp: ', datetime_str)    
    query_2 = [francies_id, takeout_flag, place_flag, delivery_flag, menu_str,price_str, datetime_str] #가맹점명 외 공란으로 작성
    query_3 = [francies_id, keyword_str, tab_name_str, feature_str_0, feature_str_1, feature_str_2, feature_str_3, feature_str_4] #가맹점명 외 공란으로 작성

    add_table2_to_csv(query_2, table2_path)
    add_table3_to_csv(query_3, table3_path)
    
#end = time.time()
#print("크롤링시간",end - start)