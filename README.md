# MARKO Developer Docs

Source de la documentation externe de l'API partenaire MARKO v1.

Le site Mintlify lit `docs.json` et génère la référence depuis `openapi.json`.
Ce contrat conserve les routes GA, operationId, scopes et security du catalogue
public. Il enrichit les types à partir des modèles du **SHA effectivement servi**
et des sérialiseurs dict/stream vérifiés. Seuls les modèles accessibles depuis
les routes publiques sont exportés; les modèles bêta/admin inutilisés sont exclus.

Les objets extensibles restent ouverts. Les exemples sont synthétiques et leur
conformité JSON Schema ne prouve pas l'exécution d'un parcours client. Les exports
filtrés par clé restent disponibles dans l'administration d'entité MARKO.

## Connexion à Mintlify

Dans le projet Mintlify qui dessert `developers.marko.fr`, connecter ce dépôt
GitHub et choisir la branche `main` comme branche de publication. Les fichiers
Mintlify se trouvent à la racine du dépôt. Après le premier déploiement,
contrôler la page d'accueil, la section « Référence API » du menu latéral, la copie Markdown et
`https://developers.marko.fr/llms.txt`.

## Vérification locale

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/check-reference.py
python3 scripts/check-reference.py --live
npx --yes mint@4.2.964 validate
npx --yes mint@4.2.964 broken-links
npx --yes mint@4.2.964 dev --port 3947
```

Le playground navigateur est désactivé dans `docs.json` : l'API de production
ne permet actuellement pas les appels CORS depuis `developers.marko.fr`.
L'exemple du guide « Premier appel » s'exécute côté serveur.

La CI vérifie les exemples, références, scopes visibles, types des réponses,
paramètres et cohérence du téléchargement complet. Un contrôle quotidien détecte
une modification du catalogue public ou du SHA servi. Il échoue pour demander
une revue; il ne publie pas automatiquement un schéma non vérifié.

## Mettre à jour les contrats

Lire `https://partner-api.marko.fr/health` et le contrat public courant. Utiliser
un checkout backend propre au `git_sha` servi et le Python existant du backend.
L'exporteur ignore l'environnement racine, bloque les connexions réseau,
n'écrit pas de bytecode et ne démarre pas l'API. Le backend n'est pas modifié.

Revoir `scripts/response_contracts.py` et les contraintes complémentaires de
`scripts/build-reference.py` si leurs sources changent. Ne pas publier un
snapshot périmé comme contrat courant.

```bash
curl --fail https://partner-api.marko.fr/v1/openapi.json -o /tmp/public-openapi.json
PYTHONDONTWRITEBYTECODE=1 /path/to/backend/.venv/bin/python scripts/export-native.py \
  --backend /path/to/clean-checkout/backend \
  --sha SERVED_GIT_SHA --output /tmp/native-openapi.json
python3 scripts/build-reference.py \
  --public /tmp/public-openapi.json --native /tmp/native-openapi.json --output openapi.json
python3 scripts/check-reference.py --write-download --live
PYTHONDONTWRITEBYTECODE=1 /path/to/backend/.venv/bin/python scripts/export-native.py \
  --backend /path/to/clean-checkout/backend --sha SERVED_GIT_SHA \
  --output /tmp/native-checked.json --examples openapi.json
```

Après une modification de guide, régénérer `downloads/marko-documentation.json` avec
`--write-download`. La copie complète utilise un petit composant React conforme
aux snippets Mintlify; les pages conservent leur copie Markdown native.
Le fichier complet contient les guides et OpenAPI avec tous ses `$ref` dans ses
composants. Son champ `markdown` contient le texte complet. Un JSON permet le
téléchargement machine. Les fichiers JSON sont lus depuis la branche publique
GitHub, car le preview Mintlify ne sert pas ces fichiers à leur URL attendue.
Cela évite aussi de dépendre du support des assets TXT réservé à Enterprise.
La référence et le téléchargement complet sont générés et vérifiés ensemble.
Tester la copie dans un vrai navigateur avant publication.

Les fichiers temporaires d'extraction, captures et rapports restent hors Git.
Aucun secret ni credential métier n'est nécessaire pour ces contrôles publics.
