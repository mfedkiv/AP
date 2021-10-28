import yaml

with open("config/config.yaml", 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    username = data["username"]
    password = data["password"]
    db_name = data["db_name"]

connection_string = f"mysql+pymysql://{username}:{password}@localhost/{db_name}"
