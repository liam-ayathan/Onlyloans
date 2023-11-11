# Telegram Bot Code

from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, InlineKeyboardButton,
    InlineKeyboardMarkup, PhotoSize, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    ConversationHandler, MessageHandler, StringCommandHandler,
    filters, PreCheckoutQueryHandler, CallbackQueryHandler, CallbackContext,
)
import os
from dotenv import load_dotenv
import logging
import io
from PIL import Image

load_dotenv() #important!

# Logger
logger = logging.getLogger(__name__)

# Telegram
TELE_TOKEN_TEST = os.getenv("TELE_TOKEN")
PORT = int(os.environ.get('PORT', 5000))
ROUTE, ADD_WALLET,CHECK_RESPONSE = range(3)

"""
This is where the fun begins
"""

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    # code below deletes users message to the bot
    user_id = update.effective_user.id
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    
    # deleting error message
    try:
        if context.user_data['error_message'] != None:
            error_message = context.user_data['error_message']
            await error_message.delete()
    except Exception as e:
        print("error message is not set")

    # deleting sample message from view sample
    try:
        if context.user_data['sample_message'] != None:
            sample_message = context.user_data['sample_message']
            await sample_message.delete()
    except Exception as e:
        print("sample message not set yet")

    # deleting score message from credit scoring
    try:
        if context.user_data['score_message'] != None:
            score_message = context.user_data['score_message']
            await score_message.delete()
    except Exception as e:
        print("score message not set yet")

    keyboard = [
        [InlineKeyboardButton("View Positive Sample", callback_data="view_positive_sample"),],
        [InlineKeyboardButton("View Negative Sample", callback_data="view_negative_sample"),],
        [InlineKeyboardButton("Calculate Credit Score", callback_data="age_selected"),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = message = ("👋 Hello and welcome to Only Loans! 🎉\n\n"
               "Our goal is to help you better assess your credit score.\n\n"
               "You can check out the Samples or Calculate your personal credit score!\n\n")

    if update.callback_query:
        
        try:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                text=message, 
                parse_mode="markdown", 
                reply_markup=reply_markup
            )
        except Exception as e:
            print('This probably a different message, i.e. send_photo from view_demo or another source')
            try:
                if context.user_data['original_message'] != None:
                    original_message = context.user_data['original_message'] # initialized during the start function
                    await original_message.delete()
            except Exception as e:
                print("original message was already deleted consider code refactor")

            original_message = await context.bot.send_message( # I want to store this message so that I can delete it later on
                chat_id=update.effective_chat.id, 
                text=message, 
                parse_mode="markdown", 
                reply_markup=reply_markup
            )
            context.user_data['original_message'] = original_message
    else: # this will execute upon first call of the start function
        original_message = await context.bot.send_message( # I want to store this message so that I can delete it later on
            chat_id=update.effective_chat.id, 
            text=message, 
            parse_mode="markdown", 
            reply_markup=reply_markup
        )
        context.user_data['original_message'] = original_message

    return ROUTE

async def view_positive_sample(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    desired_width = 200  
    desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("Your current Credit Score is 700! 🎉\n\n"
               "Any score above 560 puts you in the healthy range ✅\n\n"
               "You can look to receive favourable rates on your loan applications 😊\n\n")

    with open(f'./images/yes.png', 'rb') as f:
        image = Image.open(f)
        resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        resized_image.save(bio, format='PNG')
        bio.seek(0)

    sample_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='yes.png'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['sample_message'] = sample_message

    return ROUTE

async def view_negative_sample(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    desired_width = 200  
    desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message =  (f"Your current Credit Score is 483 🙁\n\n"
                  "Any score below 560 puts you in the unhealthy range ❌\n\n"
                  "You can expect to pay higher rates on your loan applications 😰\n\n")

    with open(f'./images/No.png', 'rb') as f:
        image = Image.open(f)
        resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        resized_image.save(bio, format='PNG')
        bio.seek(0)

    sample_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='yes.png'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['sample_message'] = sample_message

    return ROUTE

''' Calculating Credit Score Below'''


async def age_selected(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("27", callback_data="age_27"),],
        [InlineKeyboardButton("23", callback_data="age_23"),],
        [InlineKeyboardButton("21", callback_data="age_21"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("To calculate your credit score we would need to know your current age 👀\n\n"
               "Please select where appropriate from the options below\n\n")

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def occupation_selected(update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    age = query.data

    context.user_data['age_days'] = 0  # Default value for occupation score
    age_days = 0

    if age == "age_27":
        age_days = -9855
        context.user_data['age_days'] = -9855
    elif age == "age_23":
        age_days = -8395
        context.user_data['age_days'] = -8395
    elif age == "age_21":
        age_days = -7665
        context.user_data['age_days'] = -7665

    print(f'Current income is age in days is {age_days}')


    context.user_data['total_score'] = 0  # Default value for total score
    keyboard = [
        [InlineKeyboardButton("Blue Collar ", callback_data="bluecollar"),],
        [InlineKeyboardButton("Manager ", callback_data="manager"),],
        [InlineKeyboardButton("Private Service Staff / Sales", callback_data="private_worker"),],
        [InlineKeyboardButton("High Skill / IT", callback_data="high_skill"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("To calculate your credit score we would need to know your current employment status 👀\n\n"
               "Please select where appropriate from the options below\n\n")

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def income_selected(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    occupation = query.data

    context.user_data['occupation_score'] = 0  # Default value for occupation score

    occupation_score = 0
    if occupation == "bluecollar":
        occupation_score = 52
        context.user_data['occupation_score'] = 52
    elif occupation == "manager":
        occupation_score = 61
        context.user_data['occupation_score'] = 61
    elif occupation == "private_worker":
        occupation_score = 56
        context.user_data['occupation_score'] = 56
    elif occupation == "high_skill":
        occupation_score = 66
        context.user_data['occupation_score'] = 66

    print(f'Current occupation is is {occupation} and score is {occupation_score}')

    message = ("To calculate your credit score we would need to know your income range per year 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton(">200,000 💰💰💰", callback_data="income_200"),],
        [InlineKeyboardButton("100,000-200,000 💰💰", callback_data="income_100"),],
        [InlineKeyboardButton("<100,000 💰", callback_data="income_0"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def highest_education(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    income = query.data
    context.user_data['income_score'] = 0

    income_per_day = 0
    income_score = 0

    if income == "income_200":
        income_score = 250000
    elif income == "income_100":
        income_score = 150000
    elif income == "income_0":
        income_score = 50000
        
    income_per_day = income_score / context.user_data['age_days']

    income_per_day_score = 0

    if income_per_day <-23:
        income_per_day_score = 68
    elif income_per_day >-8:
        income_per_day_score = 45
    else:
        income_per_day_score = 58
        
    context.user_data['income_per_day'] = income_per_day_score

    print(f'Current income is {income} and score is {income_score}')
    print(f'Current income per day is {income_per_day} and score is {income_per_day_score}') 

    message = ("To calculate your credit score we would need to know your Highest Education Level 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    keyboard = [
        [InlineKeyboardButton("Master's Degree", callback_data="master_degree"),],
        [InlineKeyboardButton("Bachelor's Degree", callback_data="bachelor_degree"),],
        [InlineKeyboardButton("A Levels, Diploma or lower", callback_data="alevel_lower"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE


async def organization_selected(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    education = query.data  # Extract the income range from the callback data
    context.user_data['education_score'] = 0

    education_score = 0
    if education == "alevel_lower":
        education_score = 53
        context.user_data['education_score'] = education_score
    elif education == "bachelor_degree":
        education_score = 56
        context.user_data['education_score'] = education_score
    elif education == "master_degree":
        education_score = 68
        context.user_data['education_score'] = education_score

    print(f'Current education level is {education} and score is {education_score}')
    context

    message = ("To calculate your credit score we would need to know your organization category 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton("Public Service, Others", callback_data="public"),],
        [InlineKeyboardButton("Trade, Self-Employed, SME",callback_data="sme"),],
        [InlineKeyboardButton("Schools, Industry", callback_data="schools"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def amount_credit(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    organization = query.data  # Extract the income range from the callback data
    context.user_data['organization_score'] = 0

    organization_score = 0
    if organization == "public":
        organization_score = 64
    elif organization == "sme":
        organization_score = 54
    elif organization == "schools":
        organization_score = 45

    context.user_data['organization_score'] = organization_score

    print(f'Current organization is {organization} and score is {organization_score}')

    message = ("To calculate your credit score we would need to know your amount currently credited 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton("<60000", callback_data="amount<60000"),],
        [InlineKeyboardButton(">60000", callback_data="amount>60000"),],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def credit_utilization(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    amount_credit = query.data  # Extract the income range from the callback data
    context.user_data['amount_credit'] = 0

    amount_credit_score = 0
    if amount_credit == "amount<60000":
        amount_credit_score = 58
    elif amount_credit == "amount>60000":
        amount_credit_score = 57

    context.user_data['amount_credit'] = amount_credit_score

    print(f'Current amount credited is {amount_credit} and score is {amount_credit_score}')

    message = ("To calculate your credit score we would need to know your credit utilization rate 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton("<0.412", callback_data="util<0.412"),],
        [InlineKeyboardButton("0.412 to 0.825",callback_data="util<0.825"),],
        [InlineKeyboardButton(">0.825", callback_data="util>0.825"), ],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def days_credit_selected(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    credit_utilization = query.data  # Extract the income range from the callback data
    context.user_data['credit_utilization'] = 0

    credit_utilization_score = 0

    if credit_utilization == "util<0.412":
        credit_utilization_score = 60
    elif credit_utilization == "util<0.825":
        credit_utilization_score = 57
    elif credit_utilization == "util>0.825":
        credit_utilization_score = 48

    context.user_data['credit_utilization'] = credit_utilization_score

    print(f'Current credit utilization is {credit_utilization} and score is {credit_utilization_score}')

    message = ("To calculate your credit score we need to know when did you last apply for Credit 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton("More than 6 years ago", callback_data=">6yrs"),],
        [InlineKeyboardButton("Between 6 years to 1.5 years ago",callback_data="6-1.5yrs"),],
        [InlineKeyboardButton("Between 1.5 years and 5 months ago", callback_data="1.5yrs"), ],
        [InlineKeyboardButton("5 months or less", callback_data="5mnths"), ],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def days_employed_selected(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    days_credit = query.data  # Extract the income range from the callback data
    context.user_data['days_credit'] = 0

    days_credit_score  = 0

    if days_credit == ">6yrs":
        days_credit_score = 64
    elif days_credit == "6-1.5yrs":
        days_credit_score = 59
    elif days_credit == "1.5yrs":
        days_credit_score = 56
    elif days_credit == "5mnths":
        days_credit_score = 52

    context.user_data['days_credit'] = days_credit_score

    print(f'Current days since last credit application is {days_credit } and score is {days_credit_score }')

    message = ("To calculate your credit score we need to how long you have had your current job for 👀\n\n"
               "Please select where appropriate from the options below\n\n")
    
    keyboard = [
        [InlineKeyboardButton("More than 6.5 years", callback_data=">6.5yrs"),],
        [InlineKeyboardButton("Between 6.5 years and 4 years",callback_data="6.5-4yrs"),],
        [InlineKeyboardButton("Less than 4 years", callback_data="<4yrs"), ],
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    else: 
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

    return ROUTE

async def calculate_credit(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    days_employed = query.data  # Extract the income range from the callback data
    context.user_data['days_employed'] = 0

    days_employed_score = 0
    if days_employed == ">6.5yrs":
        days_employed_score = 69
    elif days_employed == "6.5-4yrs":
        days_employed_score = 61
    elif days_employed == "<4yrs":
        days_employed_score = 53
        
    context.user_data['days_employed'] = days_employed_score
    print(f'Current days employed is {days_employed} and score is {days_employed_score}')
    context

    context.user_data['total_score'] = 63 + context.user_data['education_score'] + context.user_data['income_per_day'] + context.user_data['occupation_score'] + context.user_data['organization_score'] + context.user_data['amount_credit'] + context.user_data['credit_utilization'] + context.user_data['days_credit'] + context.user_data['days_employed']

    print("-----------------")
    print("trouble shooting")
    edu = context.user_data['education_score']
    print(edu)
    print(63)
    occupation = context.user_data['occupation_score']
    print(occupation)
    org = context.user_data['organization_score']
    print(org)
    amt_credit = context.user_data['amount_credit']
    print(amt_credit)
    crdit_util = context.user_data['credit_utilization']
    print(crdit_util)
    days_cr = context.user_data['days_credit']
    print(days_cr)
    income = context.user_data['income_per_day']
    print(f'{income}')
    emply = context.user_data['days_employed']
    print(emply)
    print("-----------------")
    #63 because we did no include income type

    await publish_result(update,context)

    return ROUTE

async def publish_result(update, context: ContextTypes.DEFAULT_TYPE):
    total_score = context.user_data['total_score']
    print(f'Your total score is {total_score}')

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    desired_width = 200  
    desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if total_score >= 560:
        
        with open(f'./images/yes.png', 'rb') as f:
            image = Image.open(f)
            resized_image = image.resize((desired_width, desired_height))

            bio = io.BytesIO()
            resized_image.save(bio, format='PNG')
            bio.seek(0)

        message = (f"Your current Credit Score is {total_score}! 🎉\n\n"
                  "Any score above 560 puts you in the healthy range ✅\n\n"
                  "You can look to receive favourable rates on your loan applications 😊\n\n")

        score_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                      photo=InputFile(bio, filename='yes.png'),
                                                      caption=message,
                                                      reply_markup=reply_markup)

        context.user_data['score_message'] = score_message
    
    else:
        
        with open(f'./images/No.png', 'rb') as f:
            image = Image.open(f)
            resized_image = image.resize((desired_width, desired_height))

            bio = io.BytesIO()
            resized_image.save(bio, format='PNG')
            bio.seek(0)

        message = (f"Your current Credit Score is {total_score} 🙁\n\n"
                  "Any score below 560 puts you in the unhealthy range ❌\n\n"
                  "You can expect to pay higher rates on your loan applications 😰\n\n")

        score_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                      photo=InputFile(bio, filename='No.png'),
                                                      caption=message,
                                                      reply_markup=reply_markup)

        context.user_data['score_message'] = score_message
    return ROUTE

'''Handle Unknowns'''

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry did not understand please use or press the /start command again" 
    )
    context.user_data['error_message'] = error_message

    #deleting error causing message
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN_TEST).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        fallbacks=[MessageHandler(filters.TEXT, unknown)],
        states = {
            ROUTE: {                
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(view_positive_sample, pattern="^view_positive_sample$"),
                CallbackQueryHandler(view_negative_sample, pattern="^view_negative_sample$"),
                CallbackQueryHandler(age_selected, pattern="^age_selected$"),
                CallbackQueryHandler(occupation_selected, pattern="^(age_27|age_23|age_21)$"),
                CallbackQueryHandler(income_selected, pattern="^(bluecollar|manager|private_worker|high_skill)$"),
                CallbackQueryHandler(highest_education, pattern="^(income_200|income_100|income_0)$"),
                CallbackQueryHandler(organization_selected, pattern="^(master_degree|bachelor_degree|alevel_lower)$"),
                CallbackQueryHandler(amount_credit, pattern="^(public|sme|schools)$"),
                CallbackQueryHandler(credit_utilization, pattern="^(amount<60000|amount>60000)$"),
                CallbackQueryHandler(days_credit_selected, pattern="^(util<0.412|util<0.825|util>0.825)$"),
                CallbackQueryHandler(days_employed_selected, pattern="^(>6yrs|6-1.5yrs|1.5yrs|5mnths)$"),
                CallbackQueryHandler(calculate_credit, pattern="^(>6.5yrs|6.5-4yrs|<4yrs)$"),
                CallbackQueryHandler(publish_result, pattern="^publish_result$"),
            },
            })

    application.add_handler(conversation_handler)
    if os.getenv("WEBHOOK_URL"):
        application.run_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=TELE_TOKEN_TEST,
                            webhook_url=os.getenv("WEBHOOK_URL") + TELE_TOKEN_TEST)
        logger.info("Application running via webhook: ", TELE_TOKEN_TEST)
    else:
        application.run_polling()
        logger.info("Application running via polling")
