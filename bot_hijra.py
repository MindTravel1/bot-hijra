from datetime import time
from telegram import Update, ChatMemberUpdated, Poll
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler,
    filters, ChatMemberHandler, JobQueue
)
import random
import os

TOKEN = "8138157778:AAHnQIe1g6md147PbsVjzjECtZMd3iHJzkc"

users_interactifs = set()

REPONSES = {
    "visa": "🎫 Les Français peuvent rester 90 jours sans visa. Pour plus, il faut une carte de séjour.",
    "carte de séjour": "📌 Nécessite : passeport, logement, ressources, casier judiciaire, dossier à déposer à la police des étrangers.",
    "logement": "🏠 À Tunis : 1000–1500 TND/mois. À Djerba : 400–800 TND. Cherche sur Tayara.tn ou MarketPlace Facebook.",
    "mariage": "💍 Un mariage avec un(e) Tunisien(ne) permet d’obtenir un titre de séjour plus facilement.",
    "permis": "🚗 Le permis français est valable 1 an en Tunisie. Échange possible si tu fais les démarches à temps.",
    "travail": "💼 Pour travailler : passe par l’ANETI.tn ou les groupes Facebook. Il faut un employeur qui t’embauche légalement.",
    "santé": "🏥 Il existe des cliniques privées et hôpitaux publics. La CMU ne fonctionne pas ici. Prends une assurance expat.",
    "prix": "🛒 Voici quelques prix moyens : pain 0.2 TND, eau 1L : 0.6 TND, viande 25 TND/kg, loyer Tunis : 1200 TND."
}

RAPPELS = [
    "📖 ﴿ فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ﴾ — Sourate Al-Inshirah, v.6\n(traduction rapprochée : En vérité, avec la difficulté est certes une facilité)",
    "📖 ﴿ وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ﴾ — At-Talaq, v.2\n(traduction rapprochée : Et quiconque craint Allah, Il lui donne une issue favorable)",
    "📖 Le Prophète ﷺ a dit : « L’affaire du croyant est étonnante. Tout ce qu’Allah lui réserve est un bien pour lui. » (Muslim 2999)"
]

QUIZ = [
    {"q": "Quelle est la capitale de la Tunisie ?", "o": ["Tunis", "Sfax", "Monastir"], "a": 0},
    {"q": "Quelle est la monnaie de la Tunisie ?", "o": ["Euro", "Dinar tunisien", "Franc CFA"], "a": 1},
    {"q": "Quel est l’indicatif téléphonique ?", "o": ["+216", "+213", "+212"], "a": 0},
    {"q": "Quelle est la grande mosquée de Kairouan ?", "o": ["Zitouna", "Okba Ibn Nafi", "Al-Azhar"], "a": 1},
    {"q": "Couleur des taxis à Tunis ?", "o": ["Rouge", "Jaune", "Blanc"], "a": 1},
    {"q": "Plat local tunisien ?", "o": ["Couscous", "Tajine", "Mafé"], "a": 0}
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_interactifs.add(user_id)
    text = update.message.text.lower()

    if "ebook" in text:
        await update.message.reply_text("📘 Voici ton guide PDF :")
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open("ebook.pdf", "rb"),
            filename="Guide_Expatriation_Tunisie.pdf"
        )
        return

    for motcle, reponse in REPONSES.items():
        if motcle in text:
            await update.message.reply_text(reponse)
            return

    await update.message.reply_text("❓ Je n'ai pas compris. Tu peux poser une question comme 'visa', 'logement', 'permis', etc.")

async def welcome(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.status == "member":
        prenom = update.chat_member.new_chat_member.user.first_name
        await context.bot.send_message(
            chat_id=update.chat.id,
            text=f"🎉 Bienvenue {prenom} ! Qu’Allah te facilite la hijra. Écris 'ebook' pour recevoir le guide 🇹🇳"
        )

async def send_rappel(context: ContextTypes.DEFAULT_TYPE):
    message = random.choice(RAPPELS)
    await context.bot.send_message(chat_id=context.job.chat_id, text=message)

async def rappel_prive(context: ContextTypes.DEFAULT_TYPE):
    for user_id in users_interactifs:
        try:
            await context.bot.send_message(chat_id=user_id, text=random.choice(RAPPELS))
        except:
            continue

async def send_quiz(context: ContextTypes.DEFAULT_TYPE):
    quiz = random.choice(QUIZ)
    await context.bot.send_poll(
        chat_id=context.job.chat_id,
        question=quiz["q"],
        options=quiz["o"],
        type=Poll.QUIZ,
        correct_option_id=quiz["a"]
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_interactifs.add(update.effective_user.id)
    await update.message.reply_text(
        "Salam alaykoum 🌙\n\nJe suis ton assistant Hijra en Tunisie 🇹🇳\n\n"
        "• Écris 'ebook' pour recevoir le guide PDF\n"
        "• Pose tes questions : visa, logement, permis...\n"
        "• Je t’enverrai chaque jour un rappel 📖 et un quiz 🇹🇳 !"
    )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    job_queue = app.job_queue
    await job_queue.start()

    chat_id_groupe = -1002504033435
    job_queue.run_daily(send_rappel, time(hour=9), chat_id=chat_id_groupe)
    job_queue.run_daily(send_rappel, time(hour=14), chat_id=chat_id_groupe)
    job_queue.run_daily(send_rappel, time(hour=20), chat_id=chat_id_groupe)
    job_queue.run_daily(send_quiz, time(hour=17), chat_id=chat_id_groupe)

    job_queue.run_daily(rappel_prive, time(hour=10))
    job_queue.run_daily(rappel_prive, time(hour=15))
    job_queue.run_daily(rappel_prive, time(hour=21))

    print("✅ Bot lancé avec succès...")
    await app.run_polling()

import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Render a déjà une boucle en cours
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

