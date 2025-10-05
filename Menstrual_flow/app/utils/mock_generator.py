import random
from datetime import datetime, timedelta

def generate_daily_flow():
    """Return random flow amount in ml for a day (0 = no flow)."""
    return random.randint(0, 80)

def generate_cycle_data(user_email, days=28):
    """Generate one cycle of daily flows, each reading with timestamp and user_email."""
    cycle = []
    start_date = datetime.now() - timedelta(days=days)
    for i in range(days):
        day_data = {
            "timestamp": (start_date + timedelta(days=i)),
            "flow_ml": generate_daily_flow(),
            "user_email": user_email
        }
        cycle.append(day_data)
    return cycle

def generate_multiple_cycles(user_email, num_cycles=3):
    """Generate multiple cycles for a user, fully Pydantic-ready."""
    all_cycles = []
    for _ in range(num_cycles):
        cycle_length = random.randint(25, 32)
        cycle_data = generate_cycle_data(user_email, cycle_length)
        all_cycles.append(cycle_data)
    return all_cycles
