# File of functions for finding cell wall widths (and area and perimeter of cells)

import numpy as np
import scipy
from scipy.ndimage import measurements, morphology, gaussian_filter
#from scipy.cluster.vq import *
from scipy.misc import imresize,imfilter
from pylab import *
from PIL import Image
import re, getopt, sys
from math import atan2


# Function for histogram equalization (to increase image contrast); from Jan Erik Solem: Programming with Computer Vision pg. 24
def histeq(im,nbr_bins=256):
   imhist,bins = histogram(im.flatten(),nbr_bins,normed=True) #flatten to 2D array, setting bins for hist image
   cdf = imhist.cumsum() #cumulative distribution function from hist cumulative sum
   cdf = 255*cdf/cdf[-1] #normalize values to lie between 0 and 1
   im2 = interp(im.flatten(),bins[:-1],cdf) #linear interpolation of cdf to find new pixel values
   return im2.reshape(im.shape),cdf

# Function to calculate distance between x,y coordinates
def distance(a,b):    # a and b are x,y points
  dist = (np.linalg.norm(np.array(a) - np.array(b)))  # same as dist = dist = sqrt((a[0]-b[0])**2+(a[1]-b[1])**2) 
  return(dist)
  
# Function to calculate shortest distance between two arrays of edges
def get_shortest_dist(edges1,edges2):    # pass in array of edges of one segment (cell); find distances between cells
  shortest_dist = 10000     # arbitrary large number
  # Loop through cluster points and get pairwise distances
  for edge1 in edges1:
    for edge2 in edges2:
      dist = distance(edge1,edge2)  # distance is calculated with function
      #print "function dist", dist
      if ((dist < shortest_dist) and (dist > shortest_dist_minimum)):   # keep shortest distance value that is greater than shortest distance minimum
        shortest_dist = dist
  return(shortest_dist)   # Return single shortest distance value greater than 1

# Function to calculate area of a 'cell' based on polygon of edge points
# Implementation of Green's Theorum from http://code.activestate.com/recipes/578275-2d-polygon-area/ by Jamie Bull
def area2D_Polygon(poly):
  total = 0.0
  N = len(poly)
  for i in range(N):
    v1 = poly[i]
    v2 = poly[(i+1) % N]
    total += v1[0]*v2[1] - v1[1]*v2[0]
  return abs(total/2)

# Function to calculate perimeter given a list of coordinates arranged around edge of polygon
def perimeter(coord):         # edge coordinates of 1 object input to function  (list of tuples)
  coord1 = coord   # avoid changing original list ?
  perim = 0.0
  coord1.append(coord1[0])    # concatenate tuples: add first coordinate to end of array to get distance between last and first coordinates
  num_edges = len(coord1)
  for i in range(num_edges-1):  # only need to go to second-to-last element since node2 will get last
    node1 = coord1[i]           # current coordinate
    node2 = coord1[i+1]         # next, adjacent coordinate
    perim = perim + distance(node1,node2)  # perimeter value is sum of distance between current node and next node (coordinate values)
  return(perim)

# Function to sort edge coordinates for proper input into area and perimeter functions
def sort_coord(xycoord):
  scoords = []
  ang = {}
  xcoord = tuple(x[0] for x in xycoord)
  ycoord = tuple(x[1] for x in xycoord)
  xmean = sum(xcoord)/len(xcoord)   #mean x = centroid
  ymean = sum(ycoord)/len(ycoord)
  for i in range(0,len(xycoord)):
    angle = atan2(ycoord[i] - ymean, xcoord[i] - xmean);   # get angle in radians (between -pi and pi)
    #print "Angles ", angle
    ang[angle] = xycoord[i]  # key is xy coordinate, value = angle in radians 
  sangles = sorted(ang.keys(),key=lambda coord:coord)
  #print "Sangles func",sangles
  for sang in sangles:
    scoords.append(ang[sang])
  #print "Scoord",scoords
  return scoords

# Function to make scatterplot in matlab
from matplotlib import pyplot as plt    # matplotlib scatter plot fxn to test coordinate mapping
def plot_scatter(xvalues,yvalues,xlabel,ylabel,mycolor,saveas,saveformat,axis,title):
	fig = plt.figure()
	plt.plot(xvalues, yvalues, linestyle='solid',c=mycolor, marker="o", markersize=2)
	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.axis(axis)
	plt.savefig(saveas, format=saveformat)
	print saveas, "holds output file"


################## Main Program
