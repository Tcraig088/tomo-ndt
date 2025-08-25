
from tqdm import tqdm 
import logging
import time 
from datetime import timedelta

from qtpy.QtWidgets import QProgressBar, QHBoxLayout, QWidget, QLabel
from qtpy.QtCore import Signal, QObject

class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.elapsedtimewidget = QLabel('Elapsed Time: 0')
        self.bar = QProgressBar()
        self.remainingtimewidget = QLabel('Remaining Time: 0')
        
        self.layout = QHBoxLayout()

        self.layout.addWidget(self.elapsedtimewidget)
        self.layout.addWidget(self.bar)
        self.layout.addWidget(self.remainingtimewidget)

        self.setLayout(self.layout)
        self.show()
        
    def setMaximum(self, value):
        self.bar.setMaximum(value)
        
    def setValue(self, value):
        self.bar.setValue(value)
        
    def close(self):
        self.bar.close()
        
    def setTimes(self, elapsed, remaining):
        self.elapsedtimewidget.setText(f'Elapsed Time: {str(elapsed)}')
        self.remainingtimewidget.setText(f'Remaining Time: {str(remaining)}')
        
class ProgressBarGlobal(QObject):
    _instance = None
    isActiveChanged = Signal(bool)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.isnapari = False
            cls._instance._isactive = False
            cls._instance.time_elapsed = 0
            cls._instance.time_remaining = 0
            cls._instance.time_start = 0
            cls._instance.current_step = 0
            cls._instance.maximum_step = 0
            cls._instance.ismulti = False

        return cls._instance

    @property 
    def isactive(self):
        return self._isactive
    
    @isactive.setter 
    def isactive(self, value):
        if self._isactive != value:
            self._isactive = value
            self.isActiveChanged.emit(value)
        
    def setup(self, total):
        if self.isactive:
            self.maximum_step = total*self.maximum_step
            self.ismulti = True
            self.logbar.total = self.maximum_step
            self.logbar.refresh()
            if self.isnapari:
                self.qtbar.setMaximum(self.maximum_step)
        else:
            self.curent_step = 0
            self.time_elapsed  = 0
            self.time_remaining = 0
            self.time_start =  time.time()
            self.ismulti = False
            self.logbar = tqdm(total=total)
            if self.isnapari:
                self.qtbar = ProgressWidget()
                self.qtbar.setMaximum(total)
            self.isactive = True
                
    def update(self, isouterloop=False):
        activity_index = (self.ismulti, isouterloop)
        match activity_index:
            case (True, True):
                self._check_finished()
            case (False, True):
                self._update_progress()
                self._check_finished()
            case (True, False):
                self._update_progress()
            case (False, False):
                self._update_progress()
                self._check_finished()
            case _:
                raise Exception('Error occured in the progress bar values')

    
    def _update_progress(self):
        self.current_step += 1
        currenttime = time.time()
        self.time_elapsed = timedelta(seconds=int(currenttime - self.time_start))
        timerstep = (currenttime - self.time_start)/self.current_step
        self.time_remaining = timedelta(seconds=int(timerstep*(self.maximum_step - self.current_step)))
        
        self.logbar.update(self.current_step - self.logbar.n)
        if self.isnapari:
            self.qtbar.setValue(self.current_step)
            self.qtbar.setTimes(self.time_elapsed, self.time_remaining)
            
        logging.info(f'Time Elapsed: {str(self.time_elapsed)} Estimated Time Remaining: {str(self.time_remaining)}')
        
        
    def _check_finished(self):
        if self.current_step == self.maximum_step:
            self.isactive = False
            self.ismulti = False
            self.current_step = 0
            self.maximum_step = 0
            self.time_elapsed = 0
            self.time_remaining = 0
            self.time_start = 0
            self.logbar.close()
            if self.isnapari:
                self.qtbar.close()
            
progressbar = ProgressBarGlobal()