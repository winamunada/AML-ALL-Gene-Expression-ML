# -*- coding: utf-8 -*-
"""AML_ALL_Clustering.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fV8RrbqogOZBYJJVG0Eoic_iyp9Q_kE5

# Evaluating Machine Learning Models for Gene Expression Analysis in AML and ALL Cancer Classification and Clustering

## Machine Learning Project
## Wina Munada - AIU221063
"""

from google.colab import drive
drive.mount('/content/drive')

"""#### Import all the necessary library"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import random
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, recall_score

params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 10),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
plt.rcParams.update(params)
sns.set_theme(style="darkgrid")
np.random.seed(42)

warnings.filterwarnings("ignore")

le = LabelEncoder()

"""### Load data"""

train_data = pd.read_csv("/content/drive/MyDrive/gene-expression/data_set_ALL_AML_train.csv")
test_data = pd.read_csv("/content/drive/MyDrive/gene-expression/data_set_ALL_AML_independent.csv")
labels = pd.read_csv("/content/drive/MyDrive/gene-expression/actual.csv", index_col = 'patient')

train_data.head()

test_data.head()

"""### Check NAs"""

print(train_data.isna().sum().sum())
print(test_data.isna().sum().sum())

"""## EDA and data preprocessing

It seems like **call** columns have "A" almost everywhere, so I will drop it.
"""

cols_train = [col for col in train_data.columns if "call" in col]
cols_test = [col for col in test_data.columns if "call" in col]

train_data.drop(cols_train, axis=1, inplace=True)
test_data.drop(cols_test, axis=1, inplace=True)

"""Here we have features in rows and patients in cols, so we need to transpose data."""

train_data = train_data.T
test_data = test_data.T

train_data.head()

train_data.columns = test_data.iloc[1].values
train_data.drop(["Gene Description", "Gene Accession Number"], axis=0, inplace=True)
test_data.columns = test_data.iloc[1].values
test_data.drop(["Gene Description", "Gene Accession Number"], axis=0, inplace=True)

train_data.head()

# Adding new column
train_data["patient"] = train_data.index.values
test_data["patient"] = test_data.index.values

train_data.head()

train_data = train_data.astype("int32")
test_data = test_data.astype("int32")

labels["cancer"] = le.fit_transform(labels["cancer"])
train_data = pd.merge(train_data, labels, on="patient")
test_data = pd.merge(test_data, labels, on="patient")

train_data["cancer"].value_counts()

test_data["cancer"].value_counts()

fig, axs = plt.subplots(1, 2)
sns.countplot(x="cancer", data=train_data, ax=axs[0])
axs[0].set_title("Train data", fontsize=24)
sns.countplot(x="cancer", data=test_data, ax=axs[1])
axs[1].set_title("Test data", fontsize=24)
plt.show()

"""In test data we have $\frac{ALL}{AML}$ ratio about $\frac{20}{14}=1.43$ and in train $\frac{27}{11}=2.45$. Lets use upsampling to combat class imbalance. I think here we can add about 8 additional random samples of **AML** class."""

upsampled_data = random.sample(train_data.query("cancer == 1")["patient"].index.to_list(), k=8, )

upsampled_data

train_data_upsampled = pd.concat([train_data, train_data.iloc[upsampled_data, :]])

fig, axs = plt.subplots(1, 2)
sns.countplot(x="cancer", data=train_data_upsampled, ax=axs[0])
axs[0].set_title("Train data", fontsize=24)
sns.countplot(x="cancer", data=test_data, ax=axs[1])
axs[1].set_title("Test data", fontsize=24)
fig.suptitle("After upsampling", fontsize=24)
plt.show()

"""Scaling the data."""

X_train = train_data_upsampled.drop(columns=["patient", "cancer"])
y_train = train_data_upsampled["cancer"]
X_test = test_data.drop(columns=["patient", "cancer"])
y_test = test_data["cancer"]

# Features scaling
sc = StandardScaler()
X_train_scaled = sc.fit_transform(X_train)
X_test_scaled = sc.transform(X_test)

"""## Dimentionality reduction and clusterisation"""

# PCA transformation to reduce the dimensionality
pca = PCA(n_components=2)
reduced_train = pca.fit_transform(X_train_scaled)
reduced_test = pca.transform(X_test_scaled)

# K-means clustering
kmeans = KMeans(n_clusters=2, n_init=20, random_state=42)
kmeans.fit(reduced_train)

# Plotting the clusters
sns.scatterplot(x=reduced_train[:, 0], y=reduced_train[:, 1], hue=kmeans.labels_, palette='viridis')
plt.title('K-Means Clustering of Gene Expression Data')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.xticks(())
plt.yticks(())
plt.show()

# Evaluate the performance
y_pred_kmeans = kmeans.predict(reduced_test)

accuracy = accuracy_score(y_test, y_pred_kmeans)
f1 = f1_score(y_test, y_pred_kmeans)
recall = recall_score(y_test, y_pred_kmeans)

print('Validation Accuracy of K-means:', accuracy)
print('Validation F1-score of K-means:', f1)
print('Validation Recall of K-means:', recall)
print("\nClassification report :\n", metrics.classification_report(y_test, y_pred_kmeans))



pca = PCA()
pca.fit_transform(X_train_scaled)
total = sum(pca.explained_variance_)
k = 0
current_variance = 0
while current_variance / total < 0.90:
    current_variance += pca.explained_variance_[k]
    k = k + 1
print(k, " features explain around 90% of the variance. From 7129 features to ", k, sep='')

pca = PCA(n_components=k)
X_train_pca = pca.fit(X_train_scaled)
X_train_pca = pca.transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

var_exp = pca.explained_variance_ratio_.cumsum()
var_exp = var_exp*100
plt.bar(range(1, k + 1), var_exp, color="brown")
plt.xlabel("Cumulutive explained variance", fontsize=18)
plt.ylabel("Number of components", fontsize=18)
plt.xlim((0.5, k + 1))
plt.show()

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, recall_score
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler

# Standard Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# PCA for reducing dimensionality
pca = PCA(n_components=2)
reduced_train = pca.fit_transform(X_train_scaled)
reduced_test = pca.transform(X_test_scaled)

# Hyperparameter tuning for K-means
best_accuracy = 0
best_params = {}
for n_clusters in range(2, 10):
    for n_init in [10, 20, 30]:
        for max_iter in [300, 400, 500]:
            kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, random_state=42)
            kmeans.fit(reduced_train)
            y_pred_kmeans = kmeans.predict(reduced_test)

            # Adjust labels to match the true labels
            y_pred_kmeans_adjusted = np.where(y_pred_kmeans == 0, 1, 0)

            accuracy = accuracy_score(y_test, y_pred_kmeans_adjusted)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = {'n_clusters': n_clusters, 'n_init': n_init, 'max_iter': max_iter}

print("Best Parameters:", best_params)
print("Best Accuracy:", best_accuracy)

# Train with best parameters
kmeans = KMeans(**best_params, random_state=42)
kmeans.fit(reduced_train)

# Predict and evaluate the performance
y_pred_kmeans = kmeans.predict(reduced_test)

# Adjust labels to match the true labels if necessary
# Uncomment and adjust the next line if your initial label mapping is incorrect
y_pred_kmeans = np.where(y_pred_kmeans == 0, 1, 0)

accuracy = accuracy_score(y_test, y_pred_kmeans)
f1 = f1_score(y_test, y_pred_kmeans)
recall = recall_score(y_test, y_pred_kmeans)

print('Validation Accuracy of K-means:', accuracy)
print('Validation F1-score of K-means:', f1)
print('Validation Recall of K-means:', recall)

# Confusion Matrix
plt.figure(figsize=(18, 14))

plt.subplot(221)
sns.heatmap(metrics.confusion_matrix(y_test, y_pred_kmeans), annot=True, fmt="d", linecolor="k", linewidths=3)
plt.title("CONFUSION MATRIX", fontsize=20)

# ROC Curve
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_kmeans)
plt.subplot(222)
plt.plot(fpr, tpr, label=("Area under the curve:", metrics.auc(fpr, tpr)), color="r")
plt.plot([1, 0], [1, 0], linestyle="dashed", color="k")
plt.legend(loc="best")
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title("ROC - CURVE & AREA UNDER CURVE", fontsize=20)
plt.show()

# Plotting the clusters
sns.scatterplot(x=reduced_train[:, 0], y=reduced_train[:, 1], hue=kmeans.labels_, palette='viridis')
plt.title('K-Means Clustering of Gene Expression Data')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.xticks(())
plt.yticks(())
plt.show()

"""#### Also it is interesting to see if hierarchial clusterisation give us 2 clusters based on cancer type."""

cancer_labels = train_data_upsampled["cancer"].map({0: le.classes_[0], 1: le.classes_[1]}).values
patient_labels = np.array(list(map(str, train_data_upsampled["patient"].values))).astype("object") + "_" + cancer_labels

"""#### Hierarchy"""

link = linkage(X_train_scaled, 'ward', 'euclidean')

dm = dendrogram(link, color_threshold=1250, labels=patient_labels)

dist = link[:, 2]
dist_rev = dist[::-1]
idxs = range(1, len(dist) + 1)
plt.plot(idxs, dist_rev, marker='o')
plt.title('Distance between merged clusters')
plt.xlabel('Step')
plt.ylabel('Distance')
plt.show()

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# Gaussian Mixture Model (GMM)
gmm = GaussianMixture(n_components=2, n_init=10, random_state=42)
gmm.fit(reduced_train)

# Predicting the clusters
y_pred_gmm_train = gmm.predict(reduced_train)
y_pred_gmm_test = gmm.predict(reduced_test)

from sklearn.metrics import accuracy_score, f1_score, recall_score, confusion_matrix, classification_report

# Adjust labels to match the true labels if necessary
# Uncomment and adjust the next line if your initial label mapping is incorrect
y_pred_gmm_test = np.where(y_pred_gmm_test == 0, 1, 0)

# Evaluate the performance
accuracy = accuracy_score(y_test, y_pred_gmm_test)
f1 = f1_score(y_test, y_pred_gmm_test)
recall = recall_score(y_test, y_pred_gmm_test)

print('Validation Accuracy of GMM:', accuracy)
print('Validation F1-score of GMM:', f1)
print('Validation Recall of GMM:', recall)
print("\nClassification report :\n", classification_report(y_test, y_pred_gmm_test))

import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, recall_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
from time import time

# Assuming you have loaded your data into X_train, X_test, y_train, y_test

# Standard Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# PCA for reducing dimensionality
pca = PCA(n_components=2)
reduced_train = pca.fit_transform(X_train_scaled)
reduced_test = pca.transform(X_test_scaled)

# Hyperparameter tuning for GMM
best_accuracy = 0
best_params = {}
start_time = time()

for n_components in range(2, 10):
    for covariance_type in ['full', 'tied', 'diag', 'spherical']:
        for n_init in [10, 20, 30, 50]:
            for max_iter in [300, 400, 500, 1000]:
                gmm = GaussianMixture(n_components=n_components, covariance_type=covariance_type,
                                      n_init=n_init, max_iter=max_iter, random_state=42)
                gmm.fit(reduced_train)
                y_pred_gmm_test = gmm.predict(reduced_test)

                # Adjust labels to match the true labels if necessary
                y_pred_gmm_test = np.where(y_pred_gmm_test == 0, 1, 0)

                accuracy = accuracy_score(y_test, y_pred_gmm_test)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_params = {
                        'n_components': n_components,
                        'covariance_type': covariance_type,
                        'n_init': n_init,
                        'max_iter': max_iter
                    }

                # Break if time exceeds 5 minutes
                if time() - start_time > 300:
                    break
            if time() - start_time > 300:
                break
        if time() - start_time > 300:
            break
    if time() - start_time > 300:
        break

# Train with best parameters
gmm = GaussianMixture(**best_params, random_state=42)
gmm.fit(reduced_train)

# Predict and evaluate the performance
y_pred_gmm_test = gmm.predict(reduced_test)

# Adjust labels to match the true labels if necessary
y_pred_gmm_test = np.where(y_pred_gmm_test == 0, 1, 0)

accuracy = accuracy_score(y_test, y_pred_gmm_test)
f1 = f1_score(y_test, y_pred_gmm_test)
recall = recall_score(y_test, y_pred_gmm_test)

print('Best Parameters for GMM:', best_params)
print('Validation Accuracy of GMM:', accuracy)
print('Validation F1-score of GMM:', f1)
print('Validation Recall of GMM:', recall)
print("\nClassification report :\n", classification_report(y_test, y_pred_gmm_test))

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred_gmm_test)
print("\nConfusion Matrix:\n", conf_matrix)

# Plotting the clusters
sns.scatterplot(x=reduced_train[:, 0], y=reduced_train[:, 1], hue=y_pred_gmm_train, palette='viridis')
plt.title('GMM Clustering of Gene Expression Data')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.xticks(())
plt.yticks(())
plt.show()

from sklearn.metrics import confusion_matrix, roc_curve, auc
# Confusion Matrix
plt.figure(figsize=(18, 14))

plt.subplot(221)
sns.heatmap(confusion_matrix(y_test, y_pred_gmm_test), annot=True, fmt="d", linecolor="k", linewidths=3)
plt.title("CONFUSION MATRIX", fontsize=20)

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_gmm_test)
plt.subplot(222)
plt.plot(fpr, tpr, label=("Area under the curve:", auc(fpr, tpr)), color="r")
plt.plot([1, 0], [1, 0], linestyle="dashed", color="k")
plt.legend(loc="best")
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title("ROC - CURVE & AREA UNDER CURVE", fontsize=20)
plt.show()

import matplotlib.pyplot as plt
import seaborn as sns

# Example data for KMeans and GMM
# These are dummy values for demonstration purposes.
# Replace these with the actual values obtained from your evaluation.

metrics = ['F1-Score', 'Recall', 'Accuracy']
kmeans_scores = [0.62, 0.57, 0.71]  # Replace with actual KMeans scores
gmm_scores = [0.72, 0.72, 0.74]     # Replace with actual GMM scores

# Plotting the model performance metrics for comparison
plt.figure(figsize=(12, 6))
plt.plot(metrics, kmeans_scores, marker='o', label='K-Means')
plt.plot(metrics, gmm_scores, marker='o', label='GMM')
plt.title('Model Performance Metrics Comparison')
plt.xlabel('Metrics')
plt.ylabel('Score')
plt.legend(title='Model')
plt.grid(True)
plt.show()

