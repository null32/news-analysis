import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ['bs4', 'lxml', 'gensim', 'sklearn', 'matplotlib', 'nltk', 'requests']
for p in packages:
    print('Installing', p)
    install(p)

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_ru')