import pymongo
import mysql.connector as mysql

user_input = input(str("Enter mySQL password : "))
#Connecting to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["ILS"]
col = database["Books"]

#Connecting to MySQL Database
db = mysql.connect(host="localhost",
                   user="root",
                   password = user_input,  
                   database="ils2",
                   autocommit = True)
command_handler = db.cursor(buffered=True)


#Getting all MongoDB data
data = col.find({},{"title":1, "publishedDate":1, "authors":1, "categories":1})

for i in data:
    authors=''
    for element in i['authors']:
        if authors=="":
            authors+=element
        else:
            authors+=", " + element
    categories=''
    for element in i['categories']:
        if categories=="":
            categories+=element
        else:
            categories+=", " + element
    publishedDate = 0
    if len(i)==5:
        publishedDate= int(str(i["publishedDate"])[0:4])
    if publishedDate!=0:
        values = (str(i['_id']), i['title'], publishedDate ,authors, categories)
        command_handler.execute("INSERT INTO book (BookID, Title, PublicationYear, Author, Category) VALUES (%s,%s,%s,%s,%s)", values)
    else:
        values = (str(i['_id']), i['title'],authors, categories)
        command_handler.execute("INSERT INTO book (BookID, Title, PublicationYear, Author, Category) VALUES (%s,%s,NULL,%s,%s)", values)
