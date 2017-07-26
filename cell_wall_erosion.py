#!/usr/bin/env python
# encoding: utf-8


################################################################################################################
# Get width of cell walls from fluorescent images
#  - convert image to greyscale, normalize with histogram, smooth with gaussian blur, threshold on mean pixel brightness, binary opening
#  - label objects (cells) in image
#  - map pixel coordinates to their label
#  - binary erosion to get border within each label
#  - find area and perimeter of each cell
#  - find distribution of cell wall widths by keeping track of iteratively dilated objects
#  - plot contour edges (with binary erosion) and segmenting of image
#  - plot distribution of cell wall widths
#
#  Caroline Rempe - implemented method in python
#  Josh Grant - gathered data and added to code
#  Joe Hughes - developed method
#  Fall 2013
#################################################################################################################

#####################################
# Dependancies
#
#  numpy
#  scipy
#  pylab
#  matplotlib
#  Python Imaging Library (PIL)
#
######################################


# Access libraries and import necessary functions
from cww_functions import *
import os
import glob
from os import walk
#import numpy as np
#import scipy
#from scipy.ndimage import measurements, morphology, gaussian_filter
#from scipy.misc import imresize,imfilter
#from pylab import *
#from PIL import Image
#import re, getopt, sys
#from math import atan2

####################  Assign input/output file names and shortest distance ranges

# Run with basic single file argv input: ./cell_wall_widths_combo.py filename.txt
file_in = sys.argv[1]
file_array = file_in.split("\\")
file_name = file_array[-1]

file_out = file_name.replace(".tif",".tsv")
png_name = file_name.replace(".tif",".png")

print file_out
print file_in

#######################################
#  Command-line input implementation  #
#######################################
# create the argument parser
#parser = argparse.ArgumentParser(description="This script is designed to " +
#                                 "analyze plant cell wall characteristics" +
#                                 "from microscopy images.")

# add an argument for the image
#parser.add_argument('input image', metavar="-i", type=str, help='the file '+
#                    'which will be read by the script')

# add an argument for the shortest distance minimum
# the nargs='?' allows for the argument to be optional
#parser.add_argument('dilation iterations', metavar="--dilation_iterations",
#                    type=int, help="assignment of number of dilation iterations", default=15, #nargs='?')

############  Assign max iterations for dilating image objects (and avoiding noise)
#threshold = 170              # assign black/white cutoff threshold; or calculate mean
dilation_iterations = 15    # assign max number of dilation iterations
area_cutoff = 3000
perimeter_cutoff = 350
############


#### Process image

print "Open image file"

# Open image file and convert to grayscale
im_raw = array(Image.open(file_in).convert("L"))   #.convert('RGB')) #,'f') #L converts to grayscale, f to float; 1 converts to black and white

# Contrast stretch/normalize with histogram
im,cdf = histeq(im_raw)  # call histogram function to normalize color from 0 to 1 instead of 0 to 255; contrast is increased by distributing the histogram

# Get average value of pixels > 0 and find mean, set threshold to mean
sum_pix = 0
count = 0
for line in im:
  for pix in line:
    if pix>0:
      sum_pix = sum_pix + pix
      count = count + 1

# Threshold is mean of all grey pixels
#   Need good separation of cell wall from cell
#   --mean should work, but will miss walls of small cells
#   --150-170 work, 170 gets some of small cell walls
#   **small cell walls will 'break' first, when objects merge
#   to very few, only noise blobs (not good cell wall representations) will be left.


threshold = (sum_pix/count)     #150 to 170 good, 190 ok(some objects merge) **** 170 good for wt.tif
print "Threshold =",threshold

# Smooth the image (to remove small objects) with gaussian blur
im = gaussian_filter(im, 3)

# Threshold image to make binary
im = 1*(im<threshold)      # threshold and *1 to make binary not boolean; anything <128 becomes black
where(im > 1, 1, 0)        # threshold anything greater than 1 = 1

# Widen subgroups based on neighbors of current pixel  #### might not be necessary
im_open = morphology.binary_opening(im,ones((3,3)),iterations=1) #groups based on neighbors (ones) one above, one below, and the current pixel for x and y

# Label objects within image and count number of objects
labels_open,num_objects_open = measurements.label(im_open)
print "Number of objects: ", num_objects_open

# Get edges (contours) of image, use binary erosion to see edges within labeled segments
contours = imfilter(im_open,'contour') # contour image filter
# Need one preliminary binary erosion to clean data (connect contours) for area & perim
contours = morphology.binary_erosion(labels_open)  # erode label object at borders to get full edges
centroids = measurements.center_of_mass(im_open, labels_open, xrange(1,num_objects_open+1))  # should be in order of labels
x_center = tuple(x[0] for x in centroids)
y_center = tuple(x[1] for x in centroids)


#########  Get area and perimeter of cells

coord = {}
# Map labels to x,y coordinates
for x in range(len(labels_open-1)):
  for y in range(len(labels_open[x]-1)):
    #print labels_open[x][y]
    coord.setdefault(labels_open[x][y], []).append(tuple([x,y]))  # for each unique label value (key), its x,y tuple is appended to the current list of tuples (value)


edges = {}
# Iterate through each cluster in dictionary of clusters and identify edge pixels for each cluster
for cluster in coord.keys():
  #print "Cluster", cluster
  clust = coord[cluster]  # get value (list of points in single cluster) from key
  #print "value",clust, "clust size", len(clust)
  for pixel in clust:  # check each value in list to see if it is an edge (if it is a contour)
    x,y = pixel[0],pixel[1]
    if contours[x][y] == 0:   # black edge of cell segments, these are bordering segments, not inside segments...
      # contours present in binary opening are assigned as edges
      # potential alternative method: erode labeled object within image; (image - erosion) to get border
      edges.setdefault(cluster, []).append(tuple([x,y]))

# Open output file
output = open(file_out,'w')
output.write('object_label, area, perimeter\n')


edges_relisted = []
area_list = []
labels = sorted(edges.keys())
for i in range(0,len(labels)):
  output.write(str(labels[i]))
  edge_list = edges[labels[i]]                  # 0th is background, will end on last i+1 (=last j)
  sangles = sort_coord(edge_list)
  #print "Sangles: ",sangles
  area = area2D_Polygon(sangles)  # find area of label i+1 by passing its edge coordinates to area function
  if area < area_cutoff:
    print "Area", area
    area_list.append(area)
    output.write('\t'+str(area))
  p = perimeter(sangles)  # pass edge coordinates to perimeter function
  if p < perimeter_cutoff:
    print "Perimeter", p
    output.write('\t'+str(p))
  #print "EDGES: ",edge_list
  output.write('\n')
  edges_relisted.append(sangles)
output.close()

####### Find distribution of cell wall widths

# Open second output data file
output2 = open("widths_"+file_out,'w')
output2.write('pixel_width\tnum_cell_walls\n')

# Label objects within image and count number of objects
dilating,total = measurements.label(labels_open)
#print "Number of objects post initial erode: ", total
max_merged = 0
prev_merged = 0
pixel_count = []
object_count = []
all_widths = []
# Iteratively erode and then count objects
for i in range(1,dilation_iterations):
  # Erode objects 1 pixel width at a time (2  objects touching side of edge at time, so 2 pixels off cell wall)
  dilating = morphology.binary_dilation(dilating,iterations=1)
  # Label objects within image and count number of objects
  labels_open,num_objects_open = measurements.label(dilating)
#  print "Number of objects with ", i, "dilations: ", num_objects_open
  merged_objects = total - num_objects_open
  print  merged_objects - prev_merged," cell walls with width of ", i*2, "pixels\n",
  all_widths.extend([(i*2)] * (merged_objects-prev_merged))
  output2.write(str(i*2)+'\t'+str(merged_objects-prev_merged)+'\n')
  pixel_count.append(i*2)
  object_count.append(merged_objects - prev_merged)
  prev_merged = merged_objects
  if max_merged < merged_objects:  # for optimizing y axis in plot
    max_merged = merged_objects

output2.close()

######### Print list of all widths (including repeated values) to new output file all_widths_filename
output3 = open("all_widths_"+file_out,'w')
output3.write('pixel_width\n')

for i in all_widths:
  output3.write(str(i)+"\n")

output3.close()

#########  Plot distribution of cell wall widths

plot_scatter(pixel_count,object_count,"Cell Wall Pixel Width","Number of Cell Walls",'b',"distribution_"+png_name,"png",[0,(dilation_iterations*2)+5,0,max_merged+5],"Distribution of Cell Wall Widths")



####### Plots modified from canny edge detector tutorial: http://scikit-image.org/docs/dev/auto_examples/plot_canny.html

# Display results on image; x and y axis switched since (0,0) is in upper left corner
plt.figure(figsize=(10, 4))

# Subplot 1s
plt.subplot(131)
plt.imshow(im_raw, cmap=plt.cm.gray)
plt.axis('off')
plt.title('Grey image', fontsize=20)
plt.scatter(x=y_center, y=x_center, c='r', s=10)

# Subplot 2
plt.subplot(132)
plt.imshow(contours, cmap=plt.cm.gray)
plt.axis('off')
plt.title('Contours, binary erosion', fontsize=20)
# Annotate each cell object with its label (corresponds to edge array numbers output to keep track of which cells are being measured)
for i in range(1,len(labels)-1):
  label1 = labels[i] # skip the background, label 0
  x = y_center[i-1]
  y = x_center[i-1]
  plt.annotate(label1,xy = (x,y), xytext = (x,y), color = 'r')

# Subplot 3
plt.subplot(133)
plt.imshow(labels_open, cmap=plt.cm.gray)
plt.axis('off')
plt.title('Centers, post-dilation', fontsize=20)
plt.scatter(x=y_center, y=x_center, c='r', s=10)

# Create Figure
plt.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                    bottom=0.02, left=0.02, right=0.98)

plt.savefig(png_name)
#plt.show()

##########
print "Done"
##########

