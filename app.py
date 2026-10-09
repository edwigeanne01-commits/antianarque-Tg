from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "antiarnaque.db"

TYPES_ARNAQUE = [
    "Faux agent Mobile Money",
    "Fausse promotion / faux gain",
    "Menace / extorsion",
    "Faux operateur telephonique",
    "Autre"
]

MOTS_CLES_SUSPECTS = {
    "gagne": 3, "felicitations": 3, "cliquez ici": 4, "clique ici": 4,
    "compte bloque": 4, "verifiez vos informations": 5, "t-money": 3,
    "tmoney": 3, "flooz": 3, "urgent": 2, "gratuit": 2, "bit.ly": 4
}


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS signalements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            type_arnaque TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verifier", methods=["GET", "POST"])
def verifier():
    resultats = None
    numero = ""
    if request.method == "POST":
        numero = request.form.get("numero", "").strip()
        if numero:
            conn = get_db()
            resultats = conn.execute(
                "SELECT * FROM signalements WHERE numero = ? ORDER BY date DESC",
                (numero,)
            ).fetchall()
            conn.close()
    return render_template("verifier.html", resultats=resultats, numero=numero)


@app.route("/signaler", methods=["GET", "POST"])
def signaler():
    message = None
    if request.method == "POST":
        numero = request.form.get("numero", "").strip()
        type_arnaque = request.form.get("type_arnaque", "").strip()
        description = request.form.get("description", "").strip()

        if numero and type_arnaque:
            conn = get_db()
            conn.execute(
                "INSERT INTO signalements (numero, type_arnaque, description, date) VALUES (?, ?, ?, ?)",
                (numero, type_arnaque, description, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
            conn.close()
            message = f"Signalement enregistre pour {numero}."
    return render_template("signaler.html", types=TYPES_ARNAQUE, message=message)


@app.route("/analyser", methods=["GET", "POST"])
def analyser():
    resultat = None
    if request.method == "POST":
        texte = request.form.get("message", "").strip().lower()
        score = 0
        trouves = []
        for mot, poids in MOTS_CLES_SUSPECTS.items():
            if mot in texte:
                score += poids
                trouves.append(mot)

        if score >= 8:
            verdict = "TRES SUSPECT"
            couleur = "rouge"
        elif score >= 4:
            verdict = "Suspect"
            couleur = "orange"
        else:
            verdict = "Risque faible"
            couleur = "vert"

        resultat = {"score": score, "trouves": trouves, "verdict": verdict, "couleur": couleur}

    return render_template("analyser.html", resultat=resultat)


@app.route("/liste")
def liste():
    conn = get_db()
    rows = conn.execute(
        "SELECT numero, COUNT(*) as nb FROM signalements GROUP BY numero ORDER BY nb DESC"
    ).fetchall()
    conn.close()
    return render_template("liste.html", numeros=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)