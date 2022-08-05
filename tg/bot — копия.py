import telegram
import logging
from telegram.ext import Updater, ConversationHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


EMOJI = '\u2705'

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
        self.multiple_choice = []
        self.raw_answers = None


    def update_poll(self, response):
        self.poll = self.poll[response]

    def increase_current_state(self):
        self.last_state = self.current_state
        self.current_state += 1
        return self.current_state


class Bot():
    def __init__(self, token, polls):
        self.updater = Updater(token=token, use_context=True)#, workers=15)
        self.dispatcher = self.updater.dispatcher
        self.polls = polls
        self.greeting = 'Здравствуйте!'
        self.bye = 'Goodbye!'
        self.users = {}
        self.current_poll = None  
        self.settings = [[poll['name'] for poll in polls], ['uz', 'ru']]

    
    def greet(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not chat_id in self.users.keys() or self.users[chat_id].settings == None:
            text = f'{self.greeting}\nВы еще не выбрали тему опроса. Пожалуйста, зайдите в меню и нажмите "Выбрать опрос".'
            context.bot.send_message(chat_id=chat_id, text=text)
            update.message.reply_text(text, reply_markup=self.reply_markup(['Далее'], finish=True))

        else:
            # print(self.users[chat_id].settings)
            text = f'Выбранный опрос: {self.users[chat_id].poll["name"]}\nЯзык: {self.users[chat_id].lang}'
            update.message.reply_text(text, reply_markup=self.reply_markup(['Далее']))
        
        
        # update.message.reply_text(self.greeting, reply_markup=self.reply_markup(list(self.poll.keys())))
        # self.users[chat_id] = User(chat_id, self.poll)

        if chat_id in self.users.keys():
            self.users[chat_id].current_handler = 'poll'
            self.users[chat_id].current_state = 0
            self.users[chat_id].wrap_up = False

        return 0
    
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
            states[i] = [MessageHandler((Filters.text & ~Filters.command), callback_func, run_async=True)]
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

    def choose(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        update.message.reply_text('Choose poll', reply_markup=self.reply_markup(self.settings[0]))
        
        self.users[chat_id] = User(chat_id)
        self.users[chat_id].current_handler = 'choose'
        self.users[chat_id].current_state = 0
        self.users[chat_id].wrap_up = False
        return 0

    def choose_conv_handler(self, states, entry, fallback):
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler(entry, self.choose)],
            states = states,
            fallbacks = [CommandHandler(fallback, self.cancel)],
            allow_reentry=True, 
            # conversation_timeout=1,
        )
        return self.conv_handler

    def settings_respond(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        self.users[chat_id].type_ = 'single'
        response = update.message.text
        if chat_id in self.users.keys():
            if not self.users[chat_id].current_handler == 'choose':
                self.clear_user_data(chat_id)
                return ConversationHandler.END
            if self.users[chat_id].wrap_up:
                
                if self.can_save(chat_id, response, settings=True):
                    self.save_settings(chat_id, response)
                    self.clear_user_data(chat_id)
                    print(self.users[chat_id].results)
                    return ConversationHandler.END 
    
        if self.can_save(chat_id, response, settings=True):
            self.save_settings(chat_id, response)
        
        else:
            if not self.users[chat_id].just_started:
                self.users[chat_id].current_state = self.users[chat_id].last_state
        
        # text = f'Chosen survey name: {response}'
        # context.bot.send_message(chat_id=chat_id, text=text)
        
        next_state = self.update_user_data(chat_id, response, 'single', settings=True)

        if next_state == len(self.settings)-1:
            self.users[chat_id].wrap_up = True
            print('wrapping')
            update.message.reply_text(f'You can now start with the poll: {response}', reply_markup=self.reply_markup(['/start']))
            return self.users[chat_id].last_state

        return next_state


    def reply_markup(self, options_list, request_location=False, finish=False):
        keys = []
        button_column = []
        column = 0
        for i, option in enumerate(options_list):
            button_column.append(column)
            if column == 0:
                column = 1
            elif column == 1:
                column = 0
            self.callback_data = i
            if request_location:
                keys.append([KeyboardButton(option, callback_data=self.callback_data, request_location=True)])
            else:
                if column == 1:
                    keys.append([KeyboardButton(option, callback_data=self.callback_data,)])
                else:
                    keys[-1].append(KeyboardButton(option, callback_data=self.callback_data,))

        if finish:
            return ReplyKeyboardRemove()
            
        return ReplyKeyboardMarkup(keys, one_time_keyboard=True, resize_keyboard=False, from_column=button_column)



    def update_user_data(self, chat_id, response, type_, settings=False):
        if self.users[chat_id].just_started:
            if settings:
                poll_names = [poll_name for poll_name in self.settings[0]]
                poll_idx = poll_names.index(response)
                self.users[chat_id].poll = self.polls[poll_idx]
            else:
                self.users[chat_id].just_started = False
        self.users[chat_id].increase_current_state()
        self.users[chat_id].type_ = type_
        return self.users[chat_id].current_state
    

    # def  validator(self, response):

    def handle_multiple_choice(self, chat_id, answers, response, type_):
        if self.users[chat_id].answers != None and type_ == 'multiple':
            answers_pure = answers[1:]
            if EMOJI in response:
                response_pure = response[2:]

                if response_pure in answers_pure:
                    idx = answers_pure.index(response_pure)
                    
                    self.users[chat_id].answers[idx+1] = response_pure # idx+1 because answers_pure does not have 'Далее' option
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
        if self.users[chat_id].raw_answers != None and self.users[chat_id].type_ != 'multiple':   ## Checking if next question makes a leap if yes then set it to the current state
            next_question = [a[1] for a in self.users[chat_id].raw_answers if a[0] == response][0]
            if next_question - 1 != self.users[chat_id].current_state:
                self.users[chat_id].current_state = next_question - 1
        
        current_state = self.users[chat_id].current_state
        data = self.users[chat_id].poll['data']['uz'][current_state]
        
        question = data['question']
        answers = data['answers']
        
        raw_answers = answers
        answers = [a[0] for a in answers]
        type_ = data['type']
        finish = data['finish']
        if type_ == 'multiple':
            answers = self.handle_multiple_choice(chat_id, answers, response, type_)

        return question, answers, type_, finish, raw_answers

    def is_valid(self, chat_id, response, type_, settings=False):
        last_state = self.users[chat_id].last_state
        lang = self.users[chat_id].lang
        just_started = self.users[chat_id].just_started
        if settings:
            if response in self.settings[0]:
                return True
        
        if type_ == 'multiple':
            if response != 'Далее' or len(self.users[chat_id].multiple_choice) == 0:
                return False
            
        
        answers = [a[0] for a in self.users[chat_id].poll['data'][lang][last_state]['answers']]
        
        if not response in answers and not just_started:
            return False

        
        return True

    def save_settings(self, chat_id, response):
        self.users[chat_id].settings = {'poll_name': response, 'lang': 'uz'}
    
    def save(self, chat_id, response):
        last_state = self.users[chat_id].last_state
        lang = self.users[chat_id].lang

        if len(self.users[chat_id].results['responses']) == 0:
            self.users[chat_id].results['user_id'] = chat_id
            self.users[chat_id].results['poll_id'] = self.users[chat_id].poll['id']
            self.users[chat_id].results['date'] = datetime.now()
        answers = self.users[chat_id].poll['data'][lang][last_state]['answers']
        answers_id_list = [a[2] for a in answers if a[0] == response]
        if len(answers_id_list) != 0:
            answer_id = answers_id_list[0]

        question_id = self.users[chat_id].poll['data'][lang][last_state]['question_id']
        response = [response]
        if self.users[chat_id].type_ == 'multiple':
            answer_id = []
            for r in self.users[chat_id].multiple_choice:
                answer_id.append([a[2] for a in answers if a[0] == r][0])
            response = self.users[chat_id].multiple_choice
        else:
            answer_id = [answer_id]

        self.users[chat_id].results['responses'].append([response, question_id])  ### CHANGE response TO answer_id LATER
    
    def can_save(self, chat_id, response, settings=False):
        type_ = self.users[chat_id].type_ 
        if not self.is_valid(chat_id, response, type_, settings=settings):
            return False
        if self.users[chat_id].just_started and not settings:
            return False
        return True

    def clear_user_data(self, chat_id):
        self.users[chat_id].current_state = 0
        self.users[chat_id].last_state = 0

    def keep_multiple(self, chat_id, answers):
        self.users[chat_id].multiple_choice = [a[2:] for a in answers if EMOJI in a]

    def respond(self, update:Update, context:CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        response = update.message.text
        self.users[chat_id].response = response
        if not chat_id in self.users.keys() or not self.users[chat_id].current_handler == 'poll':
            self.clear_user_data(chat_id)
            return ConversationHandler.END

        if self.users[chat_id].wrap_up:
            if self.can_save(chat_id, response):
                self.save(chat_id, response)
                print('WRAPPED UP!')
                print(self.users[chat_id].results)
                self.clear_user_data(chat_id)
                return ConversationHandler.END

           
        if self.can_save(chat_id, response):
            self.save(chat_id, response)
        
        else:
            if not self.users[chat_id].just_started:
                self.users[chat_id].current_state = self.users[chat_id].last_state
                # if type_

        question, answers, type_, finish, raw_answers = self.user_screen(chat_id, response)

        self.keep_multiple(chat_id, answers)
        self.users[chat_id].answers = answers
        self.users[chat_id].question = question
        self.users[chat_id].type_ = type_
        self.users[chat_id].finish = finish
        self.users[chat_id].raw_answers = raw_answers
        update.message.reply_text(question, reply_markup=self.reply_markup(answers))
        
        next_state = self.update_user_data(chat_id, response, type_)
        
        
        if next_state == len(self.users[chat_id].poll['data']['uz']) or self.users[chat_id].finish == 1:
            self.users[chat_id].wrap_up = True
            return self.users[chat_id].last_state
        
        return next_state