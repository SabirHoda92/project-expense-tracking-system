import mysql.connector
from contextlib import contextmanager


from logging_setup import setup_logger
import bcrypt

logger = setup_logger('db_helper')

@contextmanager
def get_db_cursor(commit=True):
    connection = mysql.connector.connect(
        host= "localhost",
        user= "root",
        password= "root",
        database= "expense_manager"
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    cursor.close()
    connection.close()



def fetch_expense_for_date(expense_date):
    logger.info(f"fetch_expense_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("select * from expenses where expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses

def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expense_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("delete from expenses where expense_date = %s",(expense_date,))

def insert_expenses(expense_date,amount,category,notes):
    logger.info(f"insert_expense called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "insert into expenses (expense_date, amount, category, notes) values (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )

def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute('''
            select category, sum(amount) as total_amount 
            from expenses
            where expense_date between %s and %s
            group by category
            order by total_amount;''',
   (start_date, end_date)
        )
        data = cursor.fetchall()
        return data


def fetch_expenses_for_month():
    logger.info(f"fetch_expense_for_month called ")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''select 
                     month(expense_date) as expense_month,
                     monthname(expense_date) as month_name,
                     sum(amount) as total_amount
                     from expenses
                     group by expense_month, month_name
                     order by total_amount desc;'''
        )
        data = cursor.fetchall()
        return data

def insert_user_information(email, password):
    logger.info(f"insert_user_information called for email: {email}")
    #Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_db_cursor() as cursor:
        cursor.execute(
            "insert into users (email, password) values (%s, %s)",
            (email,hashed_password)
        )

def db_user_login(email, password):
    logger.info(f"select_user_information called for email: {email}")
    with get_db_cursor() as cursor:
        cursor.execute(
            "select * from users where email = %s",
            (email,)
        )
        user_record = cursor.fetchone()

        #check if user exists
        if user_record is None:
            logger.warning("Login failed: user not found")
            raise ValueError("Invalid email and password")


        #check the if the provided password match the hashed password
        hashed_password = user_record['password']
        if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
            logger.warning("Login failed: Incorrect password")
            raise ValueError("Invalid email or password")



if __name__ == "__main__":
    expenses = fetch_expense_for_date("2024-08-1")
    print(expenses)
    # insert_expenses("2024-08-25","300","food","Eat testy samosa chart")
    # delete_expenses_for_date("2024-08-25")
    summary = fetch_expense_summary("2024-08-01","2024-08-05")
    for record in summary:
        print(record)
