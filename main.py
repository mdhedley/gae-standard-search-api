# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
import urllib2
import json
import zlib

# [START imports]
from flask import Flask, render_template, request
from google.appengine.api import search

# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]


@app.route('/indexdocs')
def index():
    html = open('products.json','r').read()
    products = json.loads(html)
    index = search.Index('products')
    #Should really batch here
    current_docs = []
    count = 0
    index_count = 1
    print(str(len(products)))
    for product in products:
        fields = [
            search.NumberField(name='sku',value=product['sku']),
            search.TextField(name='name',value=product['name']),
            search.TextField(name='description',value=product['description']),
            search.TextField(name='url',value=product['url']),
            search.TextField(name='image',value=product['image'])
        ]
        doc = search.Document(doc_id=str(product['sku']),fields=fields)
        current_docs.append(doc)
        count = count + 1
        if count > 199:
            print("Index " + str(index_count)+","+str(count))
            index_count = index_count + 1
            index.put(current_docs)
            current_docs = []
            count = 0
    print("Final Index!!")
    index.put(current_docs)
    return "Complete"


@app.route('/shortsearch')
def shortsearch():
    index = search.Index('products')
    name = request.args.get('name')
    query_string = 'name:'+name
    query_options = search.QueryOptions(
        limit=5
    )
    query = search.Query(query_string=query_string,options=query_options)
    results = index.search(query)
    output_results = []
    for result in results:
       output_results.append({'id':result.doc_id,'name':result.fields[1].value})

    return json.dumps(output_results)

@app.route('/fullsearch')
def fullsearch():
    index = search.Index('products')
    query_string = request.args.get('query')
    query = search.Query(query_string=query_string)
    results = index.search(query)
    output_results = []
    for result in results:
        output_results.append(
            {
                'id':result.doc_id,
                'name':result.fields[1].value,
                'description':result.fields[2].value,
                'url':result.fields[3].value,
                'image':result.fields[4].value
            }
        )
    return json.dumps(output_results)





@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]



