import os
from flask import Flask, send_from_directory
import xml.etree.ElementTree as ET

app = Flask(__name__.split('.')[0])


def get_resource_directory():
    return os.path.join(app.root_path, 'resource')

tree = ET.parse(get_resource_directory() + '\\user_data.xml')
root = tree.getroot()

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(get_resource_directory(), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/users', methods=['GET'])
def list_users():
    output = 'users:[';
    for child in root:
        print('child', child.tag, child.attrib)
        output += str(child.attrib) + ','
        output += ']';
    return output

@app.route('/user/<int:idName>', methods=['GET'])
def get_user(idName):
    print(idName)
    for child in root:
        if child.attrib['id'] == str(idName):
            return str(child.attrib)
    return 'Not found'

if __name__ == '__main__':
    #print(get_resource_directory() + '\\user_data.xml')
    #print(app.url_map)
    app.run(host='localhost')