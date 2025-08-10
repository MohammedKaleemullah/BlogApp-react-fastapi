
import psycopg2
from dotenv import load_dotenv
import os

def create_connection():
    load_dotenv()

    conn = psycopg2.connect(user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        host=os.getenv("db_host"),
        port=os.getenv("db_port"),  
        database=os.getenv("db_database"))


    curr = conn.cursor()
    return conn, curr

def create_table():
    try:
        conn, curr = create_connection()
        try:
            curr.execute("CREATE TABLE IF NOT EXISTS \
            cartoon(cartoonID INTEGER, name TEXT,\
            cartoonImg BYTEA)")
            
        except(Exception, psycopg2.Error) as error:
            print("Error while creating cartoon table", error)
        finally:
            conn.commit()
            conn.close()
    finally:

        pass

def write_blob(cartoonID,file_path,name):
    try:

        drawing = open(file_path, 'rb').read()
        conn, cursor = create_connection()
        try:           

            cursor.execute("INSERT INTO cartoon\
            (cartoonID,name,cartoonImg) " +
                    "VALUES(%s,%s,%s)",
                    (cartoonID,name, psycopg2.Binary(drawing)))

            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while inserting data in cartoon table", error)
        finally:
            conn.close()
    finally:

        pass
   
create_table()

write_blob(1,r"D:\OneDrive - 1CloudHub\Desktop\full-blog-app\backend\app\assets\pikachu.jpg","pikachu")
# write_blob(2,"F:\\TeachPytho\\GFGPhotos\\archie.jpg","Archie")
# write_blob(3,"F:\\TeachPytho\\GFGPhotos\\tintin.png","Tintin")
# write_blob(4,"F:\\TeachPytho\\GFGPhotos\\pikachu.jpg","Pikachu")
# write_blob(5,"F:\\TeachPytho\\GFGPhotos\\kungfupanda.jpg","Kung Fu Panda")