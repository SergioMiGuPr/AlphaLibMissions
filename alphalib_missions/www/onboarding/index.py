import frappe
from alphalib_missions.onboarding.gate import client_du_user, tunnel_termine, ETAPES

no_cache = 1
no_sitemap = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/onboarding"
        raise frappe.Redirect

    if tunnel_termine():
        frappe.local.flags.redirect_location = "/mes-documents"
        raise frappe.Redirect

    customer = client_du_user()
    context.customer = frappe.get_doc("Customer", customer) if customer else None
    context.suivi = frappe.get_doc("AlphaLib Onboarding", {"customer": customer})
    context.etapes = ETAPES

    # La lettre preparee par le cabinet, si elle existe deja.
    # Sans elle, les etapes relecture et signature restent en attente.
    context.lettre = frappe.db.get_value(
        "AlphaLib Lettre Mission",
        {"customer": customer, "docstatus": ("<", 2)},
        ["name", "statut", "honoraires_mensuel_ht", "forfait_juridique_annuel_ht"],
        as_dict=True,
    )

    context.no_header = True
    context.title = "Bienvenue chez Alpha Leonis"
    return context
