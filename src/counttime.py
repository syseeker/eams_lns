

from datetime import datetime
from datetime import timedelta

a = datetime.strptime("2014-09-09 02:29:48.878572", "%Y-%m-%d %H:%M:%S.%f")   
b = a + timedelta(seconds=7200)
print a.time()
print b.time()


