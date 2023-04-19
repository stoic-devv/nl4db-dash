
from typing import ContextManager
from lib import apriori
from flask import jsonify

import logging
import os


logger = logging.getLogger(__name__)
OUT_PATH = './src/out/association_rules.csv'

def get_multi_ar(df):

    context = {}
    col_names = list(df)

    ### modify so that each entry has it corresponding column name indicator
    df = df[col_names].astype(str)
    
    for j, colname in enumerate(list(df)):
        df[colname] = colname + ":" + df[colname].astype(str)

    # sampling 
    # ToDo: How do we get this seed value
    if df.shape[0] * (2**df.shape[1]) > 3584000:
        df = df.sample(n=int(3584000 / (2**df.shape[1])), replace=False)

    # too many columns
    if df.empty:
        return [{'data': {'id': 'TOO MANY COLUMNS', 'label': 'TOO MANY COLUMNS'}}]

    # drop the spaces and commas
    # df.to_csv(gnl.app.config["CURRENT_TEMP_FILE"], index=False)

    #ToDo: remove the drop na
    df_notna = df.dropna(axis=1, how='any')
    df_notna.to_csv(OUT_PATH, index=False)

    # start apriorie
    # ToDo: How do we adjust the parameter?
    a = apriori.Apriori(OUT_PATH, 0.25, -1)
    a.run()

    node_set, link_set, nodes, links = set(), set(), [], []
    for ar in a.true_associations:
        l, r = ar.split("=>")
        node_set.add(l)
        node_set.add(r)
        link_set.add((l, r))

    for node in node_set:
        nodes.append({"id": hash(node)//1000, 'label': node})
    for link in link_set:
        links.append({'data':{"source": hash(link[0])//1000, "target": hash(link[1])//1000}})

    if not nodes: nodes.append({'data': {"id": "NO ASSOCIATION RULE EXISTS"}})
    context["nodes"] = nodes
    context["links"] = links

    logger.info(context["nodes"])
    logger.info(context['links'])
    # return jsonify(context["nodes"] + context['links'])
    # return context["nodes"] + context['links']
    #return [{'data':{'id': 'role_id:1'}}, {'data':{'id': 'person_id:4'}}, {'data':{'source': 'person_id:4', 'target': 'role_id:1'}}]
    return context["nodes"] + context['links']

"""

            {'data': {'id': 'ca', 'label': 'Canada'}}, 
            {'data': {'id': 'on', 'label': 'Ontario'}}, 
            {'data': {'id': 'qc', 'label': 'Quebec'}},
            {'data': {'source': 'ca', 'target': 'on'}}, 
            {'data': {'source': 'ca', 'target': 'qc'}}

"""