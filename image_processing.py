import glob
import cv2 as cv
import numpy as np


def BGR2HSV(bgrimg):
    HSVimg = np.empty(bgrimg.shape, np.uint16)
    for r in range(HSVimg.shape[0]):
        for c in range(HSVimg.shape[1]):

            Blue = int(bgrimg[r][c][0])
            Green = int(bgrimg[r][c][1])
            Red = int(bgrimg[r][c][2])

            Max = max(Blue,Green,Red)
            Min = min(Blue,Green,Red)

            # value V
            value = Max

            #Calculate Saturation. Saturation is 0 if red,green, blue are all 0
            saturation = int(255*((Max-Min)/Max)) if (Max!=0) else 0

            if saturation == 0:
                hue=361
            else:
                delta=Max-Min #determine hue

                if Red==Max:
                    hue=(Green-Blue)/delta #Resultting color is between yellow and magenta

                elif Green==Max:
                    hue=2+(Blue-Red)/delta #Resulting color is between cyan and yellow

                elif Blue==Max:
                    hue=4+(Red-Green)/delta #Resulting color is between magenta and cyan

                hue*=60 #convert hue to degree

                if hue<0:
                    hue+=360 #make sure hue is nonnegative

            HSVimg[r,c] = np.array([hue,saturation,value])

    return HSVimg


def yellow_mask(HSVimg):
    yellowMask = np.zeros((HSVimg.shape[0], HSVimg.shape[1]), np.uint8)

    for r in range(yellowMask.shape[0]):
        for c in range(yellowMask.shape[1]):

            hue = int(HSVimg[r][c][0])
            saturation = int(HSVimg[r][c][1])
            value = int(HSVimg[r][c][2])

            #ignore pixels whose saturation and/or value are below 50
            if value>50 and saturation>35:
                #select yellow hue
                if hue>=50 and hue<=62:
                    yellowMask[r,c] = 255

    return yellowMask


def green_mask(HSVimg):
    greenMask = np.zeros((HSVimg.shape[0], HSVimg.shape[1]), np.uint8)
    for r in range(greenMask.shape[0]):
        for c in range(greenMask.shape[1]):

            hue = int(HSVimg[r][c][0])
            saturation = int(HSVimg[r][c][1])
            value = int(HSVimg[r][c][2])

            #ignore pixels whose saturation and/or value are below 50
            if(value>50 and saturation>50):
                #select green hue
                if (hue>75 and hue<150):
                    greenMask[r,c] = 255

    return greenMask


def compute_HS_histogram(HSVimg):
    #make 45 bins
    histogram = np.zeros([9,5], np.double)

    sum = 0

    for r in range(HSVimg.shape[0]):
        for c in range(HSVimg.shape[1]):

            hue = HSVimg[r][c][0]
            saturation = HSVimg[r][c][1]
            value = HSVimg[r][c][2]

            #ignore all pixels with saturation below 50, too low, closer to white pixels
            #ignore all pixels with value below 50, closer to black pixels
            if value>50 and saturation>50:
                #update sum
                sum += 1

                if ((saturation-50)//41 == 5):
                    histogram[hue//40][4] += 1

                else:
                    histogram[hue//40][(saturation-50)//41] += 1

    #normalize this histogram
    histogram = np.reshape(histogram, 45)

    for i in range(len(histogram)):
        histogram[i] /= sum

    return histogram


def L1(HISimg1, HISimg2):

    return sum(abs(HISimg1-HISimg2))


def L2(HISimg1, HISimg2):

    return (sum((HISimg1-HISimg2)**2))**0.5


def nn1(listOfImg, distanceFunc='L1'):
    #set first image as key image to compare
    keyImg = listOfImg[0]
    key_img = cv.imread(keyImg)
    keyHSVimg = BGR2HSV(key_img)
    keyHistogramImg = compute_HS_histogram(keyHSVimg)


    least=None
    least_img=''

    for i in range(1, len(listOfImg)):
        #read, convert to HSV and convert to histogram
        img = cv.imread(listOfImg[i])
        newHSVimg = BGR2HSV(img)
        histogramImg = compute_HS_histogram(newHSVimg)

        #if input dist is equal to L1 do L1 function
        #if input dist is equal to L2 do L2 function
        distance=L2(keyHistogramImg, histogramImg) if distanceFunc=='L2' else L1(keyHistogramImg, histogramImg)


        if least == None:
            least = distance
            least_img = listOfImg[i]

        elif distance<least:
            least = distance
            least_img = listOfImg[i]

    return keyImg, least_img



filelist = glob.glob('example-images/*.jpg')

listoflists = []

for i in range(len(filelist)):
    listoflists.append(filelist.copy()) # make a copy of the list of names and append it
    save = filelist[0]
    filelist.remove(filelist[0])
    filelist.append(save)            # these 3 lines move the first file name to the end
                                     # which makes the list have a different first element

# listoflists now contains n versions of the filelist with
# a different file name as the first element (to act as the key)

for i in range(len(listoflists)):
    #debug code to make sure the lists really had a different first element
    print("list", i)
    for j in range(len(listoflists[i])):
        print(listoflists[i][j])
    keyimgname, matchimgname = nn1(listoflists[i], 'L1')
    keyimg = cv.imread(keyimgname)
    matchimg = cv.imread(matchimgname)
    cv.imshow('key image', keyimg)
    cv.imshow('match image', matchimg)
    cv.waitKey(0)
    cv.destroyAllWindows()
