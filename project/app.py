#imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import random
from cs50 import SQL


db = SQL("sqlite:///project.db")


page_url = 'https://www.scrapethissite.com/pages/simple/'
response = requests.get(page_url)
soup = BeautifulSoup(response.content, 'html.parser')
countries_list = soup.find_all('div', class_= 'col-md-4 country')

def get_country_info(country):
    name = country.find('h3', class_= 'country-name').text.strip()
    capital = country.find('span', class_= 'country-capital').text
    population = country.find('span', class_= 'country-population').text
    area = country.find('span', class_= 'country-area').text
    return name, capital, population, area


def convert_to_number(value):
    """Convert scientific notation (e.g., '1.71E7') or numeric strings to float or int."""
    try:
        num = float(value)  # Convert to float first
        return int(num) if num.is_integer() else num  # Convert to int if no decimals
    except (ValueError, TypeError):
        return value


#2D array of type Country, first index contains name of country. second index is a class object containing data about country
Countries_Array = [{} for _ in range(len(countries_list))]

for i in range(0, len(countries_list)):
    currentName, currentCapital, currentPopulation, currentArea = get_country_info(countries_list[i])
    Countries_Array[i]["name"] = currentName
    Countries_Array[i]["capital"] = (currentCapital if currentCapital != "None" else "No Capital")
    Countries_Array[i]["population"] = convert_to_number(currentPopulation)
    Countries_Array[i]["area"] = convert_to_number(currentArea)




def export_to_excel(Array, file_name):
    # Create a new Excel writer object
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        # Create a DataFrame to hold all the data
        data = []
        for i in range(len(Array)):
            # Append data from each Country object to the list
            current_country = Array[i]  # This is the Country object
            data.append({
                'Country': current_country["name"],
                'Capital': current_country["capital"],
                'Population': current_country["population"],
                'Area': current_country["area"],
            })

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data)
        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False, sheet_name='Countries')

export_to_excel(Countries_Array, "scraped-countries.xlsx")


#WEBSITE

app = Flask(__name__)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list", methods=['POST', 'GET'])
def list():
    global Countries_Array
    def bubble_sort(Array, category):
        for i in range(0, len(Array)):
            for j in range(0, len(Array) - i - 1):

                value1 = Array[j][category]
                value2 = Array[j + 1][category]

                # Convert numeric values but keep strings unchanged
                if isinstance(value1, str) and value1.isdigit():
                    value1 = int(value1)
                if isinstance(value2, str) and value2.isdigit():
                    value2 = int(value2)
                if category == "name" or category == "capital":
                    if Array[j][category] > Array[j + 1][category]:
                        Array[j], Array[j + 1] = Array[j + 1], Array[j]
                elif category == "population" or category == "area":
                    if Array[j][category] < Array[j + 1][category]:
                        Array[j], Array[j + 1] = Array[j + 1], Array[j]
        return Array


    if request.method == "POST":
        countryName = request.form.get('countryName')
        countryCapital = request.form.get('countryCapital')
        categorySortedBy = request.form.get('listOrder')

        if countryName is None and countryCapital is None:
            if categorySortedBy:
                out_list = bubble_sort(Countries_Array, categorySortedBy)
                print(out_list)
                return render_template("list.html", Countries_Array=out_list)

        filtered_list = Countries_Array

        if countryName:
            countryName = countryName.lower()
            filtered_list = [
            country for country in filtered_list
            if countryName in country["name"].lower()]

        if countryCapital:
            countryCapital = countryCapital.lower()
            filtered_list = [
            country for country in filtered_list
            if countryCapital in country["capital"].lower()]

        #If list needs to be sorted:
        if categorySortedBy:
            filtered_list = bubble_sort(filtered_list, categorySortedBy)

        return render_template("list.html", Countries_Array=filtered_list)


    return render_template("list.html", Countries_Array=Countries_Array)



@app.route("/trivia", methods=['POST', 'GET'])
def triviaMain():
    global Countries_Array
    if request.method == "POST":
        gamemode = request.form.get('gamemode')
        streak = request.form.get('streak')
        userAnswer = request.form.get('answer')
        correctAnswer = request.form.get('correctAnswer')

        streak = int(streak) if streak is not None else 0

        if gamemode is None:
            return render_template("options.html")

        if userAnswer is not None:
            if userAnswer == correctAnswer:
                streak += 1
            else:
                return render_template("gameover.html", streak=streak, correctAnswer=correctAnswer, gamemode=gamemode)

        index = random.randint(0, len(Countries_Array)-1)
        country = Countries_Array[index]["name"]
        option1 = Countries_Array[index][gamemode]
        outOptions = [option1] + [Countries_Array[random.randint(0, len(Countries_Array) - 1)][gamemode] for _ in range(3)]
        random.shuffle(outOptions)
        return render_template("question.html", gamemode=gamemode, country=country,outOptions=outOptions, streak=streak, correctAnswer=option1)



    return render_template("options.html")


@app.route("/updateScores", methods=['POST', 'GET'])
def addScore():
    if request.method == "POST":
        streak = request.form.get("streak")
        name = request.form.get("name")
        gamemode = request.form.get("gamemode")

        if streak == 0 or name is None or name == "":
            return render_template("index.html")
        db.execute("INSERT INTO record (name, score, gamemode) VALUES (?,?,?)", name, streak, gamemode)
        return render_template("index.html")


@app.route("/displayHighscores", methods=['POST', 'GET'])
def displayHighscores():
    gamemode = None
    if request.method == "POST":
        gamemode = request.form.get('gamemode')
    if gamemode == None or gamemode == "":
        gamemode = 'capital'
    topTen = db.execute("SELECT name, score FROM record WHERE gamemode = ? ORDER BY score DESC LIMIT 10", gamemode)
    return render_template("highscores.html", topTen=topTen, gamemode=gamemode)
