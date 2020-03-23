from google.cloud import monitoring_v3      

import argparse
import os
import pprint
import time
import uuid
from datetime import datetime
import json
from matplotlib import pyplot as plt

project_id = 'ecas-2019'

# [START monitoring_read_timeseries_reduce]
client = monitoring_v3.MetricServiceClient()
project_name = client.project_path(project_id)
interval = monitoring_v3.types.TimeInterval()
now = time.time()
interval.end_time.seconds = int(now)
interval.start_time.seconds = int(now - (6*7*24*60*60))  # 6 weeks before
aggregation = monitoring_v3.types.Aggregation()
aggregation.alignment_period.seconds = 60  # 20 minutes
aggregation.per_series_aligner = (
    monitoring_v3.enums.Aggregation.Aligner.ALIGN_SUM)
aggregation.cross_series_reducer = (
    monitoring_v3.enums.Aggregation.Reducer.REDUCE_SUM)

# get reserved cores
metrics = ['cpu/reserved_cores', 'uptime', 'cpu/usage_time', 'network/sent_bytes_count']
date = datetime.fromtimestamp(interval.end_time.seconds)

for metric in metrics:
    print ('Saving to file data from project: %s, metric: %s, date: %s  ...' % ( project_id, metric, date))
    results = client.list_time_series(
        project_name,
        'metric.type = "compute.googleapis.com/instance/%s" AND resource.type = "gce_instance"' % (metric),
        interval,
        monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL,
        aggregation)
    t = []
    v = []    
    for result in results:
        for point in result.points:
            t.append(point.interval.start_time.seconds)
            v.append(point.value.double_value)
    data = {'times': t, 'values': [float(val) for val in v]}
    
    filename = 'list_time_series_%s_%s_%s' % (metric.replace('/','_'), project_id, date)
    with open(filename+'.json', 'w') as f:
        json.dump(data, f)
    plt.figure(figsize=(10,6))
    plt.plot(t, v)
    plt.savefig(filename+'.png')
