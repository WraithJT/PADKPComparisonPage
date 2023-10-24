"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request
from PADKPComparisonPage import app
from urllib.request import Request, urlopen
import json


class Character:
    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        return self.name < other.name

    def __getitem__(self, item):
        return getattr(self, item)


class CharacterDKP:
    def __init__(self, name, rank, currentdkp, thirtyday, sixtyday, ninetyday):
        self.name = name
        self.rank = rank
        self.currentdkp = currentdkp
        self.thirtyday = thirtyday
        self.sixtyday = sixtyday
        self.ninetyday = ninetyday

    def __eq__(self, other):
        return self.currentdkp == other.currentdkp and self.name == other.name

    def __lt__(self, other):
        if self.currentdkp != other.currentdkp:
            return other.currentdkp < self.currentdkp
        else:
            return self.name < other.name


def GetCharacters():
    characterReq = Request(
        "https://3h19u5fy8e.execute-api.us-east-2.amazonaws.com/prod/characters"
    )
    characterReq.add_header("accept", "application/json, text/plain, */*")
    characterReq.add_header("clientid", "8bc66c6ca9f69")
    characterData = json.load(urlopen(characterReq))
    print(characterData)
    characters = []
    for c in characterData:
        if c["Rank"] in (
            "Senior Officer",
            "Operations Specialist",
            "Class Lead",
            "Raider",
            "Guest",
        ):
            characters.append(
                Character(
                    c["Name"],
                )
            )
        print("")
    characters.sort()
    count = 0
    table = '<table class="center"><tbody><tr>'
    end = 0
    for i in range(len(characters)):
        end = 0
        name = characters[i]["name"]
        table += (
            '<td><input type="checkbox" id="'
            + name
            + '" name="character" value='
            + name
            + " /><label for="
            + name
            + "> "
            + name
            + " </label></td>"
        )
        if (i + 1) % 5 == 0:
            table += "</tr>"
            end = 1
    if end == 0:
        table += "</tr></tbody></table>"
    else:
        table += "</tbody></table>"
    return table


def CompareDKP(search):
    dkpReq = Request("https://7gnjtigho4.execute-api.us-east-2.amazonaws.com/prod/dkp")
    dkpReq.add_header("accept", "application/json, text/plain, */*")
    dkpReq.add_header("clientid", "8bc66c6ca9f69")
    dkpData = json.load(urlopen(dkpReq))
    characterDKPs = []
    for c in dkpData["Models"]:
        if c["CharacterName"] in search:
            characterDKPs.append(
                CharacterDKP(
                    c["CharacterName"],
                    c["CharacterRank"],
                    c["CurrentDKP"],
                    "{:.1%}".format(c["Calculated_30"]),
                    "{:.1%}".format(c["Calculated_60"]),
                    "{:.1%}".format(c["Calculated_90"]),
                )
            )
    characterDKPs.sort()
    table = '<table class="center"><tbody><tr><th>Name</th><th>Current DKP</th><th>30-Day Attendance</th><th>60-Day Attendance</th><th>90-Day Attendance</th></tr>'
    for c in characterDKPs:
        table += (
            "<tr><td>"
            + c.name
            + '</td><td style="text-align:right">'
            + str(int(c.currentdkp))
            + '</td><td style="text-align:right">'
            + c.thirtyday
            + '</td><td style="text-align:right">'
            + c.sixtyday
            + '</td><td style="text-align:right">'
            + c.ninetyday
            + "</td></tr>"
        )
    table += "</tbody></table>"
    return table


@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "GET":
        characters = GetCharacters()
        """Renders the home page."""
        return render_template(
            "index.html",
            title="Home Page",
            year=datetime.now().year,
            characters=characters,
        )
    else:
        characterDKP = CompareDKP(request.form["search"])
        return render_template("compare.html", search=characterDKP)


@app.route("/compare", methods=["POST", "GET"])
def compare():
    characterDKPs = CompareDKP(request.form.getlist("character"))
    return render_template(
        "compare.html",
        title="Compare",
        year=datetime.now().year,
        characterDKPs=characterDKPs,
    )
