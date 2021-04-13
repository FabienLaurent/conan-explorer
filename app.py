from flask import Flask, render_template, request
from flask_autoindex import AutoIndex
import package
import asyncio

app = Flask(__name__)

data = []

async def get_all_info():
    list_package_info = await package.call_conan("search")
    packages = []
    for r in list_package_info['results']:
        items = r['items']
        for i in items:
            packages.append(package.Reference(i))
            
    await asyncio.gather(*[p.init() for p in packages])
    
    global data,app
    [data.append(p.to_treeview()) for p in packages]


@app.route('/')
def index():
    return render_template('index.html', data=data,searchTerm="")

AutoIndex(app, browse_root="/")    

asyncio.run(get_all_info())

if __name__ == "__main__":    
    app.run(debug=True)