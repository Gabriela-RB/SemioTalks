# -*- coding: utf-8 -*-
"""Curso SemioTalks.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15TqJ30nkvL4tvFY1PVknhC-GTCmV1JHq

# **1. Importação de Bibliotecas**

Bibliotecas padrão para manipulação de dados e visualização.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

!pip install bertopic

"""Ferramentas utilizadas para modelagem de tópicos e redução de dimensionalidade."""

from bertopic import BERTopic
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from hdbscan import HDBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from sentence_transformers import SentenceTransformer

"""Biblioteca para manipulação de linguagem natural, usada aqui para lidar com *stopwords* no português."""

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

stopwords_pt = set(stopwords.words('portuguese'))
stopwords_pt=list(stopwords_pt)
vectorizer_model  = CountVectorizer(stop_words=stopwords_pt)

"""Usado para "montar" o Google Drive no Google Colab, possibilitando acesso a arquivos armazenados nele.

"""

from google.colab import drive
drive.mount('/content/drive')

"""# **2. Pré-Processamento**



"""

df=pd.read_csv('/content/drive/MyDrive/Geral.csv', sep='|')
df.head()

"""Substituir as marcações [mention] encontradas no texto por uma string vazia (''), removendo-as."""

def remover_tag(texto):
    return texto.replace('[mention]', '')

"""Decodificar entidades HTML para caracteres normais.

"""

import html
def decode_html_entities(text):
    decoded_text = html.unescape(text)
    return decoded_text

"""
Remover URLs do texto utilizando uma expressão regular."""

def remove_links(text):
    link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))href+="about:invalid#zCSafez'
    text_without_links = re.sub(link_pattern, '', text)

    return text_without_links

"""Remover palavras ou padrões que representam risadas.

"""

def remove_risada(text):
    padrao_risada = r'\b(?:k{2, }|haha|hehe|hahaha|hehehe|rsrs)\b'
    texto_sem_risada = re.sub(padrao_risada, '', text, flags=re.IGNORECASE)
    return texto_sem_risada

"""Substituir todos os emojis encontrados no texto por uma string vazia (''), removendo-os."""

import re

def caracter_especial_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emojis gerais
                               u"\U0001F300-\U0001F5FF"  # Emojis de símbolos e transportes
                               u"\U0001F700-\U0001F77F"  # Emojis de alquimia
                               u"\U0001F780-\U0001F7FF"  # Emojis de Geometria
                               u"\U0001F800-\U0001F8FF"  # Emojis de sinais gregos
                               u"\U0001F900-\U0001F9FF"  # Emojis de sinais suplementares
                               u"\U0001FA00-\U0001FA6F"  # Emojis de esportes
                               u"\U0001FA70-\U0001FAFF"  # Emojis de comida
                               u"\U0001F680-\U0001F6FF"  # Emojis de transporte terrestre
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    return text

df['text'] = df['text'].apply(caracter_especial_emoji)

"""Remover quebras de linha (\n) do texto."""

def remove_newlines(text):
    texto_limpo = text.replace("\n", " ")
    return texto_limpo

df['text'] = df['text'].apply(remove_newlines)

df

"""Transformar a coluna "text" em uma lista de strings para a análise de tópicos e configuração para rotular os textos."""

documents = df['text'].tolist()

custom_headers = ['Document']

df['text']

"""# **3. Bertopic**"""

from bertopic.representation import MaximalMarginalRelevance
from transformers import pipeline
from bertopic.representation import TextGeneration
from bertopic.representation import KeyBERTInspired
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from hdbscan import HDBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic

umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')
hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
topic_model = BERTopic(umap_model=umap_model, embedding_model = 'paraphrase-multilingual-mpnet-base-v2', language='multilingual', vectorizer_model  = vectorizer_model  )

"""Devido à natureza estocástica do UMAP, os resultados do BERTopic podem ser diferentes mesmo que você execute o mesmo código várias vezes. Se quiser reproduzir os resultados, às custas do desempenho, você pode definir um random_state no UMAP para evitar qualquer comportamento estocástico:"""

from bertopic import BERTopic
from umap import UMAP

umap_model = UMAP(n_neighbors=15, n_components=5,
                  min_dist=0.0, metric='cosine', random_state=42)
topic_model = BERTopic(umap_model=umap_model)

topics, probs = topic_model.fit_transform(documents)

topic_model.get_topic_info()

"""# **4. Hierarquização**

Cálculo da matriz de similaridade entre os tópicos, e organização das informações em um formato tabular, identificando os 20 pares de tópicos mais similares.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

distance_matrix = cosine_similarity(np.array(topic_model.topic_embeddings_))
dist_df = pd.DataFrame(distance_matrix, columns=topic_model.topic_labels_.values(),
                       index=topic_model.topic_labels_.values())

tmp = []
for rec in dist_df.reset_index().to_dict('records'):
    t1 = rec['index']
    for t2 in rec:
        if t2 == 'index':
            continue
        tmp.append(
            {
                'topic1': t1,
                'topic2': t2,
                'distance': rec[t2]
            }
        )

pair_dist_df = pd.DataFrame(tmp)

pair_dist_df = pair_dist_df[(pair_dist_df.topic1.map(lambda x: not x.startswith('-1'))) &
                            (pair_dist_df.topic2.map(lambda x: not x.startswith('-1')))]
pair_dist_df = pair_dist_df[pair_dist_df.topic1 < pair_dist_df.topic2]
pair_dist_df.sort_values('distance', ascending=False).head(20)

"""Mesclagem"""

topic_model.merge_topics(df['text'], [[117, 95, 54], [35, 8, 53, 10, 65], [120, 50, 10], [19, 4], [102, 34], [119, 51], [30, 9], [6, 94, 16], [126, 48], ])
df['merged_topic'] = topic_model.topics_

topic_model.get_topic_info()

custom_headers = ['Document']

"""Hierarquia"""

hierarchical_topics = topic_model.hierarchical_topics(df['text'])

topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)

"""Redução"""

topic_model.merge_topics(df['text'], [[56, 43, 52], [92, 62, 65, 47], [39, 13, 18, 46], [21, 1, 26], [24, 6, 9, 5, 10, 0, 3, 22], [27, 17], [100, 40, 83], [68, 91, 29, 57], [104, 70, 28, 51], [86, 20, 19, 33], [30, 35, 11, 16, 12, 67, 58, 73], [99, 98], [89, 55, 93, 80], [53, 111], [63, 23, 97], [36, 50], [110, 101, 96, 113, 105, 103, 31, 25, 99, 95, 109, 74], [15, 84, 77, 32, 38], [85, 14, 69, 102, 8, 114], [106, 37, 41, 61, 49], [48, 60, 54, 87, 82, 59, 44], [42, 79, 2, 45, 71], [81, 7, 72, 66, 4, 34, 75, 64, 112, 94], [78, 108, 107, 88]])
df['merged_topic'] = topic_model.topics_

topic_model.get_topic_info()

topic_model.merge_topics(df['text'], [[-1, 2], [5, 8, 10, 13, 24], [6, 18, 19, 21], [17, 20], [22, 25]])
df['merged_topic'] = topic_model.topics_

topic_model.get_topic_info()

"""Extrair todos os documentos de cada tópico (arquivo csv)"""

doc_info = topic_model.get_document_info(documents)

from collections import defaultdict

topic_docs = defaultdict(list)
for index, row in doc_info.iterrows():
    topic = row['Topic']
    doc = row['Document']
    topic_docs[topic].append(doc)

target_topic = 0
documents_in_topic_0 = topic_docs[target_topic]
print(documents_in_topic_0)

topic_0_df = pd.DataFrame(documents_in_topic_0, columns=["Document"])

topic_0_file_name = "documents_in_topic_0.csv"

topic_0_df.to_csv(topic_0_file_name, index=False)

print(f"Documents in topic 0 saved to {topic_0_file_name}")

doc_info = topic_model.get_document_info(documents)

from collections import defaultdict

topic_docs = defaultdict(list)
for index, row in doc_info.iterrows():
    topic = row['Topic']
    doc = row['Document']
    topic_docs[topic].append(doc)

target_topic = 4
documents_in_topic_4 = topic_docs[target_topic]

topic_4_df = pd.DataFrame(documents_in_topic_4, columns=["Document"])

topic_4_file_name = "documents_in_topic_4.csv"

topic_4_df.to_csv(topic_4_file_name, index=False)

print(f"Documents in topic 4 saved to {topic_4_file_name}")

"""Extrair os documentos *Outliers*"""

outliers = doc_info[doc_info['Topic'] == -1]

outlier_file_name = "outlier_documents.csv"
outliers.to_csv(outlier_file_name, index=False)

print(f"Outlier documents saved to {outlier_file_name}")

"""# **Visualizações**

Gráfico de barras que exibe os tópicos mais relevantes e suas palavras-chave.
"""

topic_model.visualize_barchart(top_n_topics = 15, n_words = 20)

"""Matriz que indica a semelhança de determinados tópicos entre si"""

topic_model.visualize_heatmap(n_clusters=8)

"""Informações gerais sobre o tópico, inclusive seu tamanho e suas palavras correspondentes"""

topic_model.visualize_topics()

"""Para mais informações, consulte: [https://maartengr.github.io/BERTopic/index.html](https://)"""