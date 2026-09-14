import os
import sys
import time
import urllib.request

# Suppress the urllib3 warning
import warnings
warnings.filterwarnings("ignore")

import google.genai as genai

# Print available model methods
c = genai.Client(api_key="placeholder")
methods = [m for m in dir(c.models) if not m.startswith('_')]
print("Available models methods:", methods)
