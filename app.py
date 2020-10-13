from flask import Flask, render_template, request, redirect, url_for
import bs4 as bs
import urllib.request
import re
import nltk.tokenize
import requests
from bs4 import BeautifulSoup
import urllib.parse
from lxml import etree
from urllib.request import FancyURLopener

app = Flask(__name__)

@app.route('https://app-letmeknow.herokuapp.com/')
def Index():
    return render_template('index.html')

@app.route('https://app-letmeknow.herokuapp.com/busqueda', methods=['POST'])
def busqueda():
    if request.method == 'POST':
        Tema_Principal = request.form['Tema Principal']
        Subtema = request.form['Subtema']

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}

        url = "https://www.google.com/search?q=" + Tema_Principal + Subtema

        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')

        final = []
        webs = []

        #class AppURLopener(urllib.request.FancyURLopener):
        #    version = "Mozilla/5.0"

        for link in soup.find_all('a'):
            web = link.get('href')
            fin = web.replace("/url?q=","").split("&sa=")[0]
            val = fin.find("http")
            if val == 0:
                pdf = fin
                ten = pdf.find(".pdf")      #filtra pdf
                if ten == -1:
                    conh = pdf
                    ult = conh.find("google.com")    #filtra paginas extras de google
                    if ult == -1:
                        siny = conh
                        fin = siny.find("youtube.com")      #filtra videos de Youtube
                        if fin == -1:
                            pin = siny
                            alo = pin.find("pinterest")
                            if alo == -1:
                                decoded = urllib.parse.unquote(pin)               

                                #opener = AppURLopener()
                                #response = opener.open(decoded)
                                req = urllib.request.Request(decoded, headers=headers)
                                response = urllib.request.urlopen(req)
                                article = response.read()

                                parsed_article = bs.BeautifulSoup(article,'lxml')
                                sumado = []

                                for p in parsed_article.find_all('p'):                                                #adquirimos los parrafos de a uno para ser analizados indvidualmente
                                    article_text = p.text

                                    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
                                    article_text = re.sub(r'\s+', ' ', article_text)

                                    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )  
                                    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
                                    

                                    sentence_list = nltk.sent_tokenize(article_text)
            
                                    stopwords = nltk.corpus.stopwords.words('spanish')

                                    word_frequencies = {}  
                                    for word in nltk.word_tokenize(formatted_article_text):  
                                        if word not in stopwords:
                                            if word not in word_frequencies.keys():
                                                word_frequencies[word] = 1
                                            else:
                                                word_frequencies[word] += 1
                        
                                    if word_frequencies:
                                        pass
                                    else:
                                        break

                                    maximum_frequncy = max(word_frequencies.values())

                                    for word in word_frequencies.keys():  
                                        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

                                    sentence_scores = {}  
                                    for sent in sentence_list:  
                                        for word in nltk.word_tokenize(sent.lower()):
                                            if word in word_frequencies.keys():
                                                if len(sent.split(' ')) < 30:
                                                    if sent not in sentence_scores.keys():
                                                        sentence_scores[sent] = word_frequencies[word]
                                                    else:
                                                        sentence_scores[sent] += word_frequencies[word]

                                    import heapq  
                                    summary_sentences = heapq.nlargest(15, sentence_scores, key=sentence_scores.get)
                                    
                                    summary=' '.join(summary_sentences)

                                    if summary != '':
                                        pedacitos=summary.split()
                                        for i in pedacitos:
                                            if i != '\u200b':
                                                sumado.append(i)
                                            else:
                                                pass
                                    else:
                                        pass
                                
                                if len(sumado) > 100:
                                    final.append(sumado)
                                    webs.append(decoded)
                                else:
                                    pass

              
                                
        return render_template('resultados.html', Tema_Principal = Tema_Principal, Subtema = Subtema, Resumenes = final, Link = webs)     
        
@app.route('/pruebas')
def Pruebas():
    return render_template('pruebas.html')

@app.route('https://app-letmeknow.herokuapp.com/uso')
def Uso():
    return render_template('uso.html')


if __name__=='__main__':
    app.run(port = 3000, debug = True)
