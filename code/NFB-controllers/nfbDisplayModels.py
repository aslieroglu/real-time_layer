import numpy as np
from psychopy import visual
class timeseriesNFB(object):
    def __init__(self,
                window,
                volumes=1,
                baseline=1.0,
                nfb_scale=dict(lower=0.95,upper=1.05),
                block_def=dict(order=(),colour={})
                ):
        self.baseline = baseline
        self.win = window
        self.volumes = volumes
        #unpack the block structure
        self.block_colours = block_def['colour']
        self.stim_series = block_def["order"]
        self.scale = nfb_scale # values below lower of scale and above  upper of scale are clipped
        self.feedback_range = self.baseline * (self.scale['upper'] - self.scale['lower'])
        self.min_feedback = self.baseline * self.scale['lower']
        self.max_feedback = self.baseline * self.scale['upper']
        self.y_min = -0.75
        self.y_max = 0.75
        self.x_min = -0.75
        self.x_max = 0.75
        self.rect_w = (self.x_max - self.x_min)/self.volumes
        self.x_start = np.arange(self.volumes) * self.rect_w + self.x_min
        self.x_end = self.x_start + self.rect_w
        self.y_delta = (self.y_max - self.y_min)/self.feedback_range
        #self.y_base = baseline * self.scale['lower']
        self.y_base = self.y_min + self.y_delta * self.baseline * (1 - self.scale['lower'])
        self.n_blocks = 0
        self.feedback_hist = np.full(self.volumes,0.0)
        #self.feedback_hist[0] = self.y_min
        self.feedback_hist[0] = self.y_base
        self.lines = np.full(self.volumes, None)
        self.background = np.full(self.volumes, None)
        self.y_labels = np.full(4,None)
        self.bbox = visual.ShapeStim(self.win,
                                   lineColor='white',
                                   lineWidth=2,
                                   fillColor=None,
                                   closeShape=True,
                                   vertices=[[self.x_min,self.y_min],
                                             [self.x_min,self.y_max],
                                             [self.x_max,self.y_max],
                                             [self.x_max,self.y_min]],
                                   autoDraw=False
                                   )
        #prebuild the background blocks
        self.prebuild_background()
        #prebuild the feedback lines
        self.prebuild_lines()
        # prebuild the y labe;s
        #self.prebuild_labels()

    def prebuild_background(self):
        if len(self.stim_series) !=0 and self.block_colours:
            for idx in range(self.volumes):
                self.background[idx] = visual.ShapeStim(self.win,
                                           lineColor=None,
                                           lineWidth=0,
                                           fillColor=block_colours[self.stim_series[idx]],
                                           vertices=[[self.x_start[idx], self.y_min],
                                                     [self.x_start[idx], self.y_max],
                                                     [self.x_end[idx], self.y_max],
                                                     [self.x_end[idx], self.y_min]],
                                           autoDraw=False
                                           )
        else:
            print("Design structure not supplied to NFB stim constructor")

    def show_bounding_box(self):
        self.bbox.setAutoDraw(True)

    
    def show_block(self,block=[],first_block=False):            
        for idx in block:
            self.background[idx].setAutoDraw(True)

    def prebuild_lines(self):
        for idx in range(self.volumes):
            self.lines[idx] = visual.Line(self.win,
                                          start=[self.x_start[idx], 0],
                                          end=[self.x_end[idx], 0],
                                          lineColor='white',
                                          lineWidth=2,
                                          autoDraw=False
                                         )

    def show_feedback(self, vol_id, feedback):
        y_start = self.feedback_hist[vol_id]
        scaled_feedback = min(max(feedback - self.min_feedback,0),self.feedback_range)
        y_end = self.y_min + scaled_feedback * self.y_delta
        #y_end = scaled_feedback
        if vol_id < self.volumes - 1:
            self.feedback_hist[vol_id + 1] = y_end
        self.lines[vol_id].start += (0, y_start)
        self.lines[vol_id].end += (0, y_end)
        self.lines[vol_id].setAutoDraw(True)

    def prebuild_labels(self):
        labels = np.round(np.linspace(self.y_base, self.y_base*self.scale['upper']/self.scale['lower'], 4),2)
        y = np.linspace(self.y_min,self.y_max,4)
        x = self.x_min - 0.05
        for idx in range(4):
            self.y_labels[idx] = visual.TextStim(self.win,
                                                text=labels[idx],
                                                pos=(x,y[idx]),
                                                height=0.05,
                                                color='white',
                                                autoDraw=False
                                                )

    def reset(self):
        self.feedback_hist = np.full(self.volumes, 0.0)
        self.feedback_hist[0] = self.y_base
        self.bbox.setAutoDraw(False)
        #for idx in range(4):
        #    self.y_labels[idx].setAutoDraw(False)
        for idx in range(self.volumes):
            self.background[idx].setAutoDraw(False)
            self.lines[idx].setAutoDraw(False)
            self.lines[idx].start = [self.x_start[idx], 0]
            self.lines[idx].end = [self.x_end[idx], 0]




