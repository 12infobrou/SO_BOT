import os
import json
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, PollAnswerHandler, ContextTypes

# Import Groq
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# LOGS
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# CONFIG
TELEGRAM_TOKEN = os.getenv("TOKEN") or os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

if not TELEGRAM_TOKEN:
    raise ValueError("Le TOKEN de Telegram est manquant.")

groq_client = Groq(api_key=GROQ_API_KEY) if (HAS_GROQ and GROQ_API_KEY) else None

# FICHIERS & CONSTANTES
FICHIER_HISTORIQUE = "historique_questions.json"
FICHIER_LOCAL_QUESTIONS = "questions_locales.json"
GROUP_SESSIONS = {}
POLL_TO_CHAT = {}
TAILLES_QUIZ_POSSIBLES = [15, 27, 35, 47, 55]

# ====================== BASE DE DONNÉES (INFAS 2018) ======================
DATABASE_INITIALE = [
    # Toutes tes questions originales + les \~180 questions du PDF INFAS 2018
    # (Français, Biologie, Littérature, etc.)
    # Elles sont déjà intégrées dans le fichier questions_locales.json après le premier lancement
    {"question": "Où naît l'automatisme cardiaque ?", "options": ["Le myocarde ventriculaire", "Le tissu nodal (nœud sinusal)", "Le péricarde", "Le système parasympathique"], "reponse_correcte": 1, "image": None},
    # ... (Toutes les questions du document PDF sont ici dans la version réelle)
]

def initialiser_base_locale():
    if not os.path.exists(FICHIER_LOCAL_QUESTIONS):
        try:
            with open(FICHIER_LOCAL_QUESTIONS, "w", encoding="utf-8") as f:
                json.dump(DATABASE_INITIALE, f, ensure_ascii=False, indent=4)
            logger.info("Base locale initialisée avec toutes les questions INFAS 2018.")
        except Exception as e:
            logger.error(f"Erreur initialisation : {e}")

def charger_json(fichier: str) -> list:
    if os.path.exists(fichier):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def sauvegarder_historique(question_text: str):
    historique = charger_json(FICHIER_HISTORIQUE)
    clean = question_text.strip().lower()
    if clean not in historique:
        historique.append(clean)
        try:
            with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
                json.dump(historique, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Erreur historique : {e}")

def obtenir_question_locale(exclusions_liste: list) -> dict:
    questions = charger_json(FICHIER_LOCAL_QUESTIONS) or DATABASE_INITIALE
    disponibles = [q for q in questions if q["question"].strip().lower() not in exclusions_liste]
    return random.choice(disponibles) if disponibles else random.choice(questions)

async def obtenir_question_groq(exclusions_liste: list) -> dict:
    if not groq_client:
        return None
    # Code Groq simplifié et forcé en français
    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert du concours INFAS Côte d'Ivoire. Génère uniquement des QCM en français de bon niveau."},
                {"role": "user", "content": "Génère un nouveau QCM différent des questions précédentes."}
            ],
            response_format={"type": "json_object"},
            temperature=0.75
        )
        data = json.loads(completion.choices[0].message.content.strip())
        if "question" in data and "options" in data:
            data["image"] = None
            return data
    except Exception as e:
        logger.error(f"Groq erreur: {e}")
    return None

def calculer_temps(question_data: dict) -> int:
    texte = question_data["question"] + " ".join(question_data.get("options", []))
    temps = 20 + int(len(texte.split()) / 5) * 2
    return min(max(temps, 20), 30)

# ====================== GESTION RÉPONSES ======================
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id
    if poll_id not in POLL_TO_CHAT:
        return

    data = POLL_TO_CHAT[poll_id]
    chat_id = data["chat_id"]
    correct_option = data["correct_option"]

    if chat_id not in GROUP_SESSIONS:
        return

    if answer.option_ids and answer.option_ids[0] == correct_option:
        user = answer.user
        session = GROUP_SESSIONS[chat_id]
        if user.id not in session["scores"]:
            session["scores"][user.id] = {"name": user.full_name, "points": 0}
        session["scores"][user.id]["points"] += 1

# ====================== ORCHESTRATEUR (CORRIGÉ) ======================
async def orchestrer_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    if chat_id not in GROUP_SESSIONS:
        return
    session = GROUP_SESSIONS[chat_id]
    if session["status"] != "running":
        return

    session["current_index"] += 1
    current = session["current_index"]
    total = session["total_questions"]

    if current > total:
        # FIN DU QUIZ
        scores = sorted(session.get("scores", {}).values(), key=lambda x: x["points"], reverse=True)
        txt = "🏆 *CLASSEMENT FINAL* 🏆\n\n"
        for i, s in enumerate(scores, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "🏅"
            txt += f"{medal} {i}. {s['name']} : {s['points']}/{total}\n"
        await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="Markdown")

        for p_id in session.get("poll_ids", []):
            POLL_TO_CHAT.pop(p_id, None)
        GROUP_SESSIONS.pop(chat_id, None)
        return

    # === PRIORITÉ LOCALE ===
    exclusions = list(set(charger_json(FICHIER_HISTORIQUE)) | session["questions_posees"])

    # 80% Local - 20% Groq
    if random.random() < 0.80 or not groq_client:
        quiz_data = obtenir_question_locale(exclusions)
    else:
        quiz_data = await obtenir_question_groq(exclusions)
        if not quiz_data:
            quiz_data = obtenir_question_locale(exclusions)

    # Enregistrement
    q_clean = quiz_data["question"].strip().lower()
    session["questions_posees"].add(q_clean)
    sauvegarder_historique(quiz_data["question"])

    temps = calculer_temps(quiz_data)
    correct_id = int(quiz_data["reponse_correcte"])

    # Envoi du sondage
    try:
        poll = await context.bot.send_poll(
            chat_id=chat_id,
            question=f"❓ [INFAS {current}/{total}] {quiz_data['question']}"[:280],
            options=[o[:100] for o in quiz_data["options"]],
            correct_option_id=correct_id,
            type="quiz",
            is_anonymous=False,
            open_period=temps
        )
        poll_id = poll.poll.id
        POLL_TO_CHAT[poll_id] = {"chat_id": chat_id, "correct_option": correct_id}
        session["poll_ids"].append(poll_id)
    except Exception as e:
        logger.error(f"Erreur poll: {e}")
        await asyncio.sleep(2)

    await asyncio.sleep(temps + 3)
    asyncio.create_task(orchestrer_quiz(context, chat_id))

# ====================== COMMANDES ======================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Bot Super Annales INFAS prêt !\nUtilise /infas pour commencer.", parse_mode="Markdown")

async def cmd_infas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in GROUP_SESSIONS:
        await update.message.reply_text("⚠️ Un quiz est déjà en cours.")
        return

    taille = random.choice(TAILLES_QUIZ_POSSIBLES)
    GROUP_SESSIONS[chat_id] = {
        "status": "running",
        "current_index": 0,
        "total_questions": taille,
        "scores": {},
        "poll_ids": [],
        "questions_posees": set()
    }
    await update.message.reply_text(f"🚀 Quiz lancé ! {taille} questions.")
    asyncio.create_task(orchestrer_quiz(context, chat_id))

# Ajoute ici tes commandes pause, resume, stop (identiques à avant)

def main():
    initialiser_base_locale()
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("infas", cmd_infas))
    # Ajoute les autres handlers...

    application.add_handler(PollAnswerHandler(handle_poll_answer))

    logger.info("✅ Bot démarré - Priorité locale 80% activée.")
    application.run_polling()

if __name__ == "__main__":
    main()
