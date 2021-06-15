#Généraux
import pandas as pd
import re
import numpy as np

#Beautiful Soup
from bs4 import BeautifulSoup
import urllib.parse
import requests

#Wikidata
import qwikidata
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api


def ListEntities2df (df,revue,colname):
    """ Cette fonction permet de lister et grouper les entités 
    trouvées pour pouvoir ensuite leur attribuer une localisation
    
    input : 1. le df 
            2. le nom de la revue (pour le output path)
            3. la colonne à traiter
    output : un df des entités de la colonne"""
    dfent=pd.DataFrame()
    dfent[colname]=df[colname] #Créer un nouveau df avec la Serie qu'onsouhaite traiter
    dfentDiv=dfent[colname].str.split(",",expand=True) #Diviser la Série en fonction du nombre de ",". Output = plusieurs colonnes

    listents=[]
    lCol = dfentDiv.columns #liste des colonnes créées
    for i in range (len(lCol)):
        colENT = dfentDiv[lCol[i]]
        for ENT in colENT:
            if type(ENT) is float:
                    pass
            elif ENT == '':
                pass
            else:
                listents.append(ENT)

    while None in listents:
        listents.remove(None) #Retirer les NoneType qui se sont faufillées
    
    dfent = pd.DataFrame(listents)#Retour à la liste de départ que l'on remplace par les données nettoyées
    dfent_group = dfent.groupby(by=0).sum()#Grouper les ents
    output_path = "./output/2-Exploration_GPH-IREL/Revue_ParEntityLabel/"+revue+"/"+revue+colname+".csv"
    dfent_group.to_csv(output_path,index=False)
    print("fichier créé dans",output_path)
    print("Output:liste des entités",colname,"\n")
    return dfent_group.index.values.tolist()




########### RECONSTITUTION ET EXPLOITAITON DES URL ##############


def urlencode (placename):
    """Encoder les noms de lieux (utf8) aux normes url"""
    encoded = urllib.parse.quote(placename)
    return encoded


def Extract_longlat_IREL (url):
    """Extraire les coordonnées géographiques d'un lieu sur la base IREL."""
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    Coordonnees = "".join([coord.text for coord in soup.find_all("span", {"id":"coordonneesGPS"})])
    return Coordonnees

def Extract_longlat_WikiData (List_Q_code,output_path):
    """Extraire les coordonnées géographiques d'un lieu sur la base WikiData.
        NB: nous savons que WikiData offre de bien plus grande possiblités en ayant 
        recours à SQL mais nous n'avons pas eu le temps de nous y former.
    """
    list_lat=[]
    list_long=[]
    list_noCoord =[]

    for Q_code in List_Q_code:
        if type(Q_code) == float:
            print("est nan : ",Q_code)
            list_lat.append("0")
            list_long.append("0")
        else:
            q_dict = get_entity_dict_from_api(Q_code)

            if "P625"in q_dict["claims"] : #Si l'entité a des coordonnées
                
                if 'datavalue' in q_dict["claims"]["P625"][0]["mainsnak"]: #Si on a "datatype" et non "datavalue" 
                    
                    #Latitude
                    q_latitude = q_dict["claims"]["P625"][0]["mainsnak"]['datavalue']['value']['latitude']
                    list_lat.append(q_latitude)

                    #Longitude:
                    q_longitude= q_dict["claims"]["P625"][0]["mainsnak"]['datavalue']['value']['longitude']
                    list_long.append(q_longitude)
                else:
                    print("N'a pas de coordonnées  : ",Q_code)
                    list_noCoord.append(Q_code)
                    list_lat.append("0")
                    list_long.append("0") 

                    

            else:
                print("n'a pas de coordonnées  : ",Q_code)
                list_noCoord.append(Q_code)
                list_lat.append("0")
                list_long.append("0") 

    #Vérifier la taille des listes pour se prémunir d'un 
    print("\nTaille de chaque liste: \n  Liste latitude : ",len(list_lat),"\n  Liste longitude : ",len(list_long),"\n  List_Q_code : ",len(List_Q_code))

    #Récupérer laliste des entités n'ayant pas de coordonnées:
    print("\nQ_code sans coordonnées : ",list_noCoord)
    
    # #création d'un df qui rassemble toutes les infos voulues et que l'on pourra merge par Q_code : 
    df=pd.DataFrame({"Q_code":List_Q_code,"latitude":list_lat,"longitude":list_long})
    
    #Exportation du df :
    print("\n CSV créé ! Chemin vers csv : ",output_path)
    df.to_csv(output_path,index=False)
    #Return :
    return df 

########### NETTOYAGE DES DATAFRAMES ! #########

def nettoyage_df_IREL(dico_IREL):

    df_IREL = pd.DataFrame.from_dict(dico_IREL,orient='index')
    df_IREL = df_IREL.drop(columns=[1])
    df_IREL = df_IREL.rename(columns={0:'titre'})

    #Isoler le titre entier pour pouvoir reconstituer les url
    df_IRELtitre_entier = df_IREL["titre"]
    df_IRELtitre_entier=df_IRELtitre_entier.str.replace(", ","")
    df_IRELtitre_entier=df_IRELtitre_entier.str.replace("'","")

    #Nettoyage du df : 
    df_IREL=df_IREL.titre.str.split(r"\, \'",expand=True)
    df_IREL=df_IREL[1].str.split(r"\(",expand=True)
    df_IREL[1]=df_IREL[1].str.replace(r"\)\'?'","")
    df_IREL[0]=df_IREL[0].str.split(r"\,$",expand=True)
    dfBis = df_IREL[0].str.split(r"\, ",expand=True)
    #Renommer le df: 
    dfBis=dfBis.rename(columns={0:"localité",1:"type",2:"inutile"})
    df_IREL= pd.concat([df_IREL,dfBis],axis=1)
    NewColNames=["Localité","Administration","Lieu-dit","Type","Inutile"]
    df_IREL.rename(columns=dict(zip(df_IREL.columns,NewColNames)),inplace=True)
    
    df_IREL = df_IREL.drop(columns=["Inutile"])
    df_IREL = df_IREL.drop(columns=["Localité"])
    
    #Concaténation avec la Serie contenant les titres entiers
    df_IREL = pd.concat([df_IREL,df_IRELtitre_entier],axis=1)

    print("return: df_IREL nettoyé")
    return df_IREL
    print("fichié créé dans ./IREL/df_IREL.csv")
    df_IREL.to_csv("./IREL/df_IREL.csv")


    
def IREL_Nettoyage_AdminLieuDit(df_IREL):
    """ 
    Nettoyage des colonnes "Administration" et "Lieu-dit" de df_IREL pour pouvoir 
    par la suite rechercher si les noms de notre df apparaîssent dans la base de donnée IREL.
    Le nettoyage concerne 3 problèmes de ponctuation : "/" ";" "\'"
    Dans le cas de "/" et ";", l'objectif est de diviser chaque entité en créant une nouvelle colonne.
    """
    # Patterns à nettoyer :
    pattern_semicolon = r"(\D+) ?\; ?(\D+)"
    pattern_slash = r"(\D+) ?\/ ?(\D+)"
    pattern_apostrophe = r"(\D+)\\(\'\D+)"
    pattern_endspace =r" $"

    #Les deux colonnes auxquelles on souhaite appliquer la fonction :
    colNames=["Administration","Lieu-dit"]

    #Boucle
    for colname in colNames:
        #Préparation de la nouvelle colonne
        new_colname = colname +"_bis"
        df_IREL[new_colname]=df_IREL.apply(lambda _: '', axis=1)
        n_newcolname=len(list(df_IREL.columns))-1 #Nom de la colonne créée
        
        print("\nnouvelle colonne créée : ",new_colname,". au rang : ", n_newcolname)
        
        for i in range (len(df_IREL)):
            entree = df_IREL.iloc[i,0]


            if type(entree) is str:
                if re.search(pattern_endspace,entree): #pour les espaces en fin de string
                    entree=re.sub(pattern_endspace,"",entree)
                
                if re.search(pattern_apostrophe,entree): #pour les "\'"
                    av_apo = re.search(pattern_apostrophe,entree).group(1)
                    ap_apo = re.search(pattern_apostrophe,entree).group(2)
                    entree = av_apo+ap_apo
                    df_IREL.iloc[i,0]=entree
                    
                if re.search(pattern_slash,entree): #pour les "/"
                    df_IREL.iloc[i,0]=re.search(pattern_slash,entree).group(1)
                    df_IREL.iloc[i,n_newcolname]=re.search(pattern_slash,entree).group(2)
                    entree = re.search(pattern_slash,entree).group(2)
                    
                if re.search(pattern_semicolon,entree):# pour les ";"
                    df_IREL.iloc[i,0]=re.search(pattern_semicolon,entree).group(1)
                    df_IREL.iloc[i,n_newcolname]=re.search(pattern_semicolon,entree).group(2)

    return df_IREL




########## LIER LES DF DE REVUES ET LA BASE DE DONNÉES IREL ###################


def MatchGPELOC_IREL(list_GPELOC,IREL_listeclean):
    """ Cette fonction sert à identifier les GPE et LOC de notre df qui sont reconnus par la base de données IREL """
    L_MatchDF_IREL = []
    L_NotMatchDF_IREL = []

    for entree in list_GPELOC:
        if entree in IREL_listeclean:
            L_MatchDF_IREL.append(entree)
        else:
            L_NotMatchDF_IREL.append(entree)
    
    print("nombre d'occurences identifiablespar IREL : ",len(L_MatchDF_IREL),
      "\nnombre d'occurences non identifiables par IREL : ",len(L_NotMatchDF_IREL))
    print("2 outputs : "
          "\n 1/L_MatchDF_IREL"
          "\n 2/L_NotMatchDF_IREL")
    return L_MatchDF_IREL,L_NotMatchDF_IREL


def EgaliserTaille_MatchNot_IREL(L_Match,L_NotMatch):
    """ Fonction pour réégaliser la taille des listes L_Match et L_NotMatche afin de pouvoir les comparer dans un df"""
    
    lengthDiff=abs(len(L_NotMatch)-len(L_Match))

    if len(L_NotMatch) > len(L_Match):
        L_Match += list(np.empty(shape = (lengthDiff)))
        print("nouvelle taille L_Match_IREL2",len(L_Match))

    elif len(L_NotMatch) < len(L_Match):
        L_NotMatch += list(np.empty(shape = (lengthDiff)))
        print("nouvelle taille L_NotMatch_IREL2",len(L_Match))

    else:
        pass
    
    return (L_Match,L_NotMatch)

#Nettoyage en fonction de la désambiguisation 
def nettoyage_desambiguisation(Dico_desambiguisation,list_GPELOC):
    
    """ nettoyage de list_GPELOC en fonction des ajouts manuels au dictionnaire suite aux observations
        input : dico_desambiuisation // list_GPELOC
        output : liste_GPELOC nettoyée
    """
    for i in range(len(list_GPELOC)):
        placename=list_GPELOC[i]
        for key, LValues in Dico_desambiguisation.items():
            for val in LValues:
                if placename == val:#si le nom de lieu correspond à une value du dico
                    list_GPELOC[i]=key #remplacer la value par la clé (identique à celle trouvée dans L_MatcheDF_IREL)
                else:
                    pass
    return(list_GPELOC)








