import os
import json
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, PollAnswerHandler, ContextTypes

# Essayer d'importer Groq, sinon fallback propre
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# CONFIGURATION DES LOGS
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# CONFIGURATION ET ENVIRONNEMENT
TELEGRAM_TOKEN = os.getenv("TOKEN") or os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

if not TELEGRAM_TOKEN:
    raise ValueError("Le TOKEN de Telegram est manquant dans les variables d'environnement.")

groq_client = Groq(api_key=GROQ_API_KEY) if (HAS_GROQ and GROQ_API_KEY) else None

# CONSTANTES ET FICHIERS
FICHIER_HISTORIQUE = "historique_questions.json"
FICHIER_LOCAL_QUESTIONS = "questions_locales.json"
GROUP_SESSIONS = {}
POLL_TO_CHAT = {}  # Permet de lier l'ID d'un sondage à son groupe et sa bonne réponse
TAILLES_QUIZ_POSSIBLES = [15, 27, 35, 47, 55]

# BASE DE DONNÉES INITIALE EXTRAITE DES PHOTOS
DATABASE_INITIALE = [
    # --- THÈME : LE COEUR ET LA CIRCULATION ---
    {"question": "Où naît l'automatisme cardiaque ?", "options": ["Le myocarde ventriculaire", "Le tissu nodal (nœud sinusal)", "Le péricarde", "Le système parasympathique"], "reponse_correcte": 1},
    {"question": "Quel est l'effet de l'acétylcholine sur le cœur ?", "options": ["Cardio-accélérateur (tachycardie)", "Cardio-modérateur (bradycardie)", "Augmentation de la force systolique", "Infarctus immédiat"], "reponse_correcte": 1},
    {"question": "La phase de contraction du muscle cardiaque s'appelle :", "options": ["La diastole", "La systole", "La phase réfractaire", "L'arythmie"], "reponse_correcte": 1},
    {"question": "Les vaisseaux qui nourrissent directement le cœur sont :", "options": ["Les artères carotides", "Les artères coronaires", "Les veines caves", "L'artère aorte"], "reponse_correcte": 1},
    {"question": "Quel nerf transmet l'effet cardio-modérateur au cœur ?", "options": ["Le nerf sympathique", "Le nerf vague (X)", "Le nerf sciatique", "Le nerf phrénique"], "reponse_correcte": 1},
    
    # --- THÈME : LE REIN ET L'EXCRÉTION ---
    {"question": "Quelle est l'unité fonctionnelle du rein ?", "options": ["Le neurone", "Le néphron", "Le hile rénal", "La vessie"], "reponse_correcte": 1},
    {"question": "Où se déroule la filtration glomérulaire ?", "options": ["Dans le tube collecteur", "Dans la capsule de Bowman", "Dans l'urètre", "Dans l'anse de Henle"], "reponse_correcte": 1},
    {"question": "L'hormone ADH (Hormone Anti-Diurétique) a pour rôle de :", "options": ["Augmenter l'excrétion d'eau", "Favoriser la réabsorption de l'eau", "Diminuer la pression artérielle", "Sécréter du glucose"], "reponse_correcte": 1},
    {"question": "L'urine primitive ne contient normalement jamais de :", "options": ["Urée", "Protéines de gros poids moléculaire", "Eau", "Sels minéraux"], "reponse_correcte": 1},
    {"question": "Quelle hormone sécrétée par les surrénales augmente la réabsorption du Sodium (Na+) ?", "options": ["L'insuline", "L'aldostérone", "Le cortisol", "L'adrénaline"], "reponse_correcte": 1},

    # --- THÈME : LE SYSTÈME NERVEUX ---
    {"question": "Comment s'appelle la zone de communication entre deux neurones ?", "options": ["L'axone", "La synapse", "La dendrite", "La gaine de myéline"], "reponse_correcte": 1},
    {"question": "Quelle substance accélère la vitesse de conduction de l'influx nerveux ?", "options": ["La myéline", "La mélanine", "L'acétylcholine", "Le liquide céphalo-rachidien"], "reponse_correcte": 0},
    {"question": "Le système nerveux de la vie de relation et des mouvements volontaires est le :", "options": ["Système autonome", "Système cérébro-spinal (somatique)", "Système parasympathique", "Système entérique"], "reponse_correcte": 1},
    {"question": "Quel ion entre massivement dans le neurone lors de la dépolarisation du potentiel d'action ?", "options": ["Le Potassium (K+)", "Le Sodium (Na+)", "Le Chlore (Cl-)", "Le Calcium (Ca2+)"], "reponse_correcte": 1},
    {"question": "Le centre nerveux responsable des réflexes involontaires rapides est :", "options": ["Le cerveau", "La moelle épinière", "Le cervelet", "L'hypophyse"], "reponse_correcte": 1},

    # --- THÈME : REPRODUCTION ET HORMONES ---
    {"question": "Quelle hormone déclenche directement l'ovulation chez la femme ?", "options": ["La FSH", "La LH", "La progestérone", "L'œstrogène"], "reponse_correcte": 1},
    {"question": "Où se déroule précisément la spermatogenèse ?", "options": ["Dans la prostate", "Dans les tubes séminifères", "Dans le canal déférent", "Dans les vésicules séminales"], "reponse_correcte": 1},
    {"question": "Quelle hormone maintient le corps jaune au début de la grossesse ?", "options": ["La progestérone", "L'hCG", "La prolactine", "L'oxytocine"], "reponse_correcte": 1},
    {"question": "Les cellules interstitielles de Leydig sécrètent :", "options": ["Les spermatozoïdes", "La testostérone", "La LH", "L'inhibine"], "reponse_correcte": 1},
    {"question": "Le lieu normal de la fécondation est :", "options": ["L'utérus", "Le tiers externe de la trompe de Fallope", "L'ovaire", "Le vagin"], "reponse_correcte": 1},

    # --- THÈME : IMMUNOLOGIE ---
    {"question": "Quelles cellules sont responsables de la sécrétion des anticorps ?", "options": ["Les Lymphocytes T4", "Les Plasmocytes (Lymphocytes B activés)", "Les Macrophages", "Les Éosinophiles"], "reponse_correcte": 1},
    {"question": "La phagocytose est un mécanisme appartenant à :", "options": ["L'immunité spécifique", "L'immunité innée (non spécifique)", "L'immunité à médiation cellulaire", "La vaccination"], "reponse_correcte": 1},
    {"question": "Quelles molécules marquent l'identité biologique unique de chaque individu ?", "options": ["Les anticorps", "Les molécules du CMH (SLA)", "Les interleukines", "Les antigènes circulants"], "reponse_correcte": 1},
    {"question": "Le VIH détruit spécifiquement quelle population cellulaire ?", "options": ["Les Lymphocytes B", "Les Lymphocytes T4 (CD4)", "Les globules rouges", "Les Plaquettes"], "reponse_correcte": 1},
    {"question": "L'immunité acquise passivement de façon immédiate mais temporaire s'appelle :", "options": ["La vaccination", "La sérothérapie", "La phagocytose", "L'inflammation"], "reponse_correcte": 1},

    # --- THÈME : GÉNÉTIQUE ---
    {"question": "Une cellule humaine somatique possède combien de chromosomes ?", "options": ["23 chromosomes", "46 chromosomes", "48 chromosomes", "92 chromosomes"], "reponse_correcte": 1},
    {"question": "Quelle division cellulaire produit les gamètes haploïdes ?", "options": ["La mitose", "La méiose", "La duplication", "La scissiparité"], "reponse_correcte": 1},
    {"question": "Comment appelle-t-on les différentes versions d'un même gène ?", "options": ["Le phénotypes", "Les allèles", "Les locus", "Les nucléotides"], "reponse_correcte": 1},
    {"question": "Si deux parents sont de groupe sanguin O, leurs enfants seront :", "options": ["Uniquement de groupe O", "De groupe A ou B", "De groupe AB", "N'importe quel groupe"], "reponse_correcte": 0},
    {"question": "Le syndrome de Down (Trisomie 21) est dû à :", "options": ["Une mutation génétique ponctuelle", "Une anomalie du nombre de chromosomes", "Une absence de chromosome X", "Une exposition aux UV"], "reponse_correcte": 1}
]

def initialiser_base_locale():
    if not os.path.exists(FICHIER_LOCAL_QUESTIONS):
        try:
            with open(FICHIER_LOCAL_QUESTIONS, "w", encoding="utf-8") as f:
                json.dump(DATABASE_INITIALE, f, ensure_ascii=False, indent=4)
            logger.info("Fichier questions_locales.json initialisé.")
        except Exception as e:
            logger.error(f"Erreur d'initialisation de la base : {e}")

def charger_json(fichier: str) -> list:
    if os.path.exists(fichier):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur de lecture de {fichier} : {e}")
    return []

def sauvegarder_historique(question_text: str):
    historique = charger_json(FICHIER_HISTORIQUE)
    clean_text = question_text.strip().lower()
    if clean_text not in historique:
        historique.append(clean_text)
        try:
            with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
                json.dump(historique, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Erreur de sauvegarde de l'historique : {e}")

def obtenir_question_locale() -> dict:
    questions = charger_json(FICHIER_LOCAL_QUESTIONS)
    if not questions:
        questions = DATABASE_INITIALE
    historique = charger_json(FICHIER_HISTORIQUE)
    disponibles = [q for q in questions if q["question"].strip().lower() not in historique]
    if not disponibles:
        return random.choice(questions)
    return random.choice(disponibles)

async def obtenir_question_groq() -> dict:
    if not groq_client:
        return None
    historique = charger_json(FICHIER_HISTORIQUE)[-30:]
    exclusions = "\n".join([f"- {q}" for q in historique])

    system_prompt = (
        "Tu es un concepteur expert du concours d'entrée INFAS (CI).\n"
        "Génère un QCM à choix unique de niveau professionnel sur l'un de ces thèmes : "
        "Anatomie, Cardiovasculaire, Système rénal, Neurologie, Reproduction humaine, Immunologie ou Pharmacologie.\n\n"
        "Format de réponse JSON strict exigé :\n"
        "{\n"
        "  \"question\": \"Intitulé de la question\",\n"
        "  \"options\": [\"Option 0\", \"Option 1\", \"Option 2\", \"Option 3\"],\n"
        "  \"reponse_correcte\": 0\n"
        "}\n"
        f"INTERDICTION de générer ces questions existantes :\n{exclusions}"
    )

    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Génère un QCM médical INFAS."}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        return json.loads(completion.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"Échec Groq : {e}")
        return None

def calculer_temps(question_data: dict) -> int:
    texte = question_data["question"] + " ".join(question_data["options"])
    temps = 20 + int(len(texte.split()) / 5) * 2
    return min(max(temps, 20), 45)

# CAPTURE DES RÉPONSES ET GESTION DES POINTS
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id

    if poll_id not in POLL_TO_CHAT:
        return

    chat_id = POLL_TO_CHAT[poll_id]["chat_id"]
    correct_option = POLL_TO_CHAT[poll_id]["correct_option"]

    if chat_id not in GROUP_SESSIONS:
        return

    # Si l'utilisateur a choisi la bonne option
    if answer.option_ids and answer.option_ids[0] == correct_option:
        user = answer.user
        user_id = user.id
        user_name = user.full_name

        session = GROUP_SESSIONS[chat_id]
        if user_id not in session["scores"]:
            session["scores"][user_id] = {"name": user_name, "points": 0}
        
        session["scores"][user_id]["points"] += 1

# ORCHESTRATEUR DE LA SESSION
async def orchestrer_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    if chat_id not in GROUP_SESSIONS:
        return

    session = GROUP_SESSIONS[chat_id]
    
    while chat_id in GROUP_SESSIONS and GROUP_SESSIONS[chat_id]["status"] == "paused":
        await asyncio.sleep(1)

    if chat_id not in GROUP_SESSIONS or session["status"] != "running":
        return

    session["current_index"] += 1
    total = session["total_questions"]

    # FIN DU QUIZ : Génération et affichage du classement final
    if session["current_index"] > total:
        scores = session.get("scores", {})
        sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)

        txt_classement = "🏆 *CLASSEMENT FINAL DU CONCOURS BLANC* 🏆\n\n"
        if not sorted_scores:
            txt_classement += "😢 *Aucun participant n'a marqué de points durant cette session.* Relisez vos leçons !"
        else:
            for i, score_data in enumerate(sorted_scores, start=1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                txt_classement += f"{medal} *{i}. {score_data['name']}* : {score_data['points']} pt(s) / {total}\n"
        
        await context.bot.send_message(chat_id=chat_id, text=txt_classement, parse_mode="Markdown")
        
        # Nettoyage de la mémoire pour cette session
        for p_id in session.get("poll_ids", []):
            POLL_TO_CHAT.pop(p_id, None)
        GROUP_SESSIONS.pop(chat_id, None)
        return

    source = random.choice(["groq", "local"])
    quiz_data = None

    if source == "groq" and groq_client:
        msg = await context.bot.send_message(chat_id=chat_id, text=f"🔄 _Génération de la question {session['current_index']}/{total} par Groq..._")
        quiz_data = await obtenir_question_groq()
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        except Exception:
            pass

    if not quiz_data:
        quiz_data = obtenir_question_locale()

    sauvegarder_historique(quiz_data["question"])
    temps_reflexion = calculer_temps(quiz_data)
    correct_id = int(quiz_data["reponse_correcte"])

    try:
        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=f"❓ [INFAS {session['current_index']}/{total}] {quiz_data['question']}"[:300],
            options=[opt[:100] for opt in quiz_data["options"]],
            correct_option_id=correct_id,
            type="quiz",
            is_anonymous=False,
            open_period=temps_reflexion
        )
        
        # Enregistrement du sondage actif pour le suivi des points
        poll_id = message.poll.id
        POLL_TO_CHAT[poll_id] = {
            "chat_id": chat_id,
            "correct_option": correct_id
        }
        session["poll_ids"].append(poll_id)

    except Exception as e:
        logger.error(f"Erreur d'envoi du sondage : {e}")
        asyncio.create_task(orchestrer_quiz(context, chat_id))
        return

    # Attente de la fin du timer
    for _ in range(temps_reflexion + 3):
        await asyncio.sleep(1)
        if chat_id not in GROUP_SESSIONS:
            return

    asyncio.create_task(orchestrer_quiz(context, chat_id))

# COMMANDES TELEGRAM
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 *Bienvenue sur le Bot Super-Annales INFAS !*\n\n"
        "Prêt pour le grand jour ? Ce bot teste vos connaissances en groupe et affiche un classement à la fin.\n\n"
        "🛠 *Commandes de contrôle :*\n"
        "• `/infas` : Lance une session (Taille aléatoire de 15, 27, 35, 47 ou 55 questions)\n"
        "• `/pause` : Suspend le flux du quiz\n"
        "• `/resume` ou `/reprendre` : Reprend le cours du jeu\n"
        "• `/stop` : Arrête définitivement le quiz"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_infas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in GROUP_SESSIONS:
        await update.message.reply_text("⚠️ Un quiz est déjà en cours ici. Terminez-le ou tapez `/stop`.")
        return

    taille_session = random.choice(TAILLES_QUIZ_POSSIBLES)
    GROUP_SESSIONS[chat_id] = {
        "status": "running",
        "current_index": 0,
        "total_questions": taille_session,
        "scores": {},       # Contiendra les scores : {user_id: {"name": ..., "points": ...}}
        "poll_ids": []      # Liste pour nettoyer POLL_TO_CHAT après le quiz
    }

    await update.message.reply_text(f"🚀 *Début de l'épreuve !* Ce round contient `{taille_session}` questions. Que le meilleur gagne !")
    asyncio.create_task(orchestrer_quiz(context, chat_id))

async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in GROUP_SESSIONS:
        GROUP_SESSIONS[chat_id]["status"] = "paused"
        await update.message.reply_text("⏸ *Quiz mis en pause.* Envoyez `/resume` pour continuer.")
    else:
        await update.message.reply_text("Aucun exercice n'est en cours.")

async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in GROUP_SESSIONS and GROUP_SESSIONS[chat_id]["status"] == "paused":
        GROUP_SESSIONS[chat_id]["status"] = "running"
        await update.message.reply_text("▶️ *Reprise du concours !* Préparation de la question...")
    else:
        await update.message.reply_text("Le quiz n'est pas suspendu.")

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in GROUP_SESSIONS:
        session = GROUP_SESSIONS[chat_id]
        for p_id in session.get("poll_ids", []):
            POLL_TO_CHAT.pop(p_id, None)
        GROUP_SESSIONS.pop(chat_id, None)
        await update.message.reply_text("🛑 *Session coupée définitivement.* Aucun classement ne sera publié.")
    else:
        await update.message.reply_text("Aucun quiz actif à stopper.")

def main():
    initialiser_base_locale()
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("infas", cmd_infas))
    application.add_handler(CommandHandler("pause", cmd_pause))
    application.add_handler(CommandHandler("resume", cmd_resume))
    application.add_handler(CommandHandler("reprendre", cmd_resume))
    application.add_handler(CommandHandler("stop", cmd_stop))
    
    # Handler crucial pour écouter et compter les bonnes réponses en direct
    application.add_handler(PollAnswerHandler(handle_poll_answer))

    logger.info("Bot Démarré avec système de classement actif.")
    application.run_polling()

if __name__ == "__main__":
    main()
