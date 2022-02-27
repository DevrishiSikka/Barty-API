import requests
import json
import time
import mysql.connector
from random import randint

mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="root",
  database="barty"
)

conn = mydb.cursor()

all_list = []
url = "http://www.thecocktaildb.com/api/json/v1/1/random.php"

while True:
    req = requests.get(url)
    data = json.loads(req.content)
    drink_name = data["drinks"][0]["strDrink"]
    if drink_name not in all_list:
        all_list.append(drink_name)
        id = ''.join(["{}".format(randint(0, 9)) for num in range(0, 5)])
        video_link = data["drinks"][0]["strVideo"]
        category = data["drinks"][0]["strCategory"]
        alcoholic = data["drinks"][0]["strAlcoholic"]
        glass_type = data["drinks"][0]["strGlass"]
        instruction = data["drinks"][0]["strInstructions"]
        drink_image = data["drinks"][0]["strDrinkThumb"]
        ingredient = ""
        for i in range(1,16):
            if (data["drinks"][0][f"strIngredient{i}"] != None) and (data["drinks"][0][f"strMeasure{i}"] != None ):
                things = data["drinks"][0][f"strIngredient{i}"]
                measure = data["drinks"][0][f"strMeasure{i}"]
                if ingredient != "" or measure != "":
                    ingredient += f"{things}({measure})/"
            else:
                break
        ingredient = ingredient.rstrip().lstrip().split("/")
        # print(f'''insert into drinks (id,drink_name,category,alcoholic,glass_type,instruction,drink_image,ingredient) values ({int(id)},"{str(drink_name)}","{str(category)}","{str(alcoholic)}","{str(glass_type)}","{str(instruction)}","{str(drink_image)}","{str(ingredient)}")''')

        try:
            conn.execute(f'''insert into drinks (id,drink_name,category,alcoholic,glass_type,instruction,drink_image,ingredient) values ({int(id)},"{str(drink_name)}","{str(category)}","{str(alcoholic)}","{str(glass_type)}","{str(instruction)}","{str(drink_image)}","{str(ingredient)}")''')
            mydb.commit()
            print(len(all_list))
            time.sleep(4)
        except:
            continue
    else:
        continue

