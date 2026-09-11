app_name = "alphalib_missions"
app_title = "AlphaLib Missions"
app_publisher = "AlphaLib"
app_description = "Lettre de mission, onboarding client et espace documentaire"
app_email = "contact@alphalib.fr"
app_license = "MIT"

# erpnext en plus de frappe : l app s appuie sur le doctype Customer.
# Sans cette declaration, l installation sur un site sans ERPNext echoue
# a la premiere migration au lieu d echouer proprement a l installation.
required_apps = ["frappe", "erpnext"]

# ---------------------------------------------------------------------------
# Tunnel d onboarding
# ---------------------------------------------------------------------------

# DESACTIVE AU PREMIER DEPLOIEMENT.
#
# Ces trois hooks verrouillent le portail : tout utilisateur portant le role
# Customer est redirige vers /onboarding tant qu il n a pas de lettre signee.
# Les activer maintenant enfermerait immediatement tous les clients qui ont
# deja un acces portail, alors que le tunnel n est pas encore complet.
#
# A decommenter seulement quand permissions.py, documents.py, sirene.py et
# signature/ existent, et apres un test sur un site de recette.
# get_website_user_home_page = "alphalib_missions.onboarding.gate.page_accueil"
# before_request = ["alphalib_missions.onboarding.gate.garde_tunnel"]
# on_session_creation = ["alphalib_missions.onboarding.gate.a_la_connexion"]

# ---------------------------------------------------------------------------
# Permissions portail
# ---------------------------------------------------------------------------

# À décommenter quand permissions.py sera écrit.
# permission_query_conditions = {
#     "AlphaLib Lettre Mission": "alphalib_missions.permissions.lettre_query",
#     "File": "alphalib_missions.permissions.file_query",
# }
#
# has_permission = {
#     "AlphaLib Lettre Mission": "alphalib_missions.permissions.lettre_has_permission",
# }

# ---------------------------------------------------------------------------
# Evenements documents
# ---------------------------------------------------------------------------

# À décommenter quand documents.py, onboarding/lcbft.py et signature/ seront écrits.
# doc_events = {
#     "Customer": {
#         "after_insert": "alphalib_missions.documents.creer_arborescence",
#         "validate": "alphalib_missions.onboarding.lcbft.evaluer",
#     },
#     "AlphaLib Lettre Mission": {
#         "on_submit": "alphalib_missions.signature.client.demander_signature",
#     },
# }

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
# Les filtres sont indispensables : sans eux, bench export-fixtures ramasse
# tous les custom fields du site, ERPNext compris, et le prochain migrate les
# reecrit sur les autres environnements.

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "AlphaLib Missions"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "AlphaLib Missions"]]},
    {"dt": "Workflow", "filters": [["document_type", "=", "AlphaLib Lettre Mission"]]},
    {"dt": "Workflow State", "filters": [["name", "in", [
        "Brouillon", "En attente de signature", "Signee", "Refusee", "Expiree",
    ]]]},
]

# Le Print Format n est pas une fixture : cree en developer mode dans le module
# AlphaLib Missions avec standard = "Yes", il est ecrit sur disque par Frappe.
#
# Les conditions generales ne sont pas une fixture non plus : c est de la donnee
# metier qui evolue, seedee une fois via un patch puis geree depuis l interface.

# ---------------------------------------------------------------------------
# Taches planifiees
# ---------------------------------------------------------------------------

# À décommenter quand signature/client.py sera écrit.
# scheduler_events = {
#     "daily": [
#         "alphalib_missions.signature.client.relancer_en_attente",
#     ],
# }

# ---------------------------------------------------------------------------
# Routes portail
# ---------------------------------------------------------------------------

website_route_rules = [
    {"from_route": "/mes-documents/<path:dossier>", "to_route": "mes-documents"},
]

# ---------------------------------------------------------------------------
# Note de configuration
# ---------------------------------------------------------------------------
# La cle API du prestataire de signature se declare dans site_config.json,
# comme anthropic_api_key dans alphalib_chat :
#
#   Dashboard > Sites > alphalib > Site Config
#   { "yousign_api_key": "...", "yousign_webhook_secret": "..." }
#
# Lecture cote serveur : frappe.conf.get("yousign_api_key")
# Jamais dans un doctype Settings : le contenu d un doctype part dans les
# sauvegardes et s affiche dans l interface.
