import pickle
import spacy
parser = spacy.load('en')

class SDGSuggester(object):
    def __init__(self, max_length=3):
        self.keyword_sentence_dict = pickle.load(open("Suggestions/keyword_sentence_dict.p", "rb"))
        self.sentence_keyword_dict = pickle.load(open("Suggestions/sentence_keyword_dict.p", "rb"))
        self.MAX_LENGTH = max_length

    def process_message(self, message_text):
        parsed = parser(message_text)
        sent = []
        for word in parsed:
            sent.append(word.lemma_)
        sentences = set()
        for kwd in self.keyword_sentence_dict:
            if kwd in sent:
                sentences.update(kwd_sent[kwd])
        sentences_to_return = []
        count = 0
        for sent in sentences:
            sentence = self.sentence_keyword_dict[sent]["sentence"]
            if len(sentence) > 320:
                sent_arr = sentence.split(".")
                mid_idx = len(sent_arr)/2
                sentences_to_return.append("".join(sent_arr[:mid_idx]))
                sentences_to_return.append("".join(sent_arr[mid_idx:]))
            else:
                sentences_to_return.append(sentence)

            count += 1
            if count == self.MAX_LENGTH:
                break
        return sentences_to_return
