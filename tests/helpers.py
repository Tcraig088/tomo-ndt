from  datetime import datetime
import os 
import pandas as pd
import time 
import numpy as np
import shutil

def define_save_dir():
    todays_date = datetime.today().strftime('%Y-%m-%d')
    path = os.path.join(os.getcwd(), "data")
    run = 0
    while os.path.exists(path):
        run += 1
        path = os.path.join(os.getcwd(), "data", "test_run_" + todays_date + "_" + str(run))
    os.mkdir(path)
    os.mkdir(os.path.join(path, "data"))

def get_save_dir():
    todays_date = datetime.today().strftime('%Y-%m-%d')
    path = os.path.join(os.getcwd(), "data")
    run = 0
    while os.path.exists(path):
        run += 1
        path = os.path.join(os.getcwd(), "data", "test_run_" + todays_date + "_" + str(run))
    run -= 1
    path = os.path.join(os.getcwd(), "data", "test_run_" + todays_date + "_" + str(run))
    pandas_path = os.path.join(path, "test_times.csv")
    if not os.path.exists(pandas_path):
        df = pd.DataFrame(columns=['test', 'comment', 'time'])
        df.to_csv(pandas_path, index=False)
    data_path = os.path.join(path, "data")
    return path, pandas_path, data_path

def refresh_subdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    
def get_times_angles():
    angle_range = np.radians(140)
    times = np.linspace(1, 30, 30)
    gr = (1+np.sqrt(5))/2
    angles = np.degrees(((times*gr*angle_range) % angle_range)-(angle_range/2))
    return times, angles

def copy_file(src, dest ):
    if os.path.isfile(src):
        os.remove(dest)
    shutil.copy(src, dest)

def update_data_path(path, file, new_name):
    new_path = os.path.join(path, new_name)
    shutil.copy(file, new_path)

def get_datapath_objs(path):
    files = os.listdir(path)
    files = [os.path.join(path, f) for f in files]
    return files

class EvalTimer():
    def __init__(self,pandas_path):
        self.pandas_path = pandas_path
        self.df = pd.read_csv(self.pandas_path)

    def start(self):
        self._start = time.time()
        self.new = True

    def end(self, name, comment, divisor=1):
        if self.new:
            self._end = time.time() - self._start
            self.new = False
        data = {'test': [name], 'comment': [comment], 'time': [self._end/divisor]}
        self.df = pd.concat([self.df, pd.DataFrame(data)])
        self.df.to_csv(self.pandas_path, index=False)
