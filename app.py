# -*- coding: utf-8 -*-
from requests_html import HTMLSession
from flask import Flask, jsonify
import os


app = Flask(__name__)
session = HTMLSession()

r = session.get("https://www.iranjib.ir")
main_links = {i.text:i.attrs['href'] for i in r.html.find('a[href*="showgroup"]')}

def convert_fa_numbers(input_str:str):
    mapping = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '.': '.',
    }
    for i in mapping:
        input_str = input_str.replace(i, mapping[i])
    return input_str


def scrap_page(url):
    r = session.get(url)
    tables = r.html.find('table[class="items_table persian"][dir="rtl"]')
    data = {}
    for i in tables:
        if i.find("tr") != []:
            classname = i.find('.catsection', first=True).text
            # print(classname)
            headers = [x.text for x in i.find('tr[class="header"]', first=True).find('th[dir="rtl"]')]
            # print(headers)
            rows = [[convert_fa_numbers(column.text) for column in row.find('td:not([class="thincol"])')] for row in i.find('tr:not([class])')]
            data[classname] = {"headers":headers, "rows":rows}
    # print(data)
    return data

def get_jib():
    data = {}
    # r = session.get("https://www.iranjib.ir")
    # main_links = {i.text:i.attrs['href'] for i in r.html.find('a[href*="showgroup"]')}
    # print(main_links)
    # scrap_page("https://www.iranjib.ir/showgroup/23/realtime_price/")
    for i in main_links:
        # print(i)
        data[i] = scrap_page(main_links[i])
    return data


@app.route("/jsonjib")
def mainjsonjib_route():
    try:
        res = {
            "error":0,
            "data":get_jib()
        }
    except Exception as e:
        res = {
            "error":1,
            "msg":str(e)
        }
    return jsonify(res)

@app.route("/jsonjib/<NAME>")
def jsonjib_route(NAME):
    try:
        res = {
            "error":0,
            "data":scrap_page(main_links[NAME])
        }
    except Exception as e:
        res = {
            "error":1,
            "msg":str(e)
        }
    return jsonify(res)

if __name__ == "__main__":
    app.run(
        host=os.environ.get("PYJIB_HOST", '127.0.0.1'),
        port=int(os.environ.get("PYJIB_PORT", '8877'))
    )