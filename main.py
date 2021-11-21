#!/usr/bin/env python3

import os
import re
import datetime

from bs4 import BeautifulSoup
from lxml import html
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
import nltk
import requests

from config import Config

config = Config.load('config.json')

def get_headlines():
    if not os.path.exists(config.cache):
        os.mkdir(config.cache)
    entries = os.listdir(config.cache)
    today = datetime.date.today().strftime('%Y.%m.%d')
    if not today in entries:
        os.mkdir(os.path.join(config.cache, today))
        for site in config.sites:
            fileName = f'{site.alias}.html'
            filePath = os.path.join(config.cache, today, fileName)

            if not os.path.exists(filePath):
                resp = requests.get(site.url, headers=config.headers)
                resp.raise_for_status()

                f = open(filePath, 'w', encoding='utf-8')
                f.write(BeautifulSoup(resp.content, 'html.parser').prettify())
                f.close()

    headlines = []

    for folder in entries:
        for site in config.sites:
            fileName = f'{site.alias}.html'
            filePath = os.path.join(config.cache, folder, fileName)
            
            if os.path.exists(filePath):
                f = open(filePath, 'r', encoding='utf-8')
                doc = html.fromstring(f.read())
                f.close()
                raw_headlines = doc.xpath(site.xpath)
                headlines += raw_headlines

    headlines = [re.sub(r'\s+', ' ', x.lower()) for x in headlines]
    # print('total:', len(headlines))

    return headlines

def pre_process(data):
    res = []
    for line in data:
        words = nltk.word_tokenize(line)
        functors_pos = {'CONJ', 'ADV-PRO', 'CONJ', 'PART'}
        
        a = ' '.join([word for word, pos in nltk.pos_tag(words, lang='rus') if pos not in functors_pos and len(word) > 2 and not (word in config.banwords)])
        res.append(a)
    
    return res

def visualize(data):
    # if os.path.exists('model.bin'):
    #     model = Word2Vec.load('model.bin')
    # else:
    model = Word2Vec(sentences=[x.split(' ') for x in data], vector_size=1000, window=5, min_count=1, workers=4)
    # model.wv.save('model.bin')
    # model.wv.save_word2vec_format('model.bin')

    # print(model)

    words = {k:v for k, v in model.wv.key_to_index.items() if model.wv.get_vecattr(v, 'count') > 1}
    topWords = {a:b for a, b, c in (sorted([[k, v, model.wv.get_vecattr(v, 'count')] for k, v in model.wv.key_to_index.items()], reverse= True, key= lambda x: x[2]))[0:10]}
    # print('words w/ > 1 occurances', len(words))

    word_similarity = {}
    for k1, v1 in topWords.items():
        word_similarity[k1] = {}
        for k2, v2 in words.items():
            if k1 == k2 or k2 in topWords:
                continue
            sim = abs(model.wv.similarity(k1, k2))
            word_similarity[k1][k2] = sim
            # print(f'{k1} -> {k2} = {sim}')

    for k1, v1 in word_similarity.items():
        # aboba[k1] = {a:model.wv.key_to_index[a] for a, b in (sorted([[c, d] for c, d in v1.items()], reverse= True, key= lambda x: x[1]))[0:random.randint(3, 12)]}
        temp = sorted([[c, d] for c, d in v1.items()], reverse= True, key= lambda x: x[1])
        t_min = min(map(lambda x: x[1], temp))
        t_max = max(map(lambda x: x[1], temp))
        word_similarity[k1] = {a:model.wv.key_to_index[a] for a, b in filter(lambda x: x[1] > t_min + t_max * 0.83, temp)}
    # X = model.wv[model.wv.key_to_index]
    # X = model.wv[words]
    words = topWords
    for k, v in word_similarity.items():
        for k1, v1 in v.items():
            words[k1] = v1
    X = model.wv[words]
    X = X - X.min()
    X = X / X.max()

    colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'orange', 'lime', 'pink', 'purple', 'gray']
    color_codes = {k:v for v, k in enumerate(list(word_similarity))}
    def findColor(name):
        for k, v in word_similarity.items():
            if name == k:
                return colors[color_codes[k]]
            for k1, v1 in v.items():
                if k1 == name:
                    return colors[color_codes[k]]
        return 'black'

    pca = PCA(n_components=2)
    result = pca.fit_transform(X)
    sizes = [50 * model.wv.get_vecattr(v, 'count') for k, v in words.items()]
    colors1 = [findColor(k) for k, v in words.items()]
    pyplot.scatter(result[:, 0], result[:, 1], s=sizes, c=colors1, alpha=0.5)
    words1 = {v:k for k, v in enumerate(list(words))}

    for i, word in enumerate(list(words)):
        pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
    for k1, v1 in word_similarity.items():
        for k2, v2 in v1.items():
            pyplot.plot([result[words1[k1], 0], result[words1[k2], 0]], [result[words1[k1], 1], result[words1[k2], 1]], linewidth=0.5, c=colors[color_codes[k1]])
    
    pyplot.show()
    for k1, v1 in word_similarity.items():
        res = k1 + ' '
        for k2, v2 in v1.items():
            res += k2 + ' '
        print(res)

if __name__ == '__main__':
    visualize(pre_process(get_headlines()))