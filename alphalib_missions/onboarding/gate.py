"""
Verrouillage de l'application tant que la lettre de mission n'est pas signee.

A declarer dans hooks.py :

    get_website_user_home_page = "alphalib_missions.onboarding.gate.page_accueil"
    before_request = ["alphalib_missions.onboarding.gate.garde_tunnel"]
    on_session_creation = ["alphalib_missions.onboarding.gate.a_la_connexion"]

Les clients doivent etre crees en type "Website User" et non "System User" :
le desk /app leur est alors inaccessible par construction, et cette garde n a
plus qu a proteger les pages du portail.
"""

import frappe

# Routes toujours joignables, meme tunnel en cours.
# /contact est la sortie de secours : sans elle, un client qui refuse de signer
# se retrouve enferme dans le tunnel sans moyen de joindre le cabinet.
ROUTES_LIBRES = (
    "/onboarding",
    "/contact",
    "/login",
    "/logout",
    "/update-password",
    "/api",
    "/assets",
    "/files",
    "/private/files",
)

ETAPES = [
    "societe",
    "activite",
    "representant",
    "justificatifs",
    "relecture",
    "signature",
]


def client_du_user(user=None):
    """Customer rattache a l utilisateur connecte, via son Contact."""
    user = user or frappe.session.user
    return frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Customer",
            "parenttype": "Contact",
            "parent": ("in", frappe.db.get_all(
                "Contact Email", {"email_id": user}, pluck="parent"
            ) or [""]),
        },
        "link_name",
    )


def tunnel_termine(user=None):
    """Vrai si une lettre de mission signee existe pour ce client."""
    customer = client_du_user(user)
    if not customer:
        return False
    return bool(
        frappe.db.exists(
            "AlphaLib Lettre Mission",
            {"customer": customer, "statut": "Signee", "docstatus": 1},
        )
    )


def est_client(user=None):
    return "Customer" in frappe.get_roles(user or frappe.session.user)


def page_accueil(user):
    """Homepage dynamique : le tunnel tant qu il n est pas termine."""
    if est_client(user) and not tunnel_termine(user):
        return "onboarding"
    return "mes-documents"


def a_la_connexion(login_manager=None):
    """Premiere connexion : cree l enregistrement de suivi et redirige."""
    user = frappe.session.user
    if user == "Guest" or not est_client(user):
        return

    customer = client_du_user(user)
    if customer and not frappe.db.exists("AlphaLib Onboarding", {"customer": customer}):
        frappe.get_doc({
            "doctype": "AlphaLib Onboarding",
            "customer": customer,
            "user": user,
            "etape_courante": ETAPES[0],
            "statut": "En cours",
        }).insert(ignore_permissions=True)

    if not tunnel_termine(user):
        frappe.local.response["home_page"] = "/onboarding"


def garde_tunnel():
    """Intercepte toute requete portail vers une page protegee."""
    if not getattr(frappe.local, "request", None):
        return

    user = frappe.session.user
    if user in ("Guest", "Administrator") or not est_client(user):
        return

    path = frappe.request.path or "/"
    if path.startswith(ROUTES_LIBRES):
        return

    if not tunnel_termine(user):
        frappe.local.flags.redirect_location = "/onboarding"
        raise frappe.Redirect


# ---------------------------------------------------------------------------
# Enregistrement des etapes, appele depuis la page du tunnel
# ---------------------------------------------------------------------------

CHAMPS_AUTORISES = {
    "societe": (
        "customer_name", "forme_juridique", "siren", "rcs_ville",
        "code_ape", "capital_social",
    ),
    "activite": (
        "activite_principale", "nature_activite", "cloture_jour",
        "cloture_mois", "effectif_personnel", "organisation_comptable",
    ),
    "representant": (
        "rep_civilite", "rep_prenom", "rep_nom", "rep_fonction",
        "rep_email", "rep_mobile",
    ),
}


@frappe.whitelist()
def enregistrer_etape(etape, valeurs):
    """Ecrit les champs d une etape sur le Customer, puis avance le suivi.

    La liste blanche evite qu un client puisse ecrire sur n importe quel champ
    de sa fiche en forgeant la requete (les honoraires, notamment).
    """
    import json

    if etape not in CHAMPS_AUTORISES:
        frappe.throw("Etape inconnue.")

    customer = client_du_user()
    if not customer:
        frappe.throw("Aucune fiche client rattachee a votre compte.")

    valeurs = json.loads(valeurs) if isinstance(valeurs, str) else valeurs
    a_ecrire = {
        k: v for k, v in valeurs.items() if k in CHAMPS_AUTORISES[etape]
    }

    doc = frappe.get_doc("Customer", customer)
    doc.update(a_ecrire)
    doc.save(ignore_permissions=True)

    suivi = frappe.get_doc("AlphaLib Onboarding", {"customer": customer})
    index = ETAPES.index(etape)
    if index + 1 < len(ETAPES):
        suivi.etape_courante = ETAPES[index + 1]
    suivi.save(ignore_permissions=True)

    return {"etape_suivante": suivi.etape_courante}
