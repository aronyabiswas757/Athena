
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import learner

print("Testing Learner Reflection...")
result = learner.reflect()
print(f"Reflection Result: {result}")
