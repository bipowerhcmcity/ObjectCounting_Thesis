import numpy as np

class ROI:
    def __init__(self, txt_name, im_size=(1920,1080)):
        self.file_name=txt_name
        self.file = open(self.file_name,"r")
        self.im_size= im_size

    def xywh(self):
        xywhs = []
        # Get value from line
        for line in self.file:
            print(line)
            xywh=[]
            line=line.replace("\n","")
            arr = line.split(",")

            # Append to xywh
            xywh.append(float(arr[1]) * self.im_size[0])
            xywh.append(float(arr[2]) * self.im_size[1])
            xywh.append(float(arr[3]) * self.im_size[0])
            xywh.append(float(arr[4]) * self.im_size[1])

            # Append to result:
            xywhs.append(xywh)

        # Convert to numpy arr:
        xywhs= np.array(xywhs)
        return xywhs