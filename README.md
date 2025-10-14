# Plateforme d'achat des tickets des jeux olympiques en ligne

## Description
Ce projet est une application Django permettant aux utilisateurs d'acheter des tickets en ligne et de procéder au paiement sécurisé via Stripe. 

## Fonctionnalités
- Système d'achat de tickets en ligne
- Paiement sécurisé avec Stripe
- Gestion des Webhooks Stripe pour le suivi des paiements
- Interface utilisateur intuitive
- Gestion des offres par l'administrateur du site
- Génération de code Qr pour chaque ticket acheté

### Requirements
Pour éxècuter le projet en local, assurez vous d'avoir installés les prérequis :
    - Installer Python : https://www.python.org/
    - Installer un gestionnaire de paquets comme PIP : https://pypi.org/project/pip/
    - Installer Django : py -m pip install Django pour Windows ou python -m pip install Django pour Linux
    - Versions des outils utilisés sur le projet : Python 3.10.12, Pip 22.0.2, Django 5.0.7

### Installation PostgreSQl
    - Installation PostgreSQL pour Django : pip install psycopg2 ou utiliser la version binaire : pip install psycopg2-binary

### Lancement du projet
1. Clonez le projet depuis le dépôt github vers votre machine en local
2. Installer les dépendances avec pip install -r  requirements.txt
3. Copiez le fichier .env.example pour créer le fichier d'environnement .env
4. Démarrer le serveur de développement de Django
    - python3 manage.py runserver, cette commande lancera le serveur de développement 
    sur l'adresse http://localhost::8000
    - accéder au lien qui vous menèra sur lapage d'acueil du projet

### 1. **Commandes à èxécuter**
- pip install -r  requirements.txt
- pip install stripe

### 2. **Stripe Webhook**
- Installez stripe : pip install stripe
- Dans le .env mettez les clés  ==> STRIPE_SECRET_KEY_TEST, STRIPE_PUBLIC_KEY_TEST
- Créez un compte Stripe et activez le webhook
- Configurez le webhook pour envoyer les données de paiement vers votre application
- Dans votre application, configurez le webhook pour recevoir les données de paiement
- Tester avec Sripe CLI
    Pour installer la CLI Stripe sous Linux sans gestionnaire de paquets :

        Téléchargez le dernier fichier tar.gz linux depuis [GitHub](https://github.com/stripe/stripe-cli/releases/tag/v1.26.1).
        Décompressez le fichier : tar -xvf stripe_X.X.X_linux_x86_64.tar.gz.
        Déplacez ./stripe sur votre chemin d’exécution.
        (Documentation)[https://docs.stripe.com/stripe-cli]

    Se connecter à l'interface de ligne de commande

        Èxécuter dans voter invite de commande stripe login
        Appuyez sur la touche Entrée de votre clavier pour effectuer le processus d’authentification dans votre navigateur.

    stripe listen --forward-to localhost:8000/webhook/stripe/ 
        Cette commande renvoie la clé secrète webhook qu'on met dans le point .env qu'on a nommé STRIPE_WEBHOOK_SECRET
        NB : Assurez-vous d'avoir le serveur démarré avant l'éxécution de cette commande

# https://dbdiagram.io/d

   

    dwuwpalcbhziljbw
