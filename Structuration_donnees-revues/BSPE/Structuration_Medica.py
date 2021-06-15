""" 
L'intérêt de ce fichier est d'obtenir un df pandas ayant un article_id en plus des autres données.
    Il peut être appliqué à n'importe lequel des fichiers Excel envoyés par l'équipe du projet Medica de la Bibliothèque interuniversitaire de médecine (préalablement tranformés en tsv!!!)

"""

import requests
import csv
import pandas as pd
import re

def Medica_to_dfMedica (tsv):
    """ L'intérêt de cette fonction est d'obtenir un df pandas ayant un article_id en plus des autres données.
    Il peut être appliqué à n'importe lequel des fichiers Excel envoyés par l'équipe du projet Medica de la Bibliothèque interuniversitaire de médecine (préalablement tranformés en tsv!!!)
    
    Format de l'id : "REVUEABBR-ANNEE-PAGE"
    
    """
    
    #1. Entrer un des fichiers envoyés par l'équipe de MEDICA en format tsv 
    
    with open (tsv) as BSPE_Medica:
	df_Medica = pd.read_csv(BSPE_Medica,sep='\t')
    
    
    #2. Retirer la colonne "Unnamed:O" qui ne sert à rien
    df_Medica.drop('Unnamed: 0',
    axis='columns', inplace=True)
    
    #3.1. Création de l'id de chaque article : 

    #3. Créer les colonnes qui accueilleront les données 
    
    #3.1.1. Nouvelle colonne pour l'article-id : 
    df_Medica["article_id"] = df_Medica.apply(lambda _: '', axis=1)

    #3.1.2. Nouvelle colonne pour l'année : 
    df_Medica["revue_annee"] = df_Medica.apply(lambda _: '', axis=1)

    #3.2. Réorganisation des colonnes pour mettre en avant article_id, page,chapitre, année qui sont les éléments que je retrouve dans mon df personnel. 
    df_Medica = df_Medica[['cote',
     'article_id',
     'page',
     'chapitre',
     'revue_annee',
     'pagecle',
     'refimg',
     'pagimgcle',
     'pagimg',
     'pagimgtxt',
     'pagimgtxtcom']]
    
    
    #3.3. Création du "article_id" de chaque entrée 
    ##NB : cette opération est très longue car les df de Medica comptent  pour le moins 50 000 lignes car ils contiennent le descriptif de chacune des pages.

    for i in range (len(df_Medica)):
    #3.3. Extraction de l'année : 
    df_Medica.iloc[i,4] = re.search(r'\d{4}',df_Medica.iloc[i,0]).group(0)
    
    #3.2. Constitution de l'article_id
    df_Medica.iloc[i,1] = "BSPE-"+df_Medica.iloc[i,4]+"-"+df_Medica.iloc[i,2]
    
    #4. Exportation
    return df_Medica
    
    df_Medica.to_csv("./df_Medica_article_id.tsv", sep="\t", index=False)
    
    print("df_Medica créé. Un document 'df_Medica_article_id.tsv' est à retrouver dans le repository de votre notebook.")
   

    
def dfMedica_to_ShortdfMedica (doc_Medica):
    """ Raccourcir le df_Medica pour ne conserver que les colonnes 
    => "article_id" : pour faire le Merge avec mes df personnels.
    => "chapitre" : d'om on va extraire les informations sur les Séances et les Sections
    
    
    doc peut être un pd.df ou un fichier tsv ! 
    """
    #Si doc_Medica == df
    if type(doc_Medica) is pd.core.frame.DataFrame:
        df_Medica_court = doc_Medica[["article_id","chapitre"]]
    
    
    #Si doc_Medica == tsv
    elif type(doc_Medica) is <class '_io.TextIOWrapper'> :
        with open (doc_Medica) as BSPE_Medica:
            df_Medica = pd.read_csv(BSPE_Medica,sep='\t')
            df_Medica_court = df_Medica[["article_id","chapitre"]]
        
    return df_Medica_court
    df_Medica.to_csv("./df_Medica_court.tsv", sep="\t", index=False)
    print("df_Medica créé. Un document 'df_Medica_court.tsv' est à retrouver dans le repository de votre notebook.")
    
    
    
    
    
    
    
    
    
