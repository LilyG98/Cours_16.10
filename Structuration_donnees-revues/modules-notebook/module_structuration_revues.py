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

def url_to_df_AHMC (url):
    
    """
    Cette fonction a pour objectif de structurer en un dataframe l'ensemble des articles des Annales de médecine et d'hygiène coloniales à partir des descriptifs d'articles contenus sur le site de la Bibliothèque interuniversitaire de Santé.
    """
    
    # 1 : Extraire de chaque page de sommaire d'un numéro sur BIUS la page et le titre des articles ###

    ## 1.1. A partir de l'url du sommaire du numéro 
    Liste_entrees = []
    r = requests.get(url)
    
    ## 1.2. Recours à BeautifulSoup pour analyser l'HTML
    
    ##### extraction du corpus html du numéro 
    numero_AHMC_soup = BeautifulSoup (r.text, features="lxml")

    ##### extration des balises <div class='titre' ...> </div>
    div_ens_tag = numero_AHMC_soup.find_all("div", {"class":"tableau1"})


    ##### 1.2.2. extraire les href / l'année / le numéro
    for balise in div_ens_tag:
        l = list(balise)
        ahref = str(l[1])
        SearchStr = "x([0-9]{4})x([0-9]{2})"
        Result = re.search(SearchStr,ahref)
        intermed = str(Result)

        revue_annee = re.search(r"[0-9]{4}",intermed).group(0)
        revue_numero = re.search(r"([0-9]{2})'",intermed).group(1)

    
    # 2 : Nettoyer les entrées pour ne conserver que les articles#####

    ## 2.1. Liste ne conservant que la page et le contenu de l'entrée
    
    ##### NB : je fais exprès de dire "entrée" et non "article" car il y a d'autres contenus que des articles
    
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
            else :
                Liste_entrees_no_doublesentrees.append(tupple_to_list)

    #### 2.3 Retirer les sections qui ne nous intéressent pas
                
    Liste_articles = []

    for entree in Liste_entrees_no_doublesentrees :
    
        #Bulletins officiels 
        if re.search(r"(.*)?Bulletin officiel(.*)?", entree[1]):
            pass 

        #Journaux
        elif re.search(r"(.*)?((J|j)ournaux)(.*)?",entree[1]):
            pass

        #Livres recus
        elif re.search(r"(.*)?(Livres reçus)(.*)?",entree[1]):
            pass

        #Bibliographies
        elif re.search(r"(.*)?(Bibliographies?)(.*)?",entree[1]):
            pass

        #Revue analytique
        elif re.search(r"(.*)?(Revue (analytique)?)(.*)?",entree[1]):
            pass
        
        #Table analytique
        elif re.search(r"(.*)?(Table (analytique)?)(.*)?",entree[1]):
            pass
        
        #Nécrologies
        elif re.search(r"(.*)?(N(e|é)crologie)(.*)?",entree[1]):
            pass

        else :
            Liste_articles.append(entree)

    ######### 3 : MISE EN DATAFRAME #########

     ### 3.1. List to DF ###
    df = pd.DataFrame(Liste_articles)
    #print(df)
    df.columns = ['article_page', 'article_titre','revue_annee','revue_numero']
    
    
    ### 3.2.SEPARATION : TITRE ARTICLE ET AUTEUR ###

    #3.2.1. créer une nouvelle colonne avec nom(s)  auteur(s) (et ce qui suit) : 
    SearchAuteur = "(.*) (P|p)ar (.*)"
    df['article_auteur'] = df["article_titre"].str.split(SearchAuteur).str[3]

    #3.2.2. retirer nom(s) auteur(s) (et ce qui suit) de article_titre
     
    df.article_titre = df.article_titre.str.replace(SearchAuteur, r"\1") 
    
    ### 3.3. SEPARATION : AUTEUR ET DETAIL ARTICLE
    
    ##Séparer les noms d'auteurs du détail des articles 
    SearchDetail = "(.*)\.(.*)"
    df['article_detail'] = df["article_auteur"].str.split(SearchDetail).str[2]

    #retirer nom auteurs (et ce qui suit) de article_titre
    for index in range(len(df.article_auteur)-1):
        if type(df.iloc[index,4]) == str:
            df.iloc[index,4] = re.sub(SearchDetail, r"\1", df.iloc[index,4])
        
    ####3.4. INSERER : article_id 
    #modèle de l'id : NomRevue-Numero-Pagedébut
    df['article_id'] = "AHMC-"+df["revue_numero"]+"-"+df["article_page"]

        
    ###4. : MISE AU PROPRE POUR EXPORTATION #####
   
    ####4.1. Reorganisation des colonnes suite aux ajouts            
    cols = df.columns.tolist()
    cols = [cols[6],cols[4],cols[5],cols[1],cols[2],cols[3],cols[0]]
    df=df[cols]
    
    #### 4.2. Retirer les white spaces en début de string 
    for i in range(len(df)):
        for col in range (1,4):
            if type(df.iloc[i,col]) is str :
                if re.match(r"^ ",df.iloc[i,col]):
                    df.iloc[i,col] = df.iloc[i,col].replace(r"^ ",r"")
    
    ##### 4.3. : Return du df et mise en csv
    
    return df
    



    """ AUTRE FONCTION POUR LES "ARCHIVES DE MÉDECINE NAVALE" EN RAISON D'UN FORMATAGE DIFFERENT DES INFORMATIONS"""
    

def url_to_df_AMN (url):
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

        #isoler année : 
        if re.search(r"[0-9]{4}",intermed) is None:
            pass
        else :
            revue_annee = re.search(r"[0-9]{4}",intermed).group(0)

        #isoler numéro : 
        if re.search(r"[0-9]{4}",intermed) is None:
            pass
        else :
            revue_numero = re.search(r"([0-9]{2})'",intermed).group(1)


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

    #print(Liste_entrees)
    #### 2.2. Pour les pages d'un nouvel article qui débute, ne conserver que le nom du nouveau
    Liste_entrees_no_doublesentrees= []

    for entree_t_list in Liste_entrees :
        for entree_t_tupple in entree_t_list :
                tupple_to_list = list(entree_t_tupple)
                tupple_to_list.append(revue_annee)
                tupple_to_list.append(revue_numero)
    #            if re.search(r"(.*\/(.*))",tupple_to_list[1],0, re.MULTILINE):
    #                tupple_to_list[1] = re.sub(r"(.*\/(.*))","\\2",tupple_to_list[1],0, re.MULTILINE)
    #                tupple_to_list[1] = re.sub(r"^ ","",tupple_to_list[1])
                Liste_entrees_no_doublesentrees.append(tupple_to_list)

    #### 2.3 Retirer les sections qui ne nous intéressent pas

    Liste_articles = []

    for entree in Liste_entrees_no_doublesentrees :

        #Bulletins officiels 
        if re.search(r"(.*)?Bulletin officiel(.*)?", entree[1]):
            pass 

        #Journaux
        elif re.search(r"(.*)?((J|j)ournaux)(.*)?",entree[1]):
            pass

        #Livres recus
        elif re.search(r"(.*)?(Livres reçus)(.*)?",entree[1]):
            pass

        #Bibliographies
        elif re.search(r"(.*)?(Bibliographies?)(.*)?",entree[1]):
            pass

        #Table analytique
        elif re.search(r"(.*)?(Table (analytique)?)(.*)?",entree[1]):
            pass

        #Nécrologies
        elif re.search(r"(.*)?(N(e|é)crologie)(.*)?",entree[1]):
            pass

        else :
            Liste_articles.append(entree)


    ######### 3 : MISE EN DATAFRAME #########
     ### 3.1. List to DF ###
    df = pd.DataFrame(Liste_articles)
    #print(df)
    df.columns = ['article_page', 'article_titre','revue_annee','revue_numero']


    ### 3.2.SEPARATION : TITRE ARTICLE ET AUTEUR ###

    #3.2.1. créer une nouvelle colonne avec nom(s)  auteur(s) (et ce qui suit) : 
    SearchAuteur = "(.*) (P|p)ar (.*)"
    df['article_auteur'] = df["article_titre"].str.split(SearchAuteur).str[3]

    #3.2.2. retirer nom(s) auteur(s) (et ce qui suit) de article_titre

    df.article_titre = df.article_titre.str.replace(SearchAuteur, r"\1") 


    ### 3.3. DETAIL ARTICLES ###

    ##Séparer les noms d'auteurs du détail des articles 
    SearchDetail = "\.{3}(.*)"

    # for auteur in df["article_auteur"] :
    #     if type(re.search(SearchDetail,auteur)) == "_regex.Match" :
    #         df['article_detail'] = re.search(SearchDetail,auteur).str[1]

    df['article_detail'] = df["article_auteur"].str.split(SearchDetail).str[1]

    # #retirer nom auteurs (et ce qui suit) de article_titre
    df.article_auteur = df.article_auteur.apply(str).str.replace(SearchDetail,r"")


    #### 3.4. SECTIONS DE LA REVUE ####
# Liste_article_section = ["Notes et mémoires originaux","Bulletin clinique","Hygiène et épidémiologie","Revue analytique"]
# List_section = []

# for titre in df['article_titre']:
#     for section in Liste_article_section :
#         if re.search(section,titre):
#             print(titre)

    ####3.5. Reorganisation des colonnes suite aux ajouts            
    cols = df.columns.tolist()
    cols = [cols[4],cols[5],cols[1],cols[2],cols[3],cols[0]]
    df=df[cols]
    
    return (df)
    
    ##### 4 : EXPORTATION DU DF DANS LE CSV ###### 
    #df.article_titre.str.strip()
    #df.to_csv('FileName.csv')

    
    

  
""" RETIRER LES ARTICLES EN DOUBLONS (Attention : retire aussi les description, à gérer seule par ailleurs"""
def df_sans_doublons (df):
    
    df2=df.drop_duplicates(subset=['article_titre'])
    return(df2)
    


