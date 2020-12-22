import json
import os
import datetime 

from influxdb import InfluxDBClient


def handle(req):
    """Handles the data published to the temperature topic
    Args:
        req (str): mqtt message body 
    """
    data = json.loads(req)

    clinic_name = os.getenv("clinic_name")

    # Get influxdb local host and credentials
    influx_host_local = os.getenv("influx_host")
    influx_port_local = os.getenv("influx_port")
    influx_db_local = get_file("/var/openfaas/secrets/influxdb-database")
    influx_user_local = get_file("/var/openfaas/secrets/influxdb-username")
    influx_pass_local = get_file("/var/openfaas/secrets/influxdb-password")
    
    # Get influxdb cloud host and credentials
    influx_host_cloud = os.getenv("influx_cloud_host")
    influx_port_cloud = os.getenv("influx_cloud_port")
    influx_db_cloud = get_file("/var/openfaas/secrets/influxdb-cloud-database")
    influx_user_cloud = get_file("/var/openfaas/secrets/influxdb-cloud-username")
    influx_pass_cloud = get_file("/var/openfaas/secrets/influxdb-cloud-password")
    
    
    # Get current time formatted for influxDB
    current_time= datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Create the influxdb local client
    influx_client_local = InfluxDBClient(influx_host_local, influx_port_local, influx_user_local, influx_pass_local, influx_db_local)
    
    # Count the ammount of blood-oxygen alarms thrown in the last 30 minutes
    rs=client.query('SELECT count("meassured-value") FROM "alarm" WHERE "type" = \'blood-oxygen\' AND time > \'{}\' - 30m'.format(current_time))
    points=list(rs.get_points())
    blood_oxygen_value=points[0]["count"]
    
    # Count the ammount of temperature alarms thrown in the last 30 minutes
    rs=client.query('SELECT count("meassured-value") FROM "alarm" WHERE "type" = \'temperature\' AND time > \'{}\' - 30m'.format(current_time))
    points=list(rs.get_points())
    temperature_value=points[0]["count"]
    
    # Count the ammount of heartbeat alarms thrown in the last 30 minutes
    rs=client.query('SELECT count("meassured-value") FROM "alarm" WHERE "type" = \'heartbeat\' AND time > \'{}\' - 30m'.format(current_time))
    points=list(rs.get_points())
    heartbeat_value=points[0]["count"]
    
    # Create the influxdb cloud aggregation client
    influx_client_cloud = InfluxDBClient(influx_host_cloud, influx_port_cloud, influx_user_cloud, influx_pass_cloud, influx_db_cloud)
    
    # Finally, write the point to the temperature measurement
    res=influx_client.write_points([createAggregationPoint(current_time,clinic_name,blood_oxygen_value,temperature_value,heartbeat_value)])

    return json.dumps({"heart":heartbeat_value,"temperature":temperature_value,"blood_oxygen":blood_oxygen_value})

def get_file(path):
    v = ""
    with open(path) as f:
        v = f.read()
        f.close()
    return v.strip()

def createAggregationPoint(current_time,clinic_name,blood_oxygen_count,temperature_count,heartbeat_count):
    return {
        "measurement":"aggregation",
        "tags":{},
        "time":current_time,
        "fields" :{
            "clinic-name": clinic_name,
            "blood_oxygen_count": blood_oxygen_count,
            "temperature_count": temperature_count,
            "heartbeat_count": heartbeat_count
        }
    }