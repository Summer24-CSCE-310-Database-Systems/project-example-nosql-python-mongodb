from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Initialize MongoDB client
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
chef_collection = db["ChefInfo"]
dish_collection = db["Dish"]
cooks_collection = db["Cooks"]

class MongoDBObject:
    def __init__(self, **kwargs):
        self.created_at = datetime.utcnow()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        dict_out = {}
        for key in self.__slots__:
            dict_out[key] = getattr(self, key)
        dict_out['created_at'] = self.created_at
        return dict_out

class ChefInfo(MongoDBObject):
    __slots__ = ['cname', 'addr', 'phone', 'created_at']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Dish(MongoDBObject):
    __slots__ = ['dname', 'ddetail', 'created_at']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Cooks(MongoDBObject):
    __slots__ = ['chefid', 'dishid', 'created_at']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def make_id(chefid, dishid):
        return str(chefid) + ',' + str(dishid)

    def id(self):
        return Cooks.make_id(self.chefid, self.dishid)

def get_chef_fromid(chef_id):
    return chef_collection.find_one({"_id": ObjectId(chef_id)})

def get_dish_fromid(dish_id):
    return dish_collection.find_one({"_id": ObjectId(dish_id)})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/createchef')
def createchef(feedback_message=None, feedback_type=False):
    return render_template("createchef.html",
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/chefcreate', methods=['POST'])
def chefcreate():
    cname = request.form["cname"]
    addr = request.form["addr"]
    phone = request.form["phone"]

    existing_chef = chef_collection.find_one({"cname": cname})
    if existing_chef:
        return createchef(feedback_message=f'A chef named {cname} already exists. Create a chef with a different name.', feedback_type=False)

    try:
        entry = ChefInfo(cname=cname, addr=addr, phone=phone)
        chef_collection.insert_one(entry.to_dict())
    except Exception as err:
        return createchef(feedback_message=f'Database error: {err}', feedback_type=False)

    return createchef(feedback_message=f'Successfully added chef {cname}', feedback_type=True)

@app.route('/createdish')
def createdish(feedback_message=None, feedback_type=False):
    return render_template("createdish.html",
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/dishcreate', methods=['POST'])
def dishcreate():
    dname = request.form["dname"]
    ddetail = request.form["ddetail"]

    existing_dish = dish_collection.find_one({"dname": dname})
    if existing_dish:
        return createdish(feedback_message=f'A dish named {dname} already exists. Create a dish with a different name.', feedback_type=False)

    try:
        entry = Dish(dname=dname, ddetail=ddetail)
        dish_collection.insert_one(entry.to_dict())
    except Exception as err:
        return createdish(feedback_message=f'Database error: {err}', feedback_type=False)

    return createdish(feedback_message=f'Successfully added dish {dname}', feedback_type=True)

@app.route('/createcooks')
def createcooks(feedback_message=None, feedback_type=False):
    chef_names = [chef['cname'] for chef in chef_collection.find()]
    dish_names = [dish['dname'] for dish in dish_collection.find()]
    return render_template("createcooks.html",
                           chefnames=chef_names,
                           dishnames=dish_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/cookscreate', methods=['POST'])
def cookscreate():
    chef_name = request.form.get('chefnames')
    dish_name = request.form.get('dishnames')

    chef = chef_collection.find_one({"cname": chef_name})
    dish = dish_collection.find_one({"dname": dish_name})
    if not chef or not dish:
        return createcooks(feedback_message='Invalid chef or dish name.', feedback_type=False)

    entry = Cooks(chefid=chef["_id"], dishid=dish["_id"])
    entry_dict = entry.to_dict()
    entry_dict["_id"] = entry.id()  # Set the _id field to the unique identifier

    existing_cooks = cooks_collection.find_one({"_id": entry.id()})
    if existing_cooks:
        return createcooks(feedback_message=f'A cooks relationship between {chef_name} and {dish_name} already exists.', feedback_type=False)

    try:
        cooks_collection.insert_one(entry_dict)
    except Exception as err:
        return createcooks(feedback_message=f'Database error: {err}', feedback_type=False)

    return createcooks(feedback_message=f'Successfully added cooks relationship between {chef_name} and {dish_name}', feedback_type=True)

@app.route('/readchef')
def readchef():
    chef_list = [(chef['cname'], chef['addr'], chef['phone']) for chef in chef_collection.find().sort('created_at')]
    return render_template("readchef.html", cheflist=chef_list)

@app.route('/readdish')
def readdish():
    dish_list = [(dish['dname'], dish['ddetail']) for dish in dish_collection.find().sort('created_at')]
    return render_template("readdish.html", dishlist=dish_list)

@app.route('/readcooks')
def readcooks():
    cooks_list = []
    for cooks in cooks_collection.find().sort('created_at'):
        chef = get_chef_fromid(cooks['chefid'])
        dish = get_dish_fromid(cooks['dishid'])
        cooks_list.append((chef['cname'], dish['dname']))
    return render_template("readcooks.html", cookslist=cooks_list)

@app.route('/updatechef')
def updatechef(feedback_message=None, feedback_type=False):
    chef_names = [chef['cname'] for chef in chef_collection.find()]
    return render_template("updatechef.html",
                           chefnames=chef_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/chefupdate', methods=['POST'])
def chefupdate():
    chef_name = request.form.get('chefnames')
    cname = request.form["cname"]
    addr = request.form["addr"]
    phone = request.form["phone"]

    try:
        update_data = {}
        if cname:
            update_data['cname'] = cname
        if addr:
            update_data['addr'] = addr
        if phone:
            update_data['phone'] = phone
        if update_data:
            chef_collection.update_one({"cname": chef_name}, {"$set": update_data})
    except Exception as err:
        return updatechef(feedback_message=f'Database error: {err}', feedback_type=False)

    return updatechef(feedback_message=f'Successfully updated chef {chef_name}', feedback_type=True)

@app.route('/updatedish')
def updatedish(feedback_message=None, feedback_type=False):
    dish_names = [dish['dname'] for dish in dish_collection.find()]
    return render_template("updatedish.html",
                           dishnames=dish_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/dishupdate', methods=['POST'])
def dishupdate():
    dish_name = request.form.get('dishnames')
    dname = request.form["dname"]
    ddetail = request.form["ddetail"]

    try:
        update_data = {}
        if dname:
            update_data['dname'] = dname
        if ddetail:
            update_data['ddetail'] = ddetail
        if update_data:
            dish_collection.update_one({"dname": dish_name}, {"$set": update_data})
    except Exception as err:
        return updatedish(feedback_message=f'Database error: {err}', feedback_type=False)

    return updatedish(feedback_message=f'Successfully updated dish {dish_name}', feedback_type=True)

@app.route('/updatecooks')
def updatecooks(feedback_message=None, feedback_type=False):
    chef_names = [chef['cname'] for chef in chef_collection.find()]
    dish_names = [dish['dname'] for dish in dish_collection.find()]
    return render_template("updatecooks.html",
                           chefnames=chef_names,
                           dishnames=dish_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/cooksupdate', methods=['POST'])
def cooksupdate():
    chef_name1 = request.form.get('chefnames1')
    dish_name1 = request.form.get('dishnames1')

    chef_name2 = request.form.get('chefnames2')
    dish_name2 = request.form.get('dishnames2')

    try:
        chef1 = chef_collection.find_one({"cname": chef_name1})
        dish1 = dish_collection.find_one({"dname": dish_name1})
        chef2 = chef_collection.find_one({"cname": chef_name2})
        dish2 = dish_collection.find_one({"dname": dish_name2})

        prev_cooks_id = Cooks.make_id(chef1["_id"], dish1["_id"])
        new_cooks_id = Cooks.make_id(chef2["_id"], dish2["_id"])

        existing_cooks = cooks_collection.find_one({"_id": new_cooks_id})
        if existing_cooks:
            return updatecooks(feedback_message=f'A cooks relationship between {chef_name2} and {dish_name2} already exists.', feedback_type=False)

        prev_cooks = cooks_collection.find_one({"_id": prev_cooks_id})
        prev_cooks_created_at = prev_cooks['created_at']

        cooks_collection.insert_one({"_id": new_cooks_id, "chefid": chef2["_id"], "dishid": dish2["_id"], "created_at": prev_cooks_created_at})
        cooks_collection.delete_one({"_id": prev_cooks_id})
    except Exception as err:
        return updatecooks(feedback_message=f'Database error: {err}', feedback_type=False)

    return updatecooks(feedback_message=f'Successfully updated cooks relationship from ({chef_name1} and {dish_name1}) to ({chef_name2} and {dish_name2})', feedback_type=True)

@app.route('/deletechef')
def deletechef(feedback_message=None, feedback_type=False):
    chef_names = [chef['cname'] for chef in chef_collection.find()]
    return render_template("deletechef.html",
                           chefnames=chef_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/chefdelete', methods=['POST'])
def chefdelete():
    if not request.form.get('confirmInput'):
        return deletechef(feedback_message='Operation canceled. Chef not deleted.', feedback_type=False)

    chef_name = request.form.get('chefnames')

    try:
        chef = chef_collection.find_one({"cname": chef_name})
        cooks_with_chef = cooks_collection.find({"chefid": chef["_id"]})

        for cooks in cooks_with_chef:
            cooks_collection.delete_one({"_id": cooks["_id"]})

        chef_collection.delete_one({"_id": chef["_id"]})
    except Exception as err:
        return deletechef(feedback_message=f'Database error: {err}', feedback_type=False)

    return deletechef(feedback_message=f'Successfully deleted chef {chef_name}', feedback_type=True)

@app.route('/deletedish')
def deletedish(feedback_message=None, feedback_type=False):
    dish_names = [dish['dname'] for dish in dish_collection.find()]
    return render_template("deletedish.html",
                           dishnames=dish_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/dishdelete', methods=['POST'])
def dishdelete():
    if not request.form.get('confirmInput'):
        return deletedish(feedback_message='Operation canceled. Dish not deleted.', feedback_type=False)

    dish_name = request.form.get('dishnames')

    try:
        dish = dish_collection.find_one({"dname": dish_name})
        cooks_with_dish = cooks_collection.find({"dishid": dish["_id"]})

        for cooks in cooks_with_dish:
            cooks_collection.delete_one({"_id": cooks["_id"]})

        dish_collection.delete_one({"_id": dish["_id"]})
    except Exception as err:
        return deletedish(feedback_message=f'Database error: {err}', feedback_type=False)

    return deletedish(feedback_message=f'Successfully deleted dish {dish_name}', feedback_type=True)

@app.route('/deletecooks')
def deletecooks(feedback_message=None, feedback_type=False):
    chef_names = [chef['cname'] for chef in chef_collection.find()]
    dish_names = [dish['dname'] for dish in dish_collection.find()]
    return render_template("deletecooks.html",
                           chefnames=chef_names,
                           dishnames=dish_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route('/cooksdelete', methods=['POST'])
def cooksdelete():
    chef_name = request.form.get('chefnames')
    dish_name = request.form.get('dishnames')

    try:
        chef = chef_collection.find_one({"cname": chef_name})
        dish = dish_collection.find_one({"dname": dish_name})

        if not chef:
            return deletecooks(feedback_message=f"Chef {chef_name} not found.", feedback_type=False)
        if not dish:
            return deletecooks(feedback_message=f"Dish {dish_name} not found.", feedback_type=False)
        
        cooks_id = Cooks.make_id(chef["_id"], dish["_id"])

        relationship = cooks_collection.find_one({"_id": cooks_id})
        if not relationship:
            return deletecooks(feedback_message=f'No cooks relationship found between {chef_name} and {dish_name}', feedback_type=False)
        
        # cooks_collection.delete_one({"_id": cooks_id})
        result = cooks_collection.delete_one({"_id": cooks_id})
        if result.deleted_count == 0:
            return deletecooks(feedback_message=f'No cooks relationship found between {chef_name} and {dish_name}', feedback_type=False)
    except Exception as err:
        return deletecooks(feedback_message=f'Database error: {err}', feedback_type=False)

    return deletecooks(feedback_message=f'Successfully deleted cooks relationship between {chef_name} and {dish_name}', feedback_type=True)

if __name__ == '__main__':
    app.run()
