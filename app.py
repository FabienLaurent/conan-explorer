from flask import Flask, render_template, request
from flask_autoindex import AutoIndex

import package

app = Flask(__name__)

def get_all_info():
    list_package = package.call_conan("search")
    data = []
    for r in list_package['results']:
        items = r['items']
        for i in items:
            r = package.Reference(i)
            data.append(r.to_treeview())

    return data

data = get_all_info()

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    
    if text:
        new_data = []
        for entry in data:
            if text.lower() in entry['text'].lower():
                new_data.append(entry)
    else:
        new_data = data

    return render_template('index.html', data=new_data)

AutoIndex(app, browse_root="/home/fabien")    

if __name__ == "__main__":
    app.run(debug=True)