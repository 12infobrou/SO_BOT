import os
import json
import logging
import random
import asyncio
from collections import defaultdict
from telegram import Update, InputFile
from telegram.ext import (
    Application, CommandHandler, ContextTypes, PollHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

# ============ TEMPS PAR THÈME ============
POLL_TIMES = {
    "default": 30,
    "francais_commentaire_tourisme": 90,
    "francais_dissertation_sujet1": 120,
    "francais_dissertation_sujet2": 120,
    "francais_types_texte": 90
}

SESSION_SIZES = [15, 20, 25, 30, 33]

# ============ BASE DE QUESTIONS INFAS 2018 ============
QUESTIONS = {
    # Français
    "francais_dissertation_sujet1": [
        {
            "question": "SUJET 1\n« La satisfaction de l'exercice d'un métier réside dans la récompense personnelle que dans la plénitude offerte avec bénéfices »\n\nLis le sujet avant de répondre aux questions suivantes.",
            "options": ["J'ai lu le sujet"],
            "reponse_correcte": 0,
            "explication": "Passe aux questions maintenant."
        },
        {"question": "Le thème de ce sujet est :", "options": ["La récompense personnelle", "La satisfaction de l'exercice d'un métier", "L'exercice d'un métier", "Le métier"], "reponse_correcte": 1},
        {"question": "Ce sujet répond à un plan :", "options": ["Analytique", "Comparatif", "Dialectique", "Thématique"], "reponse_correcte": 2},
        {"question": "La problématique de ce sujet est l'objectif de l'exercice d'un métier.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Commenter une assertion signifie réfuter une opinion", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Le métier est un outil de socialisation de l'homme", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "L'exercice d'un métier permet à l'individu d'obtenir ses moyens d'existence.", "options": ["Vrai", "Faux"], "reponse_correcte": 0}
    ],
    "francais_dissertation_sujet2": [
        {
            "question": "SUJET 2\n« Le sous-développement (de l'Afrique) résulte de la domination coloniale et néocoloniale, qui interdit tout progrès autonome et continue des forces productrices »\n\nLis le sujet avant de répondre aux questions suivantes.",
            "options": ["J'ai lu le sujet"],
            "reponse_correcte": 0
        },
        {"question": "Le néo-colonialisme est la nouvelle forme de colonialisme après les indépendances.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "« Le progrès autonome » signifie « une avancée automatique »", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Le thème du sujet est le sous-développement de l'Afrique.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Le sujet pose le problème des causes endogènes du sous-développement de l'Afrique.", "options": ["Vrai", "Faux"], "reponse_correcte": 1}
    ],
    "francais_commentaire_tourisme": [
        {
            "question": "TOURISME MONDIAL\nL’élan du tourisme mondial est né dans les années 60. Le tiers monde pauvre a pensé qu’il avait une occasion à saisir : vendre ses paysages, ses climats ensoleillés, ses plages de sable fin, ses cultures exotiques. Il voulait recueillir des devises pour stimuler sa machine économique.\n\nPar ailleurs, on a jamais autant voyagé : gros avions à réactions, vacances programmées, étirées, agences de voyages à tous les coins de rues, jamais le monde, même lointain, n’a été aussi accessible. Au début des années 70, « le slogan le tourisme facteur de paix et d’échanges… moyen de compréhension entre les peuples » était repris en chœur par tous de l’UNESCO à la conférence des Nations Unies pour le commerce et le développement, en passant par la Banque Mondiale.\n\nMalheureusement, la rencontre fut manquée, 80% des touristes dans le monde sont originaires des pays industrialisés. C’est un « échange » à sens unique, et le tourisme, bien malgré lui, est loin d’être un personnage innocent. En effet, le voyage ne peut être isolé d’un certain contexte et de son environnement humain et social. Nous ne sommes plus au temps des explorateurs, missionnaires, pèlerins et autres poètes. Le voyage est devenu un produit, une affaire de marchands. Chaque année, plus de soixante millions d’Occidentaux prennent des vacances dans un pays en voie de développement. Visiter le tiers monde, certes, mais quel tiers monde?\n\nRien dans les dépliants et les catalogues des organisateurs et promoteurs de ce tourisme multinational ne permet de soupçonner l’effroyable misère sévissant dans ces terres paradisiaques, ni la pauvreté absolue des hommes tenus à l’écart des grands circuits touristiques. Tout au long des plages, c’est l’exotisme caricatural et racoleur qui s’étale : couples bronzés allongés sur des plages désertes, blondes voluptueuse vous invitant à l’aventure au bord de la piscine d’un hôtel quatre étoiles, formules clichées pour vendre des terres de rêve, figeant des populations typiques, folkloriques et serviles.\n\nE. Mestiri, Le Monde, 20 Septembre 1985",
            "options": ["J'ai lu le texte"],
            "reponse_correcte": 0,
            "explication": "Lis bien le texte. Les questions arrivent juste après."
        },
        {"question": "Ce texte est un texte :", "options": ["Explicatif", "Argumentatif", "Descriptif", "Narratif"], "reponse_correcte": 1},
        {"question": "Pour l'auteur, le tourisme s'avère être :", "options": ["Une évasion plébiscitée par l'UNESCO", "Un rendez-vous manqué", "Une rencontre exaltante entre les peuples", "Une épreuve pour les pays démunis"], "reponse_correcte": 1},
        {"question": "Le tourisme profite aux pays du tiers monde.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Les pays occidentaux sont plus visités.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Les dépliants et les catalogues sont des leurres.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Les touristes occidentaux sont en harmonie avec la population locale.", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Les pays occidentaux sont :", "options": ["Industrialisés", "Émergents", "Sous-développés", "Relativement développés"], "reponse_correcte": 0},
        {"question": "« Par ailleurs » est un connecteur logique :", "options": ["Addition", "Opposition", "Explication", "Concession"], "reponse_correcte": 0}
    ],
    "francais_types_texte": [
        {
            "question": "TYPES DE TEXTE\n« Les Sossos furent surpris de cette attaque soudaine. Tous croyaient que la bataille était pour le lendemain. L'éclair traverse le moins rapidement, la foudre terrorise moins, la crue surprend moins que Djatanefondit sur Sosso Balla et ses forgerons ».\n\nLis l'extrait avant de répondre.",
            "options": ["J'ai lu l'extrait"],
            "reponse_correcte": 0
        },
        {"question": "Cet extrait est :", "options": ["Un récit", "Un poème", "Une scène de dialogue"], "reponse_correcte": 0, "explication": "C'est un récit : on raconte une action, il y a des verbes d'action, des personnages."}
    ],
    "francais_litterature_genre": [
        {"question": "Le roman est :", "options": ["Un récit en prose", "Un texte versifié", "Un monologue", "Une prose poétique"], "reponse_correcte": 0},
        {"question": "« Une si longue lettre » est une œuvre écrite par Fatou Keita", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "« Le devoir de violence » est un romanesque écrit par Yambo Ouologuem", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "« Britannicus » est une œuvre théâtrale", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "« Antigone » est une œuvre romanesque", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "« Allah n'est pas obligé » est une œuvre d'Ahmadou Kourouma", "options": ["Vrai", "Faux"], "reponse_correcte": 0}
    ],
    "francais_litterature_courants": [
        {"question": "Le classicisme appartient au 18ᵉ siècle", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Aimé Césaire est un écrivain :", "options": ["Classique", "Romantique", "Parnassien", "Négritude"], "reponse_correcte": 3},
        {"question": "Le champ lexical est l'ensemble des mots utilisés pour désigner et qualifier une notion.", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "« Massacre, saccage, fracas, ravage » appartient au champ lexical de la :", "options": ["Vengeance", "Réparation", "Destruction", "Construction"], "reponse_correcte": 2},
        {"question": "La litote est une figure de style qui consiste à atténuer l'expression...", "options": ["Vrai", "Faux"], "reponse_correcte": 0}
    ],

    # Biologie
    "biologie_communication_nerveuse": [
        {"question": "La dépolarisation s'explique par :", "options": ["Entrée des ions Na⁺ dans le milieu intracellulaire", "Entrée des ions K⁺ dans le milieu intracellulaire", "Sortie de Na⁺ vers le milieu extracellulaire", "Sortie de K⁺ vers le milieu extracellulaire"], "reponse_correcte": 0},
        {"question": "Dans une synapse :", "options": ["La circulation du message nerveux est unidirectionnelle"], "reponse_correcte": 0},
        {"question": "À propos de la fibre nerveuse :", "options": ["L'intérieur est chargé positivement", "L'intérieur est chargé négativement", "L'intérieur est neutre"], "reponse_correcte": 1},
        {"question": "La valeur du potentiel de membrane :", "options": ["+70 mV", "-30 mV", "-70 mV", "+30 mV"], "reponse_correcte": 2},
        {"question": "Quand le PA arrive au niveau du bouton synaptique :", "options": ["Sortie de Ca²⁺ de la cellule", "Entrée de Ca²⁺ dans la cellule"], "reponse_correcte": 1}
    ],
    "biologie_nutrition": [
        {"question": "La digestion est le passage des aliments dans le sang", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Les nutriments sont les substances obtenues après la digestion des aliments", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "La digestion des protides donne des acides aminés", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "La digestion des glucides donne l'acide gras.", "options": ["Vrai", "Faux"], "reponse_correcte": 1}
    ],
    "biologie_immunologie": [
        {"question": "Les lymphocytes naissent dans la moelle osseuse ou le thymus :", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "Le SIDA déséquilibre le système immunitaire en s'attaquant :", "options": ["Aux lymphocytes T4", "Aux lymphocytes B"], "reponse_correcte": 0}
    ],
    "biologie_reproduction": [
        {"question": "Les règles sont déclenchées par :", "options": ["Arrêt de production des œstrogènes et de la progestérone"], "reponse_correcte": 0},
        {"question": "Le préservatif masculin empêche la rencontre des gamètes", "options": ["Vrai", "Faux"], "reponse_correcte": 0},
        {"question": "L'ovulation est provoquée par :", "options": ["Pic de sécrétion de LH et FSH"], "reponse_correcte": 0}
    ],

    # Culture Générale
    "culture_seance_1": [
        {"question": "La période de la décolonisation de la Côte d'Ivoire part :", "options": ["Du lendemain de la deuxième guerre mondiale jusqu'au 07 Août 1960"], "reponse_correcte": 0},
        {"question": "La Côte d'Ivoire compte 509 Sous-préfecture et 108 départements", "options": ["Vrai", "Faux"], "reponse_correcte": 1},
        {"question": "Le dernier pays indépendant en Afrique est :", "options": ["La Namibie", "Le Soudan", "Le Sud-Soudan"], "reponse_correcte": 2},
        {"question": "Le directeur général de l'UNESCO est Audrey Azoulay", "options": ["Vrai", "Faux"], "reponse_correcte": 0}
    ],
    "culture_seance_2": [
        {"question": "Les différentes étapes de la lutte émancipatrice sont :", "options": ["La phase de l'espoir", "La phase de la coordination", "La phase de la lutte"], "reponse_correcte": 2},
        {"question": "Les cinq Bébés Tigres sont :", "options": ["La Malaisie, l'Indonésie, la Thaïlande, les Philippines et le Brunei"], "reponse_correcte": 0}
    ],
    "culture_seance_3": [
        {"question": "En Côte d'Ivoire, le nombre de départements est de 108 :", "options": ["Vrai", "Faux"], "reponse_correcte": 1}
    ],
    "culture_seance_4": [
        {"question": "Les pays émergents appelés BRIC sont :", "options": ["Du Brésil, de la Russie, l'Inde et la Chine"], "reponse_correcte": 0},
        {"question": "Le pays le plus vaste au monde est :", "options": ["La Russie"], "reponse_correcte": 0}
    ]
}

# Stockage en mémoire
sessions = {}
user_scores = defaultdict(lambda: defaultdict(int))
used_questions = defaultdict(lambda: defaultdict(list))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    themes = "\n".join([f"- `{t}` : {len(QUESTIONS[t])} questions" for t in QUESTIONS.keys()])
    text = (
        "🎯 *INFAS QUIZ Groupe*\n\n"
        "Lance une session : `/startquiz [theme] [nombre]`\n\n"
        "*Thèmes disponibles :*\n" + themes + "\n\n"
        "*Tailles :* 15, 20, 25, 30, 33\n"
        "*Ex:* `/startquiz biologie_nutrition 20`\n\n"
        "*Commandes :*\n"
        "/classement - Classement du groupe\n"
        "/resetclassement - Reset classement\n"
        "/stopquiz - Arrêter session\n"
        "/listthemes - Voir tous les thèmes"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def listthemes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 *Thèmes disponibles :*\n\n"
    for theme, qs in QUESTIONS.items():
        text += f"- `{theme}` : {len(qs)} questions\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def startquiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in sessions and sessions[chat_id]["active"]:
        await update.message.reply_text("⚠️ Une session est déjà en cours. Fais /stopquiz pour l'arrêter.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage : `/startquiz theme nombre`\nEx: `/startquiz biologie_nutrition 20`", parse_mode="Markdown")
        return

    theme = context.args[0]
    try:
        size = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Le nombre doit être un entier.")
        return

    if theme not in QUESTIONS:
        await update.message.reply_text(f"Theme inconnu. Fais /listthemes pour voir la liste.")
        return

    if size not in SESSION_SIZES:
        await update.message.reply_text(f"Tailles autorisées : {SESSION_SIZES}")
        return

    pool = [i for i in range(len(QUESTIONS[theme])) if i not in used_questions[chat_id][theme]]
    if len(pool) < size:
        used_questions[chat_id][theme] = []
        pool = list(range(len(QUESTIONS[theme])))
        await update.message.reply_text(f"⚠️ Pool épuisé. Reset des questions pour {theme}.")

    selected = random.sample(pool, min(size, len(pool)))
    used_questions[chat_id][theme].extend(selected)

    sessions[chat_id] = {
        "active": True,
        "theme": theme,
        "questions": selected,
        "current": 0,
        "poll_id": None,
        "scores_temp": defaultdict(int)
    }

    poll_time = POLL_TIMES.get(theme, POLL_TIMES["default"])

    await update.message.reply_text(
        f"🚀 *Session lancée!*\n"
        f"Theme : `{theme}`\n"
        f"Questions : *{len(selected)}*\n"
        f"Temps : *{poll_time}s* par question\n"
        f"Démarrage dans 5s...",
        parse_mode="Markdown"
    )

    await asyncio.sleep(5)
    await send_next_question(chat_id, context)

async def send_next_question(chat_id, context):
    session = sessions.get(chat_id)
    if not session or not session["active"]:
        return

    if session["current"] >= len(session["questions"]):
        await end_session(chat_id, context)
        return

    q_index = session["questions"][session["current"]]
    q_data = QUESTIONS[session["theme"]][q_index]
    theme = session["theme"]
    poll_time = POLL_TIMES.get(theme, POLL_TIMES["default"])

    msg = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"Q{session['current']+1}/{len(session['questions'])}: {q_data['question']}"[:300],
        options=[opt[:100] for opt in q_data["options"]],
        correct_option_id=q_data["reponse_correcte"],
        type="quiz",
        is_anonymous=False,
        explanation=q_data.get("explication", "")[:200],
        open_period=poll_time
    )

    session["poll_id"] = msg.poll.id
    session["current"] += 1

    context.job_queue.run_once(
        lambda ctx: asyncio.create_task(send_next_question(chat_id, ctx)),
        poll_time + 3
    )

async def classement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    scores = user_scores[chat_id]

    if not scores:
        await update.message.reply_text("Aucun score pour l'instant. Lance un quiz avec /startquiz")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "🏆 *Classement du groupe*\n\n"
    for i, (user_id, score) in enumerate(sorted_scores, 1):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            name = member.user.first_name
        except:
            name = f"User {user_id}"
        text += f"{i}. {name} - *{score}* pts\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def resetclassement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_scores[chat_id] = defaultdict(int)
    await update.message.reply_text("🗑️ Classement réinitialisé.")

async def stopquiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in sessions:
        sessions[chat_id]["active"] = False
        await update.message.reply_text("⏹️ Session arrêtée.")
    else:
        await update.message.reply_text("Aucune session en cours.")

async def end_session(chat_id, context):
    session = sessions.get(chat_id)
    if not session:
        return

    session["active"] = False
    theme = session["theme"]

    for user_id, score in session["scores_temp"].items():
        user_scores[chat_id][user_id] += score

    await context.bot.send_message(
        chat_id,
        f"✅ *Session terminée!*\n"
        f"Theme : `{theme}`\n"
        f"Questions posées : {len(session['questions'])}\n\n"
        f"Fais `/classement` pour voir les résultats.",
        parse_mode="Markdown"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}")

def main():
    if not TOKEN:
        logger.error("TOKEN manquant dans les variables d'environnement")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("listthemes", listthemes_command))
    application.add_handler(CommandHandler("startquiz", startquiz_command))
    application.add_handler(CommandHandler("classement", classement_command))
    application.add_handler(CommandHandler("resetclassement", resetclassement_command))
    application.add_handler(CommandHandler("stopquiz", stopquiz_command))
    application.add_error_handler(error_handler)

    total_q = sum(len(v) for v in QUESTIONS.values())
    logger.info(f"Bot démarré avec {total_q} questions")
    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
