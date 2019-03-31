import time
import json
from flask import Flask, render_template, Markup, request

cumulative_hits = 0
hit_stats={}

app=Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index1():
    global cumulative_hits
    cumulative_hits+=1
    hit_stats.update({time.ctime():cumulative_hits})
    return render_template('home.html')

@app.route('/get_hits', methods=['GET','POST'])
def get_hits():
    return render_template('gethitspage.html', total_hits=cumulative_hits, hit_stats=hit_stats)


if __name__=='__main__':
    app.debug=True
    app.run(host='127.0.0.1', port=5006)
