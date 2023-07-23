import os
import yaml

secrets_path = "example-secrets.yaml"
ENV = bool(os.environ.get('ENV', False)) and not os.environ.get('ENV', False) == "False"
print(ENV)
if ENV:
    print("Using values from ENV")
    apiID = os.environ.get('apiID', None)
    apiHASH = os.environ.get('apiHASH', None)
    botTOKEN = os.environ.get('botTOKEN', None)
    truecallerAPI = os.environ.get('apiBaseURL', None)
    port = int(os.environ.get("PORT", 5000))  
    mongouri = os.environ.get("mongouri", "")
    database = os.environ.get("database", "TruthCaller")
    user_collection = os.environ.get('userCollection', "users")
    group_collection = os.environ.get('groupCollection', "groups")
    collections = {'user': user_collection, 'group': group_collection}

elif os.path.isfile(secrets_path):
    print("Using values from secrets.yaml")
    yaml_file = open(secrets_path, 'r')
    yaml_content = yaml.safe_load(yaml_file, Loader=yaml.FullLoader)
  
    apiID = yaml_content['telegram'][0]['apiID']
    apiHASH = yaml_content['telegram'][1]['apiHASH']
    botTOKEN = yaml_content['telegram'][2]['botTOKEN']

    truecallerAPI = yaml_content['truecaller'][0]['apiEndPoint']
    port = int(os.environ.get("PORT", 5000))  

    mongouri = yaml_content['MongoDB'][0]['URI']
    database = yaml_content['MongoDB'][1]["database"]
    collection = yaml_content['MongoDB'][2]["collection"]


else:
    print(
        'This app is not configured correctly. Check README or contact support.'
    )
    quit(1)