from bs4 import BeautifulSoup
from lxml import html
import requests
import regex as re
import pandas as pd

"""

Ce module a pour objectif principal de répondre au besoin de structurer les articles des revues AHMC et AMN à partir du site de la Bibliothèque interuniversitaire de santé, la BIUS.

Nous avons déjà par ailleurs créé les documents contenant l'ensemble des liens vers les pages de sommaire de chaque numéros. L'objectif est donc ici de mettre en place un ensemble de fonctions qui nous permettront de mettre en place très facilement l'ensemble des démarches pour structurer les sommaires comme on le souhaite. Il faudra après évidement les reprendre à la main parce que c'est pas drôle sinon !! 

L'idée est à terme de pouvoir faire dans mon notebook une boucle où j'enchainerais l'ensemble des fonctions définies ici ! 

"""

""" 1 : Extraire de chaque page de sommaire d'un numéro sur BIUS la page et le titre des articles """

def url_to_df (url):
    ### 1 : Extraire de chaque page de sommaire d'un numéro sur BIUS la page et le titre des articles ###
    
    #### 1.1. A partir de l'url du sommaire du numéro 
    Liste_entrees = []
    r = requests.get(url)
    
    ##### extraction du corpus html du numéro 
    numero_AHMC_soup = BeautifulSoup (r.text, features="lxml")
    
    ##### extration des balises <div class='titre' ...> </div>
    div_ens_tag = numero_AHMC_soup.find_all("div", {"class":"tableau1"})


    ##### 1.2.2. extraire les href / l'année / le numéro
    for balise in div_ens_tag:
        l = list(balise)
        ahref = str(l[1])
        SearchAnneeNum = "x([0-9]{4})x([0-9]{2})"
        Result = re.search(SearchAnneeNum,ahref)
        intermed = str(Result)
        revue_annee = re.search(r"([0-9]{4})",intermed).group(1)
        revue_numero = re.search(r"([0-9]{2})'",intermed).group(1)


    
    #### 2 : Nettoyer les entrées pour ne conserver que les articles#####

    #### 2.1. Liste ne conservant que la page et le contenu de l'entrée
    
    ######### NB : je fais exprès de dire "entrée" et non "article" car il y a d'autres contenus que des articles
    
    liste_page_titre = []
        
    for balise in div_ens_tag:
        liste_page_titre.append(balise.text)

    for entree in liste_page_titre :
        RE_entree = re.findall(r"\t(\d{1,3})(.*)",entree)
        Liste_entrees.append(RE_entree)




#### 2.2. Pour les pages d'un nouvel article qui débute, ne conserver que le nom du nouveau
    Liste_entrees_no_doublesentrees= []
    
    for entree_t_list in Liste_entrees :
        for entree_t_tupple in entree_t_list :
            tupple_to_list = list(entree_t_tupple)
            tupple_to_list.append(revue_annee)
            tupple_to_list.append(revue_numero)
            if re.search(r"(.*\/(.*))",tupple_to_list[1],0, re.MULTILINE):
                tupple_to_list[1] = re.sub(r"(.*\/(.*))","\\2",tupple_to_list[1],0, re.MULTILINE)
                tupple_to_list[1] = re.sub(r"^ ","",tupple_to_list[1])
                Liste_entrees_no_doublesentrees.append(tupple_to_list)

    Liste_articles = Liste_entrees_no_doublesentrees

    
    for entree in Liste_entrees_no_doublesentrees :
        if re.search(r"(.*)?(Bulletin officiel)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?((J|j)ournaux)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Livres reçus)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Bibliographie)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Table analytique)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(N(e|é)crologie)(.*)?",entree[1]):
            Liste_articles.remove(entree)
           
      

    ######### 3 : MISE EN DATAFRAME #########

    ### 3.1. df ###
    df = pd.DataFrame(Liste_articles)
    df.columns = ['article_page', 'article_titre','revue_annee','revue_numero']
    
    ### 3.2.DETAIL ARTICLES ###
    
    #créer une nouvelle colonne avec le nom des auteurs (et ce qui suit) : 
    SearchAuteur = ".*(P|p)ar(.*)"
    df['article_auteur'] = df["article_titre"].str.split(SearchAuteur).str[2]
    
    #df['article_auteur'] = df["article_titre"].str.split(r"Par ((.+)?(le)?) Docteur(\.)?(.*)").str[5]

    #retirer nom auteurs (et ce qui suit) de article_titre
      
    df.article_titre = df.article_titre.str.replace(r"(.*)(Par (.*)?(le)? Docteur(\.)? (.*))", r"\1") #FONCTIONNE

    ### 3.3. DETAIL ARTICLES ###
    
    ##Séparer les noms d'auteurs du détail des articles 
    df['article_detail'] = df["article_auteur"].apply(str).str.split(r"\.(.*)").str[1]

    #retirer nom auteurs (et ce qui suit) de article_titre
    df.article_auteur = df.article_auteur.apply(str).str.replace(r"\.(.*)",r"")
    
    #### 3.4. SECTIONS DE LA REVUE ####
    Liste_article_section = ["Contribution à la géographie médicale","Clinique d'Outre-Mer","Variétés","rapport"]

    for section in Liste_article_section :
        for titre in df['article_titre']:
            if re.match(section,str(titre)):
                df['article_section'] = section

    ####3.5. Reorganisation des colonnes suite aux ajouts            
    cols = df.columns.tolist()
    cols = [cols[4],cols[5],cols[1],cols[2],cols[3],cols[0]]
    df=df[cols]
    
    return (df)
    
    ##### 4 : EXPORTATION DU DF DANS LE CSV ###### 
    #df.article_titre.str.strip()
    #df.to_csv('FileName.csv')

    
    
    
    """ AUTRE FONCTION POUR AMN EN RAISON D'UN FORMATAGE DIFFERENT DES INFORMATIONS"""
    
    
    
    
    
def url_to_df_AMN (url):
    ### 1 : Extraire de chaque page de sommaire d'un numéro sur BIUS la page et le titre des articles ###
    
    #### 1.1. A partir de l'url du sommaire du numéro 
    #Liste_entrees = []
    r = requests.get(url)
    
    ##### extraction du corpus html du numéro 
    numero_AMN_soup = BeautifulSoup (r.text, features="lxml")
    
    ##### extration des balises <div class='titre' ...> </div>
    div_ens_tag = numero_AMN_soup.find_all("div", {"class":"tableau1"})


    ##### 1.2.2. extraire les href / l'année / le numéro
    for balise in div_ens_tag:
        l = list(balise)
        ahref = str(l[1])
        intermed = re.search(r"x([0-9]{4})x([0-9]{2})",ahref)
        intermed = str(intermed)
        #isoler l'année:
        revue_annee = re.search(r"[0-9]{4}",intermed) 
        #isoler le numero : 
        revue_numero = re.search(r"([0-9]{2})$",intermed)

    
    #### 2 : Nettoyer les entrées pour ne conserver que les articles#####

    #### 2.1. Liste ne conservant que la page et le contenu de l'entrée
    
    liste_page_entrees = []
    Liste_entrees = []
    
    ######### NB : je fais exprès de dire "entrée" et non "article" car il y a d'autres contenus que des articles
    for balise in div_ens_tag:
        liste_page_entrees.append(balise.text)

    for entree in liste_page_entrees :
        RE_entree = re.findall(r"\t(\d{1,3})(.*)",entree)
        Liste_entrees.append(RE_entree)


#### 2.2. Pour les pages d'un nouvel article qui débute, ne conserver que le nom du nouveau
#    Liste_entrees_no_doublesentrees= []
    
#    for entree_t_list in Liste_entrees :
#        for entree_t_tupple in entree_t_list :
#            tupple_to_list = list(entree_t_tupple)
#            tupple_to_list.append(revue_annee)
#            tupple_to_list.append(revue_numero)
#            if re.search(r"(.*\/(.*))",tupple_to_list[1],0, re.MULTILINE):
#                tupple_to_list[1] = re.sub(r"(.*\/(.*))","\\2",tupple_to_list[1],0, re.MULTILINE)
#                tupple_to_list[1] = re.sub(r"^ ","",tupple_to_list[1])
               # Liste_entrees_no_doublesentrees.append(tupple_to_list)

    #Liste_articles = Liste_entrees_no_doublesentrees

    Liste_articles = Liste_entrees
    
#    for entree in Liste_entrees_no_doublesentrees :
    for entree in Liste_entrees :
        if re.search(r"(.*)?(Bulletin officiel)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?((J|j)ournaux)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Livres reçus)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Bibliographie)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(Table analytique)(.*)?",entree[1]):
            Liste_articles.remove(entree)
        elif re.search(r"(.*)?(N(e|é)crologie)(.*)?",entree[1]):
            Liste_articles.remove(entree)

    ######### 3 : MISE EN DATAFRAME #########

    ### 3.1. df ###
    df = pd.DataFrame(Liste_articles)
    #df.columns = ['article_page', 'article_titre','revue_annee','revue_numero']
    
    ### 3.2.DETAIL ARTICLES ###
    
    #créer une nouvelle colonne avec le nom des auteurs (et ce qui suit) : 
  #  df['article_auteur'] = df["article_titre"].str.split(r"Par ((.+)?(le)?) Dr(\.)?(.*)").str[5]

    #retirer nom auteurs (et ce qui suit) de article_titre
 #   df.article_titre = df.article_titre.str.replace(r"(.*)(Par (.*)?(le)? Dr(\.)? (.*))", r"\1") #FONCTIONNE

    ### 3.3. DETAIL ARTICLES ###
    
    ##Séparer les noms d'auteurs du détail des articles 
    df['article_detail'] = df["article_auteur"].apply(str).str.split(r"\.(.*)").str[1]

    #retirer nom auteurs (et ce qui suit) de article_titre
    df.article_auteur = df.article_auteur.apply(str).str.replace(r"\.(.*)",r"")
    
    #### 3.4. SECTIONS DE LA REVUE ####
    Liste_article_section = ["Contribution à la géographie médicale","Clinique d'Outre-Mer","Variétés","rapport"]

    for section in Liste_article_section :
        for titre in df['article_titre']:
            if re.match(section,str(titre)):
                df['article_section'] = section

    ####3.5. Reorganisation des colonnes suite aux ajouts            
#    cols = df.columns.tolist()
#    cols = [cols[4],cols[5],cols[1],cols[2],cols[3],cols[0]]
#    df=df[cols]
    
    return (df)
    
    ##### 4 : EXPORTATION DU DF DANS LE CSV ###### 
    #df.article_titre.str.strip()
    #df.to_csv('FileName.csv')

