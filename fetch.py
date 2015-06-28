#!/usr/bin/python

import json
import urllib2
import time
import collections
import ConfigParser
import MySQLdb as db
import os

config = ConfigParser.RawConfigParser()
config_filename = os.path.join(os.getcwd(), 'config.cfg')
config.read(config_filename)

db_host = config.get('mysql', 'host')
db_user = config.get('mysql', 'uname')
db_pass = config.get('mysql', 'pw')
db_name = config.get('mysql', 'db_name')

sample_time = int(time.time())

con = db.connect(db_host, db_user, db_pass, db_name)
cursor = con.cursor()


def save_run_to_db(db_cursor, sampling_time):
    sql_text = """
        INSERT INTO sampling_runs (sample_time) VALUES (%s)
    """
    db_cursor.execute(sql_text, (sampling_time,))
    return db_cursor.lastrowid

def update_run_with_end_time(db_cursor, run_id, end_time):
    sql_text = """
        UPDATE  sampling_runs set end_time = %s where id = %s
    """
    db_cursor.execute(sql_text, (end_time, run_id))

run_id = save_run_to_db(cursor, sample_time)


TrafficSample = collections.namedtuple('TrafficSample', [
    'segment_id',
    'direction',
    'road_status',
    'update_time',
    'aa',
    'alert_counts',
    'ac',
    'alert_text'])

ROADS = {
    1: "EDSA",
    2: "Q.AVE",
    3: "ESPANA",
    4: "C5",
    5: "ROXAS BLVD",
    6: "SLEX",
    7: "COMMONWEALTH",
    8: "ORTIGAS",
    9: "MARCOS HIWAY"
}
ROAD_STATUSES = {
    0: "NO INFO",
    1: "LIGHT",
    2: "LIGHT-MED",
    3: "MEDIUM",
    4: "MEDIUM-HEAVY",
    5: "HEAVY"
}
NODE_TYPES = {
    0: 'TERMINATION',
    1: 'ROAD',
    2: 'INTERSECTION'
}
TRAFFIC_ENDPOINT = 'http://mmdatraffic.interaksyon.com/data.traffic.status.php'
ADVISORIES_ENDPOINT = 'http://mmdatraffic.interaksyon.com/data.traffic.advisories.php'

response = urllib2.urlopen(TRAFFIC_ENDPOINT)
traffic_points = json.load(response)

response = urllib2.urlopen(ADVISORIES_ENDPOINT)
advisories_list = json.load(response)
advisories = {}
for advisory in advisories_list:
    segment_id = advisory[1]
    info = advisory[2]
    direction = 'NB'
    text = ''
    if type(info) is dict:
        direction = 'SB'
        text = str(info)
    elif type(info) is list:
        direction = 'NB'
        text = str(info[0][0])
    if segment_id not in advisories:
        advisories[segment_id] = { 'NB': [], 'SB': []}
    advisories[segment_id][direction].append(text)


def mmda_time_to_timestamp(mmdatime):
    a = time.strptime(mmdatime, "%Y%m%d%H%M%S")
    return time.mktime(a)


def save_to_db(db_cursor, traffic_sample, run_id):
    sql_text = """
        INSERT INTO traffic_samples
            (segment_id, direction, road_status, update_time, run_id, aa, alert_counts, ac, alert_text)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db_cursor.execute(sql_text,(traffic_sample.segment_id, traffic_sample.direction,
        traffic_sample.road_status, mmda_time_to_timestamp(traffic_sample.update_time), run_id, traffic_sample.aa,
        traffic_sample.alert_counts, traffic_sample.ac, traffic_sample.alert_text))


for point in traffic_points:
    node_info = point[0]
    node_north = point[1]
    node_south = point[2]
    (road_id, node_id, intersecting_node_id, node_type_arr, is_service_node, related_node_id, is_major_intersection) = node_info
    (road_status, update_time, aa, alert_counts, ac) = node_north
    north_alert_text = ''
    south_alert_text = ''
    if node_id in advisories:
        alerts = advisories[node_id]
        if len(alerts['NB']) > 0:
            north_alert_text = " | ".join(alerts['NB'])
        if len(alerts['SB']) > 0:
            south_alert_text = " | ".join(alerts['SB'])
    n_sample = TrafficSample(node_id, 'N', road_status, update_time, aa, alert_counts, ac, north_alert_text)
    save_to_db(cursor, n_sample, run_id)
    (road_status, update_time, aa, alert_counts, ac) = node_south
    s_sample = TrafficSample(node_id, 'S', road_status, update_time, aa, alert_counts, ac, south_alert_text)
    save_to_db(cursor, s_sample, run_id)

end_time = int(time.time())
update_run_with_end_time(cursor, run_id, end_time)

con.commit()
con.close()