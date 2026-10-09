import json
import os
from datetime import datetime

# ---------- Configuration ----------
FICHIER_DB = "signalements.json"

TYPES_ARNAQUE = [
    "Faux agent Mobile Money",
    "Fausse promotion / faux gain",
    "Menace / extorsion",
    "Faux opérateur telephonique",
    "Autre"
]

MOTS_CLES_SUSPECTS = {
    "gagne": 3,
    "félicitations": 3,
    "felicitations": 3,
    "cliquez ici": 4,
    "clique ici": 4,
    "compte bloqué": 4,
    "compte bloque": 4,
    "vérifiez vos informations": 5,
    "verifiez vos informations": 5,
    "t-money": 3,
    "tmoney": 3,
    "flooz": 3,
    "urgent": 2,
    "prix": 1,
    "gratuit": 2,
    "lien": 1,
    "bit.ly": 4,
    "http": 1
}


# ---------- Base de données simple ----------
def charger_db():
    if not os.path.exists(FICHIER_DB):
        return {"signalements": []}
    with open(FICHIER_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_db(db):
    with open(FICHIER_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


# ---------- F1 : Vérifier un numéro ----------
def verifier_numero(numero):
    db = charger_db()
    resultats = [s for s in db["signalements"] if s["numero"] == numero]

    if not resultats:
        print(f"\nNumero {numero} : aucun signalement.")
        print("Statut : Aucun risque connu.\n")
        return

    nb = len(resultats)
    print(f"\nNumero {numero} : {nb} signalement(s)")
    print("Types d'arnaque signales :")
    for r in resultats:
        print(f"  - {r['type_arnaque']} ({r['date']})")

    if nb >= 5:
        print("Statut : RISQUE ELEVE. Ne repondez pas.\n")
    elif nb >= 2:
        print("Statut : Suspect. Restez prudent.\n")
    else:
        print("Statut : A surveiller.\n")


# ---------- F2 : Signaler un numéro ----------
def signaler_numero():
    numero = input("Numero a signaler : ").strip()
    if not numero:
        print("Numero vide, annulation.")
        return

    print("\nType d'arnaque :")
    for i, t in enumerate(TYPES_ARNAQUE, 1):
        print(f"  {i}. {t}")

    try:
        choix = int(input("Votre choix (numero) : "))
        if choix < 1 or choix > len(TYPES_ARNAQUE):
            print("Choix invalide.")
            return
        type_arnaque = TYPES_ARNAQUE[choix - 1]
    except ValueError:
        print("Entree invalide.")
        return

    description = input("Description (optionnel) : ").strip()

    db = charger_db()
    db["signalements"].append({
        "numero": numero,
        "type_arnaque": type_arnaque,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    sauvegarder_db(db)
    print(f"\nSignalement enregistre pour {numero}.\n")


# ---------- F3 : Analyser un message ----------
def analyser_message():
    print("\nCollez le message suspect (une seule ligne) :")
    message = input("> ").strip().lower()

    if not message:
        print("Message vide.\n")
        return

    score = 0
    trouves = []

    for mot, poids in MOTS_CLES_SUSPECTS.items():
        if mot in message:
            score += poids
            trouves.append(mot)

    print("\n--- Analyse ---")
    if trouves:
        print("Mots-cles suspects detectes :")
        for m in trouves:
            print(f"  - {m}")
    else:
        print("Aucun mot-cle suspect detecte.")

    print(f"Score de risque : {score}")

    if score >= 8:
        print("Verdict : TRES SUSPECT. Ne cliquez sur aucun lien.\n")
    elif score >= 4:
        print("Verdict : Suspect. Verifiez avant d'agir.\n")
    else:
        print("Verdict : Risque faible.\n")


# ---------- F4 : Liste des numéros signalés ----------
def liste_signalements():
    db = charger_db()
    compteur = {}
    for s in db["signalements"]:
        compteur[s["numero"]] = compteur.get(s["numero"], 0) + 1

    if not compteur:
        print("\nAucun signalement enregistre.\n")
        return

    print("\n--- Numeros les plus signales ---")
    for num, nb in sorted(compteur.items(), key=lambda x: -x[1]):
        print(f"  {num} : {nb} signalement(s)")
    print()


# ---------- Menu principal ----------
def menu():
    while True:
        print("=" * 45)
        print("     ANTIARNAQUE TG - Prototype CLI")
        print("=" * 45)
        print("1. Verifier un numero")
        print("2. Signaler un numero")
        print("3. Analyser un message suspect")
        print("4. Voir les numeros les plus signales")
        print("5. Quitter")
        print("=" * 45)

        choix = input("Votre choix : ").strip()

        if choix == "1":
            num = input("Numero a verifier : ").strip()
            verifier_numero(num)
        elif choix == "2":
            signaler_numero()
        elif choix == "3":
            analyser_message()
        elif choix == "4":
            liste_signalements()
        elif choix == "5":
            print("A bientot !")
            break
        else:
            print("Choix invalide.\n")


if __name__ == "__main__":
    menu()