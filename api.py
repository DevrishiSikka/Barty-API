import json
from auth import AuthHandler
from schema import AuthDetail
from fastapi import FastAPI, Depends, HTTPException
import mysql.connector



app = FastAPI()
auth_handler = AuthHandler()



mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="root",
  database="barty"
)


conn = mydb.cursor()
users = []



def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct





@app.post("/register", status_code=201)
def register(auth_details: AuthDetail):
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail="Username taken")
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    users.append({
        'username':auth_details.username,
        'password':hashed_password
    })
    return




@app.post("/login")
def login(auth_details: AuthDetail):
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break
    if (user is None) or (not auth_handler.verify_password(auth_details.password,user['password'])):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    token = auth_handler.encode_token(user['username'])
    return {'token':token}


# @app.get("/getall", description="Get a list of drinks with description ")
# async def all_drinks(limit: str):
#     value = {}
#     count = 0
#     conn.execute(f"select * from drinks limit {limit}")
#     for i in list(conn):
#         temp = {
#             'drinkID':i[0],
#             'drinkName':i[1],
#             'drinkCategory':i[2],
#             'drinkAlco':i[3],
#             'drinkGlass':i[4],
#             'drinkInstruction':i[5],
#             'drinkImage':i[6],
#             'drinkIngredient':i[7]
#         }
#         value.update({count:temp})
#         count+=1
#     return value

@app.get("/searchName", description="Get the details of a drink based on the name")
async def search_name(drink: str):
    value = {}
    conn.execute(f"select * from drinks where drink_name={drink}")
    try:
        i = list(conn)[0]
        temp = {
                'drinkID': i[0],
                'drinkName': i[1],
                'drinkCategory': i[2],
                'drinkAlco': i[3],
                'drinkGlass': i[4],
                'drinkInstruction': i[5],
                'drinkImage': i[6],
                'drinkIngredient': i[7]
            }
        value.update({"drink": temp})
        return value
    except IndexError:
        return {"message":"drink not found. Check for spelling mistakes or query a new drink"}




@app.get("/searchLetter", description="To search drinks using the first letter of the name")
def search_first_letter(letter: str, limit :int | None = None):
    if limit == None:
        limit = 5
    count = 0
    value = {}
    conn.execute(f"select * from drinks where drink_name like '{letter}%' limit {limit}")
    for i in list(conn):
        temp = {
            'drinkID':i[0],
            'drinkName':i[1],
            'drinkCategory':i[2],
            'drinkAlco':i[3],
            'drinkGlass':i[4],
            'drinkInstruction':i[5],
            'drinkImage':i[6],
            'drinkIngredient':i[7]
        }
        value.update({count:temp})
        count+=1
    return value





@app.get("/filter", description="To get drinks bases on alcohol preference")
def search_first_letter(alcohol: bool):
    count = 0
    value = {}
    if alcohol:
        alcohol = 'Alcoholic'
    else:
        alcohol = 'Non alcoholic'
    conn.execute(f"select * from drinks where alcoholic='{alcohol}' limit 5")
    for i in list(conn):
        temp = {
            'drinkID':i[0],
            'drinkName':i[1],
            'drinkCategory':i[2],
            'drinkAlco':i[3],
            'drinkGlass':i[4],
            'drinkInstruction':i[5],
            'drinkImage':i[6],
            'drinkIngredient':i[7]
        }
        value.update({count:temp})
        count+=1
    return value





@app.get("/listCat", description="List all th differnent categories of drinks in the database")
async def list_categories():
    value = {}
    temp = []
    counter = 0
    conn.execute("select distinct category from drinks")
    for i in list(conn):
        temp.append({"category":i[0]})

    value.update({counter:temp})
    return value





@app.get("/listGlass", description="Get a list of all the glasses in the database")
async def list_categories():
    value = {}
    temp = []
    counter = 0
    conn.execute("select distinct glass_type from drinks")
    for i in list(conn):
        temp.append({"category":i[0]})

    value.update({counter:temp})
    return value





@app.get("/suggestion",description="Get custom suggestions based on the values provided")
async def give_suggestion(category: str|None=None, alcoholic:str| None=None, glass_type:str | None=None):
    category_comm = ''
    alcoholic_comm = ''
    glass_type_comm = ''
    count = 0
    value = {}
    if category != None:
        category_comm += f" category={category} and"
    if alcoholic != None:
        alcoholic_comm += f" alcoholic={alcoholic} and"
    if glass_type != None:
        glass_type_comm += f" glass_type={glass_type} and"

    final = f"select distinct * from drinks where {category_comm}  {alcoholic_comm}  {glass_type_comm}".rstrip("and")+" limit 5"
    conn.execute(final)
    if len(list(conn)) != 0:
        for i in list(conn):
            temp = {
                'drinkID': i[0],
                'drinkName': i[1],
                'drinkCategory': i[2],
                'drinkAlco': i[3],
                'drinkGlass': i[4],
                'drinkInstruction': i[5],
                'drinkImage': i[6],
                'drinkIngredient': i[7]
            }
            value.update({count: temp})
            count += 1
        return value
    else:
        return {"message":"no drink found for the given"}




@app.get("/random",description="Get a random drink")
async def random():
    conn.execute("SELECT * FROM drinks ORDER BY RAND() LIMIT 1")
    for i in list(conn):
        temp = {
                'drinkID': i[0],
                'drinkName': i[1],
                'drinkCategory': i[2],
                'drinkAlco': i[3],
                'drinkGlass': i[4],
                'drinkInstruction': i[5],
                'drinkImage': i[6],
                'drinkIngredient': i[7]
        }
    return temp





@app.get("/getalldrinks",description="get a list of all drinks in the database")
def get_all_drinks(username = Depends(auth_handler.auth_wrapper)):
    drinks = []
    conn.execute("select drink_name from drinks")
    for i in list(conn):
        drinks.append(i[0])

    return {"drinks":drinks}

@app.get("/randomselection",description="Get 10 random cocktails")
def random_selection(username = Depends(auth_handler.auth_wrapper)):
    conn.execute("SELECT * FROM drinks ORDER BY RAND() LIMIT 10")
    counter = 0
    value = {}
    for i in list(conn):
        temp = {
                'drinkID': i[0],
                'drinkName': i[1],
                'drinkCategory': i[2],
                'drinkAlco': i[3],
                'drinkGlass': i[4],
                'drinkInstruction': i[5],
                'drinkImage': i[6],
                'drinkIngredient': i[7]
        }
        value.update({counter:temp})
        counter+=1
    return value