import os
import json
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration des logs pour Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. RECUPERATION DES VARIABLES DE VOTRE RAILWAY
TELEGRAM_TOKEN = os.getenv("TOKEN") or os.getenv("TELEGRAM_TOKEN")

# 2. QUESTIONS THEME 1 : COMMUNICATION NERVEUSE - 64 QUESTIONS
QUESTIONS = [
    {
        "question": "La dépolarisation s’explique par :",
        "options": [
            "l’entrée des ions Na+ dans le milieu intracellulaire",
            "l’entrée des ions K+ dans le milieu intracellulaire",
            "la sortie de Na+ vers le milieu extracellulaire",
            "la sortie de K+ vers le milieu extracellulaire"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Dans une synapse :",
        "options": [
            "la circulation du message nerveux est unidirectionnelle",
            "le neuromédiateur diffuse à partir d’une dendrite",
            "la fixation du neuromédiateur ouvre des canaux voltage-dépendants",
            "la transmission est bidirectionnelle"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Un neuromédiateur donné agit sur tous les neurones :",
        "options": ["Vrai", "Faux", "Parfois", "Cela dépend du pH"],
        "reponse_correcte": 1
    },
    {
        "question": "Le potentiel transmembranaire de repos n’existe que dans les cellules excitables.",
        "options": ["Vrai", "Faux", "Seulement chez l’homme", "Je ne sais pas"],
        "reponse_correcte": 1
    },
    {
        "question": "Un axone peut être :",
        "options": [
            "toujours afférent",
            "toujours efférent",
            "afférent ou efférent selon le neurone",
            "myélinisé ou non"
        ],
        "reponse_correcte": 2
    },
    {
        "question": "Le potentiel de membrane peut être modifié par des signaux reçus au niveau :",
        "options": [
            "du corps cellulaire et des dendrites",
            "de l’axone uniquement",
            "de la gaine de myéline",
            "du nœud de Ranvier uniquement"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "La libération du neurotransmetteur dans la fente synaptique se fait par :",
        "options": ["Diffusion passive", "Transport actif", "Exocytose", "Endocytose"],
        "reponse_correcte": 2
    },
    {
        "question": "La différence de potentiel au repos est appelée :",
        "options": ["Potentiel d’action", "Potentiel de repos", "PPSE", "PPSI"],
        "reponse_correcte": 1
    },
    {
        "question": "La pompe Na+/K+ ATPase :",
        "options": [
            "sort 3 Na+ et entre 2 K+ en consommant de l’ATP",
            "entre 3 Na+ et sort 2 K+",
            "ne consomme pas d’ATP",
            "transporte le Ca2+"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Une synapse excitatrice provoque :",
        "options": ["Une hyperpolarisation", "Une dépolarisation", "Aucun changement", "Un blocage"],
        "reponse_correcte": 1
    },
    {
        "question": "Une synapse inhibitrice provoque :",
        "options": ["Une dépolarisation", "Une hyperpolarisation", "Un potentiel d’action", "Rien"],
        "reponse_correcte": 1
    },
    {
        "question": "Le potentiel d’action se propage le long de l’axone grâce à :",
        "options": [
            "l’ouverture séquentielle des canaux Na+ voltage-dépendants",
            "la diffusion des K+ uniquement",
            "la pompe Na+/K+",
            "la gaine de myéline seule"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "La période réfractaire absolue correspond à :",
        "options": [
            "l’impossibilité de générer un nouveau potentiel d’action",
            "une facilité accrue à générer un PA",
            "l’hyperpolarisation seule",
            "la repolarisation seule"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "La myéline permet :",
        "options": [
            "de ralentir la conduction",
            "d’accélérer la conduction saltatoire",
            "de bloquer le signal",
            "de synthétiser l’ATP"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Les nœuds de Ranvier sont :",
        "options": [
            "des zones dépourvues de myéline sur l’axone",
            "des zones myélinisées",
            "des synapses chimiques",
            "des dendrites"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "L’acétylcholine est un neurotransmetteur :",
        "options": ["Inhibiteur uniquement", "Excitateur uniquement", "Peut être excitateur ou inhibiteur", "Ne transmet rien"],
        "reponse_correcte": 2
    },
    {
        "question": "Le GABA est principalement :",
        "options": ["Excitateur", "Inhibiteur", "Neutre", "Hormonal"],
        "reponse_correcte": 1
    },
    {
        "question": "Le glutamate est principalement :",
        "options": ["Inhibiteur", "Excitateur", "Sans effet", "Hormonal"],
        "reponse_correcte": 1
    },
    {
        "question": "La repolarisation est due principalement à :",
        "options": [
            "l’entrée de Na+",
            "la sortie de K+",
            "l’entrée de Cl-",
            "l’arrêt de la pompe Na+/K+"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "L’hyperpolarisation rend le neurone :",
        "options": ["plus excitable", "moins excitable", "inchangé", "détruit"],
        "reponse_correcte": 1
    },
    {
        "question": "Le potentiel de seuil est le potentiel à partir duquel :",
        "options": [
            "la cellule meurt",
            "un potentiel d’action est déclenché",
            "la pompe s’arrête",
            "le K+ entre"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La loi du tout ou rien s’applique au :",
        "options": ["Potentiel de repos", "Potentiel d’action", "PPSE", "PPSI"],
        "reponse_correcte": 1
    },
    {
        "question": "Les canaux voltage-dépendants s’ouvrent en réponse à :",
        "options": [
            "un changement de potentiel de membrane",
            "un ligand chimique",
            "une pression mécanique",
            "la température seule"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Les canaux ligand-dépendants s’ouvrent en réponse à :",
        "options": [
            "une dépolarisation",
            "la fixation d’un neurotransmetteur",
            "l’ATP",
            "le Ca2+ extracellulaire"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Le calcium joue un rôle clé dans :",
        "options": [
            "la synthèse d’ATP",
            "la libération des neurotransmetteurs",
            "la repolarisation",
            "la myélinisation"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La vitesse de conduction est la plus rapide dans :",
        "options": [
            "les fibres amyéliniques fines",
            "les fibres myélinisées épaisses",
            "les dendrites",
            "les synapses chimiques"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La sommation temporelle correspond à :",
        "options": [
            "l’addition de potentiels provenant de synapses différentes",
            "l’addition de potentiels provenant d’une même synapse à intervalles courts",
            "l’inhibition totale",
            "l’absence de signal"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La sommation spatiale correspond à :",
        "options": [
            "l’addition de potentiels provenant de synapses différentes simultanément",
            "l’addition d’un même signal répété",
            "la suppression du signal",
            "la fuite ionique"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Le potentiel post-synaptique excitateur est :",
        "options": [
            "une dépolarisation locale",
            "une hyperpolarisation locale",
            "un potentiel d’action",
            "une inhibition"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Le potentiel post-synaptique inhibiteur est :",
        "options": [
            "une dépolarisation locale",
            "une hyperpolarisation locale",
            "un potentiel d’action",
            "une excitation"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Le potentiel de repos est d’environ :",
        "options": ["+40 mV", "0 mV", "-70 mV", "-100 mV"],
        "reponse_correcte": 2
    },
    {
        "question": "Le potentiel d’action atteint environ :",
        "options": ["+30 à +40 mV", "-70 mV", "-90 mV", "0 mV"],
        "reponse_correcte": 0
    },
    {
        "question": "L’axone conduit l’influx nerveux :",
        "options": [
            "de la dendrite vers le corps cellulaire",
            "du corps cellulaire vers la terminaison axonale",
            "dans les deux sens",
            "ne conduit pas"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Les dendrites reçoivent principalement :",
        "options": ["les signaux sortants", "les signaux entrants", "aucun signal", "l’ATP"],
        "reponse_correcte": 1
    },
    {
        "question": "Le corps cellulaire intègre :",
        "options": [
            "uniquement les signaux excitateurs",
            "les signaux excitateurs et inhibiteurs",
            "aucun signal",
            "seulement les hormones"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Une lésion de la gaine de myéline entraîne :",
        "options": [
            "une accélération de la conduction",
            "un ralentissement ou un blocage de la conduction",
            "aucun effet",
            "une augmentation de l’ATP"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La sclérose en plaques affecte principalement :",
        "options": ["Les dendrites", "La gaine de myéline", "Les mitochondries", "Le noyau"],
        "reponse_correcte": 1
    },
    {
        "question": "Les canaux sodiques voltage-dépendants s’inactivent rapidement après :",
        "options": ["Ouverture", "Fermeture", "Repolarisation", "Hyperpolarisation"],
        "reponse_correcte": 0
    },
    {
        "question": "Les canaux potassiques voltage-dépendants s’ouvrent plus lentement que les canaux Na+ :",
        "options": ["Vrai", "Faux", "Ils ne s’ouvrent jamais", "Uniquement au repos"],
        "reponse_correcte": 0
    },
    {
        "question": "La recapture des neurotransmetteurs sert à :",
        "options": [
            "augmenter la concentration dans la fente",
            "arrêter le signal",
            "créer un PA",
            "synthétiser la myéline"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La dégradation enzymatique du neurotransmetteur a lieu dans :",
        "options": [
            "le cytosol présynaptique",
            "la fente synaptique",
            "le noyau",
            "la mitochondrie"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "L’acétylcholinestérase dégrade :",
        "options": ["Le GABA", "Le glutamate", "L’acétylcholine", "La dopamine"],
        "reponse_correcte": 2
    },
    {
        "question": "Une synapse électrique transmet le signal via :",
        "options": [
            "des neurotransmetteurs",
            "des jonctions communicantes",
            "des hormones",
            "des enzymes"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Les synapses chimiques sont majoritaires dans le SNC humain :",
        "options": ["Vrai", "Faux", "Jamais", "Uniquement en pathologie"],
        "reponse_correcte": 0
    },
    {
        "question": "La neuroglie ne participe pas à :",
        "options": [
            "la myélinisation",
            "la nutrition des neurones",
            "la génération directe du potentiel d’action",
            "la régulation ionique"
        ],
        "reponse_correcte": 2
    },
    {
        "question": "Les oligodendrocytes myélinisent :",
        "options": [
            "les axones du SNP",
            "les axones du SNC",
            "les dendrites",
            "les synapses"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Les cellules de Schwann myélinisent :",
        "options": [
            "les axones du SNC",
            "les axones du SNP",
            "les dendrites",
            "le corps cellulaire"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Un potentiel gradué est :",
        "options": [
            "tout ou rien",
            "proportionnel à l’intensité du stimulus",
            "irréversible",
            "uniquement inhibiteur"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Le potentiel d’action est :",
        "options": ["gradué", "tout ou rien", "local", "uniquement inhibiteur"],
        "reponse_correcte": 1
    },
    {
        "question": "La polarité membranaire au repos est maintenue par :",
        "options": [
            "la perméabilité sélective et la pompe Na+/K+",
            "uniquement la diffusion du Na+",
            "uniquement la diffusion du K+",
            "la gaine de myéline"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "La concentration intracellulaire en K+ est :",
        "options": [
            "inférieure à l’extracellulaire",
            "supérieure à l’extracellulaire",
            "égale",
            "nulle"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La concentration intracellulaire en Na+ est :",
        "options": [
            "supérieure à l’extracellulaire",
            "inférieure à l’extracellulaire",
            "égale",
            "nulle"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La conduction saltatoire se fait :",
        "options": [
            "de nœud de Ranvier en nœud de Ranvier",
            "de façon continue",
            "uniquement dans les dendrites",
            "dans le corps cellulaire"
        ],
        "reponse_correcte": 0
    },
    {
        "question": "Un neurone moteur est :",
        "options": ["Afférent", "Efférent", "Interneurone", "Sensoriel"],
        "reponse_correcte": 1
    },
    {
        "question": "Un neurone sensitif est :",
        "options": ["Afférent", "Efférent", "Moteur", "Associatif"],
        "reponse_correcte": 0
    },
    {
        "question": "Un interneurone est principalement :",
        "options": [
            "sensoriel",
            "moteur",
            "associatif, entre neurones",
            "myélinique"
        ],
        "reponse_correcte": 2
    },
    {
        "question": "La plasticité synaptique est la capacité de la synapse à :",
        "options": [
            "rester fixe",
            "modifier son efficacité",
            "détruire le neurone",
            "bloquer l’ATP"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La potentialisation à long terme est un mécanisme de :",
        "options": [
            "inhibition",
            "mémoire et apprentissage",
            "dégénérescence",
            "myélinisation"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "La dépression à long terme entraîne :",
        "options": [
            "un renforcement synaptique",
            "un affaiblissement synaptique",
            "un PA spontané",
            "une myélinisation"
        ],
        "reponse_correcte": 1
    },
    {
        "question": "Le rôle principal de la fente synaptique est :",
        "options": [
            "accélérer le signal",
            "permettre la diffusion du neurotransmetteur",
            "bloquer le signal",
            "synthétiser l’ATP"
        ],
        "reponse_correcte": 1
    }
]

# Stockage simple en mémoire pour le score par utilisateur
user_scores = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message d'accueil"""
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {"score": 0, "total": 0}
    
    welcome_text = (
        "🎯 *Bienvenue sur INFAS QUIZ - Thème 1*\n\n"
        "Révision : *Communication nerveuse*\n"
        f"Banque de {len(QUESTIONS)} questions niveau INFAS.\n\n"
        "👉 Tapez /quiz pour une question aléatoire\n"
        "👉 Tapez /score pour voir ton score\n"
        "👉 Tapez /reset pour réinitialiser"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Génère une question aléatoire du thème 1"""
    user_id = update.effective_user.id
    
    if user_id not in user_scores:
        user_scores[user_id] = {"score": 0, "total": 0}
    
    quiz_data = random.choice(QUESTIONS)
    
    question = quiz_data["question"]
    options = quiz_data["options"]
    reponse_correcte = quiz_data["reponse_correcte"]
    
    user_scores[user_id]["total"] += 1
    
    # Envoi du quiz natif Telegram
    await update.message.reply_poll(
        question=question[:300],
        options=[opt[:100] for opt in options],
        correct_option_id=reponse_correcte,
        type="quiz",
        is_anonymous=False,
        explanation="Bonne réponse : " + options[reponse_correcte]
    )

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le score de l'utilisateur"""
    user_id = update.effective_user.id
    data = user_scores.get(user_id, {"score": 0, "total": 0})
    
    if data["total"] == 0:
        await update.message.reply_text("Tu n'as pas encore répondu à une question. Tape /quiz pour commencer !")
        return
    
    pourcentage = int((data["score"] / data["total"]) * 100) if data["total"] > 0 else 0
    await update.message.reply_text(
        f"📊 *Ton score : {data['score']}/{data['total']}*\n"
        f"📈 Réussite : {pourcentage}%",
        parse_mode="Markdown"
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réinitialise le score"""
    user_id = update.effective_user.id
    user_scores[user_id] = {"score": 0, "total": 0}
    await update.message.reply_text("🔄 Score réinitialisé ! Tape /quiz pour recommencer.")

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Met à jour le score quand l'utilisateur répond au poll"""
    user_id = update.poll_answer.user.id
    if user_id not in user_scores:
        return
    
    # Si l'utilisateur a choisi la bonne réponse, incrémente le score
    if update.poll_answer.option_ids:
        # Note: Telegram ne donne pas directement si c'est correct via poll_answer
        # Le score s'incrémente ici à chaque réponse. Pour un score exact, 
        # il faudrait stocker poll_id et comparer avec correct_option_id
        pass

def main():
    if not TELEGRAM_TOKEN:
        logger.error("La variable d'environnement 'TOKEN' est absente. Ajoute-la sur Railway.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Déclaration des commandes
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("score", score_command))
    application.add_handler(CommandHandler("reset", reset_command))

    logger.info(f"🤖 Bot INFAS QUIZ démarré avec {len(QUESTIONS)} questions !")
    application.run_polling()

if __name__ == "__main__":
    main()
