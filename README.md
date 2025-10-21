# Plateforme de billetterie des Jeux Olympiques

Application Django permettant la gestion des offres, des réservations et des paiements Stripe pour les Jeux Olympiques. Cette version utilise désormais PostgreSQL (ou MariaDB) au lieu de SQLite et s’appuie sur Docker pour un démarrage rapide.

## Sommaire
- [Prérequis](#prérequis)
- [Configuration de l’environnement](#configuration-de-lenvironnement)
- [Lancement avec Docker](#lancement-avec-docker)
- [Lancement local (hors Docker)](#lancement-local-hors-docker)
- [Assets statiques et médias](#assets-statiques-et-médias)
- [Commandes utiles](#commandes-utiles)
- [Dépannage](#dépannage)

## Prérequis
- Python 3.10 ou supérieur (pour l’exécution hors Docker)
- Docker et Docker Compose (recommandés)
- Stripe CLI (facultatif pour simuler les webhooks)

## Configuration de l’environnement
1. Copier le fichier d’exemple :
   ```bash
   cp .env.example .env
   ```
2. Renseigner les variables obligatoires dans `.env` :
   - `SECRET_KEY` : clé Django sécurisée pour la prod
   - `DB_ENGINE` : `postgresql` (par défaut) ou `mariadb`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
   - Clés Stripe (`STRIPE_SECRET_KEY`, `STRIPE_SECRET_KEY_TEST`, `STRIPE_PUBLIC_KEY_TEST`, `STRIPE_WEBHOOK_SECRET`)
3. Ajouter si besoin `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` pour les domaines publics.

## Lancement avec Docker
```bash
docker-compose up --build
```
- Le service `postgres` démarre avec un volume persistant.
- Le service `web` attend la disponibilité de la base, exécute les migrations et `collectstatic`, puis lance `python manage.py runserver 0.0.0.0:8000`.
- Accéder à l’application sur [http://localhost:8000](http://localhost:8000).

### Exécuter les migrations manuellement
```bash
docker-compose run --rm web python manage.py migrate
```

### Collecter les fichiers statiques
```bash
docker-compose run --rm web python manage.py collectstatic --noinput
```

## Lancement local (hors Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Assurez-vous que PostgreSQL ou MariaDB est accessible et que les variables `DB_*` correspondent.

## Assets statiques et médias
- Les fichiers statiques sont servis par Django/Whitenoise. Pensez à lancer `collectstatic` en prod ou lors du build Docker.
- Les images présentes dans `static/admin/assets/img` et `static/tickets` sont accessibles via la balise `{% static %}` et ne doivent plus générer de 404.
- En développement, les fichiers médias (`MEDIA_URL`) sont servis par Django ; en production, envisagez un CDN ou un bucket S3/GCS.

## Commandes utiles
Le projet inclut un `Makefile` :

| Commande | Description |
|----------|-------------|
| `make up` | Démarre l’environnement Docker (équivalent à `docker-compose up --build`) |
| `make down` | Stoppe les services Docker |
| `make migrate` | Applique les migrations via le conteneur web |
| `make collectstatic` | Lance `collectstatic` dans le conteneur |

## Dépannage
- **La base ne répond pas** : vérifiez `docker-compose logs postgres` et que les variables `DB_*` sont cohérentes.
- **Erreur sur les fichiers statiques** : assurez-vous d’avoir exécuté `collectstatic` et que le volume `staticfiles/` est monté si nécessaire.
- **Webhooks Stripe** : utilisez `stripe listen --forward-to localhost:8000/webhook/stripe/` et mettez à jour `STRIPE_WEBHOOK_SECRET`.
- **Permissions superuser** : créez un compte avec `python manage.py createsuperuser` (ou via `docker-compose run --rm web python manage.py createsuperuser`).

Pour toute autre question, consultez la documentation Django ou ouvrez une issue sur le dépôt du projet.
