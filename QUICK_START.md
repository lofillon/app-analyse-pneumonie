# Démarrage Rapide

## Installation (1 minute)

```bash
# 1. Aller dans le répertoire du projet
cd "/Users/lapin/Desktop/App Pneumonie"

# 2. Installer les dépendances
pip install -r requirements.txt
```

**Note :** Si vous avez des problèmes avec TensorFlow, installez une version spécifique :
```bash
pip install tensorflow==2.15.0 keras==2.15.0
```

## Générer des données de test (optionnel)

Si vous n'avez pas de fichiers DICOM réels :

```bash
python3 generate_test_data.py
```

Cela créera 8 fichiers DICOM de test dans le dossier `test_data/`

## Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

**Note :** Le premier lancement peut prendre 30-60 secondes pour charger le modèle TensorFlow.

## Test rapide (10 minutes)

### 1. Connexion en tant que Préparateur
- Rôle: **Préparateur**
- Nom: **TestPrep**

### 2. Importer des fichiers

**Option A : Import DICOM**
- Onglet: **📥 Import DICOM** (colonne gauche)
- Sélectionnez les fichiers dans `test_data/` (ou vos propres fichiers DICOM)
- Cliquez sur **"Importer les fichiers DICOM"**

**Option B : Import Images Simples**
- Onglet: **📥 Import DICOM** (colonne droite "🖼️ Import Images Simples")
- Sélectionnez une ou plusieurs images (PNG, JPG, JPEG)
- Pour chaque image, saisissez :
  - **ID Patient** (obligatoire)
  - **Sexe** (optionnel)
- Saisissez **Âge** et **Date d'examen** (partagés pour toutes les images)
- Cliquez sur **"Importer les images"**
- Le sélecteur se réinitialise automatiquement après l'import

### 3. Lancer l'analyse
- Onglet: **🤖 Analyse Modèle**
- Vous verrez les images en attente d'analyse
- Cliquez sur **"🚀 Lancer l'analyse sur les images sélectionnées"**
- Le modèle TensorFlow analysera chaque image
- Attendez la fin de l'analyse (peut prendre quelques secondes par image)

### 4. Visualiser les résultats
- Onglet: **📊 Visualisation & Filtrage**
- Consultez les prédictions du modèle (sain/malade)
- Utilisez les filtres pour trouver des cas spécifiques
- Triez les résultats selon vos besoins

### 5. Annoter un patient
- Onglet: **✅ Validation & Envoi**
- Sélectionnez un patient dans la liste déroulante
- Pour chaque image du patient :
  - Visualisez l'image et la prédiction
  - **Classification** : Sélectionnez sain ou malade
  - **Confiance** : Ajustez le niveau de confiance
  - **Notes** : Ajoutez des notes
  - **Informations complémentaires** : Remplissez les champs (symptômes, signes vitaux, etc.)
  - Cliquez sur **"💾 Enregistrer l'annotation"**
- Répétez pour tous les patients

### 6. Envoyer au médecin
- Dans l'onglet **"✅ Validation & Envoi"**, section "Envoi au Médecin"
- Vérifiez que tous les patients sont annotés (sinon vous verrez un avertissement)
- Sélectionnez les patients à envoyer
- Cliquez sur **"📤 Envoyer la liste au médecin"**

### 7. Se connecter en tant que Médecin
- Cliquez sur **"Se déconnecter"** dans la barre latérale
- Rôle: **Médecin**
- Nom: **DrTest**

### 8. Valider un patient
- Onglet: **📋 Liste des Patients à Revoir**
- Sélectionnez un patient dans la liste déroulante
- Visualisez l'image, la prédiction et la classification du préparateur
- Remplissez le formulaire de validation :
  - **Diagnostic Final** : Confirmez ou corrigez (sain/malade)
  - **Confiance du diagnostic** : Ajustez si nécessaire
  - **Commentaire clinique** : Ajoutez vos observations
  - **Résultat Clinique Réel** : À compléter après traitement
- Cliquez sur **"✅ Valider le Diagnostic"**

### 9. Démarrer un traitement
- Onglet: **💊 Démarrer le Traitement & Suivi**
- Section "🚀 Démarrer un Traitement"
- Sélectionnez un patient validé
- Choisissez le type d'action :
  - **Prescription** : Remplissez médicament, posologie, durée
  - **Examens** : Sélectionnez les types d'examens, urgence
  - **Hospitalisation** : Choisissez le service, motif, durée
  - **Orientation** : Sélectionnez la destination, motif
- Ajoutez des notes complémentaires
- Cliquez sur **"✅ Démarrer le Traitement"**

### 10. Suivre les traitements
- Dans l'onglet **"💊 Démarrer le Traitement & Suivi"**, section "📋 Liste de Suivi"
- Consultez tous les patients en traitement
- Voir les statistiques (en traitement, en attente d'examens, hospitalisés)
- Pour chaque patient, vous pouvez :
  - Voir les détails du traitement
  - Mettre à jour le statut (en traitement, en attente d'examens, hospitalisé, terminé)
  - Ajouter des notes sur l'évolution

### 11. Finaliser
- Onglet: **📊 Résultats & Export**
- Consultez les patients validés
- Sélectionnez les patients à finaliser
- Cliquez sur **"✅ Marquer comme Finalisé"**
- Testez l'export : **"📥 Préparer l'Export pour Entraînement"**

## Vérification

Vérifiez que les fichiers suivants sont créés dans `data/`:
- `patients.json` - Patients importés
- `images.json` - Images et métadonnées
- `predictions.json` - Prédictions du modèle
- `annotations.json` - Annotations préparateur/médecin
- `audit_log.json` - Journal de tous les changements
- `images/` - Dossier contenant les images extraites

## Problèmes courants

**Erreur "Module not found"**
```bash
pip install --upgrade -r requirements.txt
```

**L'application ne se lance pas**
```bash
# Vérifier que Streamlit est installé
pip show streamlit

# Si non, installer
pip install streamlit
```

**Erreur lors de l'import DICOM**
- Vérifiez que les fichiers sont bien .dcm
- Utilisez le script `generate_test_data.py` pour créer des fichiers de test

**Le modèle ne charge pas**
- Vérifiez que `model.h5` est dans le dossier du projet
- Vérifiez les versions : `pip show tensorflow keras`
- Le premier chargement peut prendre 30-60 secondes

**L'application est bloquée**
- Attendez 30-60 secondes lors du premier lancement (chargement du modèle)
- Vérifiez les messages dans le terminal
- Si ça persiste, redémarrez Streamlit

**Erreur TensorFlow/Keras**
- Installez les versions compatibles : `pip install tensorflow==2.15.0 keras==2.15.0`
- Vérifiez que Python 3.9 est utilisé

## Workflow Complet Résumé

1. **Préparateur** : Import → Analyse → Visualisation → Annotation → Envoi
2. **Médecin** : Revue → Validation → Traitement → Suivi → Finalisation → Export

Chaque étape est journalisée et versionnée pour un suivi complet.
