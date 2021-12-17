import unittest
import datetime as dt
from arbitrade import __main__

class TestMain(unittest.TestCase):
    pass

if __name__ == "__main__":
    tm = dt.datetime.utcnow().strftime("%Y%m%d %H:%M:%S")
    __main__.main({"tm":tm, "assets":"ALL"})
    #unittest.main()