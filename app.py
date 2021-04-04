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
    return render_template('index.html', data=data,searchTerm="")

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['search']
    return render_template('index.html', data=data,searchTerm=text)

AutoIndex(app, browse_root="/")    

if __name__ == "__main__":
    app.run(debug=True)