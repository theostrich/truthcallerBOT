import json
from pyrogram import Client, filters
import database
from alive import run
import requests
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.enums import MessageEntityType
import pyromod.listen
from threading import Thread
from config import apiID, apiHASH, botTOKEN, truecallerAPI
import math
import time 
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

base = truecallerAPI
ostrich = Client("bot", api_id=apiID, api_hash=apiHASH, bot_token=botTOKEN)

async def ph_match(_, __, m):
  number = get_text_number(m)
  if number:
      return True
  return False
  
phone_filter = filters.create(ph_match)


@ostrich.on_message(filters.command(["stats"]))
async def stats(client, message):
  stat = database.get_statial()
  text = f'''**
TruthCaller Bot - STATS:**

**Users        :** `{stat['users']}`
**Accounts :** `{stat['accounts']}`
**Total search:** `{stat['search']}`
    '''
  await message.reply_text(text)


@ostrich.on_message(filters.command(["start"]))
async def start(client, message):

  await message.reply_text(text=f'''
**Hi {message.from_user.mention}!**
I am TruthCaller bot - an unofficial truecaller bot.

Send me any mobile number in international format to get its information.

**Ex:** `+911234567890`
	''',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup([[
                             InlineKeyboardButton("HELP",
                                                  callback_data="getHELP"),
                           ]]),
                           reply_to_message_id=message.id)
  database.scrape(message)


@ostrich.on_message(filters.command(["help"]))
async def help(client, message):

  await message.reply_text(text='''
Here is a detailed guide to use me.
You can use me to get information of unknown mobile numbers.

Send any mobile number in international format with spaces to search.
**Ex:** `+911234567890`

**Available Commands:**
/start : Check if I'm alive!
/help : Get this text

/new : Create new account
/login : Login with existing account
/logout : Remove existing account

/stats : Check my usage status
/about : Know more about me
/donate : Donate my developers and keep me alive.

**Note:** __This is not official true caller bot, all data shared by this bot is based on TrueCaller services.__''',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup([[
                             InlineKeyboardButton(
                               "Get Help",
                               url="https://t.me/ostrichdiscussion/"),
                           ]]),
                           reply_to_message_id=message.id)


def get_text_number(message):
  number = None
  if message.entities:
   for entity in message.entities:
    if entity.type == MessageEntityType.PHONE_NUMBER:
      number = message.text[entity.offset:entity.offset + entity.length].replace(
        " ", "")
      break
  return number


@ostrich.on_message(filters.command(["about"]))
async def aboutTheBot(client, message):
  keyboard = [
    [
      InlineKeyboardButton("➰Channel", url="t.me/theostrich"),
      InlineKeyboardButton("👥Support Group", url="t.me/ostrichdiscussion"),
    ],
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)

  await message.reply_text('''
**Hello! I am TruthCaller Bot - an unofficial TrueCaller Bot**

__TruthCaller Bot is not an official product of True Caller. This bot uses [TrueCallerJS](https://github.com/sumithemmadi/truecallerjs) - a custom script whose functionality is based on true caller services.__
  
**About Me :**
    - **Name        :** TruthCaller
    - **Language    :** Python 3, JavaScript
    - **Libraries   :** [Pyrogram](https://docs.pyrogram.org/), [TrueCallerJS](https://github.com/sumithemmadi/truecallerjs) 

If you enjoy using me and want to help me survive, do donate with the /donate command - my creator will be very grateful! Doesn't have to be much - every little helps! Thanks for reading :)
  ''',
                           reply_markup=reply_markup,
                           disable_web_page_preview=True)


@ostrich.on_message(filters.command(["donate"]))
async def donate(client, message):
  keyboard = [
    [
      InlineKeyboardButton("Donate",
                           url="https://donate.stripe.com/4gwaEKcIrfoCf5K28b"),
    ],
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)
  await message.reply_text('''
Thank you for your wish to contribute. I hope you enjoyed using our services. Make a small donation/contribute to let this project alive.

**Stripe:**
https://donate.stripe.com/4gwaEKcIrfoCf5K28b

**UPI:** `theostrich@upi`

**BTC:**
`12cNBHVnuCjriPfbfxPazHjpxffq6hRQDG`

**USDT (TRC20):**
`TDnv7TLzGdqCnZYavt68LupsfELUgTR8o8`

If you face any issues, contact us at @ostrichdiscussion
        ''',
                           reply_markup=reply_markup,
                           disable_web_page_preview=True)


@ostrich.on_message(filters.command(["logout"]))
async def logout(client, message):
  accounts = database.getAccounts(message.chat.id)
  if not accounts:
    await message.reply(
      "You are not logged in.\nLogin with your mobile number before using logout",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]),
      reply_to_message_id=message.id)
    return
  accButton = []
  for i in range(len(accounts)):
    text = accounts[i]['phone_number']
    account = [
      InlineKeyboardButton(text, callback_data=f"rm_{i}"),
    ]
    accButton.append(account)
  reply_markup = InlineKeyboardMarkup(accButton)
  await message.reply('Choose an account to logout:',
                      reply_markup=reply_markup,
                      reply_to_message_id=message.id)


@ostrich.on_message(filters.command(["login"]))
async def login(client, message):
  accounts = database.getAccounts(message.chat.id)
  if not accounts:
    await new_acc(client, message)
    return
  accButton = []
  for i in range(len(accounts)):

    text = f"{accounts[i]['phone_number']}"
    if accounts[i]["status"] == "active":
      text = text + " ✅"
    acc = [
      InlineKeyboardButton(text, callback_data=f"activate_{i}"),
    ]
    accButton.append(acc)

  accButton.append([
    InlineKeyboardButton("New Account", callback_data="new"),
  ])
  reply_markup = InlineKeyboardMarkup(accButton)
  await message.reply('Choose an account:',
                      reply_markup=reply_markup,
                      reply_to_message_id=message.id)


async def new_acc(client, message):
  d = database.getAccounts(message.from_user.id)
  ask_phone = await message.chat.ask(
    "Please send your mobile number in international format (with no space).\n\n**Ex:** `+911234567890`",
    reply_to_message_id=message.id,reply_markup=ForceReply())

  try:
    phone = get_text_number(ask_phone)
  except:
    await message.reply(
      "Invalid mobile number. Please enter your mobile number in international format (with no space).\n\n**Ex:** `+911234567890`",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]),
      reply_to_message_id=ask_phone.id)
    return
  if not phone or not phone.startswith("+"):
    await message.reply(
      "Invalid mobile number. Please enter your mobile number in international format (with no space).\n\n**Ex:** `+911234567890`",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]),
      reply_to_message_id=ask_phone.id)
    return
  if phone == "+911234567890":
    await message.reply(
      "This mobile number is given as an example to guide users.\nUse your own mobile number to login.\n\n**Format:** __+(country_code)(mobile_number)__\n**Ex:** `+911234567890`\n\nStill have doubt?\nContact @ostrichdiscussion for help.",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]),
      reply_to_message_id=message.id)
    return
  if d:
    for i in range(len(d)):
      acc = d[i]
      if phone ==  acc["phone_number"]:
        database.rm_account( message.chat.id, i)

  data1 = {"number": phone}

  r1 = requests.post(base + "login", json=data1)
  if r1.text == "error":
    await message.reply(
      "**Error sending OTP**\n\nGot unknown response from truecaller. Use other account or try again later.",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]),
      reply_to_message_id=message.id)
    return
  try:
    json_data = json.loads(r1.text)
  except:
    await message.reply(
      "Got unknown response from truecaller.\nContact support @ostrichdiscussion or try again later.",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Ask Help", url="t.me/ostrichdiscussion")]]),
      reply_to_message_id=message.id)
    return

  status = json_data['status']
  if (status == 1 or status == 9):
    process_completed = False
    text = "Send me the 6 digit otp code sent to your mobile number\nOTP is valid for 5 minutes."
    retries = 0
    while (not process_completed):
      if  retries > 4:
        await message.reply("Retries limit reached. Try again after 5 minutes.")
        break
      otp = await message.chat.ask(text, reply_to_message_id=ask_phone.id, 
      reply_markup=ForceReply())

      data2 = {"number": phone, "json_data": json_data, "otp": otp.text}
      print(process_completed)
      process_completed = await verify_otp(message, data2,json_data,phone,otp)
      text = "**ERROR:**\nWRONG OR INVALID OTP.\n\nSEND ME THE OTP AGAIN."
      retries += 1
  
  elif (status == 6 or status == 5):
    await message.reply(
      "**ERROR:**\nVERIFICATION ATTEMPTS EXCEEDED. TRY AGAIN LATER.",
      reply_to_message_id=message.id)
    return
  else:
    await message.reply(
      "**ERROR:**\nUNKNOWN RESPONSE CONTACT SUPPORT @ostrichdiscussion or try again later.",
      reply_to_message_id=message.id)

    return


async def verify_otp(message, data2,json_data,phone,otp):
  process_completed = False
  r2 = requests.post(base + "loginOTP", json=data2)
  try:
    res = json.loads(r2.text)
  except:
    await message.reply(
      "Got unknown response from truecaller.\nContact support @ostrichdiscussion or try again later.",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Get Help", url="t.me/ostrichdiscussion")]]),
      reply_to_message_id=message.id)
    process_completed = True
    return process_completed 
  tatus = res['status']
  if (tatus == 2):
    if (res['suspended']):
      await message.reply("**ERROR:**\nTHIS TRUECALLER ACCOUNT IS SUSPENDED\nUse some other mobile number to login.",
                          reply_to_message_id=message.id,reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Login", callback_data="login")]]))
      process_completed = True
      return process_completed
    database.inactive_current(message.chat.id)
    account = {
      "phone_number": phone,
      "country": json_data['parsedCountryCode'],
      "requestId": json_data['requestId'],
      "userId": res['userId'],
      "installationID": res['installationId'],
      "status": "active"
    }
    database.add_account(message.from_user.id, account)
    await message.reply(
      "Logged in successfully. Now send me any mobile number to search (with no spaces).\n**Ex:** `+911234567890`",
      reply_to_message_id=otp.id)
    process_completed = True
  elif (tatus == 11):
    print("Invalid otp")
  elif (tatus == 7):
    await message.reply("**ERROR:**\nRETRIES LIMIT EXCEED.\n\nYou can login again later.", reply_to_message_id=otp.id)
    process_completed = True
  else:
    await message.reply(
      "**ERROR:**\nUNKNOWN RESPONSE CONTACT SUPPORT @ostrichdiscussion",
      reply_to_message_id=otp.id, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Get Help", url="t.me/ostrichdiscussion")]]))
    process_completed = True

  return process_completed


@ostrich.on_callback_query()
async def cb_handler(client, query):
  if query.data == "new":
    await new_acc(client, query.message.reply_to_message)
    await query.message.delete()
  if query.data == "getHELP":
    await help(client, query.message.reply_to_message)
    await query.message.delete()
  if query.data == "login":
    await login(client, query.message.reply_to_message)
    await query.message.delete()
  if query.data == "logout":
    await logout(client, query.message.reply_to_message)
    await query.message.delete()
  if query.data.startswith("rm"):
    index = query.data[3:]
    database.rm_account(query.message.reply_to_message.chat.id, index)
    await query.message.delete()

  if query.data.startswith("activate_"):
    index = query.data[9:]
    database.inactive_current(query.message.chat.id)
    database.active(query.message.chat.id, index)
    await login(client, query.message)
    await query.message.reply("Logged in successfully...")

    await query.message.delete()


async def notjoined(client, user):
  try:
    user_exist = await client.get_chat_member('theostrich', user)
    return False
  except:
    return True


@ostrich.on_message(phone_filter)
async def truth(client, message):
 try:
  consumed = database.get_consumed(message.chat.id)
  if consumed > 2 and await notjoined(client, message.chat.id):
    await message.reply_text(
      text="**To make more requests, join the channel and try again.**",
      reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton(text="Join theostrich",
                             url="https://t.me/theostrich")
      ]]))
    return

  phone = get_text_number(message).replace(" ", "")
  if not phone.startswith("+"):
    await message.reply(
      "Invalid phone number. Please enter your number in international format (with no space).\n\n**Ex:** `+911234567890`")
    return

  id = database.getID(message.from_user.id)

  if not id:
    await message.reply("Please /login to continue searching.",
                        reply_markup=InlineKeyboardMarkup([[
                          InlineKeyboardButton("Login", callback_data="login")
                        ]]),
                        reply_to_message_id=message.id)
    return
  data = {
    "number": phone,
    "installationID": id,
  }
  print(data)
  requests.get(base)
  r = requests.post(base + "truth", json=data)

  if "status" in json.loads(r.text):
    if (json.loads(r.text)["status"] == 429):
      await message.reply(
        "Too many requests, Try again later or use other account")
      return
    if (json.loads(r.text)['status'] == 401):
      await message.reply( "**Error:** Unauthorised.\n\nThis happens if you logged in some other app. You can login again to continue searching. ",reply_markup=InlineKeyboardMarkup( [[
                          InlineKeyboardButton("Login", callback_data="login")
                        ]]
      ) ,reply_to_message_id=message.id)
      database.remove_id(message.chat.id,id)
      return
    if (json.loads(r.text)['status'] == 426):
      print("426 user")
      await message.reply( "**Error:** Unauthorised.\n\nUse some other number to login. ",reply_markup=InlineKeyboardMarkup( [[
                          InlineKeyboardButton("Login", callback_data="login")
                        ]]
      ) ,reply_to_message_id=message.id)
      database.remove_id(message.chat.id,id)
      return
  print(r.text)
  print(base)
  data = json.loads(r.text)["data"][0]
  reports = "Unavailable"
  
  try:
    name = data["name"]
  except:
    name = "Unavailable"
  try:
    about = data["about"]
  except:
    about = None
  try:
    companyName = data["companyName"]
  except:
    companyName = None
  try:
    type = data["phones"][0]["numberType"]
  except:
    type = "Unavailable"
  try:
    carrier = data["phones"][0]["carrier"]
    if carrier == '':
      carrier = "Unavailable"
  except:
    carrier = "Unavailable"

  try:
    address = data["addresses"][0]["address"]
  except:
    address = None

  try:
    street = data["addresses"][0]["street"]
  except:
    street = None
  email = None
  website = None
  if data["internetAddresses"]:
    if not len(data["internetAddresses"]) == 0:
      for i in data["internetAddresses"]:
        if i["service"] == "email":
          email = i["id"]
        if i["service"] == "link":
          website = i["id"]

  try:
    zipCode = data["addresses"][0]["zipCode"]
  except:
    zipCode = None

  try:
    city = data["addresses"][0]["city"]
  except:
    city = None

  try:
    countryCode = data["addresses"][0]["countryCode"]
    try:
      countryData = json.loads(open('countries.json', "r").read())
      country = countryData[countryCode]["name"]
    except:
      country = countryCode
  except:
    country = "Unavailable"

  try:
    tzone = data["addresses"][0]["timeZone"]
  except:
    tzone = "Unavailable"

  try:
    spam = data["spamInfo"]
    isSPAM = True
    try:
      spamType = spam["spamType"]
    except:
      spamType = "Unavailable"
    try:
      spamType = spam["spamType"]
    except:
      spamType = "Unavailable"
    try:
      spamStats = spam["spamStats"]

      try:
        reports = spamStats["numReports"]
      except:
        reports = "Unavailable"
      try:
        calls = spamStats["numCalls60days"]
      except:
        calls = None
      try:
        callsAns = spamStats["numCallsAnswered"]
      except:
        callsAns = None
    #  try:
    #  callsUnans = spamStats["numCallsNotAnswered"]
    #  except:
    #    callsUnans = None
      pick_rate = None
      if callsAns and calls:
        pick_rate = math.ceil((callsAns / calls) * 100)

      try:
        searches = spamStats["numSearches60days"]
      except:
        searches = "Unavailable"
      try:
        spammerType = spamStats["spammerType"]
      except:
        spammerType = "Unavailable"
      spamCountries = []
      if spamStats["topSpammedCountries"]:
        for i in spamStats["topSpammedCountries"]:
          if i["countryCode"]:
            try:
              countryData = json.loads(open('countries.json', "r").read())
              country = countryData[i["countryCode"]]["name"]
              spamCountries.append(country)
            except:
              spamCountries.append(i["countryCode"])

    except:
      spamStats = None
      

  except:
    isSPAM = False
  text = "\ud83d\udd0d **Truecaller says:**\n\n"
  if isSPAM:
    text += "⚠️ **Spammer alert!!!**"
    if spamStats:
     if not reports == 'Unavailable':
      text += f"\n⚠️ `{reports}` __users reported this number as SPAM__"
    text += "\n\n"

  text += f"**Name  :** `{name}`\n"
  if companyName:
    text += f"**Company Name  :** `{companyName}`\n"
  if about:
    text += f"**About  :** `{about}`\n"

  companyName
  text += f"**Phone :** `{phone}`\n"
  text += f"**Type  :** `{type}`\n"
  text += f"**Carrier :** `{carrier}`\n\n"
  text += f"**Addresses:**\n"
  if address:
    text += f"  - **Address :** `{address}`\n"
  if street:
    text += f"  - **Street :** `{street}`\n"
  if city:
    text += f"  - **City :** `{city}`\n"
  text += f"  - **Country :** `{country}`\n"
  if zipCode:
    text += f"  - **ZipCode :** `{zipCode}`\n"

  text += f"  - **Timezone :** `{tzone}`\n\n"
  if isSPAM:
    text += "**Spam info:**\n"
    text += f"  - **Spam Type :** `{spamType}`\n"
    if spamStats:
     text += f"  - **Spammer Type :** `{spammerType}`\n"
     text += "  - **Stats :**\n"
     if not reports == 'Unavailable':
      text += f"        - **reports :** `{reports}`\n"
     text += f"        - **look-ups :** `{searches}`\n"
     if calls:
      text += f"        - **calls made:** `{calls}`\n"
     if pick_rate:
      text += f"        - **Pick-up rate:** `{pick_rate}%`\n"

     if spamCountries:
      text += f"  - **Top countries:** `{','.join(spamCountries)}`\n"
  if email:
    text += f"**Email  :** `{email}`\n"
  if website:
    text += f"**Website  :** `{website}`\n"

  await message.reply(text, disable_web_page_preview=True)
  database.statial("search", 1)
  database.add_usage(message.chat.id)


 except Exception as e:
   logger.exception(e)
   await message.reply("Something went wrong, Contact support @ostrichdiscussion",reply_markup=InlineKeyboardMarkup( [[
                          InlineKeyboardButton("Support Group", url="https://t.me/ostrichdiscussion")
                        ]]
      ) )

@ostrich.on_message(filters.command(["broadcast"]))
async def broadcast(client, message):
    chat_id = message.chat.id
    botOwnerID = [1775541139, 1520625615]
    if chat_id in botOwnerID:
        await message.reply_text("Broadcasting...")
        collection = database.db["usercache"]
        chat = collection.find({})
        chats = [sub['user_info']['id'] for sub in chat]
        failed = 0
        for chat in chats:
            try:
                await message.reply_to_message.forward(chat)
                print("broadcasting")
                time.sleep(2)
            except:
                failed += 1
                print("Couldn't send broadcast to %s, group name %s", chat)
        await message.reply_text(
            "Broadcast complete. {} users failed to receive the message, probably due to being kicked."
            .format(failed))
    else:
        await client.send_message(
            1520625615, f"Someone tried to access broadcast command,{chat_id}")


 
@ostrich.on_message()
async def on_message(client, message):
  await message.reply(
    "Send me any number in international format (with no space) to search.\n\n**Ex:** `+911234567890`"
  )


server = Thread(target=run)
server.start()
ostrich.run()
