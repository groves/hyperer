# This is an autofixable error, so it has one format
import os

try:
    print("Hey")
# This isn't an autofixable error, so it has a different format
except:
    pass
