"""
    scrape un suggestions website and create dictionaries
"""

from bs4 import  BeautifulSoup
import urllib

import spacy
parser = spacy.load('en')
from nltk.corpus import stopwords

import string
string.punctuation
punct = " ".join(string.punctuation).split(" ")

from numpy import dot
from numpy.linalg import norm

import pickle


def get_levels(soup):
    levels = {}
    count = 1
    for strong_tag in soup.find_all('strong'):
        levels[count] = strong_tag.text
        count += 1
    return levels


def get_suggestions():
    url = "http://www.un.org/sustainabledevelopment/takeaction/"
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r)
    levels = get_levels(soup)
    bullet_points = soup.find_all("ul")
    li_list_full = []
    for ul_tag in bullet_points:
        for li_tag in ul_tag.find_all('li'):
            a = li_tag.text.split(" ")
            if len(a) > 4:
                li_list_full.append(li_tag)
    #entering sentence lines manually because
    #something wrong with beautifulsoup parsing html
    level_bullets = {}
    level_bullets[1] = li_list_full[36:47]
    level_bullets[2] = li_list_full[48:63]
    level_bullets[2] = li_list_full[64:77]
    return level_bullets, levels


def get_np(sent):
    parsed = parser(sent)
    np = []
    STOP_POS= ["PRON"]
    POS_TO_INCLUDE = ["VERB", "NOUN", "PROPN"]
    for noun_phrase in parsed.noun_chunks:
        if len(noun_phrase) == 1:
            for tok in noun_phrase:
                if tok.pos_ not in STOP_POS:
                    np.append(noun_phrase.orth_.lower())
        elif noun_phrase.orth_ not in np:
            without_stop = ' '.join([word.orth_.lower() for word in noun_phrase if word.orth_ not in stopwords.words('english') + punct])
            np.append(noun_phrase.orth_.lower())
            if n not in np:
                np.append(without_stop)
            for token in noun_phrase:
                if token.pos_ in POS_TO_INCLUDE:
                    lemma = token.lemma_
                    if lemma not in np:
                        np.append(lemma)
    all_keywords.update(np)
    return np

def get_np_v2(sent):
    parsed = parser(sent)
    np = []
    STOP_POS= ["PRON"]
    POS_TO_INCLUDE = ["VERB", "NOUN", "PROPN"]
    for word in parsed:
        # for w in word:
        if word.pos_ not in STOP_POS and word.pos_ in POS_TO_INCLUDE and\
                word.orth_ not in stopwords.words('english') + punct:
            np.append(word.orth_.lower())
            np.append(word.lemma_)
    np = list(set(np))

    return np

def cosine_sim(v1,v2):
    return dot(v1, v2) / (norm(v1) * norm(v2))


def find_related_keywords(keywords, all_words):
    related = []
    for word in keywords:
        if len(word.split(" ")) == 1:
            parsed_word = parser.vocab[word]
            all_words.sort(key=lambda w: cosine_sim(w.vector, parser(word).vector), reverse = True)
            for word in all_words[:10]:
                #get top 10 similar words
                if word not in keywords:
                    related.append(word.orth_)
    return related


def find_links(sent):
    links = []
    for a in sent.find_all('a', href=True):
        links.append(a["href"])
    return links


def create_sentence_object(l, sent):
    sent_object = {}
    sent_object["level"] = l
    sent_object["level_name"] = levels[l]
    sent_object["sentence"] = sent.text
    sent_object["links"] = find_links(sent)
    # sent_object["keywords"] = get_np(sent.text)
    sent_object["keywords"] = get_np_v2(sent.text)
    return sent_object


def create_inverse_dict(sentence_keyword_dict):
    keyword_sentence_dict = {}
    for sent in sentence_keyword_dict:
        keywords = sentence_keyword_dict[sent]["keywords"]
        # related_keywords = sentence_keyword_dict[sent]["related keywords"]
        all_keywords = keywords #+ related_keywords
        for kwd in all_keywords:
            if kwd not in keyword_sentence_dict:
                keyword_sentence_dict[kwd] = []
                keyword_sentence_dict[kwd].append(sent)
            else:
                keyword_sentence_dict[kwd].append(sent)
    return keyword_sentence_dict


if __name__ == '__main__':
    all_keywords = set()
    sentence_keyword_dict = {}
    level_bullets, levels = get_suggestions()
    running_count = 0
    for l in level_bullets:
        for sent in level_bullets[l]:
            sentence_keyword_dict[running_count] = create_sentence_object(l, sent)
            running_count += 1
    keyword_sentence_dict = create_inverse_dict(sentence_keyword_dict)
    pickle.dump(keyword_sentence_dict, open("keyword_sentence_dict_v2.p", "wb"))
    pickle.dump(sentence_keyword_dict, open("sentence_keyword_dict_v2.p", "wb"))
