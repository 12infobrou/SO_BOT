import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration des logs pour suivre l'activité du bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- BANQUE DE DONNÉES ---
QUIZ_DATA = {
  "matiere": "Biologie",
  "themes": {
    "theme_1": {
      "titre": "COMMUNICATION NERVEUSE",
      "questions": [
        {"num": 1, "question": "La dépolarisation s'explique par :", "options": ["A -l'entrée des ions Na⁺ dans le milieu intracellulaire", "B -l'entrée des ions K⁺ dans le milieu intracellulaire", "C -la sortie de Na⁺ vers le milieu extracellulaire", "D -la sortie de K⁺ vers le milieu extracellulaire"]},
        {"num": 2, "question": "Dans une synapse :", "options": ["A -la circulation du message nerveux is unidirectionnelle", "B -le neuromédiateur diffuse à partir d'une dendrite", "C -la fixation du neuromédiateur ouvre des canaux voltage dépendants"]},
        {"num": 3, "question": "Un neuromédiateur donné agit sur tous les neurones :", "type": "Vrai/Faux"},
        {"num": 4, "question": "Le potentiel transmembranaire de repos n'existe que dans les cellules excitables.", "type": "Vrai/Faux"},
        {"num": 5, "question": "Un axone :", "options": ["A-est toujours afférent par rapport au système nerveux central", "B- est toujours efférent par rapport au système nerveux central", "C- est afférent ou efférent selon les neurones", "D-peut-être myélinisé ou non"]},
        {"num": 10, "question": "Le potentiel transmembranaire de repos correspond à une différence de potentiel électrique :", "type": "Vrai/Faux"},
        {"num": 13, "question": "À propos de la fibre nerveuse :", "options": ["A- l'intérieur est chargé positivement", "B- l'intérieur est chargé négativement", "C- l'intérieur est neutre."]},
        {"num": 14, "question": "La valeur du potentiel de membrane de la fibre nerveuse avoisine :", "options": ["A-(+70 mV)", "B-(-30 mV)", "C-(-70 mV)", "D-(+30 mV)"]},
        {"num": 17, "question": "Quand le PA arrive au niveau du bouton synaptique, il provoque :", "options": ["A- une sortie de Ca²⁺ de la cellule", "B- une entrée de Ca²⁺ dans la cellule"]}
      ]
    },
    "theme_2": {
      "titre": "NUTRITION",
      "questions": [
        {"num": 1, "question": "La digestion est le passage des aliments dans le sang", "type": "Vrai/Faux"},
        {"num": 2, "question": "Les nutriments sont les substances obtenues après la digestion des aliments", "type": "Vrai/Faux"},
        {"num": 3, "question": "La digestion des protides donne des acides aminés", "type": "Vrai/Faux"},
        {"num": 4, "question": "L'eau, les sels minéraux et les vitamines sont digérés par l'organisme", "type": "Vrai/Faux"},
        {"num": 5, "question": "La digestion des glucides donne l'acide gras.", "type": "Vrai/Faux"},
        {"num": 6, "question": "Concernant l'absorption :", "options": ["A- est le passage des nutriments dans le sang", "B- se fait essentiellement au niveau du gros intestin", "C- se fait essentiellement au niveau de l'intestin grêle", "D- elle s'effectue par transports passifs ou actifs"]},
        {"num": 13, "question": "L'unité anatomique fonctionnelle du rein est :", "options": ["A : le nerf", "B : l'épithélium", "C : le sarcomère", "D : le néphron"]}
      ]
    },
    "theme_3": {
      "titre": "IMMUNOLOGIE",
      "questions": [
        {"num": 1, "question": "Les lymphocytes naissent dans la moelle osseuse ou le thymus :", "type": "Vrai/Faux"},
        {"num": 2, "question": "L'immunité à médiation humorale :", "options": ["A –est appelé ainsi car elle dépend d'hormones", "B –détruit ses cibles grâce à des molécules solubles, les immunoglobulines", "C –est responsable du rejet des greffes"]},
        {"num": 13, "question": "Le SIDA déséquilibre le système immunitaire de l'Homme en s'attaquant :", "options": ["A- aux lymphocytes T4", "B- aux lymphocytes B"]},
        {"num": 14, "question": "Le VIH contient une enzyme appelée transcriptase inverse. Celle-ci sert à :", "options": ["A- à transformer l'ARN viral en ADN proviral", "B-transcrire l'ADN proviral en ARN viral"]}
      ]
    },
    "theme_4": {
      "titre": "LA REPRODUCTION HUMAINE",
      "questions": [
        {"num": 1, "question": "Les règles sont déclenchées par :", "options": ["A- un arrêt de production des œstrogènes et de la progestérone", "C- une diminution des concentrations sanguines d'œstrogènes et de progestérones"]},
        {"num": 4, "question": "La pilule combinée bloque l'ovulation et le cycle mensuel.", "type": "Vrai/Faux"},
        {"num": 6, "question": "Le préservatif masculin empêche la rencontre des gamètes", "type": "Vrai/Faux"},
        {"num": 9, "question": "L'ovulation :", "options": ["B- est provoquée par le pic de sécrétion de LH et FSH"]},
        {"num": 16, "question": "Chez la femme l'ovocyte termine sa maturation dans l'ovaire", "type": "Vrai/Faux"},
        {"num": 19, "question": "Chez la femme :", "options": ["A- l'ovaire libère des hormones qui contrôlent le cycle de l'utérus"]}
      ]
    }
  }
}

def generer_liste_questions():
    liste_complete = []
    for key_theme, info_theme in QUIZ_DATA["themes"].items():
        titre_theme = info_theme["titre"]
        for q in info_theme["questions"]:
            question_data = q.copy()
            question_data["theme_titre"] = titre_theme
            liste_complete.append(question_data)
    return liste_complete

# --- COMMANDES DU BOT ---

async def infas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /infas : Démarre la préparation au concours."""
    context.user_data["questions"] = generer_liste_questions()
    context.user_data["index_actuel"] = 0
    context.user_data["score"] = 0
    context.user_data["en_pause"] = False  # Suivi de l'état pause
    
    msg = (
        f"📚 *Préparation Concours INFAS - {QUIZ_DATA['matiere'].upper()}* 📚\n\n"
        f"Nous allons commencer un test de {len(context.user_data['questions'])} questions sans aucune répétition.\n\n"
        "🛠 *Commandes utiles pendant le quiz :*\n"
        "⏸ /pause - Mettre le quiz en attente\n"
        "▶️ /reprendre - Continuer là où tu t'es arrêté\n"
        "⏹ /arret - Stopper définitivement le test"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown")
    # On envoie immédiatement la première question
    await envoyer_question(update, context)

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /pause : Suspend les réponses aux questions."""
    if "index_actuel" not in context.user_data:
        await update.message.reply_text("❌ Tu n'as pas de quiz en cours. Tape /infas pour commencer.")
        return
        
    context.user_data["en_pause"] = True
    await update.message.reply_text(
        "⏸ *Quiz mis en pause.*\nVos réponses ne seront plus comptabilisées pour le moment.\n"
        "Pour continuer votre progression, envoyez la commande /reprendre.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

async def reprendre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /reprendre : Relance le quiz à l'index mémorisé."""
    if "index_actuel" not in context.user_data:
        await update.message.reply_text("❌ Aucun quiz n'est en cours. Tape /infas pour commencer.")
        return
        
    if not context.user_data.get("en_pause", False):
        await update.message.reply_text("ℹ️ Le quiz est déjà en cours d'exécution.")
        return
        
    context.user_data["en_pause"] = False
    await update.message.reply_text("▶️ *Reprise du quiz !* Voici ta question :", parse_mode="Markdown")
    await envoyer_question(update, context)

async def arret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /arret : Arrête définitivement la session."""
    if "index_actuel" not in context.user_data:
        await update.message.reply_text("❌ Aucun quiz n'est actif actuellement.")
        return
        
    score = context.user_data.get("score", 0)
    total_repondu = context.user_data.get("index_actuel", 0)
    
    await update.message.reply_text(
        f"⏹ *Quiz arrêté définitivement.*\n"
        f"📊 Résultat partiel : *{score}/{total_repondu}* bonnes réponses sur les questions tentées.\n\n"
        f"Pour relancer un nouvel entraînement sans répétition, réutilise /infas.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    context.user_data.clear()  # Efface l'état de l'utilisateur

# --- AFFICHAGE DE LA QUESTION ---

async def envoyer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = context.user_data.get("questions", [])
    index = context.user_data.get("index_actuel", 0)
    
    if index >= len(questions):
        score = context.user_data.get("score", 0)
        await update.message.reply_text(
            f"🎉 *Félicitations, entraînement terminé !*\n\n"
            f"Tu es venu à bout de toutes les questions uniques.\n"
            f"🏆 Score final : *{score}/{len(questions)}*\n\n"
            "Bonne chance pour ton concours INFAS ! Prêt pour un autre tour ? /infas",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        context.user_data.clear()
        return

    q_actuelle = questions[index]
    texte_affiche = f"📁 *Thème : {q_actuelle['theme_titre']}*\n"
    texte_affiche += f"❓ *Question {index + 1}/{len(questions)} :* {q_actuelle['question']}\n\n"
    
    if q_actuelle.get("type") == "Vrai/Faux":
        options_boutons = [["Vrai", "Faux"]]
    else:
        options_boutons = [[opt] for opt in q_actuelle["options"]]
        for opt in q_actuelle["options"]:
            texte_affiche += f"{opt}\n"

    reply_markup = ReplyKeyboardMarkup(options_boutons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(texte_affiche, reply_markup=reply_markup, parse_mode="Markdown")

# --- TRAITEMENT DES TEXTES ENVOYÉS ---

async def gerer_reponse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Si aucun profil n'est initialisé
    if "index_actuel" not in context.user_data:
        await update.message.reply_text("⚠️ Pour démarrer le quiz d'entraînement, envoie la commande /infas.")
        return

    # Si l'utilisateur clique sur un bouton alors que le bot est en pause
    if context.user_data.get("en_pause", False):
        await update.message.reply_text("⏸ Le quiz est en pause. Envoie /reprendre pour pouvoir répondre à nouveau.")
        return

    # TODO: Intégrer ici le système de vérification de la bonne réponse
    # Pour l'instant, on attribue le point de manière systématique
    context.user_data["score"] += 1 
    
    # Passage à la question suivante (Zéro répétition)
    context.user_data["index_actuel"] += 1
    await envoyer_question(update, context)

# --- CONFIGURATION DU REPRÉSENTANT ---
def main():
    TOKEN = "8636766361:AAFxW6gZkKhcCZAneVel4a4nZ2voQ-MIRck"  # Remplacez par votre Token @BotFather
    
    if TOKEN == "8636766361:AAFxW6gZkKhcCZAneVel4a4nZ2voQ-MIRck":
        print("⚠️ ERREUR : Remplace '8636766361:AAFxW6gZkKhcCZAneVel4a4nZ2voQ-MIRck' par ton jeton API.")
        return

    app = Application.builder().token(TOKEN).build()

    # Déclaration des commandes explicites
    app.add_handler(CommandHandler("infas", infas))
    app.add_handler(CommandHandler("pause", pause))
    app.add_handler(CommandHandler("reprendre", reprendre))
    app.add_handler(CommandHandler("arret", arret))
    
    # Gestionnaire des réponses textuelles (Clics sur boutons)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_reponse))

    print("🤖 Bot INFAS connecté et prêt au déploiement...")
    app.run_polling()

if __name__ == "__main__":
    main()
