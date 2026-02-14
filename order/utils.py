import time
import random

def generate_transaction_id():
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    return f'TX{timestamp}{random_num}'