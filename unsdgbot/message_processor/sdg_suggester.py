import pickle
from nltk.stem import WordNetLemmatizer
import string

class SDGSuggester(object):
    def __init__(self, max_length=3):
        self.keyword_sentence_dict = pickle.load(open("message_processor/Suggestions/keyword_sentence_dict.p", "rb"))
        self.sentence_keyword_dict = pickle.load(open("message_processor/Suggestions/sentence_keyword_dict.p", "rb"))
        self.wnl = WordNetLemmatizer()
        self.punct = " ".join(string.punctuation).split(" ")
        self.MAX_LENGTH = max_length


    def process_message(self, message_text):
        message_text = message_text.lower()
        for p in self.punct:
            if p in message_text:
                message_text = message_text.replace(p, "")
        parsed = message_text.split(" ")
        sent = []
        for word in parsed:
            sent.append(self.wnl.lemmatize(word))
        sentences = set()
        for kwd in self.keyword_sentence_dict:
            if kwd in sent:
                sentences.update(self.keyword_sentence_dict[kwd])
        sentences_to_return = []
        count = 0
        for sent in sentences:
            sentence = self.sentence_keyword_dict[sent]["sentence"]
            url = self.sentence_keyword_dict[sent]["links"]
            if len(sentence) > 320:
                sent_arr = sentence.split(".")
                mid_idx = len(sent_arr)/2
                sentences_to_return.append("".join(sent_arr[:mid_idx]))
                sentences_to_return.append("".join(sent_arr[mid_idx:]))
            else:
                sentences_to_return.append(sentence)
            if len(url) > 1:
                sentences_to_return.append("Go to these links to find out more: " +
                                           ", ".join(url))
            elif len(url) > 0:
                sentences_to_return.append("Go here to find out more: " + " ".join(url))
            count += 1
            if count == self.MAX_LENGTH:
                break
        return sentences_to_return
