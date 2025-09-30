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

        Téléchargez le dernier fichier tar.gz linux depuis GitHub.
        Décompressez le fichier : tar -xvf stripe_X.X.X_linux_x86_64.tar.gz.
        Déplacez ./stripe sur votre chemin d’exécution.

    Se connecter à l'interface de ligne de commande

        Èxécuter dans voter invite de commande stripe login
        Appuyez sur la touche Entrée de votre clavier pour effectuer le processus d’authentification dans votre navigateur.

    stripe listen --forward-to localhost:8000/webhook/stripe/ 
        Cette commande renvoie la clé secrète webhook qu'on met dans le point .env qu'on a nommé STRIPE_WEBHOOK_SECRET

<!!code pour page des offres>>
{% load static %}
<!DOCTYPE html>
<html lang="fr">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liste des Offres</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'tickets/style.css' %}">

    <!-- Vendor CSS Files -->
    <link href="{% static 'admin/assets/vendor/bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/bootstrap-icons/bootstrap-icons.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/boxicons/css/boxicons.min.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/quill/quill.snow.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/quill/quill.bubble.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/remixicon/remixicon.css' %}" rel="stylesheet">
    <link href="{% static 'admin/assets/vendor/simple-datatables/style.css' %}" rel="stylesheet">

    <!-- Template Main CSS File -->
    <link href="{% static 'admin/assets/css/style.css' %}" rel="stylesheet">
</head>

<body>
    <!-- Barre de navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">Jeux Olympiques 2024</a>
            <a href="/" class="btn btn-outline-light">Accueil</a>
        </div>
        {% if request.user.is_authenticated %}
        <a href="{% url 'logout' %}" class="btn btn-outline-light">Déconnexion</a>
        {% else %}
        <a href="{% url 'login' %}" class="btn btn-outline-light">Connexion</a>
        {% endif %}

    </nav>

    <!-- Liste des offres -->
    <div class="container mt-5">
        <h1 class="mb-4 text-center">Nos Offres Disponibles</h1>
        <div class="row">
            {% for offre in offres %}
            <div class="col-md-4">
                <div class="card mb-4 shadow-sm" style="background-color: aquamarine;">
                    <div class="card-body">
                        <h5 class="card-title">{{ offre.nom }}</h5>
                        <p class="card-text">{{ offre.description }}</p>
                        <p class="fw-bold text-primary">Prix : {{ offre.prix }} €</p>
                        <a href="{% url 'ajouter_au_panier' offre.id %}" class="btn btn-success">Ajouter au panier</a>
                        <a href="{% url 'reservation_create' %}?offre_id={{ offre.id }}"
                            class="btn btn-primary">Réserver</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light py-3 mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2024 Jeux Olympiques | Tous droits réservés</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% load sweetify %}
    {% sweetify %}
</body>

</html>

    
