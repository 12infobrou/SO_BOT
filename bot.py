import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration des logs pour voir ce qui se passe dans la console Docker
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Récupération du token (défini dans l'environnement ou écrit directement ici)
TOKEN = os.getenv("TELEGRAM_TOKEN", "VOTRE_TOKEN_TELEGRAM_ICI")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour la commande /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Bonjour {user.first_name} ! Votre bot est opérationnel et prêt à l'emploi."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestionnaire pour les messages textuels classiques"""
    text_received = update.message.text
    # Exemple simple d'écho : le bot répète ce qu'il reçoit
    await update.message.reply_text(f"Vous avez dit : {text_received}")

def main() -> None:
    """Fonction principale pour lancer le bot"""
    if TOKEN == "VOTRE_TOKEN_TELEGRAM_ICI" or not TOKEN:
        logger.error("Erreur : Aucun token Telegram n'a été configuré.")
        return

    # Initialisation de l'application
    application = Application.builder().token(TOKEN).build()

    # Association des commandes et des messages aux fonctions de gestion
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Lancement du bot en mode d'écoute continue (polling)
    logger.info("Le bot démarre...")
    application.run_polling()

if __name__ == '__main__':
    main()
