"""Editorial descriptions reviewed against the served models and serializers.

Types and validators stay in the backend export. This file explains their
meaning; ambiguous names (status, type, scope, source) use model overrides.
"""

COMMON = dict(line.split("|", 1) for line in """
accepted|Indique si la proposition d'événement a été acceptée.
accepted_at|Date d'acceptation de la demande ou de la recommandation.
action|Action effectuée sur le compte utilisateur.
actions|Actions d'effacement enregistrées dans le dossier; leur présence ne signifie pas que toutes sont terminées.
active_events|Nombre d'événements de risque encore ouverts.
actor_email|Adresse e-mail de l'auteur de l'événement, si elle est disponible.
actor_id|Identifiant de l'auteur de l'événement.
actor_name|Nom de l'auteur affiché dans la chronologie.
actor_type|Nature de l'auteur: utilisateur, système ou intégration selon l'événement.
adresse|Adresse postale déclarée pour la société ou le dirigeant.
adresse_ligne_1|Première ligne de l'adresse postale.
adresse_ligne_2|Deuxième ligne de l'adresse postale.
adresse_ligne_3|Troisième ligne de l'adresse postale.
adresse_siege|Adresse du siège social issue des données de la société.
ai_enabled|Indique si les fonctions IA sont activées pour l'entité; les droits de la clé restent requis.
alert_config|Configuration des règles d'alerte associées à ce champ métier.
alert_persistence_failed|Indique que la comparaison a produit un résultat mais que l'enregistrement de son alerte a échoué.
alert_status|État de traitement de l'alerte, distinct de son niveau de gravité.
alert_type|Type d'alerte auquel cette préférence s'applique.
applied_suggestions|Nombre de suggestions appliquées pour ce job.
approved_at|Date d'approbation du compte utilisateur.
approved_by|Identifiant de l'utilisateur qui a approuvé ce compte.
archived_at|Date d'archivage de la tâche; null si elle n'est pas archivée.
asset_manager_nom|Nom de l'asset manager associé à la cible de la tâche.
assignee_id|Identifiant utilisateur du responsable de la tâche; ce champ n'est pas nécessairement un UUID.
assignment_label|Libellé du rapprochement du remboursement avec l'échéancier.
assignment_status|État du rapprochement du remboursement avec l'échéancier.
attempts|Nombre de tentatives de traitement de cet élément d'import.
audit_entries|Événements d'audit exportables pour cet utilisateur; consulter le manifeste pour les sources non exportées.
aum_des_fonds|Actifs sous gestion agrégés des fonds, issus des valeurs documentaires disponibles.
aum_du_fonds|Actifs sous gestion de ce fonds, issus de ses valeurs documentaires.
author_name|Nom de l'auteur de la note ou du commentaire.
authority_mode|Mode d'autorité appliqué à la recherche documentaire.
auto_applied|Nombre de suggestions appliquées automatiquement par le job; distinct du nombre de suggestions créées.
beneficiaire_effectif|Bénéficiaire effectif déclaré pour la SPV.
beneficiaires_effectifs|Bénéficiaires effectifs connus dans les données de la société.
blocked_reason_codes|Codes des motifs qui limitent ou bloquent l'accès aux résultats documentaires.
brand_baseline|Texte de signature associé à la marque de l'entité.
bundle_key|Clé du groupe de recommandations à matérialiser.
bundles|Recommandations regroupées par thème et accompagnées de leurs compteurs.
cabinet_avocat|Cabinet d'avocats chargé du contentieux.
cached|Indique que les données SIREN proviennent d'un résultat déjà disponible.
calculation_dependencies|Champs nécessaires au calcul de cette propriété métier.
calculation_formula|Formule de calcul déclarée pour cette propriété.
calculation_trigger|Événement ou mode qui déclenche le calcul de cette propriété.
can_edit|Indique si l'utilisateur délégué peut modifier ce dashboard.
can_manage|Indique si l'utilisateur délégué peut gérer le partage de ce dashboard.
cancel_requested|Indique qu'une annulation du job a été demandée; les éléments déjà terminés sont conservés.
canonical_code|Code MARKO canonique associé à cette option, lorsqu'il existe.
capability|Capacité de création à laquelle se rapporte le reçu d'idempotence.
capital_social|Capital social déclaré de la société.
categorie|Catégorie de la tâche Kanban, distincte de sa priorité et de son statut.
certificate_reference|Référence du certificat d'effacement, si elle existe; null ne constitue pas une preuve d'effacement.
classe_actif|Classe d'actif de l'opération. Pour une écriture externe, consulter la dimension asset_class de GET /taxonomies.
client_request_id|Identifiant durable de la création manuelle; conserver la même valeur pour reprendre la même création.
code|Code stable de la ressource ou de l'option. Conserver la valeur retournée par MARKO.
code_pays|Code pays fourni avec l'adresse.
code_postal|Code postal de l'adresse.
color|Couleur d'affichage; respecter les valeurs ou le format indiqués dans le schéma.
column_name|Nom de la colonne de stockage associée à la propriété métier.
columns|Colonnes à afficher, dans l'ordre transmis.
complement_adresse|Complément d'adresse postale.
completed_items|Nombre d'éléments d'import traités avec une mutation réussie.
confidence|Indice de confiance associé au résultat; il ne remplace pas une validation humaine.
config|Configuration métier du workflow.
conflict_items|Nombre d'éléments d'import arrêtés par un conflit à résoudre.
conflict_payload|Informations sur les valeurs en conflit; comparer la cible actuelle avant une reprise.
content|Contenu du commentaire ou de la note.
contentieux_items|Contentieux détaillés rattachés à la SPV.
count|Nombre de notifications non lues.
covenant_id|Identifiant du covenant contrôlé.
covenant_type|Type d'engagement contractuel contrôlé.
covenants|Covenants à surveiller dans la synthèse RCCI.
covenants_breach_count|Nombre de covenants en dépassement de seuil.
covenants_warning_count|Nombre de covenants en zone d'avertissement.
crd_mezzanine|Capital restant dû sur les tranches mezzanine.
crd_senior|Capital restant dû sur les tranches senior.
crd_total|Capital restant dû total à la date de référence.
crd_total_source|Origine du capital restant dû: financing_tranches ou operation_data.
created|Indique si une nouvelle fiche documentaire a été créée par cet appel.
created_by|Identifiant de l'utilisateur qui a créé le template.
created_workflow_key|Clé du workflow créé depuis la recommandation, si cette création a eu lieu.
critical_count|Nombre d'éléments classés critiques dans ce groupe.
dashboard_sort_order|Position de la tâche dans le board consolidé.
date_ag_annuelle|Date de l'assemblée générale annuelle de la SPV.
date_cessation|Date de cessation d'activité de la société.
date_closing_prevue|Date prévisionnelle du closing du deal.
date_cloture_exercice|Date de clôture de l'exercice de la société.
date_cloture_exercice_exceptionnelle|Date de clôture exceptionnelle de l'exercice, si elle est renseignée.
date_creation|Date de création de la société, du fonds ou du dossier; distincte de created_at dans MARKO.
date_dernier_calcul|Date du dernier calcul du covenant.
date_liquidation|Date de liquidation du fonds, lorsqu'elle est renseignée.
date_naissance|Date de naissance du dirigeant.
date_prise_de_poste|Date de prise de fonction du dirigeant.
date_prochaine_cloture_exercice|Prochaine date de clôture d'exercice connue.
date_radiation|Date de radiation de la société du registre.
date_reference|Date à laquelle les valeurs du snapshot KPI se rapportent.
date_reference_reporting|Date de référence utilisée par le reporting de l'entité.
date_sourcing|Date d'entrée du deal dans le pipeline.
days|Nombre de jours de report demandé pour la recommandation.
deadline|Date limite attendue pour la pièce documentaire.
deal_id|UUID du deal auquel la note est rattachée.
debt_yield|Rendement de la dette, exprimé en fraction: 0.08 signifie 8 %.
decision|Décision d'accès appliquée à la recherche documentaire.
default_schedule_kind|Mode de planification proposé par défaut pour ce preset.
default_scope|Périmètre métier initial du dashboard.
default_status|Statut canonique proposé par défaut pour une opération.
demo_state|État de démonstration associé au profil dans l'export RGPD.
denied_reason|Motif du refus d'accès aux résultats documentaires.
denomination|Dénomination du dirigeant lorsqu'il s'agit d'une personne morale.
description|Description libre de la ressource.
detail|Informations détaillées sur le problème ou le dossier.
detected_at|Date de détection de l'événement de risque.
differences|Écarts constatés entre les données du Kbis et celles du fournisseur.
dimension|Dimension de taxonomie à laquelle cette option appartient.
dirigeants|Dirigeants connus de la société.
dismissed_at|Date à laquelle la recommandation a été classée non pertinente.
display_label|Libellé de l'option à afficher; utiliser code comme identifiant stable.
document|Fiche du document associée à l'identifiant externe.
document_ids|UUID des pièces associées au contentieux.
document_type|Type métier du document; distinct de son type MIME.
document_values|Valeurs du fonds extraites de ses documents.
documents|Pièces documentaires prises en compte dans la synthèse RCCI.
documents_compared|Documents utilisés pour la comparaison KYB.
documents_missing_count|Nombre de pièces documentaires manquantes dans la synthèse RCCI.
download_url|URL de téléchargement disponible pour ce document. Elle peut être absente; ne pas la traiter comme un identifiant permanent.
dscr|Ratio de couverture du service de la dette, exprimé comme un multiple: 1.25 signifie une couverture de 1,25 fois.
due_date|Date d'échéance de la tâche, au format YYYY-MM-DD.
email|Adresse e-mail du compte utilisateur.
email_brand_name|Nom de marque utilisé dans les e-mails de l'entité.
email_branding_mode|Mode de personnalisation des e-mails.
email_branding_version|Version de la configuration de marque des e-mails.
email_from_address|Adresse d'expédition configurée pour les e-mails.
email_reply_to|Adresse proposée pour répondre aux e-mails.
email_sending_domain|Domaine d'expédition configuré pour l'entité.
email_sending_domain_status|État de validation du domaine d'expédition.
email_verified|Indique si l'adresse e-mail du compte a été vérifiée.
entity_databases|Résultats des sources de données de l'entité incluses dans l'inventaire ou l'export RGPD.
entity_id|Identifiant de l'entité MARKO à laquelle cette ressource appartient.
entity_type|Type de ressource auquel se rapporte la vue ou le traitement.
entreprise_cessee|Indique si la société est déclarée en cessation d'activité.
entries|Événements de la chronologie de l'opération.
entry_type|Catégorie de l'événement dans l'historique technique.
enum_values|Valeurs proposées pour cette propriété métier lorsqu'elle possède un choix fermé.
error|Message d'échec de l'enrichissement SIREN, lorsqu'il existe.
escalation_level|Niveau d'escalade de l'alerte ou de la notification.
event_date|Date et heure de l'événement de calendrier.
event_type|Type de l'événement.
evidence|Données utilisées pour établir la recommandation; ne constituent pas à elles seules une autorisation d'écriture.
expected_updated_at|Valeur updated_at lue avant la modification. Une version concurrente exige une nouvelle lecture et une réévaluation.
expires_at|Date d'expiration du bearer.
export_date|Date de génération de l'export RGPD.
export_id|Identifiant de l'export RGPD.
extraction_confidence_threshold|Seuil de confiance configuré pour l'extraction de cette propriété.
extraction_hints|Indications destinées à l'extraction de cette propriété depuis les documents.
failed_items|Nombre d'éléments d'import en échec.
fetched_at|Date de récupération des données SIREN auprès de leur source.
field|Propriété sur laquelle porte la différence KYB.
field_key|Clé stable de la propriété métier.
field_name|Nom du champ modifié dans l'événement d'historique.
fields|Champs configurables proposés par le preset.
filters|Filtres enregistrés pour la vue, le dashboard ou le template.
first_name|Prénom de l'utilisateur.
follow_up|Politique de création manuelle des notes de suivi.
fond|Politique de création manuelle des fonds.
fond_ids|UUID des fonds à inclure dans le périmètre.
fond_name|Nom du fonds associé à la ressource.
format|Format de sortie demandé pour le reporting.
forme_juridique|Forme juridique déclarée de la société.
forme_societe_mere|Forme juridique de la société mère de l'opérateur.
frequence_reporting|Fréquence de reporting configurée pour l'entité.
generated_at|Date de génération des recommandations.
groups|Résultats de recherche regroupés par type de ressource.
has_critical|Indique si au moins une notification critique non lue existe.
headers|En-têtes des colonnes de l'aperçu de reporting, dans le même ordre que les cellules.
highlight_id|Identifiant de l'élément à mettre en évidence dans l'interface.
icon|Icône d'affichage de la vue sauvegardée; respecter la liste de valeurs autorisées.
icon_key|Clé de l'icône associée à l'option de taxonomie.
icr|Ratio de couverture des intérêts, exprimé comme un multiple.
idempotency_key|Clé utilisée pour cette intention; la conserver avec le job ou la ressource.
idempotency_receipt|Reçu de création manuelle indiquant notamment si une création précédente a été rejouée.
identite_entreprise|Identité structurée de la société et informations de registre.
ids|Identifiants des ressources incluses dans le périmètre sélectionné.
image|Image de profil de l'utilisateur, si elle est renseignée.
impact|Indication de l'effet métier attendu du preset.
importance|Importance attribuée à cette propriété dans le référentiel métier.
info_count|Nombre d'événements de risque informatifs.
interest|Part d'intérêts du remboursement enregistré.
invitation_delivery|Résultat de l'envoi de l'invitation; la création du compte ne garantit pas la livraison de l'e-mail.
invitation_expires_at|Date d'expiration de l'invitation du compte.
is_active|Indique si l'élément est actif.
is_composite|Indique si la notification regroupe plusieurs informations.
is_default|Indique si cette vue ou ce template est défini par défaut.
is_draft|Indique si la SPV est encore à l'état de brouillon.
is_pending_invite|Indique si l'utilisateur doit encore activer son invitation.
is_radiee|Indique si la société est radiée du registre.
is_required|Indique si cette propriété est requise dans le référentiel métier; distinct des champs obligatoires du corps HTTP.
is_resolved|Indique si le commentaire ou l'événement de risque est résolu.
is_shared|Indique si le dashboard est partagé.
is_visible|Indique si l'option est visible dans le catalogue de l'entité.
issued_at|Date d'émission du bearer.
item_kind|Nature de l'élément importé: opération ou note de suivi.
job_type|Type de traitement exécuté par le job.
job_types|Types de traitements associés à cette définition de workflow.
juridiction|Juridiction compétente pour le contentieux.
justice_pappers|Données judiciaires fournies pour la SPV.
kbis_value|Valeur lue dans le Kbis pour la propriété comparée.
key|Clé stable du preset ou du groupe de recommandations.
kpi_snapshot|Indicateurs financiers à la date de référence; utiliser les unités définies dans le guide Pagination et données.
kpis|Indicateurs de suivi des recommandations, distincts des KPI financiers d'une opération.
kyb_comparison|Comparaison des informations de registre avec les pièces disponibles.
label|Libellé à afficher pour cette option, ce groupe ou ce preset.
label_editable|Indique si le libellé de l'option peut être modifié dans MARKO.
label_fr|Libellé français de la propriété métier.
label_ids|UUID des labels à associer à la tâche.
labels|Labels actuellement associés à la tâche.
last_error|Dernière erreur enregistrée pour cette définition de workflow.
last_name|Nom de famille de l'utilisateur.
last_run_at|Date de la dernière exécution du workflow.
latest_event_at|Date du dernier événement de risque connu.
latitude|Latitude géographique de l'adresse.
layout|Disposition des widgets du dashboard.
lead_operateur_id|UUID MARKO de l'opérateur principal de l'opération.
level|Niveau du périmètre métier du dashboard.
litiges_detail|Détails des litiges déclarés pour la société.
litiges_en_cours|Indique si des litiges sont déclarés en cours.
logo_url|URL du logo de l'entité.
longitude|Longitude géographique de l'adresse.
ltc|Loan-to-Cost en fraction: 0.65 signifie 65 %. La valeur persistée est comprise entre 0 et 2.
ltv|Loan-to-Value en fraction: 0.65 signifie 65 %. La valeur persistée est comprise entre 0 et 2.
luhn_valid|Indique si les neuf chiffres du SIREN satisfont le contrôle Luhn.
manifest|Manifeste de l'export: sources lues, indisponibles ou exclues. Le vérifier avant de considérer l'export comme complet.
manual_creation_policy|Politique de création manuelle par famille de ressources.
manual_review_required|Indique qu'une revue humaine reste nécessaire pour ce dossier ou cette action.
marge_pct|Marge calculée par rapport au seuil contractuel du covenant.
marked_read|Nombre de notifications marquées comme lues par cet appel.
member_ids|Identifiants des membres concernés par le partage du dashboard.
memory_policy|Politique appliquée aux données de mémoire dans cette recherche.
message|Message destiné à l'affichage ou au diagnostic.
metadata|Informations complémentaires de l'événement; leurs clés dépendent de son type.
min_severity|Gravité minimale des alertes pour lesquelles la préférence s'applique.
mode_reporting|Mode de reporting configuré pour l'entité.
montage|Montage financier de la SPV; utiliser une valeur de l'énumération.
montant_demande|Montant réclamé dans le contentieux.
montant_estime|Montant prévisionnel du deal.
monthly_false_negative_proxy_count|Nombre mensuel d'événements utilisés comme indicateur indirect de faux négatifs; ce n'est pas un décompte exhaustif des erreurs.
monthly_false_positive_count|Nombre mensuel de recommandations déclarées comme faux positifs.
name_modifiable|Indique si le nom de la propriété peut être modifié dans le référentiel.
narrative|Résumé textuel produit par l'extraction IA.
nature|Nature du contentieux.
new_sort_order|Nouvelle position de la tâche dans le périmètre de réordonnancement.
new_status|Statut cible de la tâche après son déplacement.
new_value|Valeur du champ après la modification enregistrée.
next_run_at|Date de la prochaine exécution planifiée, si elle existe.
noi|Net Operating Income: revenu opérationnel net utilisé pour les ratios financiers.
nom|Nom de famille de la personne.
nombre_de_spv|Nombre de SPV indiqué dans les valeurs documentaires du fonds.
noop_items|Nombre d'éléments traités sans changement de la ressource.
note|Commentaire associé à la décision sur la recommandation.
note_type|Type de note ou de commentaire.
notifications|Notifications exportables de cet utilisateur.
numero_tva_intracommunautaire|Numéro de TVA intracommunautaire connu pour la société.
old_value|Valeur du champ avant la modification enregistrée.
operateur|Politique de création manuelle des opérateurs.
operateur_nom|Nom de l'opérateur associé à la cible de la tâche.
operation|Politique de création manuelle des opérations.
operation_name|Nom de l'opération concernée.
operation_piloting_url|Lien vers le pilotage de l'opération dans MARKO.
operation_resolution|Résultat du rattachement du job d'extraction à une opération.
operation_url|Lien vers la fiche de l'opération dans MARKO.
operations_at_risk_count|Nombre d'opérations signalées à risque dans la synthèse RCCI.
operations_count|Nombre d'opérations rattachées à la SPV.
optional_count|Nombre de recommandations optionnelles dans ce groupe.
ordering_scope|Périmètre du déplacement: board de l'opération ou board consolidé.
ordre_affichage|Position de la propriété dans son groupe d'affichage.
organisation_pappers|Données d'organisation obtenues du fournisseur pour la SPV.
outcome|Résultat de la synchronisation: created, updated, noop, restored ou bound. Conserver marko_id quel que soit ce résultat.
page_count|Nombre de pages connu pour le document trouvé.
page_onglet|Onglet de l'interface auquel la propriété est rattachée.
pappers_request_metadata|Métadonnées exportables des requêtes fournisseur associées au sujet RGPD.
pappers_value|Valeur fournie par Pappers pour la propriété comparée.
parent_code|Code de l'option parente dans la taxonomie, lorsqu'elle existe.
parent_external_id|Identifiant externe de l'opération parente d'une note importée.
partie_adverse|Partie adverse dans le contentieux.
partner_metadata|Métadonnées fournies par l'intégration partenaire pour ce document.
payload_digest|Empreinte du contenu de la création manuelle utilisée pour détecter une reprise incompatible.
pays|Nom du pays dans l'adresse fournie.
pct_perte_estimee|Perte estimée en fraction comprise entre 0 et 1: 0.03 signifie 3 %.
pending_suggestions|Nombre de suggestions de ce job qui attendent encore un traitement.
permission|Niveau de permission accordé par le partage du dashboard.
personne_morale|Indique si le dirigeant est une personne morale.
phase|Phase métier de l'opération; distincte de son statut.
phase_key|Clé de phase métier à laquelle la tâche est rattachée.
policy_decision|Détails de la décision de politique appliquée à la recherche documentaire.
portfolio_goals|Objectifs portefeuille configurés pour l'entité.
position|Position de l'élément dans sa liste.
preferences|Préférences de l'utilisateur délégué, limitées aux propriétés acceptées par la route.
prefill_edit_rate|Taux de modification des valeurs préremplies des recommandations.
prenom|Prénom de la personne.
preset_key|Clé du preset de workflow; utiliser une valeur du catalogue de presets.
presidents|Présidents connus de la société.
primary_color|Couleur principale de la marque de l'entité.
principal|Part de capital du remboursement enregistré.
priority|Priorité de l'élément; les valeurs acceptées figurent dans le schéma.
privacy_case_id|UUID du dossier durable de traitement RGPD.
privacy_cases|Dossiers RGPD exportables associés au sujet.
procedure_collective|Indique si une procédure collective est déclarée pour la SPV.
procedures_collectives|Procédures collectives connues de la société.
processed_items|Nombre d'éléments du lot qui ont reçu un résultat de traitement.
profile|Profil du sujet concerné par l'export RGPD.
provider|Fournisseur utilisé par le job d'extraction IA.
provider_event_id|Identifiant de l'événement dans le système du fournisseur.
provision|Provision déclarée pour le contentieux.
pv_ag_document_id|UUID du document contenant le procès-verbal d'assemblée générale.
qualite|Fonction ou qualité du dirigeant.
qualites|Fonctions ou qualités connues du dirigeant.
query|Texte de recherche reçu par le service.
raison_sociale|Dénomination légale de la société.
raw_data|Données de l'événement fournies par sa source, avec une structure propre au fournisseur.
raw_result|Résultat brut public du job IA. Sa structure dépend du traitement et ne garantit pas une application des suggestions.
read|Indique si la notification ou l'alerte a été lue.
reason|Motif donné pour la décision sur la recommandation.
reason_code|Code structuré du motif de refus; préférable au texte du message pour le diagnostic.
reason_codes|Codes des motifs ayant conduit à cette recommandation.
recommendation_acceptance_rate|Taux d'acceptation des recommandations du périmètre.
recommendation_dismiss_rate|Taux de recommandations classées non pertinentes.
recommendation_id|UUID de la recommandation persistée à l'origine de cette définition; ne pas fournir un identifiant preview.
recommendation_snooze_rate|Taux de recommandations reportées.
recommendations_total|Nombre total de recommandations du périmètre.
recommended_count|Nombre de recommandations de priorité recommended dans ce groupe.
reconciliation_required|Indique que le résultat doit encore être rapproché de l'état réel du dossier.
reference|Référence de suivi de la livraison de l'invitation.
region|Région géographique déclarée de la société.
reject_reason|Motif du rejet du document.
relationship_label|Libellé du rattachement de l'opération visible dans ce contexte.
relationship_status|État du rattachement de l'opération visible dans ce contexte.
remaining_balance|Capital restant après ce remboursement.
replayed|Indique qu'une réponse liée à la même intention a été retrouvée et rejouée.
report_external_neutrality|Paramètre de neutralité du reporting externe de l'entité.
representant_legal|Représentant légal connu de la société.
reputation_gouvernance_label|Libellé du niveau de réputation et de gouvernance de l'opérateur.
reputation_gouvernance_score|Score de réputation et de gouvernance de l'opérateur.
requires_human_validation|Indique si les valeurs extraites de cette propriété requièrent une validation humaine.
resolved_at|Date de résolution de l'événement, du commentaire ou du conflit.
resolved_by|Identifiant de l'utilisateur qui a résolu le commentaire.
resolved_events|Nombre d'événements de risque résolus.
resource|État de la ressource MARKO après la synchronisation externe.
responsable|Responsable déclaré du deal.
responsable_interne|Responsable interne associé à la ressource.
result_mode|Mode de restitution du résultat d'effacement; la réponse expose les métadonnées du dossier.
resultat_net_ag|Résultat net présenté à l'assemblée générale de la SPV.
results|Résultats de recherche accessibles dans ce périmètre.
results_url|Chemin permettant de lire les résultats individuels du job; peut être relatif à l'hôte de l'API.
retry_count|Nombre de reprises enregistrées pour ce traitement.
retryable|Indique si l'échec de livraison de l'invitation peut faire l'objet d'une reprise.
review_required|Indique que le résultat demande une revue humaine.
risk_factor|Facteur de risque associé à cette propriété métier.
risk_grade|Classe de risque attribuée à l'opération.
risk_label|Libellé du niveau de risque agrégé.
risk_level|Niveau de risque de l'opération.
risk_operations|Opérations à risque incluses dans la synthèse RCCI.
risk_score|Score de risque calculé pour la ressource.
risk_score_impact|Contribution de l'événement au score de risque.
risk_score_simple|Score de risque de l'opération, en points de 0 à 100.
risk_threshold|Seuil de risque configuré pour l'entité.
risk_weight|Poids de cette propriété dans l'évaluation du risque.
role|Rôle du compte utilisateur dans l'entité.
role_id|Identifiant du rôle appliqué à la recherche documentaire.
route_id|Identifiant de la route concernée par le problème.
rows|Lignes de l'aperçu de reporting; les cellules suivent l'ordre des headers.
run|Exécution créée ou retrouvée pour ce workflow.
schedule_config|Paramètres de planification du workflow pour le schedule_kind choisi.
schedule_kind|Mode de planification: utiliser une valeur du catalogue de presets.
schedule_projection_id|Identifiant de la projection d'échéancier à laquelle le remboursement est rapproché.
schema_version|Version du format de l'export RGPD.
scope|Périmètre métier ou droit concerné; le modèle de cette réponse précise son type.
scope_id|Identifiant de la ressource du périmètre; il peut être absent pour le périmètre entité.
scope_unavailable|Indique que le périmètre enregistré du dashboard n'est pas disponible pour cet utilisateur.
score|Score de classement de la recommandation.
secondary_color|Couleur secondaire de la marque de l'entité.
section|Section d'affichage de la propriété métier.
service_dette|Service de la dette utilisé pour le calcul du DSCR; aligner sa période avec celle du NOI.
seuil_contractuel|Seuil défini dans le contrat pour ce covenant.
severity|Niveau de gravité de l'événement, distinct de son statut de traitement.
share_token|Jeton associé au partage du dashboard, lorsqu'il existe; ne pas le publier.
sharing|Visibilité, permissions et membres du partage du dashboard.
siren_mere|SIREN de la société mère de l'opérateur.
siret|Identifiant SIRET de l'établissement sur 14 chiffres, distinct du SIREN sur 9 chiffres.
snoozed_until|Date jusqu'à laquelle l'alerte ou la recommandation est reportée.
sort|Critères de tri enregistrés pour la vue.
sort_order|Position de la tâche dans le board de son opération.
source|Origine déclarée de l'événement ou du remboursement.
source_alert_id|Identifiant de l'alerte à l'origine de l'événement de calendrier.
source_display_name|Nom lisible de l'origine de l'option de taxonomie.
source_extraction|Origine des données extraites pour l'opérateur.
source_kind|Nature de l'origine de l'option: catalogue MARKO ou source propre à l'entité.
source_priority|Ordre de priorité des sources de cette propriété métier.
source_type|Type de source de l'événement ou de la propriété métier.
sources|Sources des événements de risque inclus dans la synthèse.
sources_dette_mezz|Sources documentaires prévues pour cette propriété en dette mezzanine.
sources_dette_senior|Sources documentaires prévues pour cette propriété en dette senior.
sources_equity_majoritaire|Sources documentaires prévues pour cette propriété en equity majoritaire.
sources_equity_minoritaire|Sources documentaires prévues pour cette propriété en equity minoritaire.
sources_mix|Sources documentaires prévues pour cette propriété dans un investissement mixte.
sous_classe_actif|Sous-classe d'actif de l'opération.
spv|Politique de création manuelle des SPV.
spv_count|Nombre de SPV rattachées au fonds.
spv_ids|UUID des SPV à inclure dans le périmètre.
spv_name|Nom de la SPV associée à la ressource.
started_at|Date de début du traitement.
state|État de traitement ou de validation du document.
status_url|Chemin permettant de lire l'état du job; peut être relatif à l'hôte de l'API.
statuses|Statuts du socle canonique historique; GET /taxonomies expose aussi les options visibles de l'entité.
statut|Statut de la tâche Kanban.
statut_interne|Code de statut interne de l'opération; consulter la dimension internal_status de GET /taxonomies.
statut_operationnel|Codes de statuts opérationnels de l'opération; consulter la dimension operational_status de GET /taxonomies.
statuts_internes|Statuts internes du socle canonique historique.
statuts_operationnels|Statuts opérationnels du socle canonique historique.
storage_path|Référence du fichier dans le stockage; utiliser download_url pour le télécharger.
subtitle|Informations secondaires à afficher sous le titre du résultat de recherche.
success|Indique si l'enrichissement SIREN a produit un résultat exploitable.
suggestions_count|Nombre total de suggestions associées à ce job.
suggestions_created|Nombre de suggestions créées par l'extraction; leur création ne prouve pas leur validation ou leur application.
summary|Résumé du groupe de recommandations.
support|Informations de suivi disponibles pour diagnostiquer la livraison de l'invitation.
support_badge_count|Compteur du badge de support pour cet utilisateur.
table_name|Nom de la table associée à la propriété métier.
target_filter|Filtre à appliquer lors de l'ouverture de la cible dans MARKO.
target_id|Identifiant de la ressource MARKO créée ou retrouvée par cet élément d'import.
target_name|Nom de la ressource à laquelle la tâche se rapporte.
target_tab|Onglet à ouvrir sur la cible dans MARKO.
target_type|Type de ressource à laquelle la tâche se rapporte.
target_url|Lien vers la ressource concernée dans l'interface MARKO.
task_id|UUID de la tâche Kanban à déplacer.
template|Template utilisé pour produire cet aperçu de reporting.
text|Texte de la note ou du commentaire.
time_to_activation_after_recommendation_hours|Délai d'activation après recommandation, exprimé en heures.
title|Titre affiché pour l'événement ou le problème.
titre|Titre de la tâche Kanban.
token_type|Type de jeton retourné: Bearer.
total_events|Nombre total d'événements de risque du périmètre.
total_fonds|Nombre de fonds inclus dans la synthèse portefeuille.
total_nominal|Nominal agrégé des opérations visibles dans la synthèse portefeuille.
total_notes|Nombre de notes reçues dans le lot d'import.
total_operateurs|Nombre d'opérateurs inclus dans la synthèse portefeuille.
total_operations|Nombre d'opérations du lot ou de la synthèse portefeuille.
total_rows|Nombre total de lignes correspondant aux filtres du reporting.
total_spvs|Nombre de SPV incluses dans la synthèse portefeuille.
tranche_id|UUID de la tranche de financement associée au remboursement.
tribunal|Tribunal associé à la procédure collective.
type_investissement|Code de type d'investissement; consulter la dimension investment_type de GET /taxonomies.
type_operation|Code de type d'opération; consulter la dimension operation_type de GET /taxonomies.
unit|Unité de la propriété dans le référentiel métier; la lire avant de convertir une valeur.
until|Date jusqu'à laquelle la recommandation doit être reportée.
url|Lien vers la fiche de la ressource trouvée dans MARKO.
usage_count|Nombre d'utilisations de cette option de taxonomie.
valeur_actuelle|Valeur du dernier calcul du covenant.
valeur_venale|Valeur de marché de l'actif utilisée pour calculer la LTV.
valid|Indique si le SIREN satisfait les contrôles de validation de cette route.
validation_max|Valeur maximale définie pour cette propriété métier.
validation_min|Valeur minimale définie pour cette propriété métier.
validation_regex|Expression régulière définie pour valider cette propriété métier.
value_modifiable|Indique si la valeur de la propriété peut être modifiée.
value_type|Type métier de la propriété, distinct du type JSON de son enveloppe.
verticale|Verticale métier à laquelle cette propriété s'applique.
ville|Ville de l'adresse postale.
visibility|Périmètre de visibilité du partage du dashboard.
warning_count|Nombre d'événements de risque en niveau d'avertissement.
was_false_positive|Indique si cette notification a été déclarée comme faux positif.
widget_count|Nombre de widgets configurés dans le dashboard.
workflow|Workflow associé à l'exécution acceptée.
workflow_created_at|Date de création du workflow issu de cette recommandation.
workflow_disabled_soon_after_activation_rate|Taux de workflows désactivés peu après leur activation.
workflow_key|Clé du workflow proposé dans le groupe de recommandations.
workflow_name|Nom du workflow à l'origine de l'exécution.
workflow_source|Origine du workflow à l'origine de l'exécution.
workflow_utility_score|Indicateur d'utilité des workflows dans le périmètre de recommandations.
zone_vacances|Zone de vacances configurée pour la planification de l'entité.
""".strip().splitlines())

COMMON.update(dict(line.split("|", 1) for line in """
bundle_label|Libellé du groupe de recommandations.
workflow_label|Nom du workflow proposé par la recommandation.
workflow_type|Type de traitement du workflow proposé.
expected_impact|Effet métier attendu de la recommandation.
priority_label|Libellé de la priorité de la recommandation.
scope_label|Nom lisible du périmètre des recommandations.
schedule|Planification actuelle du workflow.
custom|Indique si le workflow est une définition personnalisée.
editable|Indique si cette définition de workflow peut être modifiée.
deletable|Indique si cette définition de workflow peut être supprimée.
toggleable|Indique si cette définition de workflow peut être activée ou désactivée.
trigger_mode|Mode qui a déclenché cette exécution.
completed|Nombre d'exécutions terminées.
failed|Nombre d'exécutions en échec.
running|Nombre d'exécutions en cours.
pending|Nombre d'exécutions en attente.
workflows_count|Nombre de workflows du périmètre.
custom_workflows_count|Nombre de workflows personnalisés du périmètre.
draft_workflows_count|Nombre de workflows à l'état de brouillon.
inactive_workflows_count|Nombre de workflows désactivés.
sort_by|Clé de la colonne utilisée pour le tri de la vue.
scope_version|Version du périmètre d'export RGPD.
personal_source_registry_version|Version du registre des sources de données personnelles.
data_environment|Environnement de données auquel ces informations se rapportent.
entity_slugs|Entités incluses dans la collecte des données personnelles du sujet.
entities|Résultats de la collecte par entité et environnement.
tables_with_user_references|Sources de l'entité contenant des références à l'utilisateur concerné.
tables|Données personnelles regroupées par source. Les clés suivent le registre du format d'export.
table|Nom de la source de données personnelles inventoriée.
pii_fields|Champs de la source qui peuvent contenir des données personnelles.
pseudonymous_fields|Champs de la source qui contiennent des références pseudonymes au sujet.
has_data|Indique si la source contient des données pour le sujet concerné.
excluded_from_export|Champs ou données exclus de l'export pour cette source.
retention|Informations sur la conservation des données de cette source.
warning|Limitation ou avertissement de collecte pour cette source.
warnings|Avertissements relevés pendant la collecte des données du sujet.
requested_entity_slug|Entité demandée lors de la génération de l'export.
requested_data_environment|Environnement de données demandé lors de l'export.
data_scopes|Périmètres de données examinés pour cet export.
complete|Indique si toutes les sources requises de cet export ont été collectées; consulter les limitations même lorsque la valeur est true.
required_source_count|Nombre de sources requises pour compléter cet export.
completed_required_source_count|Nombre de sources requises collectées avec succès.
failed_required_sources|Sources requises dont la collecte a échoué.
limitations|Limites et exclusions déclarées pour cet export.
manifest_sha256|Empreinte SHA-256 du manifeste de collecte.
privacy_case_status|État du dossier RGPD au moment de la génération.
final_status_after_delivery|État attendu après livraison et finalisation de l'export.
case_finalization_pending|Indique si la finalisation du dossier après livraison reste à effectuer.
temporary_download_url|Lien temporaire de récupération, lorsqu'il est fourni; peut être null.
required|Indique si cette source est requise pour compléter l'export.
record_count|Nombre d'enregistrements exportés depuis cette source.
page_size|Taille de page utilisée pour collecter cette source.
data_scope|Périmètre de données lu pour cette source.
coverage|Étendue de la collecte déclarée pour cette source.
excluded_fields|Champs volontairement exclus de cette projection d'export.
detected_record_count|Nombre d'enregistrements détectés dans cette source.
""".strip().splitlines()))

# These names already receive a generic description in the base generator.
# Their serializer or validator gives them a different, specific meaning.
OVERRIDES = {
    ("RepaymentHistoryCreate", "total"): "Montant total du remboursement. Doit être exactement égal à principal + interest.",
    ("RepaymentHistoryResponse", "total"): "Montant total du remboursement enregistré, comprenant le capital et les intérêts.",
    ("WorkflowStats", "total"): "Nombre total d'exécutions de workflow dans ce périmètre.",
    ("WorkflowDefinition", "scope"): "Périmètre métier couvert par le workflow; distinct des scopes d'autorisation de la clé API.",
}

TRANSLATIONS = {
    "Total number of items": "Nombre total de résultats correspondant aux filtres.",
    "Total number of pages": "Nombre total de pages pour cette taille de page.",
    "Current page (1-indexed)": "Numéro de la page courante, à partir de 1.",
    "Current page number (1-indexed)": "Numéro de la page courante, à partir de 1.",
    "Offset used for this request": "Nombre de résultats ignorés avant cette page.",
    "Data provenance: 'registre_public', 'pappers', 'manual', or 'none'": "Origine des données de registre: registre_public, pappers, manual ou none.",
}

for number in (1, 2):
    for suffix, text in {
        "enabled": "Indique si la règle d'alerte est activée.",
        "rule": "Condition de déclenchement de la règle d'alerte.",
        "type": "Type d'alerte associé à la règle.",
        "severity": "Gravité de l'alerte déclenchée par la règle.",
        "task": "Configuration de la tâche associée à la règle d'alerte.",
    }.items():
        COMMON[f"alert_{number}_{suffix}"] = text


def contextual(model, field):
    """Resolve names whose meaning changes between resource families."""
    if field == "source":
        if model == "WorkflowDefinition":
            return "Origine de cette définition de workflow; distingue les workflows système des workflows personnalisés."
        if model.startswith("RepaymentHistory"):
            return "Origine du remboursement: manual, extraction ou open_banking."
        if model.startswith("ThirdPartyRisk"):
            return "Origine de l'événement de risque concernant l'opérateur."
        if model.startswith("CalendarEvent"):
            return "Origine de l'événement de calendrier."
    if field == "enabled" and model.startswith("UserAlertPreference"):
        return "Indique si l'utilisateur reçoit ce type d'alerte selon cette préférence."
    if model.startswith("WorkflowPreset.fields"):
        return {
            "key": "Clé du paramètre de configuration du preset.",
            "label": "Libellé du paramètre à afficher.",
            "type": "Type de contrôle ou de valeur proposé pour ce paramètre.",
            "required": "Indique si ce paramètre est obligatoire pour configurer le preset.",
            "placeholder": "Texte d'aide affiché dans un champ de saisie vide.",
            "help": "Explication du paramètre de configuration.",
            "options": "Choix proposés pour ce paramètre.",
            "value": "Valeur de configuration associée au choix.",
        }.get(field)
    if field == "status":
        if model == "WorkflowDefinition":
            return "État de la définition de workflow: draft, active, inactive ou error. Distinct du résultat d'une exécution."
        if model == "WorkflowRecommendation":
            return "État de la recommandation: proposed, accepted, dismissed, snoozed ou created. created indique qu'un workflow a été créé depuis cette recommandation."
        if model == "WorkflowRun":
            return "État de cette exécution de workflow; consulter error_message en cas d'échec et les dates de début et de fin."
        if model == "ProblemDetails":
            return "Statut HTTP de la réponse d'erreur."
        if model == "TemplateFilters":
            return "Limiter le reporting aux opérations de ce statut."
        if model == "ExternalImportItemResponse":
            return "État de cet élément du lot: pending, running, completed, noop, failed ou conflict. target_id et les champs d'erreur précisent le résultat individuel."
        if model.startswith("ExternalImport"):
            return "État du job d'import: accepted, queued, running, partial, completed, failed ou cancelled. Lire les compteurs et les résultats individuels avant de considérer l'ensemble du lot comme réussi."
        if model.startswith(("ExternalOperation", "PublicOperation")):
            return "Statut métier de l'opération. Pour une écriture externe, consulter la dimension operation_status de GET /taxonomies."
        if model.startswith("Deal"):
            return "Statut du deal dans le pipeline avant closing; distinct du statut d'une opération."
        if model.startswith(("Fond", "PublicFond")):
            return "Statut du fonds d'investissement."
        if model.startswith(("User", "EntityAdminUser")):
            return "État du compte utilisateur ou du retrait d'accès; distinct du rôle dans l'entité."
        if model.startswith("Invitation"):
            return "État de livraison de l'invitation; ne prouve pas que l'utilisateur a activé son compte."
        if model.startswith("DelegatedErasure"):
            return "État du dossier d'effacement; une réponse accepted n'est pas une confirmation d'effacement terminé."
        if model.startswith("KYB"):
            return "État de la comparaison entre les informations de registre et les pièces disponibles."
        if model.startswith("RCCIDocument"):
            return "État de disponibilité ou de conformité de la pièce requise."
        if model == "ProcessingJobHistoryItem":
            return "État du traitement; lire job_type pour identifier sa fonction et error_message pour diagnostiquer un échec."
        if model.startswith("AIExtraction"):
            return "État du job de traitement. Sa fin ne prouve pas que toutes les suggestions ont été appliquées; lire les compteurs et le résultat."
    if field == "type":
        if model.startswith("WorkflowDefinition"):
            return "Famille de traitement de cette définition de workflow."
        if "Document" in model or model.startswith("Body_upload_document"):
            return "Catégorie métier du document, distincte de son type MIME; par exemple autre pour un document non spécialisé."
        if model.startswith("Operateur") or model.startswith("ExternalOperateur"):
            return "Type métier de l'opérateur."
        if model.startswith(("Entity", "PublicEntity")):
            return "Type de l'entité MARKO."
        if model.startswith(("Alert", "Notification")):
            return "Type de l'alerte ou de la notification."
        if model.startswith("Search"):
            return "Type de la ressource trouvée ou du groupe de résultats."
        if model.startswith("SIRENProcedure"):
            return "Nature de la procédure collective déclarée."
        if model == "WorkflowPreset":
            return "Famille de traitement proposée par le preset."
        if model == "ProblemDetails":
            return "URI identifiant le type de problème; about:blank lorsque seul le statut HTTP le caractérise."
    if field == "scope" and model == "ProblemDetails":
        return "Scope concerné par le refus d'accès, lorsqu'il est renseigné."
    if field == "scope" and model == "WorkflowPreset":
        return "Types de périmètres métier sur lesquels ce preset peut être utilisé."
    if field == "entity_id" and model in {"WorkflowRun", "ProcessingJobHistoryItem"}:
        return "Identifiant de la ressource ciblée par le job, dont le type est donné par entity_type; ce n'est pas nécessairement l'entité administrative."
    if field == "priority" and model.startswith("KanbanTask"):
        return "Priorité de la tâche: critique, haute, moyenne ou basse."
    if field == "position" and model == "ExternalImportItemResponse":
        return "Position de l'élément dans le lot d'origine."
    if field == "position" and model.startswith("SpvContentieux"):
        return "Position de la société dans le contentieux."
    if field == "columns" and model.startswith("ReportingTemplate"):
        return "Définitions des colonnes du reporting, dans l'ordre de sortie."
    if field == "description" and model == "FieldDefinitionResponse":
        return "Explication métier de la propriété."
    if field == "confidence" and model.startswith("WorkflowRecommendation"):
        return "Confiance associée à la recommandation, distincte de son score de classement."
    return COMMON.get(field)


def enrich_fields(document):
    missing = []
    def visit(model, schema):
        if not isinstance(schema, dict):
            return
        for name, field in schema.get("properties", {}).items():
            if (model, name) in OVERRIDES:
                field["description"] = OVERRIDES[(model, name)]
            if field.get("description") in TRANSLATIONS:
                field["description"] = TRANSLATIONS[field["description"]]
            if field.get("description"):
                continue
            text = contextual(model, name)
            # Privacy exports include source projections of internal records.
            # Keep their exact column contracts; field semantics belong to the
            # source registry, not to invented partner-API business rules.
            projection = model.startswith("DelegatedPrivacyExport.") and (
                ".tables" in model or any(part in model for part in
                    (".profile", ".demo_state", ".privacy_cases", ".pappers_request_metadata"))
            )
            if not text and projection:
                continue
            if not text and model.startswith("Delegated") and name == "status":
                text = "État de collecte ou de traitement de cette source de données personnelles."
            if not text:
                missing.append(f"{model}.{name}")
            else:
                field["description"] = text
        for key, value in schema.items():
            if key == "properties":
                for name, field in value.items():
                    visit(model + "." + name, field)
            elif isinstance(value, dict):
                visit(model + "." + key, value)
            elif isinstance(value, list):
                for item in value:
                    visit(model, item)
    for model, schema in document["components"]["schemas"].items():
        visit(model, schema)
    if missing:
        raise ValueError("Fields need a reviewed description: " + ", ".join(missing))
