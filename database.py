import pymongo
from pyrogram.enums import ChatType
from config import mongouri
from datetime import datetime
import random

client = pymongo.MongoClient(mongouri, connect=False)
db = client["TruthCaller"]
collection = {'user': 'usercache', 'group': 'groupcache'}

def today():
  today = int(datetime.utcnow().strftime('%Y%m%d'))
  return today

def scrape(data):
  userid = data.chat.id
  chattype = data.chat.type
  mycollection = db[collection['user']]
  if chattype == ChatType.GROUP or chattype == ChatType.SUPERGROUP:
    mycollection = db[collection['group']]
    title = data.chat.title
  firstseen = data.date
  result = mycollection.find_one({'user_info.id': userid})

  try:
    result['user_info']['id']
    userexist = True

  except:
    userexist = False

  username = data.from_user.username
  firstname = data.from_user.first_name
  lastname = data.from_user.last_name
  dc = data.from_user.dc_id

  scraped = {
    "user_info": {
      "id": userid,
      "chattype": str(chattype).split(".")[1].lower(),
      "firstseen": firstseen,
      "active": True
    },
    "plan": {
      "type": "free",
      "limits": {
        "per_day": 10
      }
    },
    "requests": {
      "today": today(),
      "consumed": 0
    },
    "accounts": []
  }

  if chattype == 'group' or chattype == "supergroup":
    scraped['user_info']['title'] = title

  else:
    scraped['user_info']['username'] = username
    scraped['user_info']['firstname'] = firstname
    scraped['user_info']['lastname'] = lastname
    scraped['user_info']['is-banned'] = False
    scraped['user_info']['dc'] = dc

  if (userexist == False):
    mycollection.insert_one(scraped)
    statial("users", 1)
    


def add_account(user, account):
  collection = db["usercache"]
  filter = {'user_info.id': user}
  if isinstance(user, str):
    if user.startswith("@"):
      filter = {"user_info.username": user[1:]}
  newvalues = {"$addToSet": {'accounts': account}}
  collection.update_one(filter, newvalues)
  statial("accounts", 1)


def rm_account(user, index):
  collection = db["usercache"]
  filter = {'user_info.id': user}
  if isinstance(user, str):
    if user.startswith("@"):
      filter = {"user_info.username": user[1:]}

  collection.update_one(filter, {"$unset": {f'accounts.{index}': 1}})
  collection.update_one(filter, {"$pull": {'accounts': None}})


def getAccounts(user):
  collection = db["usercache"]
  filter = {'user_info.id': user}
  result = collection.find_one(filter)
  if not len(result['accounts']) == 0:
    return result['accounts']
  else:
    return None

def active(user,index):
  collection = db["usercache"]
  collection.update_one({'user_info.id': user},
                            {"$set": {
                              f"accounts.{index}.status": "active"
                            }})
def inactive_current(user):
  collection = db["usercache"]
  acc = getAccounts(user)
  if acc:
   for i in range(len(acc)):
    if acc[i]["status"] == "active":
      collection.update_one({'user_info.id': user},
                            {"$set": {
                              f"accounts.{i}.status": "inactive"
                            }})


def getID(user):
  acc = getAccounts(user)
  if acc:
    for i in acc:
      if i["status"] == "active":
         return i['installationID']
    return random.choice(acc)['installationID']
  else:
    consumed = get_consumed(user)
    if not consumed > 0:
      return get_id_from_pool()
    return None
    
def statial(what,how):
  collection = db["statache"]
  collection.update_one( {}, {"$inc": { what : how }} )
  return "ok"

def get_statial():
  collection = db["statache"]
  cursor = collection.find()
  for i in cursor:
    value = i
  return value

def get_today(user):
  collection = db["usercache"]
  r = collection.find_one( {'user_info.id': user})
  return r['requests']['today']

def add_usage(user):
  collection = db["usercache"]
  
  if not get_today(user) == today():
    collection.update_one( {'user_info.id': user},{"$set": { "requests.today": today() }} )
    collection.update_one( {'user_info.id': user}, {"$set": { "requests.consumed": 1 }})
    return
  
  collection.update_one( {'user_info.id': user}, {"$inc": { "requests.consumed": 1 }} )

def get_consumed(user):
  collection = db["usercache"]
  r = collection.find_one( {'user_info.id': user})
  if not r["requests"]["today"] == today():
    return 0
  return r['requests']['consumed']

def get_pool():
  col = db["defaults"]
  defaults = col.find_one({})
  installationIDs = defaults["idPool"]
  return installationIDs
  
def get_id_from_pool():
  installationIDs = get_pool()
  installationID = random.choice(installationIDs)
  return installationID

def remove_id(user,id):
   acc = getAccounts(user)
   if acc:
     for i in range(len(acc)):
       if acc[i]["installationID"] == id:
         rm_account(user,i)
   installationIDs = get_pool()
   collection = db["defaults"]
   for i in range(len(installationIDs)):
     installationID = installationIDs[i]
     if id == installationID:
           collection.update_one({}, {"$unset": {f'idPool.{i}': 1}})
           collection.update_one({}, {"$pull": {'idPool': None}})

