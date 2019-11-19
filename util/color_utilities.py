import sys
import inspect
import os
from enum import Enum,auto

import numpy as np
import re
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import random

class ColorFormat(Enum):
    RGB = auto()
    HEX = auto()

class ColorUtilities(object):

    @classmethod
    def __valhex(cls,str):
        return re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$',str)

    @classmethod
    def hex2RGB(cls,hex):
        ''' "#FFFFFF" -> [255,255,255] '''
        # Pass 16 to the integer function for change of base
        return [int(hex[i:i+2],16) for i in range(1,6,2)]

    @classmethod
    def RGB2hex(cls,RGB):
        ''' [255,255,255] -> "#FFFFFF" '''
        # Components need to be integers for hex to make sense
        RGB=[int(x) for x in RGB]
        return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                            "{0:x}".format(v) for v in RGB])

    @classmethod
    def __color_dict(cls,gradient):
        ''' Takes in a list of RGB sub-lists and returns dictionary of
           colors in RGB and hex form for use in a graphing function
           defined later on '''
        return {"hex": [cls.RGB2hex(RGB) for RGB in gradient],
                "r": [RGB[0] for RGB in gradient],
                "g": [RGB[1] for RGB in gradient],
                "b": [RGB[2] for RGB in gradient]}

    @classmethod
    def linear_gradient(cls,start_hex,finish_hex="#FFFFFF",n=10):
        ''' returns a gradient list of (n) colors between
           two hex colors. start_hex and finish_hex
           should be the full six-digit color string,
           inlcuding the number sign ("#FFFFFF") '''
        # Starting and ending colors in RGB form
        if not cls.__valhex(start_hex) and not cls.__valhex(finish_hex):
            raise Exception("[INFO]: Invalid color format")
        s=cls.hex2RGB(start_hex)
        f=cls.hex2RGB(finish_hex)
        # Initilize a list of the output colors with the starting color
        RGB_list=[s]
        # Calcuate a color at each evenly spaced value of t from 1 to n
        for t in range(1,n):
            # Interpolate RGB vector for color at the current value of t
            curr_vector=[int(s[j]+(float(t)/(n-1))
                             *(f[j]-s[j])) for j in range(3)]
            # Add it to our list of output colors
            RGB_list.append(curr_vector)
        return cls.__color_dict(RGB_list)

    @classmethod
    def polylinear_gradient(cls,colors,n):
        ''' returns a list of colors forming linear gradients between
           all sequential pairs of colors. "n" specifies the total
           number of desired output colors '''
        # The number of colors per individual linear gradient
        n_out=int(float(n)/(len(colors)-1))
        # returns dictionary defined by color_dict()
        gradient_dict=cls.linear_gradient(colors[0],colors[1],n_out)

        if len(colors) > 1:
            for c1,c2 in zip(colors,colors[1:]):
                next=cls.linear_gradient(c1,c2,n_out)
                for k in ("hex","r","g","b"):
                    # Exclude first point to avoid duplicates
                    gradient_dict[k]+=next[k][1:]

        return gradient_dict

    @classmethod
    def rainbow_gradient(cls,n):
        cmap=cm.rainbow(np.linspace(0.0,1.0,n))
        R=list(map(lambda x: math.floor(x*255),cmap[:,0]))
        G=list(map(lambda x: math.floor(x*255),cmap[:,1]))
        B=list(map(lambda x: math.floor(x*255),cmap[:,2]))
        return cls.__color_dict(list(zip(B,G,R)))

    @classmethod
    def rand_colors(cls,n):
        colors_hex=["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(n)]
        colors_rgb=np.array([cls.hex2RGB(x) for x in colors_hex])
        return {
            "hex": colors_hex,
            "r": colors_rgb[:,0].tolist(),
            "g": colors_rgb[:,1].tolist(),
            "b": colors_rgb[:,2].tolist()}

    @classmethod
    def rand_color(cls, format=ColorFormat.RGB):
        if format == ColorFormat.RGB:
            return tuple(cls.hex2RGB("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])))
        else:
            return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]).lower()


    @classmethod
    def plot_gradient_series(
            cls,
            color_dict,
            filename=None,
            pointsize=100,
            control_points=None):
        ''' Take a dictionary containing the color
           gradient in RBG and hex form and plot
           it to a 3D matplotlib device '''

        fig=plt.figure()
        ax=fig.add_subplot(111,projection='3d')
        xcol=color_dict["r"]
        ycol=color_dict["g"]
        zcol=color_dict["b"]

        # We can pass a vector of colors
        # corresponding to each point
        ax.scatter(xcol,ycol,zcol,c=color_dict["hex"],s=pointsize)

        # If bezier control points passed to function,
        # plot along with curve
        if control_points is not None:
            xcntl=control_points["r"]
            ycntl=control_points["g"]
            zcntl=control_points["b"]
            ax.scatter(xcntl,ycntl,zcntl,
                       c=control_points["hex"],
                       s=pointsize,marker='s')

        ax.set_xlabel('Red Value')
        ax.set_ylabel('Green Value')
        ax.set_zlabel('Blue Value')
        ax.set_zlim3d(0,255)
        plt.ylim(0,255)
        plt.xlim(0,255)

        # Save two views of each plot
        ax.view_init(elev=15,azim=68)
        # plt.savefig(filename + ".svg")
        ax.view_init(elev=15,azim=28)
        # plt.savefig(filename + "_view_2.svg")

        # Show plot for testing
        plt.show()


if __name__ == "__main__":
    colors_dict=ColorUtilities.linear_gradient("#e2f442",n=32)
    R=colors_dict["r"]
    G=colors_dict["g"]
    B=colors_dict["b"]
    # gradient = list(zip(B,G,R))
    # ColorGenerator.plot_gradient_series(colors_dict)

    colors_dict=ColorUtilities.polylinear_gradient(
        ["#4f6a96","#4f6a96","#4f6a96","#4f6a96"],n=32)
    R=colors_dict["r"]
    G=colors_dict["g"]
    B=colors_dict["b"]
    gradient=list(zip(B,G,R))
    # ColorGenerator.plot_gradient_series(colors_dict)
    # print(len(gradient))

    colors_dict=ColorUtilities.rainbow_gradient(n=32)
    R=colors_dict["r"]
    G=colors_dict["g"]
    B=colors_dict["b"]
    gradient=list(zip(B,G,R))
    # ColorGenerator.plot_gradient_series(colors_dict)
    # print(len(gradient))

    print(ColorUtilities.rand_color())
