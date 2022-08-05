from math import prod
from tokenize import group
from tg.bot import  Bot
from configs.config import TOKEN
from database.fetcher import get_poll_from_database

import sys



poll_dicts = get_poll_from_database()
bot = Bot(TOKEN, poll_dicts)

states = bot.define_states(list(range(0,999)), bot.respond)
conv_handler = bot.generate_conv_handler(states=states, entry='start', fallback='cancel')
bot.add_handler(conv_handler, group=1)

states = bot.define_states(list(range(0,999)), bot.respond)
conv_handler = bot.generate_conv_handler(states=states, entry='admin', fallback='cancel_admin')
bot.add_handler(conv_handler, group=1)

states = bot.define_states(list(range(0,999)), bot.respond)
conv_handler = bot.generate_conv_handler(states=states, entry='register', fallback='cancel_register')
bot.add_handler(conv_handler, group=1)

states = bot.define_states(list(range(0,999)), bot.respond)
conv_handler = bot.generate_conv_handler(states=states, entry='report', fallback='cancel_report')
bot.add_handler(conv_handler, group=1)

# location_handler = bot.location_handler()
# bot.add_handler(location_handler,group=0)


bot.run()