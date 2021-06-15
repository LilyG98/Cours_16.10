#Généraux : 
import spacy
import fr_core_news_md
import pandas as pd
import numpy as np
import re

#Pour la matrice document-terme:
from sklearn.feature_extraction.text import CountVectorizer
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop

#Pour la màj des StopWords: 
from spacy.lang.fr.stop_words import STOP_WORDS

#Pour le WordCloud : 
from wordcloud import WordCloud

#Importation du pretrained model en français
nlp = spacy.load("fr_core_news_md")


def df_to_txt_list_art(df,output_path):
    """ Passer les df en format txt sous forme de liste d'articles."""

    df.to_string(output_path,index=False)

def df_to_txt_fullANDlist(df,output_path):
    """ Exporter les articles de df comme un seul bloc dans un fichier .txt """

    with open (output_path,"w") as f:
#         for article in df.article_titre:
        art_list = df.article_titre.tolist()
        f.write("".join(art_list))
    return art_list
#             f.write(article+" \n ") #le output est une liste à une entrée.
#             list_articles.append(article)
#         return list_articles
    print("ensemble des articles exportés comme un bloc dans: ",output_path,"et objet list en return")
    
def doc_term_matrix(df):
    """ Création d'une matrice de mots à partir d'un dataframe simple.
    input : un df avec les années en col et les mots en ligne"""
    cv = CountVectorizer(stop_words=list(fr_stop))
    data_cv = cv.fit_transform(df.articles_annee)
    data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
    data_dtm.index = df.index
    return(data_dtm)

def top_words_dict(dtm,n):
    """ Créer un dictionnaire des n mots les plus fréquents avec leur nombre d'occurences associée
    input : 1 - la matrice de mot créée avec cod_term_matrix
            2 - n (int) le nbr de mots à récupérer"""
    dtm=dtm.transpose()
    top_dict = {}
    for c in dtm.columns:
        top = dtm[c].sort_values(ascending=False).head(n)
        top_dict[c]= list(zip(top.index, top.values))

    return top_dict
    
def visu_top_words(top_dict,n):
    """Permet de visualiser plus facilement les n principaux mots sous forme de str
    input : 1 - le dictionnaire créé avec top_words_dict 
            2 - n (int) le nbr de mots à récupérer"""               
    for annee, top_words in top_dict.items():
        print(annee)
        print(', '.join([word for word, count in top_words[0:n-1]]))
        print('---')

def visu_top_words_comparaison(top_dict,n):
    """ DICO Comparaison : Permet de visualiser plus facilement les n principaux mots sous forme de str
    input : 1 - le dictionnaire créé avec top_words_dict 
            2 - n (int) le nbr de mots à récupérer""" 
    
    for annee, top_words in top_dict.items():
        print(annee)
        for tup, count in top_words[0:n]:
            print(', '.join([tup[0],tup[1]]))
        print('---')
    

def màj_stopwords(list_add_stopwords,df):
    """ Mise à jour de la liste des StopWords au regard des observations réalisées et application à un df
    input : 1 - liste des termes à ajouter à la StopWords de spacy
            2 - le dataframe par année créé au début du notebook
    """
    
    for word in list_add_stopwords:
        STOP_WORDS.add(word)
        stop = list(fr_stop)
    
    df["articles_annee"]=df["articles_annee"].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    return df
    

def WordCloud(label):
    words = ''
    for msg in data[data[TARGET_COLUMN] == label[TEXT_COLUMN]]:
        msg = msg.lower()
        words += msg + ' '
        wordcloud = WordCloud(width=600, height=600).generate(words)
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()
        