
import uuid
import json
import sys
import requests
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

def makePoint(period, u):
    return {
        "layer": "hpl:bacnet:1",
        "uuid": u,
        "period":  {
            "seconds": period,
        }
    } 

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("{} <base url> <period>\n".format(sys.argv[0]))
        sys.exit(1)
    try:
        period = int(sys.argv[2])
    except:
        sys.stderr.write("invalid trending period: "+ sys.argv[2] + "\n")
        sys.exit(1)
    
    # FILE INPUT
    # create a variable to hold the file input dialog 
    root = Tk()
    
    # we don't want a full GUI, so keep the root window from appearing
    root.withdraw()
    
    # display the askopenfilename dialog window and set the result to filename
    root.filename = askopenfilename(title = "Select File Containing UUIDs", filetypes = (("Comma Separated Values", "*.csv"),("All Files","*.*")))

    try:
        print(f"Reading {root.filename}")
        uuidFile = pd.read_csv(root.filename, header=None)
    except Exception as e:
        sys.stderr.write(f"Fatal error importing file: {e}")
        sys.exit(1)
        
    for u in uuidFile[0]:
        try:
            uuid.UUID(u)
        except:
            sys.stderr.write("invalid uuid: "+ u + "\n")
            sys.exit(1)

    print ("Setting {} points to trend at {}s".format(len(uuidFile[0]), period))

    points = requests.post(sys.argv[1] + "/api/v1/point/points", data=json.dumps({
        "points": list(map(lambda u: makePoint(period, u), uuidFile[0]))
    }))
    print (points)
