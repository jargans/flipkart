# doing necessary imports

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
from pymongo import MongoClient
import selenium
import time
from selenium import webdriver as wb
import os
application = Flask(__name__)  # initialising the flask app with the name 'app'
@application.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")
@application.route('/review',methods=['POST','GET']) # route with allowed methods as POST and GET
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'] # obtaining the search string entered in the form
        try:
            dbConn = MongoClient("mongodb+srv://rishabh:rishabc@cluster0.gdsdm.mongodb.net/crawlerDB?retryWrites=true&w=majority")  # opening a connection to Mongo
            time.sleep(3)
            db = dbConn['crawler']  # connecting to the database called crawlerDB
            product = db[searchString].find({})  # searching the collection with the name same as the keyword
            if product.count() > 0:  # if there is a collection with searched keyword and it has records in it
                return render_template('results.html', product=product)  # show the results to user
            else:
                chrome_options = wb.ChromeOptions()
                #GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
                chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                #chrome_options.add_argument("--headless")
                #chrome_options.add_argument("--disable-dnev-shm-usage")
                #chrome_options.add_argument("--no-sandbox")
                #CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
                #webd = wb.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                webd = wb.Chrome(executable_path="./chromedriver.exe", chrome_options=chrome_options)
                baseurl='https://www.flipkart.com/search?q='+searchString # preparing the URL to search the product on flipkart
                webd.get(baseurl)
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}
                uClient = uReq(baseurl)
                flipkartPage = uClient.read()
                uClient.close()
                soup=bs(flipkartPage,'html.parser')
                productlist=soup.find_all("div", {"class": "_1AtVbE col-12-12"})
                productlinks = []
                table = db[searchString]
                if(webd.find_elements_by_class_name('_1LKTO3') == []):
                    for item in productlist:
                        for link in item.find_all('a', {'class': 's1Q9rs'}, href=True):
                            productlinks.append(baseurl + link['href'])
                        for link in item.find_all('a', {'class': '_1fQZEK'}, href=True):
                            productlinks.append(baseurl + link['href'])
                        for link in item.find_all('a', {'class': '_2UzuFa'}, href=True):
                            productlinks.append(baseurl + link['href'])
                else:
                    while (webd.find_elements_by_class_name('_1LKTO3')[-1].text == "NEXT"):
                        for item in productlist:
                            for link in item.find_all('a', {'class': 's1Q9rs'}, href=True):
                                productlinks.append(baseurl + link['href'])
                            for link in item.find_all('a', {'class': '_1fQZEK'}, href=True):
                                productlinks.append(baseurl + link['href'])
                            for link in item.find_all('a', {'class': '_2UzuFa'}, href=True):
                                productlinks.append(baseurl + link['href'])
                        try:
                            webd.find_elements_by_class_name('_1LKTO3')[-1].click()
                        except:
                            webd.find_elements_by_class_name('_1LKTO3')[-1].text == "PREVIOUS"
                product = []
                for link in productlinks[0:10]:
                    r = requests.get(link,headers=headers)
                    soup = bs(r.content, 'html.parser')
                    try:
                        name = soup.find('span', {'class': 'B_NuCI'}).text
                    except:
                        name = 'No Name'
                    try:
                        price = soup.find('div', {'class': '_30jeq3 _16Jk6d'}).text
                    except:
                        price = "NO Price"
                    try:
                        offers = soup.find('li', {'class': '_16eBzU col'}).text
                    except:
                        offers = "no offers"
                    commentbox = soup.findAll('div', {'class': '_16PBlm'})
                    if (commentbox == []):
                        comment = "no comment"
                        rating = "no rating"
                        dict1 = {"name": name, "price": price, "offers": offers, "comments": comment, "rating": rating}
                        product.append(dict1)
                        #x = table.insert_one(dict1)
                    else:
                        for c in commentbox:
                            try:
                                comtag = c.div.div.find_all('div', {'class': ''})
                                comment = comtag[0].text
                            except:
                                comment = 'No Customer Comment'
                            try:
                                rating = c.div.div.div.div.text
                            except:
                                rating = "no rating"
                            dict1 = {"name": name, "price": price, "offers": offers, "comments": comment,"rating": rating}
                            product.append(dict1)
                            x = table.insert_one(dict1)
                return render_template('results.html', product=product)
        except:
            return 'something is wrong'
    else:
        return render_template('index.html')
if __name__ == "__main__":
    application.run(debug=True) # running the app on the local machine on port 8000
