# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/RyanPerrina/wine_classification/blob/main/wine_classification.ipynb

# Progetto Programmazione di Applicazioni Data Intensive
# Ryan Perrina e Manuel Luzietti
"""

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score

"""# Descrizione del problema
Il dataset in questione riguarda le varianti di vino rosso portoghese "Vinho Verde". Il dataset descrive la qualità del vino in relazione ai componenti chimici presenti. L'obiettivo del progetto è predire la qualità del vino dai 
suoi componenti ovvero predire una variabile discreta non binaria.
"""

data = pd.read_csv("WineQT.csv")

"""# Comprensione dati"""

data.head()

"""Le features rappresentate:


*   fixed acidity | float 
*   volatile acidity | float 
*   citric acid	| float
*   residual sugar | float
*   chlorides | float
*   free sulfur dioxide	| float
*   total sulfur dioxide	| float
*   density | float
*   pH | float
*   sulphates | float
*   alcohol | float
*   quality | int
*   id | int

La variabile target è quality che assume valori da 0 a 10 con 0 qualità pessima e 10 eccellente. Id è l'identificatore dei record e verrà usato come indice del dataframe.
"""

data.set_index("Id",inplace=True)

data.describe()

"""Dal dataset possiamo notare che su alcune colonne abbiamo una variazione significativa tra media e 50 percentile, con alte std come ad esempio "total sulfur dioxide"	oppure "free sulfur dioxide" questo significa che ci sono valori particolarmente distanti dalla media agli estremi.
Si può notare anche che non sono stati rilevati vini con quality minore di 3 o maggiore di 8.
"""

data["quality"].value_counts().plot.pie(autopct="%1.1f%%",figsize=(10,8))

"""Dal grafico possiamo vedere che le classi sono sbilancite e potrebbero essere necessarie tecniche di bilanciamento. """

data.isna().sum()

"""Come possiamo vedere non sono presenti valori nulli su nessuna colonna. Il numero di dati presenti nel data set è:"""

data.shape

"""abbiamo 1143 record e 12 features.

# Data exploration
"""

data.columns

from ipywidgets import interact
@interact(features=data.columns.drop("quality"))
def prepare_plot(features):
    plt.figure(figsize=(20,20))
    data.plot.scatter(x="quality",y=features,title=features)

@interact(features=data.columns.drop("quality"), quality=(data["quality"].min(),data["quality"].max(),1))
def prepare_plot(features,quality):
    plt.figure(figsize=(5,4))
    data[features].where(data["quality"]==quality).plot.hist(title=features)

"""Costruiamo ora la matrice degli indici di correlazione tra le varie features."""

corr = data.corr()
corr.style.background_gradient(cmap='coolwarm')

"""Dalla tabella si possono notare alcune dipendenze tra le variabili di input, che verranno gestite in seguito attraverso regolarizzazione.

Possiamo notare che con l'aggiunta di features polinomiali che in generale ad alte concentrazioni di alcohol e densità corrisponde un valore maggiore di qualità.
"""

from pandas.core.frame import DataFrame
from sklearn.preprocessing import PolynomialFeatures
p = PolynomialFeatures(degree=2,include_bias=False)
d2data = p.fit_transform(data)
d2frame = DataFrame(d2data,index=data.index,columns=p.get_feature_names_out(data.columns))
d2frame.corr()["quality"].sort_values(ascending=False)[7:15]

"""Vediamo con un grafico scatter possibili correlazioni tra più features e quality:"""

@interact(features1=data.columns.drop("quality"), features2=data.columns.drop("quality"))
def prepare_plot(features1,features2):
    plt.figure(figsize=(10,8))
    a=plt.scatter(data[features1],data[features2],c=data["quality"])
    plt.colorbar(a)

"""Puliamo la tabella dai valori non interessanti e ordianiamo i valori linearmente correlati con la features quality:"""

data.corr()["quality"].drop(labels="quality").abs().sort_values(ascending=False)

"""Possiamo notare che le prime quattro features che compaiono sono alcohol, volatile acidity, sulphates, citric acid. Questo significa che queste features sono quelle con un riscontro più rilavanti sulla qualità del vino (con contributo positivo o negativo).                     """

figure, axes = plt.subplots(1, 2,figsize=(10,7))
axes[0].plot(data.groupby("quality")["alcohol"].mean().index,data.groupby("quality")["alcohol"].mean())
data.boxplot(column="alcohol", by ="quality",showmeans=True,ax=axes[1])

"""La correlazine tra alcohol e qualità è direttamnete proporzionale.L'indice di correllazione infatti è:

"""

data.corr().loc["quality","alcohol"]

figure, axes = plt.subplots(1, 2,figsize=(10,7))
axes[0].plot(data.groupby("quality")["volatile acidity"].mean().index,data.groupby("quality")["volatile acidity"].mean())
data.boxplot(column="volatile acidity", by ="quality",showmeans=True,ax=axes[1])

"""La correlazine tra volatile acidity e qualità è inversamente proporzionale.L'indice di correllazione infatti è:"""

data.corr().loc["quality","volatile acidity"]

figure, axes = plt.subplots(1, 2,figsize=(10,7))
axes[0].plot(data.groupby("quality")["sulphates"].mean().index,data.groupby("quality")["sulphates"].mean())
data.boxplot(column="sulphates", by ="quality",showmeans=True,ax=axes[1])

"""La correlazine tra sulphates e qualità è direttamente proporzionale.L'indice di correllazione infatti è:


"""

data.corr().loc["quality","sulphates"]

figure, axes = plt.subplots(1, 2,figsize=(10,7))
axes[0].plot(data.groupby("quality")["citric acid"].mean().index,data.groupby("quality")["citric acid"].mean())
data.boxplot(column="citric acid", by ="quality",showmeans=True,ax=axes[1])

"""La correlazine tra citric acid e qualità è direttamente proporzionale.L'indice di correllazione infatti è:"""

data.corr().loc["quality","citric acid"]

"""# Normalizzazione
Come possiamo vedere le features hanno scale diverse, quindi si prosegue con normalizzazione dei dati.
"""

data.drop(columns="quality").aggregate(["min","max"]).T

from sklearn.preprocessing import MinMaxScaler 
X = MinMaxScaler().fit_transform(data.drop(columns="quality"))
X = DataFrame(X,columns=data.drop(columns="quality").columns,index=data.index)
X.head()

Y = data["quality"]

"""# Rilevanza features

Dividiamo i dati in train e validation set. Creiamo un primo modello di classificazione con regolarizzazione Lasso per andare ad identificare le features più o meno rilevanti. Incorporiamo il modello in una pipeline in modo da valutare anche inserimenti di features non lineari, pesi di regolazzione e bilanciamento automatico delle classi attraverso una Grid Search.
"""

from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

X_train, X_val, y_train, y_val = train_test_split(X,Y,test_size=1/3,random_state=42)
model = Pipeline([
                  ("poly",PolynomialFeatures()),
                  ("classifier",LogisticRegression(solver="saga", random_state=42, penalty="l1", C=10,multi_class="ovr"))
])

from sklearn.model_selection import GridSearchCV
grid = {
        "poly__degree": [1,3,5],
    "classifier__C": [0.01,0.1,1,10],#peso regolarizzazione
    "classifier__class_weight" : ["balanced",None]
}
skf = StratifiedKFold(3,shuffle=True, random_state=42)
gs = GridSearchCV(model,cv=skf,param_grid=grid,return_train_score=True)

#gs.fit(X_train,y_train)

"""Prendiamo i risultati della grid search e li ordiniamo per score."""

#DataFrame(gs.cv_results_).sort_values("rank_test_score").head(10)

"""Il miglior modello trovato è qullo con peso di regolazzazione 10 e grado 5 e nessun bilanciamento sui pesi delle classi. Possiamo osservare uno score di:"""

#gs.score(X_val,y_val)

"""Essendo in un contesto multiclasse in cui abbiamo adottato il metodo "one vs all" per la classificazione, sono stati individuati sei iperpiani con rispettivi coefficenti:"""

#gs.best_estimator_.named_steps["classifier"].coef_

"""Effettuando la media di questi coefficenti possiamo verdere che ci sono 2478 features azzerate in seguito alla regolazzazione."""

#(DataFrame(gs.best_estimator_.named_steps["classifier"].coef_,columns=gs.best_estimator_.named_steps["poly"].get_feature_names_out()).mean() == 0 ).value_counts()

"""Osservando le prime 10 features ordinate per importanza dopo la regolarizzazione possiamo vedere che i primi valori sono di features non lineari."""

#DataFrame(gs.best_estimator_.named_steps["classifier"].coef_,columns=gs.best_estimator_.named_steps["poly"].get_feature_names_out()).mean().sort_values(ascending=False).head(10)

#from sklearn.metrics import confusion_matrix
#y_pred = gs.predict(X_val)
#cm = confusion_matrix(y_val,y_pred)
#DataFrame(cm,index=gs.classes_,columns=gs.classes_)

#from sklearn.metrics import f1_score
#1_score(y_val,y_pred,average="weighted")

"""# Oversampling

Come possiamo vedere le classi sono molto sbilanciate.
"""

Y.value_counts()

"""procediamo con oversampling dei dati"""

from imblearn.over_sampling import SMOTE

sm = SMOTE(random_state=42,sampling_strategy="not majority")
Xsm,Ysm = sm.fit_resample(X,Y)

Ysm.value_counts()

Xsm_train, Xsm_val, ysm_train, ysm_val = train_test_split(Xsm,Ysm,test_size=1/3,random_state=42)

#bestModel = gs.best_estimator_
#bestModel.fit(Xsm_train,ysm_train)

#bestModel.score(Xsm_val,ysm_val)

#f1_score(ysm_val,bestModel.predict(Xsm_val),average="weighted")

"""Possiamo vedere che il modello è leggermente migliorato."""

from sklearn.metrics import accuracy_score
#accuracy_score(ysm_val,bestModel.predict(Xsm_val))

"""# Alberi decisionali"""

from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier(max_depth=6)
tree.fit(Xsm_train,ysm_train)
tree.score(Xsm_val,ysm_val)

"""Addestrando un modello con profondità massima inferiore a 6 si ottiene un modello poco preciso.

Disegnamo ora l'albero ottenuto:
"""

from sklearn.tree import export_text
print(export_text(tree, feature_names=Xsm_train.columns.to_list()))

accuracy_score(ysm_val,tree.predict(Xsm_val))

#f1_score(ysm_val,model.predict(Xsm_val),average="weighted")

"""# Support Vector Machine

Questo metodo è utile per individuare iperpiani di separazione ottimi poichè non usa tutte le istanze ma solo quelle vicino al decision boundary cercando di massimizzare la distanza tra questi punti e l'iperpiano.
"""

from sklearn.svm import SVC
StratifiedKFold(3,shuffle=True, random_state=42)
svc = SVC()
grid2 = {
    'gamma' : [1, 5],
     "C": [ 0.01,0.1,1,5],
     'kernel' : ['rbf', 'poly']
}
gs_svm = GridSearchCV(svc,grid2,cv=skf,return_train_score=True)

gs_svm.fit(Xsm_train,ysm_train)

DataFrame(gs_svm.cv_results_).sort_values("rank_test_score").head(3)

"""L'accuratezza del modello è alta:"""

gs_svm.score(Xsm_val,ysm_val)

"""# KNN"""

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors = 5)
knn.fit(Xsm_train,ysm_train)

knn.score(Xsm_val,ysm_val)

"""# Perceptron

Ora utilizziamo l'algoritmo perceptron che usa al suo interno due parametri **w** e **b**. 
I due parametri sono inizialmente casuali, poi ogni volta che c'è un istanza mal classificata vengono modificati i parametri proporzionalmente al learning rate.

Ogni iperpiano sarà descritto nella forma:
**wx + b = 0**
"""

from scipy.sparse.construct import random
from sklearn.linear_model import Perceptron
perc= Perceptron()
gridPerc = {
    "penalty" : ["l1","l2",None],
    "alpha" : np.logspace(-5,-3,3)
}
gs_p = GridSearchCV(perc,param_grid=gridPerc,cv=skf)
gs_p.fit(Xsm_train,ysm_train)

"""dopo aver addestrato il modello nell'attributo risiede la matrice degli iperpiani con i valori dei pesi **w**:"""

gs_p.best_estimator_.coef_

"""invece nell'attributo intercept risiede il vettore con un valore di **b**  diverso per ogni iperpiano:"""

gs_p.best_estimator_.intercept_

"""verifichiamo anche che le classi riconosciute dal modello siano quelle che ci aspettiamo:"""

gs_p.best_estimator_.classes_

"""Calcolando l'accuratezza si ottiene uno score basso di poco sotto al 50%."""

gs_p.best_estimator_.score(Xsm_val,ysm_val)

"""# Reti Neurali"""

from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from keras import Sequential
from tensorflow.keras.layers import Dense
import keras

def getModel(nodes1,nodes2,nodes3):
  model = Sequential([
                 Dense(nodes1,activation='relu',input_dim=Xsm_train.shape[1]),
                 Dense(nodes2,activation="softmax"),
                 Dense(nodes3,activation="softmax"),
                 Dense(1)     
  ])
  model.compile(optimizer="adam",loss="categorical_crossentropy",metrics=["accuracy"])
  return model

model = KerasClassifier(build_fn=getModel)

grid3 = {
    "nodes1" : [8],
    "nodes2" : [3],
    "nodes3" : [3],
    "batch_size" : [5],
    "epochs": [200]
}

gsnn = GridSearchCV(model,grid3,return_train_score=True,cv=skf)

gsnn.fit(Xsm_train,ysm_train[:,None])

gsnn.score(Xsm_val,ysm_val[:,None])

"""# Modello Casuale di confronto"""

Xsm_train.shape

ysm_train.shape

from sklearn.dummy import DummyClassifier
model = DummyClassifier(strategy="uniform",random_state=77)
model.fit(Xsm_train,ysm_train)
model.score(Xsm_val,ysm_val)

"""#Considerazioni finali

Calcoliamo la matrice di confusione dei vari modelli e osserviamo la diagonale di ogniuna per vedere quanti valori sono stati predetti nel modo giusto, mentre fuori dalla diagonale osserviamo gli errori.
"""

from sklearn.metrics import f1_score, accuracy_score, classification_report
pred = perc.predict(Xsm_val)
c_perc=confusion_matrix(ysm_val, pred)
c_perc

pred = knn.predict(Xsm_val)
c_knn=confusion_matrix(ysm_val, pred)
c_knn

pred = gs_svm.predict(Xsm_val)
c_svm=confusion_matrix(ysm_val, pred)
c_svm

pred = tree.predict(Xsm_val)
c_tree=confusion_matrix(ysm_val, pred)
c_tree

"""Calcoliamo ora le statistiche per ogni modello trovato:"""

def calculate_precision_recall_f1(model):
    y_v_predictions = model.predict(Xsm_val)
    p = precision_score(ysm_val, y_v_predictions, pos_label=1, average="macro")
    r = recall_score(ysm_val, y_v_predictions, average="macro")
    f1 = f1_score(ysm_val, y_v_predictions, average="macro")
    return {"precision" : p, "recall": r, "f1-score": f1}

pd.DataFrame([calculate_precision_recall_f1(perc),
              calculate_precision_recall_f1(tree),
              calculate_precision_recall_f1(gs_svm),
              calculate_precision_recall_f1(knn)],
                 index=["perceptron", "tree", "svc","knn"])

"""Gli intervalli di confidenza cioè l'intervallo dei valori entro i quali si  stima che cada il risulatto con probabilità prescelta (in questo caso del 99%):
**intervallo 99% = proporzione +- 2.58**
"""

def confidence(acc, N, Z):
    den = (2*(N+Z**2))
    var = (Z*np.sqrt(Z**2+4*N*acc-4*N*acc**2)) / den
    a = (2*N*acc+Z**2) / den
    inf = a - var
    sup = a + var
    return (inf, sup)
def calculate_accuracy(conf_matrix):
    return np.diag(conf_matrix).sum() / conf_matrix.sum().sum()

pd.DataFrame([confidence(calculate_accuracy(c_perc), len(Xsm_val), 2.58),
              confidence(calculate_accuracy(c_knn), len(Xsm_val), 2.58),
              confidence(calculate_accuracy(c_svm), len(Xsm_val), 2.58),
              confidence(calculate_accuracy(c_tree), len(Xsm_val), 2.58)],
              index=["perceptron", "knn", "svm","tree"], columns=["inf", "sup"])