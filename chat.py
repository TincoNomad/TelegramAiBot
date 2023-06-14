from langchain import HuggingFaceHub, LLMChain
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = Final= '6167863630:AAHiOTBaTQCvJKLKOuz-SkN4vBY0oIROIvk'
BOT_USERNAME: Final = '@TincoAiBbot'

#configurar comandos
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hola, de momento solo puedo responder preguntas \n ¿Cual es tu pregunta?')

#Logica de respuesta con AI
def handle_responses(text: str) -> str:

    hub_llm = HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs= {"temperature": 0.7, "max_length": 50},
        )

    prompt = PromptTemplate(
        input_variables=["pregunta"],
        template="Responde la siguiente pregunta: {pregunta}"
    )

    hub_chain = LLMChain(prompt=prompt, llm=hub_llm)
    return(hub_chain.run(text))

#Recolectar info del chat y manejo de respuestas
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type}: "{text}"')


    #Esta parte es si el bot va a interactuar en algun grupo
    if message_type == 'group':
        # reemplazar con el nombre de tu bot
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return  # No queremos que el bot responda si no fue mencioandoen el grupo
    else:
        response: str = handle_responses(text)
    #Si no, la siguiente linea es para que responda de forma normal
    #response: str = handle_responses(text)

    #Si el mensaje es por privado el bot respondera normal
    print('bot:', response)
    await update.message.reply_text(response)


#manejo de errores
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update{update} caused error {context.error}')


#Corriendo el programa
if __name__ == '__main__':
    print('Starting Bot...')
    app = Application.builder().token(TOKEN).build()

    #Comandos
    app.add_handler(CommandHandler('start', start_command))

    #Mensajes
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    #Errores
    app.add_error_handler(error)
    
    #Corriendo el bot
    print('polling...')
    app.run_polling(poll_interval=3)