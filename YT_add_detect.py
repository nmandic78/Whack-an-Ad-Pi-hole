import cv2 as cv
import pandas as pd
import time
from datetime import datetime


def save_log(ad_log):
    df_ad_log = pd.DataFrame(ad_log, columns=['timestamp'])
    df_ad_log.set_index(['timestamp'], inplace=True)
    df_ad_log.to_csv(r'D:\RASPBERRY PI\DATA\cam_logged_ads_1.csv', index=True, header=True)     # save results to CSV


start_time = 0
ad_log = []
i = 0

width, height = 800, 600
cap = cv.VideoCapture("rtsp://192.168.0.18:8554/mjpeg/1")   # Put right IP where your ESP32-CAM (or other cam) serves video stream
cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
# cap.set(cv.CAP_PROP_POS_FRAMES, 50)

# Youtube can show >1 version of SKIP AD or other banners, so need to check them all (here only 2 versions are matched)
template = cv.imread('skip_ad_1.jpg', cv.COLOR_BGR2GRAY)
template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

template2 = cv.imread('skip_ads_2.jpg', cv.COLOR_BGR2GRAY)
template_gray2 = cv.cvtColor(template2, cv.COLOR_BGR2GRAY)

while(True):
    try:
        _, frame = cap.read()
        cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        img_gray = cv.cvtColor(cv2image, cv.COLOR_BGR2GRAY)

        # Template Matching
        # Possible methods: cv.TM_CCOEFF, cv.TM_CCOEFF_NORMED, cv.TM_CCORR, cv.TM_CCORR_NORMED, cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED
        # Check min_val instead of max_val for cv.TM_SQDIFF and cv.TM_SQDIFF_NORMED
        res = cv.matchTemplate(img_gray, template_gray, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        res2 = cv.matchTemplate(img_gray, template_gray2, cv.TM_CCOEFF_NORMED)
        min_val2, max_val2, min_loc2, max_loc2 = cv.minMaxLoc(res2)

        passed_time = time.time() - start_time

        if (max_val > 0.8 or max_val2 > 0.8) and (passed_time > 40):    # passed_time > seconds to skip detections after last one
            start_time = time.time()
            ad_log.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # cv.imwrite(f'new_ad_detected_{i}.jpg', frame) # uncomment to save detected snaphots to check for false positives/tune treshold
            i += 1
            if i % 5 == 0:  # save log to csv after every 5th detection (in case script brake, or camera battery dies, or nuclear war)
                save_log(ad_log)

            print('********************** ADD DETECTED **************************')

        # Monitor video feed
        cv.imshow('frame', frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord('r'):     # press r to save frame to disk
            cv.imwrite(f'screen_rec_nr_{i}.jpg', frame)
        elif key == ord('q'):   # press q to stop monitoring
            break
    except Exception as e:
        print(e)
        cap.release()   # dont quit, try again
        cap = cv.VideoCapture("rtsp://192.168.0.18:8554/mjpeg/1")
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)

save_log(ad_log)    # save CSV after recording stop
