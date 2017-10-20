# -*- coding: utf-8 -*-
import pandas as pd
from flask import Blueprint, current_app, jsonify, json, request, Response
from flask_cors import CORS, cross_origin
from geopy.distance import great_circle

api = Blueprint('api', __name__)
#  Wrap the API in the CORS module to allow x-domain access for the dual servers
CORS(api)


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)
    

@api.route('/search', methods=['GET'])
@cross_origin()
def search():

    #  Create a preferences object by reading the request arguments and converting using an eval functions
    preferences = eval(request.args.keys()[0])
    #  Create tuple var of current location for use with the great circle function
    location = (preferences['position']['lat'], preferences['position']['lng'])

    #  Read static csv files and convert to dataframes
    products = pd.read_csv('data/products.csv')
    shops = pd.read_csv('data/shops.csv')
    tagging = pd.read_csv('data/taggings.csv')
    tags = pd.read_csv('data/tags.csv', index_col='tag', header=0)

    #  If tag preferences filter tags data frame or complile dataframe as all tags
    if preferences['tags']:
        active_tags = tags.filter(items=preferences['tags'], axis=0).rename(columns={'id': 'tag_id'})
    else:
        active_tags = tags.rename(columns={'id': 'tag_id'})

    #  merge tag dataframe with tagging reference dataframe to allow merge with Shops dataframe
    mergedTags = pd.merge(active_tags, tagging, on='tag_id', how='inner')
    mergedShops = pd.merge(mergedTags, shops, left_on='shop_id', right_on='id', how='inner')

    #  convert shops dataframe lat and lng fields to tuple and use great circle function to convert to distance and filter based on preferences
    mergedShops = mergedShops[pd.Series([great_circle(
        location, (
            mergedShops['lat'][shop],
            mergedShops['lng'][shop]
            )).meters for shop in range(mergedShops.shape[0])]) < preferences['radius']]
    #  merge products dataframe with shops dataframe dataframe 
    mergedProducts = pd.merge(mergedShops, products, left_on='id_y', right_on='shop_id', how='inner')
    #  remove zero quantity and sort dataframe against popularity
    mergedProducts = mergedProducts[mergedProducts['quantity'] != 0].sort_values('popularity', ascending=False)[:preferences['count']]

    #  return the data to the client
    return jsonify({'products': [data['title'] for index,data in mergedProducts.iterrows()]})
