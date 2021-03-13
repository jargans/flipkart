from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import time

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            baseurl = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(baseurl)
            flipkartPage = uClient.read()
            uClient.close()
            time.sleep(30)
            soup = bs(flipkartPage, "html.parser")
            productlist = soup.find_all("div", {"class": "_1AtVbE col-12-12"})
            productlinks = []
            for item in productlist:
                for link in item.find_all('a', {'class': 's1Q9rs'}, href=True):
                    productlinks.append(baseurl + link['href'])
                for link in item.find_all('a', {'class': '_1fQZEK'}, href=True):
                    productlinks.append(baseurl + link['href'])
                for link in item.find_all('a', {'class': '_2UzuFa'}, href=True):
                    productlinks.append(baseurl + link['href'])
            product = []
            for link in productlinks[0:10]:
                r = requests.get(link,timeout=30)
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
                    # x = table.insert_one(dict1)
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
                        dict1 = {"name": name, "price": price, "offers": offers, "comments": comment, "rating": rating}
                        product.append(dict1)
                        # x = table.insert_one(dict1)
            return render_template('results.html', product=product)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
