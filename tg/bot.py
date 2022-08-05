from doctest import REPORT_UDIFF
from email import message
from sqlite3 import Cursor
from sre_constants import SUCCESS
from turtle import update
from django.http import QueryDict
from numpy import identity
from requests import options
import telegram
import logging
from telegram.ext import Updater, ConversationHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Location, Contact, InlineKeyboardMarkup
from datetime import datetime
from typing import Dict, List
from utils.utils import download_image, intersection, get_report, il_count
from database.updater import admin_update, upload_results, register_user
from database.connector import con
import pandas as pd
from database.fetcher import get_poll_from_database
from typing import List
import os
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)



FREE_INPUT = ['location', 'integer', 'open', 'image', 'volume', 'price', 'payment', 'quantity']

EMOJI = '\u2705'
NEXT_BUTTON = '\u27A1 Далее'
RETURN_BUTTON = 'Назад \u21A9'
LOCATION_BUTTON = 'Локация жўнатиш \U0001f4cd'
CONTACT_BUTTON = 'Kontakt yuborish \u1F4F2'
SUCCESS_EMOJI = '🟢'
CANCEL_EMOJI = '🔴'
SUCCESS_EMOJI = '🍀'

class User():
    def __init__(self, chat_id):
        self.chat_id = chat_id
        # self.polls = polls
        self.poll = None
        self.current_state = 0
        self.just_started = True
        self.lang = 'uz'
        self.results = {'responses': []}
        self.last_state = None
        self.wrap_up = False
        self.type_ = None
        self.settings = None
        self.current_handler = None
        self.question = None
        self.type_ = None
        self.answers = None
        self.response = None
        self.finish = None
        self.next_question = None
        self.multiple_choice = []
        self.raw_answers = None
        self.num_questions = []
        self.responses = []
        self.history = []
        

    def update_poll(self, response):
        self.poll = self.poll[response]

    def increase_current_state(self):
        self.last_state = self.current_state
        self.current_state += 1
        return self.current_state


class Bot(telegram.Bot):
    def __init__(self, token, polls):
        super().__init__(token=token)
        self.updater = Updater(token=token, use_context=True)#, workers=15)
        self.dispatcher = self.updater.dispatcher
        self.polls = polls
        self.greeting = 'Assalom aleykum!'
        self.bye = 'Goodbye!'
        self.users = {}
        self.current_poll = None  
        self.settings = [[poll['name'] for poll in polls], ['uz', 'ru']]
        self.success_message = f'Success! {SUCCESS_EMOJI}'
    
    def greet(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.users[chat_id] = User(chat_id)
        self.users[chat_id].current_handler = 'poll'
        self.users[chat_id].current_state = 1
        self.users[chat_id].wrap_up = False
        
        self.update_user_data(chat_id, 'Sklad', '999999', settings=True)
        users = pd.read_sql(sql="SELECT * FROM users_user WHERE confirmed = 1", con=con)
        user_id_registered = users['telegram_id'].values
        self.update_poll(chat_id)
        if not chat_id in user_id_registered:
            text = f'Siz hali registratsiyadan o\'tmadingiz. Registratsiyadan o\'tib administrator tasdiqlashini kuting.\nRaxmat!'
            update.message.reply_text(text, reply_markup=self.reply_markup([NEXT_BUTTON], finish=True))

        else:
            text = self.users[chat_id].poll['data']['uz'][0]['question']
            raw_answers = self.users[chat_id].poll['data']['uz'][0]['answers']
            self.users[chat_id].raw_answers = raw_answers
            answers = []
            if len(raw_answers) != 0:
                answers = [a[0] for a in raw_answers]
            self.users[chat_id].type_ = self.users[chat_id].poll['data']['uz'][0]['type']
            self.users[chat_id].history.append(raw_answers)
            update.message.reply_text(text, reply_markup=self.reply_markup(answers))
            self.save_num_questions(chat_id, self.users[chat_id].current_state)
        
        # update.message.reply_text(self.greeting, reply_markup=self.reply_markup(list(self.poll.keys())))
        # self.users[chat_id] = User(chat_id, self.poll)

        if chat_id in self.users.keys():
            lang = self.users[chat_id].lang
            current_state = self.users[chat_id].current_state
            self.users[chat_id].raw_answers = self.users[chat_id].poll['data'][lang][current_state]['answers']
            raw_answers = self.users[chat_id].poll['data'][lang][current_state]['answers']
            self.users[chat_id].answers = [a[0] for a in raw_answers]
            
            self.users[chat_id].current_handler = 'poll' # there are 2 conv hanlders: 'settings' and 'poll' each does its own conversation
            self.users[chat_id].current_state = 0
            self.users[chat_id].wrap_up = False
            self.users[chat_id].results['responses'] = []
            self.users[chat_id].num_questions = []
            self.users[chat_id].raw_answers = None
            self.users[chat_id].answers = None
            self.users[chat_id].last_state = 0
            
        
        return 1
    
    def cancel(self, update:Update, context:CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        context.bot.send_message(chat_id=chat_id, text=self.bye)


    def add_handler(self, handler, group):
        self.dispatcher.add_handler(handler, group=group)
        

    def run(self):
        self.updater.start_polling(timeout=99999)
        self.updater.idle()
    
    def define_states(self, poll, callback_func):
        states = {}
        for i in range(len(poll)):
            states[i] = [MessageHandler((Filters.text & ~Filters.command), callback_func, run_async=True), 
                         MessageHandler(Filters.location, self.respond),
                         MessageHandler(Filters.photo, self.respond),
                         MessageHandler(Filters.contact, self.respond)]
        return states

    def poll_conv_handler(self, states, entry, fallback):
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler(entry, self.greet)],
            states = states,
            fallbacks = [CommandHandler(fallback, self.cancel)],
            allow_reentry=True, 
            # conversation_timeout=1,
        )
        return self.conv_handler

    def admin(self, update:Update, context:CallbackContext):
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.users[chat_id] = User(chat_id)
        self.users[chat_id].current_handler = 'admin'
        self.users[chat_id].current_state = 1
        self.users[chat_id].wrap_up = False
        
        self.update_user_data(chat_id, 'Admin', '999999', settings=True)
        query = """SELECT telegram_id FROM users_user WHERE user_type = (?)"""
        cur = con.cursor()
        cur.execute(query, ('admin',))
        admin_users = [u[0] for u in cur.fetchall()]
        if len(admin_users) == 0  or not chat_id in admin_users:        
            text = f'{self.greeting}\n\nSizda admin paneliga kirish uchun yetarlicha huquq yoq.'
            # context.bot.send_message(chat_id=chat_id, text=text)
            update.message.reply_text(text, reply_markup=self.reply_markup([NEXT_BUTTON], finish=True))

        elif chat_id in admin_users:
            # print(self.users[chat_id].settings)
            text = self.users[chat_id].poll['data']['uz'][0]['question']
            raw_answers = self.users[chat_id].poll['data']['uz'][0]['answers']
            answers = []
            if len(raw_answers) != 0:
                answers = [a[0] for a in raw_answers]
                self.users[chat_id].history.append(raw_answers)
            self.users[chat_id].type_ = self.users[chat_id].poll['data']['uz'][0]['type']
            update.message.reply_text(text, reply_markup=self.reply_markup(answers))
            self.save_num_questions(chat_id, self.users[chat_id].current_state)
           
        # update.message.reply_text(self.greeting, reply_markup=self.reply_markup(list(self.poll.keys())))
        # self.users[chat_id] = User(chat_id, self.poll)

        if chat_id in self.users.keys():
            
            self.users[chat_id].current_handler = 'admin' # there are 2 conv hanlders: 'settings' and 'poll' each does its own conversation
            self.users[chat_id].current_state = 0
            self.users[chat_id].wrap_up = False
            self.users[chat_id].results['responses'] = []
            self.users[chat_id].num_questions = []
            self.users[chat_id].raw_answers = None
            self.users[chat_id].answers = None
            self.users[chat_id].last_state = 0
        
        lang = self.users[chat_id].lang
        current_state = self.users[chat_id].current_state
        self.users[chat_id].raw_answers = self.users[chat_id].poll['data'][lang][current_state]['answers']
        raw_answers = self.users[chat_id].poll['data'][lang][current_state]['answers']
        self.users[chat_id].answers = [a[0] for a in raw_answers]

        return 1

    def report(self, update:Update, context:CallbackContext):
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.users[chat_id] = User(chat_id)
        self.users[chat_id].current_handler = 'report'
        self.users[chat_id].current_state = 1
        self.users[chat_id].wrap_up = False
        self.update_user_data(chat_id, 'Report', '999999', settings=True)
        query = """SELECT telegram_id FROM users_user WHERE user_type = (?)"""
        cur = con.cursor()
        cur.execute(query, ('admin',))
        admin_users = [u[0] for u in cur.fetchall()]
        if len(admin_users) == 0  or not chat_id in admin_users:        
            text = f"{self.greeting}\n\nSizda hisobot ko'rish uchun yetarlicha huquq yoq."
            # context.bot.send_message(chat_id=chat_id, text=text)
            update.message.reply_text(text, reply_markup=self.reply_markup([NEXT_BUTTON], finish=True))

        elif chat_id in admin_users:
            # print(self.users[chat_id].settings)

            text = self.users[chat_id].poll['data']['uz'][0]['question']
            raw_answers = self.users[chat_id].poll['data']['uz'][0]['answers']
            answers = []
            if len(raw_answers) != 0:
                answers = [a[0] for a in raw_answers]
                self.users[chat_id].history.append(raw_answers)
            self.users[chat_id].type_ = self.users[chat_id].poll['data']['uz'][0]['type']
            update.message.reply_text(text, reply_markup=self.reply_markup(answers))
            self.save_num_questions(chat_id, self.users[chat_id].current_state)
           
        # update.message.reply_text(self.greeting, reply_markup=self.reply_markup(list(self.poll.keys())))
        # self.users[chat_id] = User(chat_id, self.poll)
        if chat_id in self.users.keys():
            self.users[chat_id].current_handler = 'report' # there are 2 conv hanlders: 'settings' and 'poll' each does its own conversation
            self.users[chat_id].current_state = 0
            self.users[chat_id].wrap_up = False
            self.users[chat_id].results['responses'] = []
            self.users[chat_id].num_questions = []
            self.users[chat_id].raw_answers = None
            self.users[chat_id].answers = None
            self.users[chat_id].last_state = 0
            current_state = self.users[chat_id].current_state
            self.users[chat_id].finish = self.users[chat_id].poll['data']['uz'][current_state]['finish']
            
        
        return 1

    def register(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.users[chat_id] = User(chat_id)
        self.users[chat_id].current_handler = 'Registratsiya'
        self.users[chat_id].current_state = 1
        self.users[chat_id].wrap_up = False
        
        self.update_user_data(chat_id, self.users[chat_id].current_handler, '999999', settings=True)
          
        users = pd.read_sql(sql="SELECT * FROM users_user", con=con)
        if chat_id in users['telegram_id'].values.tolist():
            mask = users['telegram_id'] == chat_id
            if users[mask]['confirmed'].values[0] == 1:
                text = f'Siz registratsiyadan o\'tib bo\'lgansiz.'
            if users[mask]['confirmed'].values[0]  == 0:
                text = f'Nomzodingiz tasdiqlanishi kutilmoqda. Iltimos administratorga murojaat qiling.'
            # context.bot.send_message(chat_id=chat_id, text=text)
            update.message.reply_text(text, reply_markup=self.reply_markup([NEXT_BUTTON], finish=True))

        else:
            # print(self.users[chat_id].settings)
            text = self.users[chat_id].poll['data']['uz'][0]['question']
            
            raw_answers = self.users[chat_id].poll['data']['uz'][0]['answers']
            self.users[chat_id].history.append(raw_answers)
            answers = [a[0] for a in raw_answers]
            self.users[chat_id].type_ = self.users[chat_id].poll['data']['uz'][0]['type']
            update.message.reply_text(text, reply_markup=self.reply_markup(answers))
        
        
        # update.message.reply_text(self.greeting, reply_markup=self.reply_markup(list(self.poll.keys())))
        # self.users[chat_id] = User(chat_id, self.poll)
        if chat_id in self.users.keys():
            self.users[chat_id].current_handler = 'Registratsiya' # there are 2 conv hanlders: 'settings' and 'poll' each does its own conversation
            self.users[chat_id].current_state = 1
            self.users[chat_id].wrap_up = False
            self.users[chat_id].results['responses'] = []
            self.users[chat_id].num_questions = []
            self.users[chat_id].raw_answers = None
            self.users[chat_id].answers = None
            self.users[chat_id].last_state = 0
            
        
        return 1

    def generate_conv_handler(self, states, entry, fallback):
        if entry == 'admin':
            self.conv_handler = ConversationHandler(
                entry_points=[CommandHandler(entry, self.admin)],
                states = states,
                fallbacks = [CommandHandler(fallback, self.cancel)],
                allow_reentry=True, 
            )
        elif entry == 'start':
            self.conv_handler = ConversationHandler(
                entry_points=[CommandHandler(entry, self.greet)],
                states = states,
                fallbacks = [CommandHandler(fallback, self.cancel)],
                allow_reentry=True, 
            )
        elif entry == 'register':
            self.conv_handler = ConversationHandler(
                entry_points=[CommandHandler(entry, self.register)],
                states = states,
                fallbacks = [CommandHandler(fallback, self.cancel)],
                allow_reentry=True, 
            )
        elif entry == 'report':
            self.conv_handler = ConversationHandler(
                entry_points=[CommandHandler(entry, self.report)],
                states = states,
                fallbacks = [CommandHandler(fallback, self.cancel)],
                allow_reentry=True, 
            )
        return self.conv_handler
    
    def location_handler(self):
        return MessageHandler(Filters.location, self.respond)
    

    


    def reply_markup(self, options_list, request_location=False, request_contact=False, finish=False):
        keys = []
        button_column = []
        column = 0
        if RETURN_BUTTON in options_list:
            return_idx = options_list.index(RETURN_BUTTON)
            options_list = options_list[:return_idx] + options_list[1+return_idx:]
            options_list.append(RETURN_BUTTON)

        if len(options_list) == 1 and options_list[0] == NEXT_BUTTON:
            options_list = [RETURN_BUTTON]
      
        for i, option in enumerate(options_list):
            button_column.append(column)
            if column == 0:
                column = 1
            elif column == 1:
                column = 0
            self.callback_data = i
            if request_location:
                keys.append([KeyboardButton(option, callback_data=self.callback_data, request_location=True)])
            elif request_contact:
                keys.append([KeyboardButton(option, callback_data=self.callback_data, request_contact=True)])
            else:
                if column == 1:
                    keys.append([KeyboardButton(option, callback_data=self.callback_data,)])
                else:
                    keys[-1].append(KeyboardButton(option, callback_data=self.callback_data,))

        if finish:
            return ReplyKeyboardRemove()

        # return InlineKeyboardMarkup(keys, one_time_keyboard=True, resize_keyboard=True, from_column=button_column)
        return ReplyKeyboardMarkup(keys, one_time_keyboard=True, resize_keyboard=True, from_column=button_column)


    def update_user_data(self, chat_id, response, type_, settings=False):
        if self.users[chat_id].just_started:
            if settings:
                poll_names = [poll_name for poll_name in self.settings[0]]
                poll_idx = poll_names.index(response)
                self.users[chat_id].poll_idx = poll_idx
                self.users[chat_id].poll = self.polls[poll_idx]
                self.users[chat_id].settings = {'poll_name': response, 'lang': 'uz'}
                return 0
            else:
                self.users[chat_id].just_started = False
        self.users[chat_id].increase_current_state()
        self.users[chat_id].type_ = type_
        

        if response == RETURN_BUTTON:
            self.users[chat_id].wrap_up = False
            # self.users[chat_id].next_questions = self.users[chat_id].next_questions[:-1]
        return self.users[chat_id].current_state
    

    # def  validator(self, response):

    def update_poll(self, chat_id):
        self.polls = get_poll_from_database()
        poll_idx = self.users[chat_id].poll_idx
        self.users[chat_id].poll = self.polls[poll_idx]

    def handle_multiple_choice(self, chat_id, answers, response, type_):
        if self.users[chat_id].answers != None and type_ == 'multiple':
            answers_pure = answers[1:]
            if isinstance(response, str) and EMOJI in response:
                response_pure = response[2:]

                if response_pure in answers_pure:
                    idx = answers_pure.index(response_pure)
                    
                    self.users[chat_id].answers[idx+1] = response_pure # idx+1 because answers_pure does not have NEXT_BUTTON option
                    answers = self.users[chat_id].answers
            elif response in answers_pure:
                answers = [EMOJI + ' '+ a if a == response else a for a in self.users[chat_id].answers]
            else: # completely wrong response
                if len(self.users[chat_id].multiple_choice) != 0:
                    keep_multiple = self.users[chat_id].multiple_choice
                    answers = [EMOJI + ' ' + a if a in keep_multiple else a for a in answers]
        return answers

    def user_screen(self, chat_id, response):
        next_question = None
        # self.users[chat_id].current_state = 3
        # print(self.users[chat_id].poll['data']['uz'])
        current_state = self.users[chat_id].current_state
        last_state = self.users[chat_id].last_state
        last_answers = self.users[chat_id].poll['data']['uz'][last_state]['answers']

        if last_state == 0:
            ans = self.users[chat_id].poll['data']['uz'][last_state]['answers']
            next_q_list = [a[1] for a in ans]
            ans = [a[0] for a in ans]
            
            if len(ans) != 0 and response in ans:
                response_idx = ans.index(response)
                self.users[chat_id].current_state = next_q_list[response_idx]-1
        if response == RETURN_BUTTON:
            
            if len(self.users[chat_id].num_questions) >=2:
                self.users[chat_id].num_questions = self.users[chat_id].num_questions[:-1]
                self.users[chat_id].current_state = self.users[chat_id].num_questions[-1]
            else:
                # self.users[chat_id].current_state = self.users[chat_id].num_questions[-1]
                self.users[chat_id].current_state =0
                self.users[chat_id].last_state = 0
        
        elif self.users[chat_id].raw_answers != None and self.users[chat_id].type_ != 'multiple' and response in self.users[chat_id].answers:  ## Check if next question makes a leap if yes then set the current state to it 
            next_question = [a[1] for a in self.users[chat_id].raw_answers if a[0] == response][0]
            self.users[chat_id].next_question = next_question
            
            # if next_question - 1 != self.users[chat_id].current_state:
            #     self.users[chat_id].current_state = next_question - 1
            if next_question - 1 != self.users[chat_id].current_state:
                for key in self.users[chat_id].poll['data']['uz'].keys():
                    if self.users[chat_id].poll['data']['uz'][key]['num'] == next_question:
                        self.users[chat_id].last_state = self.users[chat_id].current_state
                        self.users[chat_id].current_state = key
                        last_state = self.users[chat_id].last_state 

        if response == NEXT_BUTTON and any(EMOJI in ans for ans in [a[0] for a in self.users[chat_id].answers]):      
            next_state = [a[1] for a in last_answers if a[0] == response][0]-1
            if self.users[chat_id].current_state < next_state:
                self.users[chat_id].current_state = next_state
                current_state = self.users[chat_id].current_state 
           
        
        if type(self.users[chat_id].raw_answers) is list and len(self.users[chat_id].raw_answers) != 0: 
            answers_original = self.users[chat_id].poll['data']['uz'][current_state]['answers']
            next_is_prod_identifier = any([a[-1] == 'products_product' for a in self.users[chat_id].raw_answers])
            if response in [a[0] for a in self.users[chat_id].raw_answers]:
                if next_is_prod_identifier:
                        
                    
                    response_id = [a[2] for a in self.users[chat_id].raw_answers if a[0] == response][0]
                    identifiers = self.users[chat_id].poll['data']['uz'][current_state]['answers']
                    # 
                    cursor = con.cursor()
                    query = f'''SELECT {self.users[chat_id].lang} 
                                FROM products_identifier 
                                WHERE product_id = {response_id}'''
                    cursor.execute(query)
                    specific_identidiers = cursor.fetchall()
                    cursor.close()
                    specific_identidiers = [si[0] for si in specific_identidiers]
                    a = []

                    for k, identfier in enumerate(identifiers):
                        if k == 0:
                            a.append(identfier)
                        if intersection(identfier, specific_identidiers):
                            a.append(identfier)
                    self.users[chat_id].poll['data']['uz'][current_state]['answers'] = a
                    if len(a) == 1:
                        self.users[chat_id].poll['data']['uz'][current_state]['answers'] = answers_original
                
            

        current_state = self.users[chat_id].current_state
        # print(response)
        if response != RETURN_BUTTON:
            self.save_num_questions(chat_id, current_state)

        
        data = self.users[chat_id].poll['data']['uz'][current_state]
        
        
        # print(current_state, last_state)
        if current_state == 1 and self.users[chat_id].poll['name'] == 'Sklad':
            last_raw_answers = self.users[chat_id].poll['data']['uz'][0]['answers']
            # print(response, last_raw_answers)
            product_type_id = [idx[2] for idx in last_raw_answers if idx[0] == response]
            answers = data['answers']
            if response == RETURN_BUTTON:
                answers = self.users[chat_id].history[-1]
            if len(product_type_id) != 0:
                product_type_id = product_type_id[0]
                print(answers)
                if 'products_product' == answers[0][-1]:
                    query = '''SELECT * FROM products_product'''
                    df_products = pd.read_sql(query, con)
                    mask = df_products['type_id'] == product_type_id
                    answers_by_product_type = df_products[mask]['uz'].values.tolist()
                    answers = [a for a in answers if a[0] in answers_by_product_type or a[0] == RETURN_BUTTON]
                    self.users[chat_id].poll['data']['uz'][current_state]['answers'] = answers
        
                # cursor.execute(query)
        else:
            answers = data['answers']
            

        question = data['question']

        raw_answers = answers
        answers = [a[0] for a in answers]

        type_ = data['type']
        finish = data['finish']
        
        if type_ == 'multiple' and response != RETURN_BUTTON:
            answers = self.handle_multiple_choice(chat_id, answers, response, type_)
            if not response in answers and not EMOJI in response:
                last_state = self.users[chat_id].last_state
                lang = self.users[chat_id].lang
                # answers_ = self.users[chat_id].poll['data'][lang][last_state]['answers']
                answers_ = last_answers
                if len(answers_) != 0 and 'users_user' in [table[-1] for table in answers_]:
                    id = [answer[2] for answer in answers_ if response == answer[0]]
                    users = pd.read_sql(sql="SELECT * FROM users_user", con=con)

                    mask = users['id'] == id[0]
                    image = users[mask]['image'].values[0]
                    phone_num = users[mask]['telegram_num'].values[0]
                    date_submitted = users[mask]['date_submitted'].values[0]
                    self.send_photo(chat_id=chat_id, photo=open(image, 'rb'), caption=f'Full name: {response}\nPhone num: {phone_num}\nSubmission date: {date_submitted}')

        elif type_ == 'success':
            question += f'\n{self.users[chat_id].responses[-3][0]} ---> {self.users[chat_id].responses[-2][0]} ---> {self.users[chat_id].responses[-1][0]}'


        last_answers = self.users[chat_id].history[-1]
 
        if len(last_answers)!=0 and not response in [a[0] for a in last_answers] and \
            not(len(last_answers) == 1 and last_answers[0][0] == RETURN_BUTTON):
            if len(self.users[chat_id].history) == 0:
                answers = [a[0] for a in last_answers]
            else:
                raw_answers  = self.users[chat_id].history[-1]
                answers = [a[0] for a in raw_answers]
            pass
        elif response == RETURN_BUTTON:
            # if len(self.users[chat_id].history) > 1:
            
            self.users[chat_id].history = self.users[chat_id].history[:-1]
            
            raw_answers =  self.users[chat_id].history[-1]
            answers = [a[0] for a in raw_answers]
            
            
            
        elif isinstance(raw_answers, List):
            self.users[chat_id].history.append(raw_answers)

        return question, answers, type_, finish, raw_answers

    def is_valid(self, chat_id, response, type_, settings=False):
        last_state = self.users[chat_id].last_state
        lang = self.users[chat_id].lang
        just_started = self.users[chat_id].just_started 
        if settings:
            if response in self.settings[0]:
                return True
        
        if type_ == 'multiple':
            if response != NEXT_BUTTON or len(self.users[chat_id].multiple_choice) == 0:
                return False
        
        elif type_ == 'open' and isinstance(response, str):
            return True
        
        elif type_ in ['integer', 'volume', 'price', 'payment', 'quantity'] and isinstance(response, str):
            response = ''.join([r for r in response if r != ' '])
            try:
                int(response)
                return True
            except:
                pass
        elif type_ == 'location' and isinstance(response, Location):
            return True
        elif type_ == 'image' and isinstance(response, List) and len(response) != 0:
            return True

        elif type_ == 'password' and isinstance(response, str):
    
            return True
        elif type_ == 'contact' and isinstance(response, Contact):
            return True
        elif type_ == 'daterange' and isinstance(response, str):
            if '-' in response:
                dates = response.split('-')
                if len(dates) != 2:
                    return False
                a_date, b_date = dates[0].strip(), dates[1].strip()
                try:
                    datetime.strptime(a_date, "%d.%m.%Y")
                    datetime.strptime(b_date, "%d.%m.%Y")
                    return True
                except Exception as e:
                    print(e)
                    return False
            return False


            
        answers = [a[0] for a in self.users[chat_id].poll['data'][lang][last_state]['answers']]
        if not response in answers and not just_started:
            return False
        return True

    def export_report(self, responses, chat_id, context):
        out_filename = get_report(responses)
        if out_filename == None:
            text = "Bu davr bo'yicha ma'lumot yoq..."
            context.bot.send_message(text=text, chat_id=chat_id)
        else:
            root = os.getcwd()
            out_filename = os.path.join(root, out_filename)
            with open(out_filename, 'rb') as document:
                context.bot.send_document(chat_id, document)
        


    def save_settings(self, chat_id, response):
        self.users[chat_id].settings = {'poll_name': response, 'lang': 'uz'}
    
    def save(self, chat_id, response):
        last_state = self.users[chat_id].last_state
        lang = self.users[chat_id].lang
        answer_id = []
        if len(self.users[chat_id].results['responses']) == 0:
            self.users[chat_id].results['user_id'] = chat_id
            self.users[chat_id].results['poll_id'] = self.users[chat_id].poll['id']
            self.users[chat_id].results['date'] = datetime.now()
        answers = self.users[chat_id].poll['data'][lang][last_state]['answers']
        # id_source = self.users[chat_id].poll['data'][lang][last_state]['answers']
        
        answers_id_list = [a[2] for a in answers if a[0] == response]
        id_sources = [id_source[-1] for id_source in answers if isinstance(id_source[-1],str)]
   
        if len(answers_id_list) != 0:
            answer_id = answers_id_list[0]
        if len(id_sources) != 0:
            id_source = id_sources[0]
        else:
            id_source = None

        question_id = self.users[chat_id].poll['data'][lang][last_state]['question_id']
        response = [response]
        if self.users[chat_id].type_ in FREE_INPUT:
            if self.users[chat_id].type_ == 'location':
                response = [f'location:{response[0].latitude};{response[0].longitude}']
            elif self.users[chat_id].type_ == 'image':
                url = self.getFile(response[0][-1].file_id)['file_path']
                filename = self.getFile(response[0][-1].file_id)['file_unique_id']
                success, response = download_image(url, filename)
                response = [response]
                if not success:
                    print('Could not download image fro telegram')
        elif self.users[chat_id].type_ == 'multiple':
            answer_id = [] 
            for r in self.users[chat_id].multiple_choice:
                answer_id.append([a[2] for a in answers if a[0] == r][0])
            response = self.users[chat_id].multiple_choice

        elif self.users[chat_id].type_ == 'password':
            pass
        elif self.users[chat_id].type_ == 'contact':
            response = [response[0]['phone_number']]
            pass
        else:
            answer_id = [answer_id]
        
        question_type = self.users[chat_id].type_

        
        if len(answer_id) == 0:
            if not isinstance(id_source, str):
                id_source = 'survey_openanswer'
            
            self.users[chat_id].results['responses'].append([response, question_id, question_type, id_source])  ### CHANGE response TO answer_id LATER
        else:
            if not isinstance(id_source, str):
                id_source = 'survey_answer'    
                 
            self.users[chat_id].results['responses'].append([answer_id, question_id, question_type, id_source])  ### CHANGE response TO answer_id LATER
        
        self.users[chat_id].responses.append(response)
    
    def can_save(self, chat_id, response, settings=False):
        type_ = self.users[chat_id].type_ 
        if response == RETURN_BUTTON:
            return False
        if not self.is_valid(chat_id, response, type_, settings=settings):
            return False
        
        return True

    def clear_user_data(self, chat_id):
        
        self.users[chat_id].current_state = 0
        self.users[chat_id].last_state = 0

    def keep_multiple(self, chat_id, answers):
        self.users[chat_id].multiple_choice = [a[2:] for a in answers if EMOJI in a]

    def save_num_questions(self, chat_id, next_question):
        self.users[chat_id].num_questions.append(next_question)
        # self.users[chat_id].num_questions = list(set(self.users[chat_id].num_questions))
        self.users[chat_id].num_questions = list(dict.fromkeys(self.users[chat_id].num_questions))

    def handle_return_button(self, chat_id, response):
        if response == RETURN_BUTTON:
            if len(self.users[chat_id].results['responses']) >= 1:
                self.users[chat_id].results['responses'].pop()
    def declare_success(self, update:Update, context:CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        context.bot.send_message(chat_id=chat_id, text=self.success_message)

    def respond(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.update_poll(chat_id)
        request_location = False
        remove_keyboard = False
        request_contact = False
        response = update.message.text
        
        if update.message.location != None:
            response = update.message.location
        elif len(update.message.photo) != 0:
            response = update.message.photo
        elif update.message.contact != None:
            response = update.message.contact 

        self.users[chat_id].response = response
        
        # if not chat_id in self.users.keys() or not self.users[chat_id].current_handler == 'poll':
        #     self.clear_user_data(chat_id)
        #     return ConversationHandler.END
        if self.users[chat_id].current_state < len(self.users[chat_id].poll['data']['uz']):
            raw_answers = self.users[chat_id].poll['data']['uz'][self.users[chat_id].current_state]['answers']
            next_question = [nq[1] for nq in raw_answers if nq[0] == response]
            if len(next_question) !=0:
                next_question = next_question[0]
            else:
                next_question = 'asd'
        else:
            next_question = 99999
        
        

        if self.users[chat_id].current_state == len(self.users[chat_id].poll['data']['uz']) or (self.users[chat_id].finish == 1) and isinstance(next_question, int):
            self.users[chat_id].wrap_up = True
            # return self.users[chat_id].last_state
        if self.users[chat_id].wrap_up:
            if self.can_save(chat_id, response):
                self.save(chat_id, response)
                print('WRAPPED UP!')
                
                if self.users[chat_id].type_ == 'success':
                    if CANCEL_EMOJI in response:
                        self.clear_user_data(chat_id)
                        return ConversationHandler.END

                results = self.users[chat_id].results
                if self.users[chat_id].current_handler == 'Registratsiya':
                    register_user(results)
                    self.declare_success(update, context)
                elif self.users[chat_id].current_handler == 'admin':
                    admin_update(results, success=True)

                    self.declare_success(update, context)
                elif self.users[chat_id].current_handler == 'report':
                    responses = self.users[chat_id].responses
                    self.export_report(responses, chat_id, context)
                    self.declare_success(update, context)
                else:
                    self.declare_success(update, context)
                    report_df = upload_results(results)
                    query = """SELECT telegram_id FROM users_user WHERE user_type = 'admin'"""
                    cur = con.cursor()
                    cur.execute(query)
                    chat_ids = [c[0] for c in cur.fetchall()]
                    fixed_len = 20
                    # fixed_len= max([len(c) for c in report_df.columns.values])
                    if len(chat_ids) != 0:
                        for chat_id in chat_ids:
                            caption = '############### CHECK ###############\n'
                            for col in report_df.columns.values:
                                if col =='image':
                                    continue 
                                s = """{}: {:.>""" + str(2*fixed_len-len(col)-il_count(col)) + """}\n"""
                                caption += s.format(col.capitalize(), str(report_df[col].iloc[0]))
                            caption += '####################################\n'
                            


                            if 'image' in report_df.columns:
                                image = report_df['image'].iloc[0]                            
                                if isinstance( image, str):
                                    self.send_photo(chat_id=chat_id, photo=open(image, 'rb'), caption=caption)
                            else:
                                caption = caption.replace('.', '')
                                self.send_message(text=caption, chat_id=chat_id)

                
                
                
                self.clear_user_data(chat_id)
                return ConversationHandler.END

        if self.can_save(chat_id, response):
            self.save(chat_id, response)        
        else:
            if not self.users[chat_id].just_started:
                self.users[chat_id].current_state = self.users[chat_id].last_state
                

        self.handle_return_button(chat_id, response)
        question, answers, type_, finish, raw_answers = self.user_screen(chat_id, response)

        self.keep_multiple(chat_id, answers)
        self.users[chat_id].answers = answers
        self.users[chat_id].question = question
        self.users[chat_id].type_ = type_
        self.users[chat_id].finish = finish
        if self.users[chat_id].finish:
            self.users[chat_id].wrap_up = True
        self.users[chat_id].raw_answers = raw_answers
        if self.users[chat_id].type_ == 'location':
            request_location = True
            answers = [LOCATION_BUTTON]
            print('Requesting location...')
        elif self.users[chat_id].type_ == 'contact':
            request_contact = True
            answers = [CONTACT_BUTTON]
            print('Requesting contact...') 
        # elif self.users[chat_id].type_ in FREE_INPUT and not self.users[chat_id].type_ == 'open':
        #     remove_keyboard = True

        update.message.reply_text(question, reply_markup=self.reply_markup(answers, request_location=request_location, 
                                    request_contact=request_contact, finish=remove_keyboard))
        
        next_state = self.update_user_data(chat_id, response, type_)
        
        
        if next_state == len(self.users[chat_id].poll['data']['uz']) or (self.users[chat_id].finish == 1 and isinstance(next_question, int)):
            self.users[chat_id].wrap_up = True
            return self.users[chat_id].last_state
        
        return next_state