#!/usr/bin/env python3
"""   
(c) Research Group CAMMA, University of Strasbourg, IHU Strasbourg, France
Website: http://camma.u-strasbg.fr
"""

import argparse
import cv2
import numpy as np
import os, sys
from time import time
import pandas as pd
from model import build_model, preprocess

class Inference:
    def __init__(self, ckpt_path, in_video_path, out_video_path, out_text_path, transform_type, kernel_size=20):
        self.in_video_path = in_video_path
        self.out_video_path = out_video_path
        self.out_text_path = out_text_path
        self.ckpt_path = ckpt_path
        self.kernel_size = kernel_size
        self.transform_type = transform_type

        self.status      = {'eta':None, 'percents':None}
        self.stop      = False
        
    def run(self):
        
        if self.out_video_path is None and self.out_text_path is None:
            return
        
        if not isinstance(self.transform_type, str) or self.transform_type.lower() not in ['solid', 'blur']:
            raise ValueError("transform_type value should be in either 'solid' or 'blur' but found {}".format(self.transform_type))
        self.transform_type = self.transform_type.lower()

        model = build_model()

        model.load_weights(self.ckpt_path)
        
        try:
            video_in = cv2.VideoCapture(self.in_video_path)
            assert(video_in.isOpened())
        except OSError:
            print("Could not open/read file:", self.in_video_path)
            sys.exit()

        width = int(video_in.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_in.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_nframes = int(video_in.get(cv2.CAP_PROP_FRAME_COUNT))
        k = int(self.kernel_size / 100 * width )
        blur_kernel = (k, k)

        size = (width, height)
        fps = video_in.get(cv2.CAP_PROP_FPS)

        video_out_name = os.path.basename(self.in_video_path).split('.')
        video_out_name = video_out_name[0]+'_oob.'+video_out_name[1]

        if self.out_video_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_out = cv2.VideoWriter(self.out_video_path, fourcc, fps, size)

        i = 0
        ok = True

        pred_history = []
        time_0 = time()

        ok, frame = video_in.read()

        while ok and not self.stop:
            
            # Execute model
            prediction = model(preprocess(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            pred_history.append(prediction.numpy()[0,0,0])

            oob = np.round(pred_history[-1])    # binarize prediction
            
            if self.out_video_path:
                if oob:
                    if self.transform_type == 'blur':
                        frame = cv2.blur(frame, blur_kernel)

                    else:# self.transform_type == 'solid':
                        mean_rgb = frame.mean(axis=0).mean(axis=0).astype(int)
                        for c in range(3):
                            frame[:,:,c]=mean_rgb[c]
                    
                video_out.write(frame)

            eta = (time()-time_0) / (i+1) * (video_nframes - i - 1) #ms
            eta = eta / 60 #minutes
            p_complete = int((i+1)/video_nframes*100)

            self.status      = {'eta':eta, 'percents':p_complete}

            # print progress
            if i > 0 and i % 1000 == 0:
                
                print("{}% -- ETA  {} minutes".format(p_complete, int(eta)))
            
            # read next frame
            ok, frame = video_in.read()
            i += 1

        video_in.release()

        if self.out_video_path:
            video_out.release()

        if self.out_text_path:
            pred_df = pd.DataFrame({'FRAME_ID':range(len(pred_history)), 'OOB':pred_history})
            pred_df.to_csv(self.out_text_path, index=False)


if __name__ == '__main__':

    def file_path(string):
        if os.path.isfile(string):
            return string
        else:
            raise FileNotFoundError(string)

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--ckpt_path", help="Path to the pretrained weights (h5 file)", type=file_path, default='./ckpt/oobnet_weights.h5')
    parser.add_argument("--video_in", help="Path to the input video", type=file_path)
    parser.add_argument("--video_out", help="Path to the output video", type=str, default=None)
    parser.add_argument("--text_out", help="Path to the output text file", type=str, default=None)
    parser.add_argument("--transform_type", help="Transformation to apply to out-of-body frames. Must be 'solid' or 'blur'", type=str, default="solid")
    parser.add_argument("--kernel_size", help="Blurring kernel size as percent of the width of the video", type=int, default=20)
    
    args = parser.parse_args()

    video_in = args.video_in 
    video_out = args.video_out
    text_out  = args.text_out
    ckpt = args.ckpt_path
    transform_type = args.transform_type
    kernel_size = args.kernel_size
    
    model_exec = Inference(ckpt_path=ckpt, 
                            in_video_path=video_in, 
                            out_video_path=video_out, 
                            out_text_path=text_out, 
                            transform_type=transform_type,
                            kernel_size=kernel_size)
    model_exec.run()