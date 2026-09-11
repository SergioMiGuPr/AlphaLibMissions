# AlphaLib Missions

Lettre de mission, tunnel d'onboarding client et espace documentaire pour ERPNext.

Tout est écrit à la main dans ce dépôt : doctypes, print format, custom fields. Aucun
bench local n'est nécessaire, `bench migrate` pose tout à l'installation.

## Installation

### 1. Ajouter l'app au bench (Frappe Cloud)

Dashboard → Benches → votre bench → Apps → Add from GitHub
URL : `https://github.com/SergioMiGuPr/AlphaLibMissions`
Branche : `main`

Puis Deploy.

### 2. Installer sur le site

Dashboard → Sites → votre site → Install App → `alphalib_missions`

### 3. Migrer

Dashboard → Sites → votre site → Actions → Migrate

À ce stade sont créés : les 3 doctypes, le print format, et les 29 champs sur la fiche
Customer.

### 4. Créer les conditions générales

ERPNext → *Terms and Conditions* → New. Nom : `CG Lettre de mission 2026`. Coller le texte
de l'annexe 1 dans le champ *Terms*.

Ce doctype est volontairement hors de l'app : chaque nouvelle version des CG se crée dans
l'interface, et les lettres déjà signées continuent de pointer sur la version qu'elles
contenaient réellement.

### 5. Générer une première lettre

ERPNext → *AlphaLib Lettre Mission* → New. Renseigner client, entité, lieu, dates,
honoraires, conditions générales. Imprimer avec le format *AlphaLib Lettre Mission*.

## Ce qui fonctionne / ce qui reste à écrire

| Fonctionnalité | État |
|---|---|
| Champs client sur la fiche Customer | opérationnel |
| Doctypes et print format | opérationnel |
| Génération du PDF depuis le desk | opérationnel |
| Tunnel d'onboarding (page + verrou) | code présent, non branché |
| Permissions portail | à écrire (`permissions.py`) |
| Espace documentaire | à écrire (`documents.py`) |
| Signature électronique | à écrire (`signature/`), dépend du prestataire retenu |

Les hooks correspondants sont commentés dans `hooks.py`. Les décommenter au fur et à
mesure que les fichiers sont ajoutés — décommenter avant d'écrire le fichier fait échouer
la migration.

## Règle de travail

**Ce dépôt est la source de vérité.** Sans bench local, il n'y a aucun moyen de récupérer
une modification faite dans l'interface ERPNext.

Concrètement : ne modifiez pas ces doctypes ni ce print format depuis l'interface. Éditez
le JSON ici, et **incrémentez le champ `modified`** à la date du jour. Frappe compare cette
date à celle en base pour décider s'il réapplique le fichier ; sans incrément, votre
modification ne sera jamais posée.

Les custom fields sont dans `fixtures/custom_field.json` et sont rejoués à chaque migrate,
sans besoin de toucher à `modified`.

## Configuration

La clé API du prestataire de signature ira dans la configuration du site, comme
`anthropic_api_key` pour `alphalib_chat` :

Dashboard → Sites → votre site → Site Config

```json
{
  "yousign_api_key": "...",
  "yousign_webhook_secret": "..."
}
```

Lecture côté serveur avec `frappe.conf.get("yousign_api_key")`. Jamais dans un doctype
Settings : le contenu part dans les sauvegardes et s'affiche dans l'interface.

## Structure

```
alphalib_missions/
├── setup.py
├── pyproject.toml
└── alphalib_missions/
    ├── hooks.py
    ├── modules.txt                     → AlphaLib Missions
    ├── patches.txt
    ├── fixtures/
    │   └── custom_field.json           → 29 champs sur Customer
    ├── onboarding/
    │   └── gate.py                     → verrou + enregistrement des étapes
    ├── www/onboarding/
    │   ├── index.py
    │   └── index.html                  → les 6 écrans du tunnel
    └── alphalib_missions/
        ├── doctype/
        │   ├── alphalib_lettre_mission/
        │   ├── alphalib_repartition_obligation/
        │   └── alphalib_onboarding/
        └── print_format/
            └── alphalib_lettre_mission/
```
