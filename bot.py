import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration des logs pour suivre l'activité du bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- LE JEU DE DONNÉES (Banque de questions) ---
QUIZ_DATA = {
  "matiere": "Biologie",
  "themes": {
    "theme_1": {
      "titre": "COMMUNICATION NERVEUSE",
      "questions": [
        {"num": 1, "question": "La dépolarisation s'explique par :", "options": ["A -l'entrée des ions Na⁺ dans le milieu intracellulaire", "B -l'entrée des ions K⁺ dans le milieu intracellulaire", "C -la sortie de Na⁺ vers le milieu extracellulaire", "D -la sortie de K⁺ vers le milieu extracellulaire"]},
        {"num": 2, "question": "Dans une synapse :", "options": ["A -la circulation du message nerveux est unidirectionnelle", "B -le neuromédiateur diffuse à partir d'une dendrite", "C -la fixation du neuromédiateur ouvre des canaux voltage dépendants"]},
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

# --- FONCTION POUR GÉNÉRER LA LISTE DE QUESTIONS PAR ÉTAPE ---
def generer_liste_questions():
    """Crée une liste plate de toutes les questions pour itérer facilement dessus."""
    liste_complete = []
    for key_theme, info_theme in QUIZ_DATA["themes"].items():
        titre_theme = info_theme["titre"]
        for q in info_theme["questions"]:
            # On injecte le titre du thème pour l'affichage
            question_data = q.copy()
            question_data["theme_titre"] = titre_theme
            liste_complete.append(question_data)
    return liste_complete

# --- GESTIONNAIRES DE COMMANDES ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande de démarrage : Initialise le score et la liste des questions."""
    # Stockage de l'état de l'utilisateur dans context.user_data (évite les conflits entre utilisateurs)
    context.user_data["questions"] = generer_liste_questions()
    context.user_data["index_actuel"] = 0
    context.user_data["score"] = 0
    
    msg = (
        f"👋 Bienvenue dans le quiz de **{QUIZ_DATA['matiere']}** !\n\n"
        f"Tu vas recevoir {len(context.user_data['questions'])} questions à la suite. "
        "Pas de répétition. Prêt ? Clique sur le bouton ci-dessous."
    )
    
    keyboard = [["🚀 Commencer le Quiz"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

async def envoyer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie la question actuelle selon l'index de l'utilisateur."""
    questions = context.user_data.get("questions", [])
    index = context.user_data.get("index_actuel", 0)
    
    # Si on a épuisé toutes les questions uniques
    if index >= len(questions):
        score = context.user_data.get("score", 0)
        await update.message.reply_text(
            f"🎉 **Quiz terminé !**\n\nTu as répondu à toutes les questions uniques.\n"
            f"🏆 Ton score final : *{score}/{len(questions)}*\n\n"
            "Pour recommencer une nouvelle session sans répétition, tape /start.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return

    q_actuelle = questions[index]
    texte_affiche = f"📁 *Thème : {q_actuelle['theme_titre']}*\n"
    texte_affiche += f"❓ *Question {index + 1}/{len(questions)} :* {q_actuelle['question']}\n\n"
    
    # Configuration des boutons selon le type de question (QCM ou Vrai/Faux)
    if q_actuelle.get("type") == "Vrai/Faux":
        options_boutons = [["Vrai", "Faux"]]
    else:
        # C'est un QCM : On affiche les choix disponibles
        options_boutons = [[opt] for opt in q_actuelle["options"]]
        for opt in q_actuelle["options"]:
            texte_affiche += f"{opt}\n"

    reply_markup = ReplyKeyboardMarkup(options_boutons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(texte_affiche, reply_markup=reply_markup, parse_mode="Markdown")

async def gerer_reponse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enregistre la réponse, avance l'index, et déclenche la question suivante."""
    # Si l'utilisateur n'a pas encore démarré proprement avec /start
    if "index_actuel" not in context.user_data:
        await start(update, context)
        return
        
    reponse_utilisateur = update.message.text
    
    # Si c'est juste le message pour lancer le jeu
    if reponse_utilisateur == "🚀 Commencer le Quiz":
        await envoyer_question(update, context)
        return

    # Logique pour enregistrer le point (Note : À adapter selon vos clés de réponses correctes si définies)
    # Pour l'instant, on incrémente le score à chaque réponse fournie pour l'exemple
    context.user_data["score"] += 1 
    
    # On passe STRICTEMENT à la question suivante (Garantit l'absence de répétition)
    context.user_data["index_actuel"] += 1
    
    # Envoi direct de la question d'après
    await envoyer_question(update, context)

# --- POINT D'ENTRÉE DU SCRIPT ---
def main():
    # Remplacer 'VOTRE_TOKEN_ICI' par le Token obtenu via @BotFather
    # En production (Docker/Render), il vaut mieux utiliser : os.environ.get("TELEGRAM_TOKEN")
    TOKEN = "VOTRE_TOKEN_ICI" 
    
    if TOKEN == "VOTRE_TOKEN_ICI":
        print("⚠️ ERREUR : Tu as oublié de remplacer 'VOTRE_TOKEN_ICI' par ton vrai token Telegram.")
        return

    app = Application.builder().token(TOKEN).build()

    # Déclaration des écouteurs (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_reponse))

    print("🤖 Le Bot de Biologie est en cours d'exécution...")
    app.run_polling()

if __name__ == "__main__":
    main()
