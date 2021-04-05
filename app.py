from flask import Flask, render_template, request
from flask_autoindex import AutoIndex
import package
from threading import Thread

app = Flask(__name__)

data = []

def update_info(d):
    global data,app
    r = package.Reference(d)
    data.append(r.to_treeview())    

def get_all_info():
    list_package = package.call_conan("search")
    for r in list_package['results']:
        items = r['items']
        for i in items:
            print("starting threads")
            thread = Thread(target=update_info, args=(i,))
            thread.daemon = True
            thread.start()

@app.route('/')
def index():
    return render_template('index.html', data=data,searchTerm="")

AutoIndex(app, browse_root="/")    

get_all_info()

if __name__ == "__main__":    
    app.run(debug=True)