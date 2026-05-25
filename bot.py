import os
import random
import time
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types

# Initialisation du Bot avec ton Token Railway / Environnement
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TON_TOKEN_ICI")
bot = AsyncTeleBot(TOKEN)

# ==========================================
# BASE DE DONNÉES LOCALE UNIQUE (SANS DOUBLONS)
# ==========================================
QUESTIONS = {
    "Français & Littérature": [
        {
            "id": "fr_01",
            "question": "Quel est le thème du sujet de dissertation : « La satisfaction de l'exercice d'un métier réside dans la récompense personnelle que dans la plénitude offerte avec bénéfices » ?",
            "options": ["La récompense personnelle", "La satisfaction de l'exercice d'un métier", "L'exercice d'un métier", "Le métier"],
            "correct": "La satisfaction de l'exercice d'un métier"
        },
        {
            "id": "fr_02",
            "question": "À quel type de plan répond le sujet axé sur la satisfaction de l'exercice d'un métier ?",
            "options": ["Analytique", "Comparatif", "Dialectique", "Thématique"],
            "correct": "Dialectique"
        },
        {
            "id": "fr_03",
            "question": "Vrai ou Faux : La problématique de ce sujet est l'objectif de l'exercice d'un métier.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_04",
            "question": "Vrai ou Faux : Commenter une assertion signifie avant tout réfuter une opinion.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_05",
            "question": "Vrai ou Faux : L'exercice d'un métier permet fondamentalement à l'individu d'obtenir ses moyens d'existence.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_06",
            "question": "Vrai ou Faux : Le néo-colonialisme est la nouvelle forme de colonialisme observée après les indépendances.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_07",
            "question": "Vrai ou Faux : L'expression « Le progrès autonome » signifie strictement « une avancée automatique ».",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_08",
            "question": "Vrai ou Faux : Expliquer une pensée revient principalement à faciliter sa compréhension générale.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_09",
            "question": "Vrai ou Faux : Le sujet sur le sous-développement de l'Afrique pose principalement le problème des causes endogènes.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_10",
            "question": "Dans le texte 'Tourisme Mondial' d'E. Mestiri, de quel type de texte s'agit-il ?",
            "options": ["Explicatif", "Argumentatif", "Descriptif", "Narratif"],
            "correct": "Argumentatif"
        },
        {
            "id": "fr_11",
            "question": "Pour l'auteur E. Mestiri, le tourisme s'avère être globalement :",
            "options": ["Une évasion plébiscitée par l'UNESCO", "Un rendez-vous manqué", "Une rencontre exaltante entre les peuples", "Une épreuve pour les pays démunis"],
            "correct": "Un rendez-vous manqué"
        },
        {
            "id": "fr_12",
            "question": "Vrai ou Faux : D'après le texte, le tourisme profite en grande majorité aux pays du Tiers-monde.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_13",
            "question": "Vrai ou Faux : Les dépliants et les catalogues des organisateurs touristiques sont dénoncés comme des leurres.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_14",
            "question": "Quel est le synonyme contextuel du mot 'Devise' employé dans le texte ?",
            "options": ["Formule brève et frappante", "Style burlesque", "Élément attirant", "Monnaie d'échange"],
            "correct": "Monnaie d'échange"
        },
        {
            "id": "fr_15",
            "question": "Le mot 'Slogan' se définit de manière générale comme une :",
            "options": ["Formule brève et frappante", "Caricature burlesque", "Attitude servile", "Formule monétaire"],
            "correct": "Formule brève et frappante"
        },
        {
            "id": "fr_16",
            "question": "Le connecteur logique « Par ailleurs » est utilisé pour marquer :",
            "options": ["L'addition", "L'opposition", "L'explication", "La concession"],
            "correct": "L'addition"
        },
        {
            "id": "fr_17",
            "question": "Le tourisme se définit fondamentalement comme le fait de :",
            "options": ["Savoir vendre son pays aux étrangers", "Présenter des produits exotiques", "Voyager et visiter un lieu pour son plaisir", "Faire la publicité de sa région"],
            "correct": "Voyager et visiter un lieu pour son plaisir"
        },
        {
            "id": "fr_18",
            "question": "Quelle est l'œuvre littéraire romanesque écrite par l'auteur ivoirien Bernard Dadié ?",
            "options": ["Kaïdara", "Tribaliques", "Climbié", "Les fleurs du mal"],
            "correct": "Climbié"
        },
        {
            "id": "fr_19",
            "question": "À quel genre littéraire appartient l'œuvre 'Tribaliques' d'Henri Lopes ?",
            "options": ["Le roman", "Le théâtre", "Le recueil de nouvelles", "La poésie"],
            "correct": "Le recueil de nouvelles"
        },
        {
            "id": "fr_20",
            "question": "Le roman se caractérise principalement comme :",
            "options": ["Un récit en prose assez long", "Un texte obligatoirement versifié", "Un monologue théâtral", "Une pure prose poétique courte"],
            "correct": "Un récit en prose assez long"
        },
        {
            "id": "fr_21",
            "question": "Le trait caractéristique dominant de l'épopée est :",
            "options": ["L'humour", "Le merveilleux et l'héroïsme", "La comédie", "La trahison réaliste"],
            "correct": "Le merveilleux et l'héroïsme"
        },
        {
            "id": "fr_22",
            "question": "Vrai ou Faux : L'œuvre célèbre « Une si longue lettre » a été écrite par Fatou Keita.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_23",
            "question": "Vrai ou Faux : « Le devoir de violence » est un espace romanesque écrit par Yambo Ouologuem.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_24",
            "question": "Vrai ou Faux : « Allah n'est pas obligé » est un chef-d'œuvre de l'écrivain Ahmadou Kourouma.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_25",
            "question": "Quel grand mouvement littéraire a dominé le XIXe siècle en Europe ?",
            "options": ["Le baroque", "La pléiade", "Le romantisme", "Le surréalisme"],
            "correct": "Le romantisme"
        },
        {
            "id": "fr_26",
            "question": "Aimé Césaire est une figure de proue de quel mouvement littéraire ?",
            "options": ["Classique", "Romantique", "Parnassien", "Négritude"],
            "correct": "Négritude"
        },
        {
            "id": "fr_27",
            "question": "Vrai ou Faux : Le classicisme est un courant littéraire qui appartient au XVIIIe siècle.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "fr_28",
            "question": "Vrai ou Faux : Le champ lexical désigne l'ensemble des mots utilisés pour désigner et qualifier une même notion.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_29",
            "question": "« La débâcle, le massacre, l'extermination, l'affrontement » forment le champ lexical de :",
            "options": ["La victoire", "La destruction / guerre", "La réparation", "La construction"],
            "correct": "La destruction / guerre"
        },
        {
            "id": "fr_30",
            "question": "Les mots « acception » et « acceptation » possèdent des sens différents mais des formes proches. Ce sont des :",
            "options": ["Synonymes", "Paronymes", "Antonymes", "Homonymes"],
            "correct": "Paronymes"
        },
        {
            "id": "fr_31",
            "question": "Vrai ou Faux : La phrase « La soi-disant efficacité de cette organisation reste à démontrer » est correcte.",
            "options": ["Vrai", "Faux"],
            "correct": "Vrai"
        },
        {
            "id": "fr_32",
            "question": "Une strophe de poésie composée de quatre vers est appelée :",
            "options": ["Un distique", "Un tercet", "Un quatrain", "Un quintil"],
            "correct": "Un quatrain"
        },
        {
            "id": "fr_33",
            "question": "Un vers poétique classique comprenant 12 syllabes s'appelle :",
            "options": ["Un décasyllabe", "Un octosyllabe", "Un hexasyllabe", "Un alexandrin"],
            "correct": "Un alexandrin"
        },
        {
            "id": "fr_34",
            "question": "Le vers « Tout m'afflige et me nuit et conspire à me nuire » dégage une tonalité :",
            "options": ["Tragique", "Réaliste", "Polémique", "Fantastique"],
            "correct": "Tragique"
        },
        {
            "id": "fr_35",
            "question": "« Je n'arrêtais pas de bafouiller » correspond à quel niveau de langue ?",
            "options": ["Soutenu", "Familier", "Courant", "Relâché"],
            "correct": "Familier"
        },
        {
            "id": "fr_36",
            "question": "Quelle figure de style caractérise le vers : « Ma jeunesse ne fut qu'un ténébreux orage » ?",
            "options": ["Une métaphore", "Un euphémisme", "Une litote", "Une périphrase"],
            "correct": "Une métaphore"
        },
        {
            "id": "fr_37",
            "question": "L'expression stylistique « Le conseiller des grâces » pour désigner un miroir est :",
            "options": ["Une métaphore", "Une personnification", "Une périphrase", "Une métonymie"],
            "correct": "Une périphrase"
        },
        {
            "id": "fr_38",
            "question": "La figure de style consistant à atténuer l'expression en disant moins pour faire entendre plus s'appelle :",
            "options": ["L'hyperbole", "La litote", "L'anaphore", "L'ellipse"],
            "correct": "La litote"
        },
        {
            "id": "fr_39",
            "question": "« Mère décédée; enterrement demain. Sentiments distingués ». Ce style télégraphique utilise :",
            "options": ["Une anaphore", "Une ellipse", "Une gradation", "Une allitération"],
            "correct": "Une ellipse"
        }
    ],
    "Biologie": [
        {
            "id": "bio_01",
            "question": "La phase de dépolarisation lors d'un potentiel d'action s’explique par :",
            "options": ["L’entrée massive des ions Na+ dans le milieu intracellulaire", "L’entrée des ions K+ dans le milieu intracellulaire", "La sortie de Na+ vers le milieu extracellulaire", "La sortie de K+ vers le milieu extracellulaire"],
            "correct": "L’entrée massive des ions Na+ dans le milieu intracellulaire"
        },
        {
            "id": "bio_02",
            "question": "Au niveau de la fente synaptique, la transmission du message nerveux est toujours :",
            "options": ["Unidirectionnelle", "Bidirectionnelle", "Aléatoire", "Ininterrompue"],
            "correct": "Unidirectionnelle"
        },
        {
            "id": "bio_03",
            "question": "Vrai ou Faux : Un neuromédiateur donné possède la propriété d'agir sur l'intégralité des neurones.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "bio_04",
            "question": "Vrai ou Faux : Le potentiel transmembranaire de repos est une exclusivité absolue des cellules excitables.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "bio_05",
            "question": "La libération des vésicules de neurotransmetteurs dans l’espace synaptique s'effectue par :",
            "options": ["Phagocytose", "Endocytose", "Exocytose", "Pinocytose"],
            "correct": "Exocytose"
        },
        {
            "id": "bio_06",
            "question": "Comment appelle-t-on la différence de potentiel stable entre les deux faces de la membrane plasmique d'une fibre nerveuse non excitée ?",
            "options": ["Potentiel d’action", "Potentiel de repos", "PPSE", "PPSI"],
            "correct": "Potentiel de repos"
        },
        {
            "id": "bio_07",
            "question": "La valeur standard du potentiel transmembranaire de repos d'une fibre nerveuse est d'environ :",
            "options": ["+70 mV", "-30 mV", "-70 mV", "+30 mV"],
            "correct": "-70 mV"
        },
        {
            "id": "bio_08",
            "question": "Le transport d’ions opéré en permanence par la pompe Na+/K+ contre le gradient de concentration est un :",
            "options": ["Transport passif", "Transport actif (consommant de l'ATP)"],
            "correct": "Transport actif (consommant de l'ATP)"
        },
        {
            "id": "bio_09",
            "question": "L'arrivée de l'onde de dépolarisation (PA) au niveau du bouton synaptique provoque instantanément :",
            "options": ["Une sortie massive de Ca2+ de la cellule", "Une entrée sélective de Ca2+ dans la cellule"],
            "correct": "Une entrée sélective de Ca2+ dans la cellule"
        },
        {
            "id": "bio_10",
            "question": "Au niveau des synapses motrices excitatrices, le neurotransmetteur majeur libéré est :",
            "options": ["L'adrénaline", "L'acétylcholine", "La dopamine", "Le GABA"],
            "correct": "L'acétylcholine"
        },
        {
            "id": "bio_11",
            "question": "Vrai ou Faux : La digestion se résume strictement au passage direct et complet des aliments intacts dans le flux sanguin.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "bio_12",
            "question": "Les substances directement assimilables issues de la simplification moléculaire des aliments lors de la digestion sont les :",
            "options": ["Aliments composés", "Nutriments", "Enzymes digestives", "Sécrétions gastriques"],
            "correct": "Nutriments"
        },
        {
            "id": "bio_13",
            "question": "L'hydrolyse complète et terminale des protides fournit à l'organisme des :",
            "options": ["Acides gras", "Acides aminés", "Molécules de glucose", "Vitamines hydrosolubles"],
            "correct": "Acides aminés"
        },
        {
            "id": "bio_14",
            "question": "Vrai ou Faux : L’eau, les sels minéraux et les vitamines doivent impérativement subir une digestion enzymatique avant leur passage sanguin.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "bio_15",
            "question": "L’absorption intestinale des nutriments s’effectue de manière prépondérante et spécifique au niveau de :",
            "options": ["L'estomac", "L’intestin grêle", "Du gros intestin", "L'œsophage"],
            "correct": "L’intestin grêle"
        },
        {
            "id": "bio_16",
            "question": "L’unité anatomique et fonctionnelle microscopique du rein est appelée :",
            "options": ["Le nerf rénal", "L’épithélium", "Le sarcomère", "Le néphron"],
            "correct": "Le néphron"
        },
        {
            "id": "bio_17",
            "question": "Quelle hormone, produite par l'hypothalamus et libérée par l'hypophyse, stimule activement la réabsorption de l'eau par les tubes collecteurs du rein ?",
            "options": ["L’aldostérone", "L’hormone antidiurétique (ADH)", "La cortisuline", "La rénine"],
            "correct": "L’hormone antidiurétique (ADH)"
        },
        {
            "id": "bio_18",
            "question": "Vrai ou Faux : L'intégralité des lymphocytes naissent et atteignent leur pleine maturité fonctionnelle exclusivement dans le thymus.",
            "options": ["Vrai", "Faux"],
            "correct": "Faux"
        },
        {
            "id": "bio_19",
            "question": "Les cellules effectrices hautement différenciées du système immunitaire qui sécrètent les anticorps circulants sont :",
            "options": ["Les cellules phagocytaires", "Les lymphocytes T4", "Les plasmocytes", "Les lymphocytes T cytotoxiques"],
            "correct": "Les plasmocytes"
        },
        {
            "id": "bio_20",
            "question": "Quel est l’ordre séquentiel exact et chronologique des 4 phases de la phagocytose ?",
            "options": ["Absorption -> Digestion -> Adhésion -> Rejet", "Digestion -> Absorption -> Adhésion -> Rejet", "Adhésion -> Absorption -> Digestion -> Rejet"],
            "correct": "Adhésion -> Absorption -> Digestion -> Rejet"
        },
        {
            "id": "bio_21",
            "question": "Le Virus de l'Immunodéficience Humaine (VIH) paralyse le système immunitaire en infectant sélectivement :",
            "options": ["Les lymphocytes T4 (LT4)", "Les lymphocytes B", "Les macrophages alvéolaires", "Les hématies"],
            "correct": "Les lymphocytes T4 (LT4)"
        }
    ],
    "Histoire-Géographie & EDHC": [
        {
            "id": "hg_01",
            "question": "La période politique active de la décolonisation de la Côte d’Ivoire s'étend historiquement :",
            "options": ["Du lendemain de la 2e Guerre Mondiale jusqu’au 07 Août 1960", "Du lendemain de la guerre jusqu'à la loi-cadre uniquement", "De 1944 à 1947"],
            "correct": "Du lendemain de la 2e Guerre Mondiale jusqu’au 07 Août 1960"
        },
        {
            "id": "hg_02",
            "question": "Quelles structures forment les entités administratives déconcentrées de l'État en Côte d'Ivoire ?",
            "options": ["Le District, la Région, le Département, la Sous-Préfecture, le Village", "La Mairie et le Conseil de District", "Les ministères centraux uniquement"],
            "correct": "Le District, la Région, le Département, la Sous-Préfecture, le Village"
        },
        {
            "id": "hg_03",
            "question": "En Côte d'Ivoire, les collectivités territoriales décentralisées majeures prévues par la loi sont :",
            "options": ["Les Régions et les Communes", "Les Sous-préfectures", "Les chefferies traditionnelles de villages"],
            "correct": "Les Régions et les Communes"
        },
        {
            "id": "hg_04",
            "question": "L’impôt citoyen est une contribution financière obligatoire versée à :",
            "options": ["L’État", "Au contribuable local", "Aux groupements de sociétés privées"],
            "correct": "L’État"
        },
        {
            "id": "hg_05",
            "question": "Quels sont les trois grands pouvoirs constitutionnels régissant la République de Côte d’Ivoire ?",
            "options": ["Le pouvoir exécutif, le pouvoir législatif et le pouvoir judiciaire", "La primature, le sénat et l'assemblée nationale", "Le ministère de l'intérieur, de la défense et de la justice"],
            "correct": "Le pouvoir exécutif, le pouvoir législatif et le pouvoir judiciaire"
        },
        {
            "id": "hg_06",
            "question": "« La démocratie est le gouvernement du peuple, par le peuple, et pour le peuple ». Cette célèbre définition historique émane de :",
            "options": ["François Mitterrand", "Abraham Lincoln", "Nelson Mandela", "Félix Houphouët-Boigny"],
            "correct": "Abraham Lincoln"
        },
        {
            "id": "hg_07",
            "question": "Quel pays s'est positionné au premier rang mondial des puissances exportatrices en 2016-2017 ?",
            "options": ["Les États-Unis", "La Chine", "L'Allemagne", "Le Royaume-Uni"],
            "correct": "La Chine"
        },
        {
            "id": "hg_08",
            "question": "La liberté de pensée accordée par la constitution à chaque citoyen relève du :",
            "options": ["Droit collectif", "Droit individuel", "Droit d'association étatique"],
            "correct": "Droit individuel"
        },
        {
            "id": "hg_09",
            "question": "Le grand référendum historique pour l'adhésion ou le rejet de la Communauté Franco-Africaine s'est tenu le :",
            "options": ["28 septembre 1948", "28 septembre 1958", "28 septembre 1968"],
            "correct": "28 septembre 1958"
        },
        {
            "id": "hg_10",
            "question": "En Côte d’Ivoire, sur quel fleuve côtier majeur sont implantés les barrages hydroélectriques d'Ayamé I et Ayamé II ?",
            "options": ["Le Cavally", "La Bia", "Le Bandama", "Le Sassandra"],
            "correct": "La Bia"
        },
        {
            "id": "hg_11",
            "question": "Le Droit International Humanitaire (DIH) trouve son application stricte et légale :",
            "options": ["En temps de troubles internes mineurs", "En temps de conflit armé (guerre)", "En temps de paix durable"],
            "correct": "En temps de conflit armé (guerre)"
        },
        {
            "id": "hg_12",
            "question": "La taxe annuelle obligatoire prélevée sur la possession et la circulation des véhicules à moteur s'appelle :",
            "options": ["L’impôt synthétique", "La patente professionnelle", "La vignette automobile"],
            "correct": "La vignette automobile"
        }
    ]
}

# ==========================================
# ÉTATS DE JEU ET CONTRÔLE DES SESSIONS
# ==========================================
GAME_STATE = {
    "is_paused": False,
    "active_task": None,
    "current_subject": None,
    "history": [],        # Évite les répétitions au cours d'une session
    "scores": {},         # user_id: score
    "user_names": {}      # user_id: username/first_name pour le classement final
}

# ==========================================
# GESTION DU TIMER DYNAMIQUE ET HYBRIDE
# ==========================================
def calculate_dynamic_time(text: str) -> int:
    """Calcule un temps d'attente intelligent basé sur la longueur du texte (20 à 45s)."""
    base_time = 20
    added_time = len(text) // 15
    return min(max(base_time + added_time, base_time), 45)

async def simulate_groq_or_local_fetch(subject: str):
    """Moteur hybride : Sélectionne une question locale non répétée ou simule un appel API."""
    available = [q for q in QUESTIONS[subject] if q["id"] not in GAME_STATE["history"]]
    
    if not available:
        GAME_STATE["history"] = [id for id in GAME_STATE["history"] if not id.startswith(subject)]
        available = QUESTIONS[subject]
        
    question_data = random.choice(available)
    GAME_STATE["history"].append(question_data["id"])
    return question_data

# ==========================================
# COMMANDES DU BOT
# ==========================================
@bot.message_handler(commands=['start', 'reprendre', 'resume'])
async def start_quiz(message):
    if GAME_STATE["is_paused"]:
        GAME_STATE["is_paused"] = False
        await bot.reply_to(message, "▶️ **Quiz repris ! En route pour l'INFAS 2026.**")
        return

    GAME_STATE["scores"] = {}
    GAME_STATE["history"] = []
    await bot.reply_to(message, "🧠 **Bienvenue dans le Quiz de préparation INFAS 2026 !**\nChoisissez votre matière à l'aide des boutons ci-dessous :", reply_markup=get_subject_keyboard())

def get_subject_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for category in QUESTIONS.keys():
        markup.add(types.KeyboardButton(category))
    return markup

@bot.message_handler(commands=['pause'])
async def pause_quiz(message):
    GAME_STATE["is_paused"] = True
    await bot.reply_to(message, "⏸ **Le quiz est mis en pause.** Utilisez `/resume` ou `/reprendre` pour continuer.")

@bot.message_handler(commands=['stop'])
async def stop_quiz_command(message):
    GAME_STATE["is_paused"] = False
    if GAME_STATE["active_task"]:
        GAME_STATE["active_task"].cancel()
    await show_final_leaderboard(message.chat.id)

# ==========================================
# LOGIQUE DE JEU ET INTERCEPTION DES VOTRES
# ==========================================
@bot.message_handler(func=lambda msg: msg.text in QUESTIONS.keys())
async def handle_subject_selection(message):
    GAME_STATE["current_subject"] = message.text
    await bot.send_message(message.chat.id, f"🎯 **Sujet sélectionné : {message.text}**. Lancement de la session...")
    GAME_STATE["active_task"] = asyncio.create_task(game_loop(message.chat.id))

async def game_loop(chat_id):
    try:
        # On envoie une série de 10 questions uniques par session
        for _ in range(10):
            while GAME_STATE["is_paused"]:
                await asyncio.sleep(1)

            q_data = await simulate_groq_or_local_fetch(GAME_STATE["current_subject"])
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for opt in q_data["options"]:
                # On passe l'ID de la question et l'option choisie dans le callback_data
                markup.add(types.InlineKeyboardButton(opt, callback_data=f"vote|{q_data['id']}|{opt}"))
                
            question_text = f"📝 **Question :**\n{q_data['question']}"
            msg = await bot.send_message(chat_id, question_text, reply_markup=markup)
            
            # Gestion dynamique du temps
            wait_time = calculate_dynamic_time(q_data["question"])
            await asyncio.sleep(wait_time)
            
            # Fermeture de la question et affichage de la bonne réponse
            await bot.send_message(chat_id, f"🔒 **Temps écoulé !**\nLa réponse exacte était : *{q_data['correct']}*", parse_mode="Markdown")
            await asyncio.sleep(2)

        await show_final_leaderboard(chat_id)

    except asyncio.CancelledError:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("vote"))
async def handle_answer_vote(call):
    # Interception chirurgicale sans bloquer le déroulement global
    _, q_id, chosen_option = call.data.split("|")
    user_id = call.from_user.id
    
    # Trouver la question associée dans notre dictionnaire local
    correct_answer = None
    for cat in QUESTIONS.values():
        for q in cat:
            if q["id"] == q_id:
                correct_answer = q["correct"]
                break

    # Enregistrer le nom de l'utilisateur pour le classement final
    GAME_STATE["user_names"][user_id] = call.from_user.first_name or call.from_user.username or f"Candidat_{user_id}"

    if correct_answer and chosen_option.strip() == correct_answer.strip():
        # L'utilisateur gagne un point s'il a vu juste
        GAME_STATE["scores"][user_id] = GAME_STATE["scores"].get(user_id, 0) + 1
        await bot.answer_callback_query(call.id, "✅ Bonne réponse ! +1 point.", show_alert=False)
    else:
        await bot.answer_callback_query(call.id, "❌ Ce n'est pas la bonne réponse.", show_alert=False)

# ==========================================
# AFFICHAGE DU CLASSEMENT ET DES MÉDAILLES
# ==========================================
async def show_final_leaderboard(chat_id):
    if not GAME_STATE["scores"]:
        await bot.send_message(chat_id, "🏁 **Fin de la session !** Aucun point n'a été enregistré cette fois-ci.")
        return

    # Tri décroissant des scores
    sorted_scores = sorted(GAME_STATE["scores"].items(), key=lambda item: item[1], reverse=True)
    
    leaderboard_text = "🏆 **CLASSEMENT FINAL DU CONCOURS INFAS 2026** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (user_id, score) in enumerate(sorted_scores):
        name = GAME_STATE["user_names"].get(user_id, f"Candidat_{user_id}")
        medal = medals[idx] if idx < 3 else "🔹"
        leaderboard_text += f"{medal} **{idx+1}e : {name}** — {score} point(s)\n"

    leaderboard_text += "\n Félicitations à tous les participants ! Restez concentrés pour décrocher votre admission."
    await bot.send_message(chat_id, leaderboard_text)

# Lancement du bot en mode asynchrone
if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.polling(non_stop=True))
