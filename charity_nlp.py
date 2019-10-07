import nltk
import pandas as pd
import re
from textblob import TextBlob
from wordcloud import WordCloud


# key operations in this file:
#     preprocess text in mission field for each charity: filtering, tokenizing, stemming / lemmitization
#     create wordcloud for the charities' mission text
#     compare mission text using comparison wordcloud across different charity categories
#     show relationship between charity mission polarity / subjectivity and rating


