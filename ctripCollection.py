from bs4 import BeautifulSoup
import requests
import time
import re #正则表达式
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains #浏览器操作
from fileManager import ExcelFileManager #导入自定义的Excel读写文件


#跳转到目的地
def jump_destinationPage(startPlace,destination):
    #定位搜索栏
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='SearchText']")))
    except:
        print('查找不到搜索栏')
    finally:
        print('本地页面加载完毕')


    driver.find_element_by_xpath("//input[@id='SearchText']").send_keys(destination)
    print("输入目的地："+destination)
    driver.find_element_by_xpath("//*[@id='SearchBtn']").click()
    print("点击搜索按钮结束")
    time.sleep(2)

    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='js-dpSearcher']")))
    except:
        print('产品列表页加载不成功')
    finally:
        print('产品列表页加载完毕')

    #再选一次出发地，以防出错
    reSelect_StartPlace(startPlace)


    #搜索页数
    pageHtml = driver.find_element_by_xpath("//*[@id='_sort']/div/span")
    print(pageHtml.text)
    pageNumStr = pageHtml.text
    pageNumStr = pageNumStr[:-1]
    print("获取的num:" + pageNumStr)
    #正则表达式 查找页数
    pageNumS = re.findall(r'\d+',pageNumStr)
    pageNum = int(pageNumS[1])
    print(pageNum)

    tourProductList = []
    for i in range(0,pageNum):
        itemList = showCurrentPageAllData()

        #收集数据
        for j in range(0,len(itemList)):
            eachItem = collectCurrentPageEachData(j)
            tourProductList.append(eachItem)

        #点击下一页
        driver.find_element_by_xpath("//input[@id='ipt_page_txt']").clear()
        driver.find_element_by_xpath("//input[@id='ipt_page_txt']").send_keys(str(i+2))
        driver.find_element_by_xpath("//*[@id='ipt_page_btn']").click()
        print("点击下一页结束->"+str(i+2)+"页")
        time.sleep(2)

    #所有结果进行保存
    saveTourProductData(startPlace,destination,tourProductList)

    return driver

#展示当前页所有产品信息（通过移动鼠标到指定item）
def showCurrentPageAllData():
    # 搜索全部产品元素
    itemList = driver.find_elements_by_class_name("product_box")
    # 搜索全部广告元素
    itemModList = driver.find_elements_by_class_name("product_mod")
    modNum = len(itemModList)
    isNoAllShow = True
    while isNoAllShow == True:
        isNoAllShow = False
        print("itemList:" + str(len(itemList)))
        for i in range(0,len(itemList)-modNum):#要减去广告的产品数量

            strHtml = itemList[i+modNum].get_attribute('innerHTML')  # 转换成字符串
            item = BeautifulSoup(strHtml, "lxml")  # 获取item的soup对象
            # print(item.prettify())
            textarea = item.find('textarea').get_text()
            print('/////////'+str(i)+'---'+textarea)
            if len(textarea) > 0:

                # xpathStr = ("//*[@id='_rcmd']/div[{}]/textarea".format(i+1))
                xpathStr = ("//*[@id='_prd']/div[{}]".format(i + 3))
                print(xpathStr)
                try:
                    moveElement = driver.find_element_by_xpath(xpathStr)
                    ActionChains(driver).move_to_element(moveElement).perform()
                    print("移动到" + str(i) + "item")
                    time.sleep(0.2)
                    isNoAllShow = True
                except:
                    print('扫描错误')




    time.sleep(2)
    return itemList

#搜索当前页所有产品信息
def collectCurrentPageEachData(itemNum):
    itemList = driver.find_elements_by_class_name("product_box")
    str = itemList[itemNum].get_attribute('innerHTML')#转换成字符串
    # item = BeautifulSoup(str,"html.parser")#获取item的soup对象
    item = BeautifulSoup(str, "lxml")  # 获取item的soup对象
    # print("+++++++"+item.prettify())
    # 解析
    #产品名称
    titleNameHtml = item.find('h2',class_= 'product_title')
    print("-------"+titleNameHtml.get_text())
    productName = titleNameHtml.get_text()

    #产品链接
    productLink = titleNameHtml.a['href']
    productLink = productLink[2:]
    productLink = "https://"+productLink
    print("link:" + productLink)
    #产品类型
    productType = item.find('em')
    print("type:"+productType.get_text())
    productTypeStr = productType.get_text()

    #产品价格
    priceHtml = item.find('span',class_='sr_price')
    priceStr = priceHtml.strong.get_text()
    #判断是否为数字
    if priceStr.isdigit() == True :
        priceStr = "%.2f"%float(priceStr)
    print("price:"+priceStr)

    #产品供应商
    productRetail = item.find('p',class_='product_retail')
    productRetailStr = productRetail['title']
    if "供应商" in productRetailStr:
        productRetailStr = productRetailStr[4:]

    print("retail:" + productRetailStr)
    #产品评分
    try :
        gradeHtml = item.find('p', class_='grade')
        gradeStr = gradeHtml.strong.get_text()
        print("grade:" + gradeStr)
    except:
        print('查找不到评分')
        gradeStr = ''
    # 产品人数
    try:
        commentHtml = item.find('div', class_='comment')
        commentStr = commentHtml.em.get_text()
        commentNumS = re.findall(r'\d+', commentStr)
        commentNum = int(commentNumS[0])
        print("comment:",commentNum)
    except:
        print('查找不到出游人数')
        commentNum = ''
    # #产品参数
    # productScheduleHtml = item.find('div',class_='product_schedule')
    # productSchedulePid = productScheduleHtml.a['pid']
    # productScheduleLink = productScheduleHtml.a['url']
    # print("ID:"+productSchedulePid)
    # link = productScheduleLink[2:]
    # print("link：" + link)

    return {
        '名称':productName,
        '链接':productLink,
        '类型':productTypeStr,
        '价格':priceStr,
        '供应商':productRetailStr,
        '评分':gradeStr,
        '人数':commentNum,
    }

def setupDriverSetting():
    global driver
    # url = 'http://m.ctrip.com/restapi/soa2/10290/createclientid?systemcode=09&createtype=3&conte'#获取cookieID
    # 手机端
    # url = 'https://m.ctrip.com/webapp/vacations/tour/list?tab=64&kwd=%E7%8F%A0%E6%B5%B7&salecity=32&searchtype=tour&sctiy=32'
    # 电脑端
    url = 'https://weekend.ctrip.com/around/'
    # 设置用chrome启动
    driver = webdriver.Chrome()
    # #设置fireFox请求头参数
    # profile = webdriver.FirefoxProfile()
    # user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
    # profile.set_preference("general.useragent.override",user_agent)
    #
    # driver = webdriver.Firefox(profile)
    driver.get(url)

#选择出发地点
def select_StartPlace(startPlace):

    #点击出发点view
    driver.find_element_by_xpath("//*[@id='CitySelect']").click()
    #选择出发点
    cityList = driver.find_elements_by_xpath("//*[@id='CitySelect']/dd/ul")
    for link in cityList:
        links = link.find_elements(By.TAG_NAME,"a")
        for eachCity in  links:
            cityStr = eachCity.text
            if cityStr == startPlace:
                print("找到目标城市:"+eachCity.get_attribute('href'))
                driver.get(eachCity.get_attribute('href'))
                time.sleep(2)
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='SearchText']")))
                except:
                    print('出发地页面加载不成功')

                break

def reSelect_StartPlace(startPlace):

    #点击出发点view
    driver.find_element_by_xpath("//*[@id='_ssc']").click()
    #选择出发点
    try:
        WebDriverWait(driver,2).until(EC.presence_of_element_located((By.XPATH,"//*[@id='_ssc']/dd/div[2]/div[1]/input")))
    except:
        print('没有出现搜索栏')
    driver.find_element_by_xpath("//*[@id='_ssc']/dd/div[2]/div[1]/input").send_keys(startPlace)
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='_ssc']/dd/div[2]/div[2]/a")))
    except:
        print('没有出现结果栏')

    driver.find_element_by_xpath("//*[@id='_ssc']/dd/div[2]/div[2]/a").click()
    time.sleep(1)

def saveTourProductData(startPlace,destination,productList):
    #创建列表
    headRowList = ['名称','类型','价格','供应商','评分','出游人数','产品链接']
    ExcelFileManager.creatExcelFile(startPlace,destination,headRowList)
    print("创建文件成功")
    #保存数据
    productExcelList = []
    for each in productList:
        i = [each['名称'],each['类型'],each['价格'],each['供应商'],each['评分'],each['人数'],each['链接']]
        productExcelList.append(i)
    ExcelFileManager.addDataToExcelFile(startPlace,destination,productExcelList)
    print("保存数据成功")

#搜索所有热门目的地
def finAllDestinationPage():
    #查找总数组
    destType = driver.find_element_by_id("J_sub_circum")#id 决定产品范围（周边游，境外游）
    print(destType.text)
    destType1 = destType.find_element_by_class_name("side_jmp_dest")
    destTypeItem = destType1.get_attribute('innerHTML')
    item = BeautifulSoup(destTypeItem,'lxml')
    destTypeList = item.find_all('li')
    allDestinationListDic = {}
    for each in destTypeList:
        typeName = each.h4.string
        typeList  = each.find_all('a')
        list = []
        for i in  typeList:
            list.append(i.string)
            allDestinationListDic[typeName] = list

    return allDestinationListDic

if __name__ == '__main__':

    setupDriverSetting()
    #收集热门地点信息
    startPlace = '广州'
    select_StartPlace(startPlace)
    allDesDic = finAllDestinationPage()
    desList = [allDesDic['周边目的地'],allDesDic['热门景点']]
    # desList = [allDesDic['热门景点']]
    print(desList)
    driver.quit()
    print('产品目的地数据列表收集成功')

    for destinationList in desList:
        for each in destinationList:
            setupDriverSetting()
            select_StartPlace(startPlace)
            driver = jump_destinationPage(startPlace,each)
            driver.quit()

    print('数据收集成功')

    # setupDriverSetting()
    # select_StartPlace('广州')
    # driver = jump_destinationPage('广州', '深圳')

