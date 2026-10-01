# MARKO Developer Docs

Source de la documentation externe de l'API partenaire MARKO v1.

Le site Mintlify lit `docs.json` et génère la référence des endpoints depuis
`https://partner-api.marko.fr/v1/openapi.json`. Les guides éditoriaux sont dans
ce dépôt. Le schéma public contient les opérations stables ; les exports filtrés
par clé restent disponibles dans l'administration d'entité MARKO.

## Connexion à Mintlify

Dans le projet Mintlify qui dessert `developers.marko.fr`, connecter ce dépôt
GitHub et choisir la branche `main` comme branche de publication. Les fichiers
Mintlify se trouvent à la racine du dépôt. Après le premier déploiement,
contrôler la page d'accueil, l'onglet « Référence API », la copie Markdown et
`https://developers.marko.fr/llms.txt`.

## Vérification locale

```bash
npx --yes mint@latest validate
npx --yes mint@latest broken-links
npx --yes mint@latest dev
```

Le playground navigateur est désactivé dans `docs.json` : l'API de production
ne permet actuellement pas les appels CORS depuis `developers.marko.fr`.
L'exemple du guide « Premier appel » s'exécute côté serveur.
