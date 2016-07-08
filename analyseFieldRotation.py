#!/usr/local/python/bin/python
"""
Code to investigate the field rotation spotted between
the PRESURVEY images and the the AG reference image

Process:
    1. Start by getting the reference image - are they solved?
    2. Get a sample of images throughout the season
    3. Display them to compare them for rotation
    4. Check the WCS solutions for rotation

Questions:
    1. Have the reference images been solved with WCS fit?
    2. Do we have a list of apertures from the Transparency code?
    3. Do the findings match up with the Transparency issue?
"""
import pymysql
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import astropy.units as u


# connect to the different dbs
ops_db = pymysql.connect(host='ngtsdb', db='ngts_ops')
pipe_db = pymysql.connect(host='ngtsdb', db='ngts_pipe')
field_id = 'NG2100-4748'

ops_qry = """SELECT
    a.action_id, night
    FROM
    action_list AS a
    INNER JOIN action_args AS aa
    ON a.action_id=aa.action_id
    WHERE
    arg_key='field' AND
    arg_value='{0:s}'""".format(field_id)
print(ops_qry)

action_ids, night = [], []
image_ids = defaultdict(list)
with ops_db.cursor() as ops_cur:
    ops_cur.execute(ops_qry)
    for row in ops_cur:
        action_ids.append(int(row[0]))
        night.append(Time(str(row[1]), format='iso', in_subfmt='date', scale='utc'))

print("Found {0:d} actions for {1:s}".format(len(action_ids), field_id))
# now loop over all the actions and get the image_ids and WCS info
for action in action_ids:
    image_qry = """SELECT
                image_id
                FROM
                raw_image_list
                WHERE
                action_id={0:d}
                ORDER BY image_id ASC""".format(action)
    with ops_db.cursor() as ops_cur:
        ops_cur.execute(image_qry)
        for row in ops_cur:
            image_ids[action].append(row[0])

