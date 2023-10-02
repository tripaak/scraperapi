from bs4 import BeautifulSoup
import cloudscraper
import re
import os
import csv
import time
import datetime



def scrap_item(ean):

    time.sleep(1)
    item = {}
    scraper = cloudscraper.create_scraper()
    srch_resp = scraper.get(f"https://www.manomano.fr/recherche/{ean}")
    try:
        next_url = BeautifulSoup(srch_resp.content, 'html.parser').select_one('div>a[href^="/p/"]').attrs.get('href')
        print(f"Product found for EAN: {ean}")
    except:
        print(f"Product NOT found for EAN: {ean}")
        next_url = None
        item['ean'] = ean  
        item['title'] = ''
        item['avis'] = ''
        item['price'] = ''
        item['description'] =  ''
        item['image_url_1'] = ''
        item['image_url_2'] = ''
        item['image_url_3'] = ''
        item['image_url_4'] = ''
        item['image_url_5'] = ''
        return item
    
    response = scraper.get(f"https://www.manomano.fr{next_url}")
    soup = BeautifulSoup(response.content,'html.parser')
    # f = open('8014140430506.html','w',encoding='utf-8')
    # f.write(response.text)
    item['ean'] = ean
    try:
        item['title'] = soup.select_one('h1').text.strip()
    except:
        item['title'] = ""
    try:
        item['avis'] = re.findall(r"sur (.+?) avis",soup.select_one('a[data-testid="reviews-container"]').text)[0].strip()
    except:
        item['avis'] = ""
    try:
        item['price'] = soup.select_one('div[data-testid="main-price-container"]').text.strip().replace('€',',')
    except:
        item['price'] = ""
    try:
        item['description'] = soup.select_one('div[data-testid="description-content"]').text.strip()
    except:
        item['description'] =  ""
    
    image_url = []
    for image in soup.select('div>img[fetchpriority="high"]'):
        image_url.append(image.attrs.get('src'))
    try:
        item['image_url_1'] = image_url[0]
    except :
        item['image_url_1'] = ''  
    try:
        item['image_url_2'] = image_url[1]
    except :
        item['image_url_2'] = '' 
    try:
        item['image_url_3'] = image_url[2]
    except :
        item['image_url_3'] = '' 
    try:
        item['image_url_4'] = image_url[3]
    except :
        item['image_url_4'] = ''         
    try:
        item['image_url_5'] = image_url[4]
    except :
        item['image_url_5'] = ''  
    
    try:
        characteristic = []
        for char in soup.select('div>ul[class="c4Y32pt"]>li>div') :
            characteristic.append(char.text)
        characteristic_dict = dict(zip(characteristic[::2], characteristic[1::2]))
        item['characteristic'] = "\n".join("{!r}: {!r},".format(k, v) for k, v in characteristic_dict.items())
    except:
        item['characteristic'] = ''
    try:
        item['fiche'] = soup.select_one('a.o7pnC0').attrs.get('href')
    except:
         item['fiche'] = ''   
    return item

def read_input():
    found = False
    for fls in os.listdir(os.path.join(os.getcwd(),'filesystem','manomano', 'in')):
        if not '.done' in fls:
            found = True
            print(f"Processing input file: {fls} \n")
            with open(os.path.join(os.getcwd(),'filesystem','manomano','in',fls),'r',encoding='utf-8') as in_fls:
                reader = csv.DictReader(in_fls)
                out_file_name = f"output_{datetime.datetime.today().strftime('%d-%m-%Y')}.csv"
                for row in reader:
                    item = scrap_item(row['ean'])
                    write_output(item,out_file_name)
            print(f"Scraping done for file {fls}; re-naming to .done !")
            os.rename(os.path.join(os.getcwd(),'filesystem','manomano','in',fls),os.path.join(os.getcwd(),'filesystem','manomano','in',f"{fls}.{datetime.datetime.today().strftime('%d-%m-%Y-%H-%M-%S')}.done")) 
            return out_file_name
    if not found:
        print("Warning: No input file found for processing!")

def write_output(item,out_file):
    file_exist = os.path.isfile(os.path.join(os.getcwd(),'filesystem','manomano', 'out',out_file))
    with open(os.path.join(os.getcwd(),'filesystem','manomano','out',out_file),'a',encoding='utf-8',newline='') as op_fls:
        fields = ['ean','title','avis','price','description','image_url_1','image_url_2','image_url_3','image_url_4','image_url_5','characteristic','fiche']
        writer = csv.DictWriter(op_fls,fieldnames=fields,delimiter=';')
        if file_exist:
            writer.writerow(item)   
        else:
            writer.writeheader()
            writer.writerow(item)

def maintain_folder_struc():
    # maintain /in and /out folder required
    if not os.path.exists(os.path.join(os.getcwd(), 'filesystem','manomano', 'in')):
        os.makedirs(os.path.join(os.getcwd(),'filesystem','manomano', 'in'))
    if not os.path.exists(os.path.join(os.getcwd(), 'filesystem','manomano','out')):
        os.makedirs(os.path.join(os.getcwd(),'filesystem','manomano', 'out'))

def run():
    maintain_folder_struc()
    return read_input()



