from distlib import logger
from fastapi import FastAPI, HTTPException, Depends
from datetime import date

from fastapi.security import OAuth2PasswordBearer

import db_helper
from typing import List
from pydantic import BaseModel

from jwt_login import create_access_token, create_refresh_token, decode
from blcoklist import BLOCKLIST



class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str


class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date






app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    expenses = db_helper.fetch_expense_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code= 500, detail="Failed to retrieve expenses summary from the database")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expenses(expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "Expenses updated successfully"}


@app.post("/analytics")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date,date_range.end_date)
    if data is None:
        raise HTTPException(status_code= 500, detail="Failed to retrieve expenses summary from the database")

    total_amount = sum([row['total_amount'] for row in data])

    breakdown = {}
    for row in data:
        percentage = row['total_amount'] / total_amount*100 if total_amount != 0 else 0
        breakdown[row['category']] = {
            "total_amount": row['total_amount'],
            "percentage": percentage
        }
    return breakdown

@app.post("/register")
def user_register(user: UserCreate):
    logger.info("Register endpoint called")
    try:
        db_helper.insert_user_information(user.email, user.password)
    except ValueError as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "user registered successfully"}


@app.post("/login")
def user_login(user: UserLogin):
    logger.info("logging endpoint called")
    try:
        db_helper.db_user_login(user.email, user.password)
        # Generate JWT token using the login function from jwt_login.py
        access_token = create_access_token(user.email)
        token_refresh = create_refresh_token(user.email)

        return {"message": "Login successfully", "access_token": access_token, "refresh_token": token_refresh}
    except ValueError as e:
        logger.error(f"login error {e}")
        raise HTTPException(status_code=401, detail= "Invalid login credentials")



@app.post("/refresh")
def refresh_token(token:str = Depends(oauth2_scheme)):
    decoded_token = decode(token)

    # Check if the token is missing or invalid
    if decoded_token is None:
        raise HTTPException(status_code=401, detail="Token is invalid or has expired")

    # Ensure token is a refresh token
    if decoded_token.get('type') != "refresh":
        raise HTTPException(status_code=401, detail= "Invalid token type")

    #Generate new access token
    email = decoded_token['email']
    new_access_token = create_access_token(email)
    BLOCKLIST.add(token)

    return {"access_token": new_access_token}



@app.post("/logout")
def user_logout(token: str = Depends(oauth2_scheme)):
    decoded_token = decode(token)

    # Check if the token is valid and is of type "refresh" or "access"
    if decoded_token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Add the token to the blocklist
    BLOCKLIST.add(token)

    # Optional: Log out message based on email if needed
    email = decoded_token.get('email', 'Unknown user')

    return {"message": f"{email} logged out successfully"}





@app.get("/month")
def get_analytics_by_month():
       monthly_summary = db_helper.fetch_expenses_for_month()
       if monthly_summary is None:
           raise HTTPException(status_code=500, detail="Failed to retrieve expenses summary from the database")

       return monthly_summary








