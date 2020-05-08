# -*- coding:utf-8 -*-

# reference:
#  - https://stackoverflow.com/questions/8897593/how-to-compute-the-similarity-between-two-text-documents
#  - http://billchambers.me/tutorials/2014/12/21/tf-idf-explained-in-python.html


from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDFComparator:

    def __init__(self, text1, text2, lang="en"):
        self.text1 = text1
        self.text2 = text2

    def compare(self):
        vect = TfidfVectorizer(min_df=1)
        tfidf = vect.fit_transform([self.text1, self.text2])

        return (tfidf * tfidf.T).A[0][1]


