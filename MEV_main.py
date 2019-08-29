import numpy as np
import pandas as pd
from imageio import imread as imread, imsave as imsave
import os


"""
This class gets an image and matching data (list of numbers) 
Process the data into sizes of pixels
Creates 7 images for each day in a week (the data) 
Each image for each day comes out different.

Every day we have 24 numbers represent populary in precision of an hour.
This algorithm translates those numbers to pixels sixez, from top to buttom of the image.
"""
class Artwork:  

	# jpg image and the specific day data
    def __init__(self,in_path,out_path,numbers,resolution,strips =24):
        self.jpg_path = in_path
        self.jpg_out_path = out_path
        self.numbers = numbers
        self.strips = strips
        self.image = imread(self.jpg_path).astype(np.float64)/255
        self.H = self.image.shape[0]
        self.W = self.image.shape[1]
        self.factor = 10 * resolution
        self.levels = 10
	
	# saves the result on computer
    def start(self):
        self.make_image()
        self.image = (self.image * 255).astype('uint8')
        imsave(self.jpg_out_path, self.image)
        print(self.jpg_out_path, "Done!")
	
	# algorithm for making the rows and pixels
    def make_image(self):
        a = int(self.H/self.strips)
        self.rows = [a]*self.strips
        remainder = self.H - a*self.strips
        for i in range(remainder):
            self.rows[i] += 1
        max = self.numbers.max()
        min = self.numbers.min()

        self.numbers = -self.numbers + max + min

        gap = (max - min) / self.levels
        a = np.arange(min,max+gap*2,gap)
        self.sizes = np.zeros((24,))
        for i in range(24):
            k = self.numbers[i]
            j = 0
            while k >= a[j]:
                j += 1
            self.sizes[i] = j
        self.sizes = np.array(self.sizes * self.factor, int)
        self.make_channel(0)
        self.make_channel(1)
        self.make_channel(2)
	
	# pixelate image according to instructions
    def make_channel(self,I):
        im = self.image[:, :,I]
        y = 0
        bounder = 0
        for i in range(len(self.rows)):  # 24
            x = 0
            size = self.sizes[i]
            bounder += self.rows[i]
            while (y + size < bounder):
                while (x + size < self.W):
                    A = im[y:y + size, x:x + size]
                    s = size * size
                    c = A.sum() / s
                    im[y:y + size, x:x + size] = c
                    x += size
                A = im[y:y + size, x:self.W]
                s = size * (self.W - x)
                c = A.sum() / s
                im[y:y + size, x:self.W] = c
                x = 0
                y += size
            while (x + size < self.W):
                A = im[y:bounder, x:x + size]
                s = (bounder - y) * size
                c = A.sum() / s
                im[y:bounder, x:x + size] = c
                x += size
            A = im[y:bounder, x:self.W]
            s = (bounder - y) * (self.W - x)
            c = A.sum() / s
            im[y:bounder, x:self.W] = c
            y = bounder
        self.image[:, :, I] = im


"""
this class takes data from google trends csv file
  
"""
class CSV_WEEK:

	# reads data of a week and stores it
    def __init__(self,path):
        pandas = pd.read_csv(path)
        V = np.array(pandas)[2:,1]
        D = np.array(pandas)[2:,0]
        self.n = len(V)   #len: 168 (7*24)
        self.dates = np.zeros((self.n, 3), int)
        self.values = np.zeros((self.n, 1), int)
        for i in range(self.n):
            d = D[i].split("T")[0].split("-")
            if V[i].isdigit() and len(d) == 3:
                    if d[0].isdigit() and d[1].isdigit() and d[2].isdigit():
                        self.dates[i] = [d[0], d[1], d[2]]
                        self.values[i] = V[i]

            else:
                print("problem with row number " + str(i + 4))
                exit()

				
def is_numeric(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False

				
				
				
def main():
    name = input("Artwork name: ")
    c = ""
    resolt = ""
    r = 1
    day = ""
    month = ""
    year = ""
    again = True
    d = input("For week press 1, For date press 2: ")
    if (d == "2"):
        c = input("Press the date ( 8.12.2018 ) :")
        date = c.split(".")
        if date[0].isdigit() and date[1].isdigit() and date[2].isdigit():
            day = int(date[0])
            month = int(date[1])
            year = int(date[2])
        else:
            print(c+" is not valid date, please type again date ( 3.1.2019 ) :")
            return
        resolt = input("Press resolution ( 1.1 ) :")
        if is_numeric(resolt):
            r = float(resolt)

    artwork_path = os.path.join(os.path.dirname(__file__), os.path.join("artworks", name))
    jpg_path = os.path.join(artwork_path, name + ".jpg")
    csv_path = os.path.join(artwork_path, name + ".csv")
    csv = CSV_WEEK(csv_path)
    out_path = os.path.join(artwork_path, name)

    if (d == "1"):
        j = 0
        works = []
        for i in range(csv.n):
            if (i+1)%24 == 0:
                day = str(csv.dates[i][2])+"."+str(csv.dates[i][1])+"."+str(csv.dates[i][0])
                jpg_out_path = out_path+"__"+day+"__r"+str(1)+"__.jpg"
                #reso.append(sum(csv.values[j:i+1])/24)
                t = Artwork(jpg_path,jpg_out_path,np.array(csv.values[j:i+1])[:,0],r)
                j = i+1
                works.append(t)

        for t in works:
            t.start()

    if (d == "2"):
        while again:
            j = 0
            works = []
            for i in range(csv.n):
                if (i + 1) % 24 == 0:
                    if day == csv.dates[i][2] and month == csv.dates[i][1] and year == csv.dates[i][0]:
                        jpg_out_path = out_path + "__" + c + "__r" + str(r) + "__.jpg"
                        nums = np.array(csv.values[j:i + 1])[:, 0]
                        t = Artwork(jpg_path, jpg_out_path,nums,r)
                        j = i + 1
                        works.append(t)
            if len(works) == 0:
                print(c+" date is not in csv file.")
            for t in works:
                t.start()
            ne = input("\nExit press 1, more resolutions press 2: ")
            if ne.isdigit() and int(ne)== 2:
                resolt2 = input("Press resolution ( 1.1 ) :")
                if is_numeric(resolt2):
                    r = float(resolt2)
            else:
                again = False



if __name__ == '__main__':
    main()


