import pyautogui
import time
import cv2
from PIL import ImageGrab
import numpy as np
import imutils



def circle(mult):
    while True:
        pyautogui.moveRel(mult*1, mult*-1, duration=dur)
        pyautogui.moveRel(mult*1, 0, duration=dur)
        pyautogui.moveRel(mult*1, mult*1, duration=dur)
        pyautogui.moveRel(0, mult*1,duration=dur)
        pyautogui.moveRel(mult*-1, mult*1,duration=dur)
        pyautogui.moveRel(mult*-1, 0,duration=dur)
        pyautogui.moveRel(mult*-1, mult*-1,duration=dur)
        pyautogui.moveRel(0, mult*-1,duration=dur)

def hough(img):
        #resized = imutils.resize(img, width=1000)
    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img_gray = cv2.GaussianBlur(img_gray, (7, 7), 0)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1.1, minDist=15,
                     param1=50, param2=18, minRadius=1, maxRadius=22)

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            dist = distFrom(x, y)
            
            if(dist < 20000 and dist > 10000):
                pyautogui.moveTo(x+50, y+100, duration=0)
                #drawCirc(x, y, r)


def distFrom(x,y):
    centrex = 455
    centrey = 400
    return (((x - centrex)*(x-centrex)) + ((y-centrey)*(y-centrey)))
            
def drawCirc(x, y, r):
    cv2.circle(img, (x, y), r, (0, 255, 255), 4)
    cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            # show the output image
    cv2.imshow("output", img)
    cv2.waitKey(1)

def find(needle_img, haystack_img, threshold=0.5, debug_mode=None,
        method=cv2.TM_CCOEFF_NORMED):
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]
    # run the OpenCV algorithm
    result = cv2.matchTemplate(haystack_img, needle_img, method)

    # Get the all the positions from the match result that exceed our threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    #print(locations)

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        # Add every box to the list twice in order to retain single (non-overlapping) boxes
        rectangles.append(rect)
        rectangles.append(rect)

    # Stolen from: https://github.com/learncodebygaming/opencv_tutorials/tree/master/005_real_time
    # Apply group rectangles.
    # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
    # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
    # in the result. I've set eps to 0.5, which is:
    # "Relative difference between sides of the rectangles to merge them into a group."
    rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

    points = []
    if len(rectangles):
        #print('Found needle.')

        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:

            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))

            if debug_mode == 'rectangles':
                # Determine the box position
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                cv2.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                            lineType=line_type, thickness=2)
            elif debug_mode == 'points':
                cv2.drawMarker(haystack_img, (center_x, center_y), 
                            color=marker_color, markerType=marker_type, 
                            markerSize=40, thickness=2)

    #if debug_mode:
        #cv2.imshow('Matches', haystack_img)
        #cv.waitKey()
        #cv.imwrite('result_click_point.jpg', haystack_img)

    return haystack_img, points

def getScr():
    img = ImageGrab.grab(bbox=(50, 100,960,900))
    #910x 800
    # make image C_CONTIGUOUS to avoid errors that look like:
    #   File ... in draw_rectangles
    #   TypeError: an integer is required (got type tuple)
    # see the discussion here:
    # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
    img = np.ascontiguousarray(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img

def toGray(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img_gray = cv2.GaussianBlur(img_gray, (7, 7), 0)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

def closestPoint(points):

    smolPoint = 10000
    clP = (0,0)
    for point in points:
        #point = np.round(point).astype("int")
        p = distFrom(point[0],point[1])
        if p < smolPoint and p > 100:
            smolPoint = p
            clP = (point[0],point[1])
            #print(p)
    return clP

def findSnek(img):
    midwidth = int(img.shape[1]/2)
    midheight = int(img.shape[0]/2)
    img = img[midwidth-100:midwidth+100, midheight-100:midheight+100]

    imgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours, thresh

try:
    midwidth = int(getScr().shape[1]/2)
    midheight = int(getScr().shape[0]/2)
    #pyautogui.moveTo(460, 510, duration=0.25)
    #circle(mult=100) 
    loop_time = time.time()
    needle = cv2.imread("blob.png",cv2.IMREAD_UNCHANGED)
    while True:
        ogimg = getScr()
        cont, thresh = findSnek(ogimg)
        img, points = find(needle, ogimg,0.65,debug_mode='rectangles')
        cv2.drawContours(img, cont, -1, (0,255,0), 3)
        clp = closestPoint(points)
        if (clp != (0, 0)):
            # _pause defaults to true, creates large slowdown
            pyautogui.moveTo(clp[0]+50, clp[1]+100, _pause=False)
            marker_color = (255, 0, 255)
            marker_type = cv2.MARKER_CROSS

            cv2.drawMarker(img, (clp[0],clp[1]), 
                           color=marker_color, markerType=marker_type, 
                           markerSize=40, thickness=2)
        else:
            pyautogui.moveTo(midwidth, midheight, _pause=False) 
            # _pause defaults to true, creates large slowdown
        
        print('FPS {}'.format(1 / (time.time() - loop_time)))
        loop_time = time.time()
        cv2.imshow("out", img)
        cv2.moveWindow("out", 950,20)
        cv2.imshow("out2", thresh)
        cv2.moveWindow("out2", 950,200)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
except KeyboardInterrupt:
    print('done')