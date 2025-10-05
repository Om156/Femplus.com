from typing import Dict, Any, List
from datetime import datetime
from itertools import count

######### existing user and readings ##############
users_db: Dict[str, Dict[str, Any]] = users_db if 'users_db' in globals() else {}
sensor_data_db: List[Dict[str, Any]] = sensor_data_db if 'sensor_data_db' in globals() else []

############# New readings: cycles storage ##############
cycles_db: List[Dict[str, Any]] = cycles_db if 'cycles_db' in globals() else []


#### Sensor ID management ######
_next_sensor_id = globals().get("_next_sensor_id", count(1))
_next_cycle_id  = globals().get("_next_cycle_id",  count(1))

def next_sensor_id() -> int:
    return next(_next_sensor_id)

def next_cycle_id() -> int:
    return next(_next_cycle_id)
