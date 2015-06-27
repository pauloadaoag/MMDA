import json
import urllib2
import datetime
import time
import collections
TrafficSample = collections.namedtuple('TrafficSample', ['segment_id', 'direction', 'road_status', 'update_time', 'aa', 'alert_counts', 'ac', 'alert_text' ])

#Comment

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

for point in traffic_points:
    node_info = point[0]
    node_north = point[1]
    node_south = point[2]
    (road_id, node_id, intersecting_node_id, node_type_arr, is_service_node, related_node_id, is_major_intersection) = node_info
    (road_status, update_time, aa, alert_counts, ac) = node_north
    n_sample = TrafficSample(node_id, 'N', road_status, update_time, aa, alert_counts, ac, '')
    (road_status, update_time, aa, alert_counts, ac) = node_south
    s_sample = TrafficSample(node_id, 'S', road_status, update_time, aa, alert_counts, ac, '')

response = urllib2.urlopen(ADVISORIES_ENDPOINT)
advisories_list = json.load(response)
advisories = {}
# SegmentNames[142]
advisories = {}
for advisory in advisories_list:
    segment_id = advisory[1]
    info = advisory[2]
    print info



sample = traffic_points[2]
node_info = sample[0]
node_north = sample[1]
node_south = sample[2]




#is_major_intersection = Intersection between two roads
(road_id, node_id, intersecting_node_id, node_type_arr, is_service_node, related_node_id, is_major_intersection) = node_info
(road_status, update_time, aa, alert_counts, ac) = node_north
(node_type, node_type_idx, node_type_com) = node_type_arr

a = time.strptime(update_time, "%Y%m%d%H%M%S")
