import pandas as pd
import re
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


# key operations in this file:
#     preprocess text in mission field for each charity: filtering, tokenizing, stemming / lemmitization
#     create wordcloud for the charities' mission text
#     compare mission text using comparison wordcloud across different charity categories
#     show relationship between charity mission polarity / subjectivity and rating


def preprocess_text(df, field_name):
    new_field = field_name + "_nlp"
    # make all lower case
    df[new_field] = df[field_name].str.lower()
    # remove white space
    df[new_field] = df[new_field].apply(lambda x: re.sub('\s+', ' ', str(x)))
    # remove punctuation
    df[new_field] = df[new_field].apply(lambda x: re.sub('[^\w\s]', '', str(x)))
    # remove stop words
    stop = stopwords.words('english')
    df[new_field] = df[new_field].apply(lambda text: " ".join(word for word in text.split() if word not in stop))
    # lemmatize the text so different suffixes of the same root can be compared
    lemtzr = WordNetLemmatizer()
    df[new_field] = df[new_field].apply(lambda text: " ".join(lemtzr.lemmatize(word) for word in text.split()))
    # stem the text to normalize verb tenses, etc.
    custom_words = ['families', 'family', 'community', 'communities', 'volunteers', 'volunteer', 'provider', 'provides' 'provided', 'provide',
                    'providing', 'providers', 'education', 'educated', 'educating', 'educates' 'educate', 'educational', 'foundational',
                    'foundations', 'foundation', 'includes', 'include', 'including', 'inclusive', 'inclusion',
                    'institution', 'institutional', 'institute' 'institutes', 'instituted', 'animal', 'animals', 'unity',
                    'unite', 'unites', 'united']
    custom_stems = ['family', 'family', 'community', 'community', 'volunteer', 'volunteer', 'provide', 'provide', 'provide', 'provide',
                    'provides', 'provides', 'educate', 'educate', 'educate', 'educate', 'educate', 'educate', 'foundation',
                    'foundation', 'foundation', 'include', 'include', 'include', 'include', 'include',
                    'institute', 'institute', 'institute', 'institute', 'institute', 'animal', 'animals', 'unite',
                    'unite', 'unite', 'unite']
    stemmer = PorterStemmer()
    df[new_field] = df[new_field].apply(lambda text: " ".join(
        custom_stems[custom_words.index(word)] if word in custom_words else stemmer.stem(word) for word in text.split()))
    return df

def transform_mask(mask):
    def transform_format(val):
        if val == 0:
            return 255
        else:
            return val
    transformed_mask = np.zeros((mask.shape[0], mask.shape[1]), dtype=np.int32)
    for i in range(len(mask)):
        transformed_mask[i] = list(map(transform_format, mask[i]))
    return transformed_mask

def create_wordcloud(df, field_name, data_subset, mask_image=None):
    transform_exceptions = ['Environment']
    mask = None
    contour_width = 0
    max_words = 2000
    if mask_image is not None:
        raw_mask = np.array(Image.open("images/" + mask_image + ".png").convert('P'))
        if mask_image in transform_exceptions:
            mask = raw_mask
        else:
            mask = transform_mask(raw_mask)
        contour_width = 3
        max_words = 500
    wc = WordCloud(background_color="white", max_words=max_words, width=800, height=400, mask=mask, contour_width=contour_width)
    wc.generate(' '.join(df[field_name]))
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    font = {'family': 'serif',
            'color': 'black',
            'weight': 'bold',
            'size': 16,
            }
    plt.title('Mission Text Wordcloud for ' + data_subset + ' Charities', fontdict=font)
    plt.show()

def compare_wordclouds(df):
    # generate multiple word clouds to compare the language used by different categories of charities
    for category_tuple in df.groupby('category_l1'):
        create_wordcloud(category_tuple[1], 'mission_nlp', category_tuple[0], mask_image=category_tuple[0])

def sentiment_analysis(df, field_name):
    def sentiment_func(x):
        sentiment = TextBlob(x['mission_nlp'])
        x['polarity'] = sentiment.polarity
        x['subjectivity'] = sentiment.subjectivity
        return x
    sa_df = df[df[field_name].isnull() == False]
    sa_df = sa_df.apply(sentiment_func, axis=1)
    sa_df.plot.scatter('polarity', field_name, s=1)
    plt.title('Relationship Between Mission Polarity and Overall Score')
    plt.xlabel('Mission Polarity')
    plt.ylabel('Overall Score')
    plt.show()
    sa_df.plot.scatter('subjectivity', field_name, s=1)
    plt.title('Relationship Between Mission Subjectivity and Overall Score')
    plt.xlabel('Mission Subjectivity')
    plt.ylabel('Overall Score')
    plt.show()