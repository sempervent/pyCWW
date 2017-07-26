#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
# Get width of cell walls from fluorescent images                             #
#  - convert image to greyscale, normalize with histogram, smooth with        #
#       gaussian blur, threshold on mean pixel brightness, binary opening     #
#  - label objects (cells) in image                                           #
#  - map pixel coordinates to their label                                     #
#  - binary erosion to get border within each label                           #
#  - find area and perimeter of each cell                                     #
#  - find distribution of cell wall widths by keeping track of iteratively    #
#       dilated objects                                                       #
#  - plot contour edges (with binary erosion) and segmenting of image         #
#  - plot distribution of cell wall widths                                    #
#                                                                             #
#  Caroline Rempe - implemented method in python                              #
#  Josh Grant - gathered data and added to code                               #
#  Joe Hughes - developed method                                              #
#  Fall 2013                                                                  #
###############################################################################

######################################
# Dependancies                       #
#                                    #
#  numpy                             #
#  scipy                             #
#  pylab                             #
#  matplotlib                        #
#  Python Imaging Library (PIL)      #
#                                    #
######################################

# Access libraries and import necessary functions
import os
from cww_functions import *


### Assign input/output file names and shortest distance ranges
def name_files(file_in, out_path):
    tail = os.path.split(file_in)[1]
    file_out = os.path.join(out_path, tail.replace(".tif", ".tsv"))
    png_name = os.path.join(out_path, tail.replace(".tif", ".png"))
    print "OUTS", file_out, png_name
    return (file_out, png_name)


#### Process image
def process_image(file_in, file_out, threshold, gauss_blur,
                  binary_open_iterations, binary_close_iterations,
                  dilation_iterations, area_cutoff, perimeter_cutoff,
                  structuring_element):
    print "Open image file"

    # Open image file and convert to grayscale
    #.convert('RGB')) #,'f') #L converts to grayscale, f to float;
    # 1 converts to black and white
    im_raw = array(Image.open(file_in).convert("L"))

    # Contrast stretch/normalize with histogram
    # call histogram function to normalize color from 0 to 1
    # instead of 0 to 255; contrast is increased by distributing the histogram
    im, cdf = histeq(im_raw)

    # Get average value of pixels > 0 and find mean, set threshold to mean
    if threshold == 'mean':
        sum_pix = 0
        count = 0
        for line in im:
            for pix in line:
                if pix > 0:
                    sum_pix = sum_pix + pix
                    count = count + 1
                #print "sum count:",sum_pix,count
        #150 to 170 good, 190 ok(some objects merge) **** 170 good for wt.tif
        threshold = (sum_pix / count)
# Threshold is mean of all grey pixels
#   Need good separation of cell wall from cell
#   --mean should work, but will miss walls of small cells
#   --150-170 work, 170 gets some of small cell walls
#   **small cell walls will 'break' first, when objects merge
#   to very few, only noise blobs (not good cell wall representations)
#   will be left.

    print "Threshold =", threshold

    # Smooth the image (to remove small objects) with gaussian blur
    im = gaussian_filter(im, gauss_blur)

    # Threshold image to make binary
    # threshold and *1 to make binary not boolean; anything <128  becomes black
    im = 1 * (im < threshold)
    where(im > 1, 1, 0)        # threshold anything greater than 1 = 1

    # Fill holes to connect components of single object
    #im_open = morphology.binary_fill_holes(im,structuring_element)

    #im = im.view('float32')  ### Need for Ubuntu 12.04

    #print "iters", binary_open_iterations, binary_close_iterations
    # Widen subgroups based on neighbors of current pixel (might not be
    # necessary)
    #groups based on neighbors (ones) one above, one below,
    # and the current pixel for x and y
    im_open = morphology.binary_opening(im,
                                        structuring_element,
                                        iterations=binary_open_iterations)
    im_open = morphology.binary_closing(im_open,
                                        structuring_element,
                                        iterations=binary_close_iterations)

    # Label objects within image and count number of objects
    labels_open, num_objects_open = measurements.label(im_open)
    print "Number of objects: ", num_objects_open

    # Get edges (contours) of image, use binary erosion to
    # see edges within labeled segments
    contours = imfilter(im_open, 'contour')  # contour image filter
    # Need one preliminary binary erosion to clean data (connect contours)
    # for area & perim
    # erode label object at borders to get full edges
    contours = morphology.binary_erosion(labels_open)
    # should be in order of labels
    centroids = measurements.center_of_mass(im_open,
                                            labels_open,
                                            xrange(1, num_objects_open + 1))
    x_center = tuple(x[0] for x in centroids)
    y_center = tuple(x[1] for x in centroids)
    return (im_raw, labels_open, y_center, x_center, contours)


####  Get area and perimeter of cells (must run image process first!!)
def area_perim(area_cutoff, perimeter_cutoff, labels_open, contours, file_out):
    coord = {}
# Map labels to x,y coordinates
    for x in range(len(labels_open - 1)):
        for y in range(len(labels_open[x] - 1)):
            #print labels_open[x][y]
            # for each unique label value (key), its x,y tuple is
            # appended to the current list of tuples (value)
            coord.setdefault(labels_open[x][y], []).append(tuple([x, y]))

    edges = {}
    # Iterate through each cluster in dictionary of clusters and
    # identify edge pixels for each cluster
    for cluster in coord.keys():
        #print "Cluster", cluster
        # get value (list of points in single cluster) from key
        clust = coord[cluster]
        #print "value",clust, "clust size", len(clust)
        # check each value in list to see if it is an edge (if it is a contour)
        for pixel in clust:
            x, y = pixel[0], pixel[1]
            if contours[x][y] == 0:
                # black edge of cell segments, these are bordering segments,
                # not inside segments...
                # contours present in binary opening are assigned as edges
                # potential alternative method: erode labeled object within
                # image; (image - erosion) to get border
                edges.setdefault(cluster, []).append(tuple([x, y]))

    # Open output file
    output = open(file_out, 'w')
    output.write('object_label, area, perimeter\n')

    edges_relisted = []
    area_list = []
    labels = sorted(edges.keys())
    for i in range(0, len(labels)):
        output.write(str(labels[i]))
        # 0th is background, will end on last i+1 (=last j)
        edge_list = edges[labels[i]]
        sangles = sort_coord(edge_list)
        #print "Sangles: ",sangles
        # find area of label i+1 by passing its edge coordinates
        # to area function
        area = area2D_Polygon(sangles)
        if area < area_cutoff:
            print "Area", area
            area_list.append(area)
            output.write('\t' + str(area))
        p = perimeter(sangles)  # pass edge coordinates to perimeter function
        if p < perimeter_cutoff:
            print "Perimeter", p
            output.write('\t' + str(p))
        #print "EDGES: ",edge_list
        output.write('\n')
        edges_relisted.append(sangles)
    output.close()


### Find distribution of cell wall widths (must run image processing first!)
def cell_wall_widths(dilation_iterations, labels_open, file_out, png_name):
    # Open second output data file
    #output2 = open("widths_"+file_out,'w')
    # attempting to fix error where widths is added before the entire file
    # output path
    output2_list = os.path.split(file_out)
    output2_list_tail = "widths_" + output2_list[1]
    output2_path = os.path.join(output2_list[0], output2_list_tail)
    print "Outputting to %s" % output2_path
    output2 = open(output2_path, 'wb')

    output2.write('pixel_width\tnum_cell_walls\n')

    # Label objects within image and count number of objects
    dilating, total = measurements.label(labels_open)
    #print "Number of objects post initial erode: ", total
    max_merged = 0
    prev_merged = 0
    pixel_count = []
    object_count = []
    all_widths = []
    # Iteratively erode and then count objects
    for i in range(1, dilation_iterations):
        # Erode objects 1 pixel width at a time
        # (2  objects touching side of edge at time, so 2 pixels off cell wall)
        dilating = morphology.binary_dilation(dilating, iterations=1)
        # Label objects within image and count number of objects
        labels_open, num_objects_open = measurements.label(dilating)
        #print "Number of objects with ", i, "dilations: ", num_objects_open
        merged_objects = total - num_objects_open
        print (merged_objects - prev_merged, " cell walls with width of ",
               i * 2, "pixels\n", )
        all_widths.extend([(i * 2)] * (merged_objects - prev_merged))
        output2.write(str(i * 2) + '\t' +
                      str(merged_objects - prev_merged) + '\n')
        pixel_count.append(i * 2)
        object_count.append(merged_objects - prev_merged)
        prev_merged = merged_objects
        if max_merged < merged_objects:  # for optimizing y axis in plot
            max_merged = merged_objects

    output2.close()

    ### Print list of all widths (including repeated values) to
    ### new output file all_widths_filename
    output3_list_tail = "all_widths_" + output2_list[1]
    output3_path = os.path.join(output2_list[0], output3_list_tail)
    output3 = open(output3_path, 'wb')
    output3.write('pixel_width\n')

    for i in all_widths:
        output3.write(str(i) + "\n")

    output3.close()


### Find distribution of cell distances apart to identify aggregates
def cell_aggregates(dilation_iterations, labels_open, file_out, png_name):
    # Open second output data file
    output2_list = os.path.split(file_out)
    output2_list_tail = "widths_" + output2_list[1]
    output2_path = os.path.join(output2_list[0], output2_list_tail)
    output2 = open(output2_path, 'wb')
    output2.write('pixel_width\tnum_cell_walls\n')

    # Label objects within image and count number of objects
    dilating, total = measurements.label(labels_open)
    #print "Number of objects post initial erode: ", total
    max_merged = 0
    prev_merged = 0
    pixel_count = []
    object_count = []
    all_widths = []
    # Iteratively erode and then count objects
    for i in range(1, dilation_iterations):
        # Erode objects 1 pixel width at a time
        # (2  objects touching side of edge at time, so 2 pixels off cell wall)
        dilating = morphology.binary_dilation(dilating, iterations=1)
        # Label objects within image and count number of objects
        labels_open, num_objects_open = measurements.label(dilating)
        #  print "Number of objects with ", i, "dilations: ", num_objects_open
        merged_objects = total - num_objects_open
        print (merged_objects - prev_merged,
               " cell walls with width of ", i * 2, "pixels\n", )
        all_widths.extend([(i * 2)] * (merged_objects - prev_merged))
        output2.write(str(i * 2) + '\t' +
                      str(merged_objects - prev_merged) + '\n')
        pixel_count.append(i * 2)
        object_count.append(merged_objects - prev_merged)
        prev_merged = merged_objects
        if max_merged < merged_objects:  # for optimizing y axis in plot
            max_merged = merged_objects

    output2.close()

    ### Print list of all widths (including repeated values) to
    ### new output file all_widths_filename
    output3_list_tail = "widths_" + output2_list[1]
    output3_path = os.path.join(output2_list[0], output3_list_tail)
    output3 = open(output3_path, 'wb')
    output3.write('pixel_width\n')

    for i in all_widths:
        output3.write(str(i) + "\n")

    output3.close()

    ###  Plot distribution of cell wall widths
    png_name_tail = os.path.split(png_name)
    png_name_out = "distribution_" + png_name_tail[1]
    dist_png_name = os.path.join(png_name_tail[0], png_name_out)
    plot_scatter(pixel_count, object_count, "Cell Wall Pixel Width",
                 "Number of Cell Walls", 'b', dist_png_name,
                 "png", [0, (dilation_iterations * 2) + 5,
                         0, max_merged + 5],
                 "Distribution of Cell Wall Widths")
    return labels_open


    ### Plots modified from canny edge detector tutorial:
    #   http://scikit-image.org/docs/dev/auto_examples/plot_canny.html

def plot_image(im_raw, labels_open, labels_open_eroded,
               y_center, x_center, contours, png_name, show_image):
    # Display results on image; x and y axis switched since
    # (0,0) is in upper left corner
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
    # Annotate each cell object with its label (corresponds to edge array
    # numbers output to keep track of which cells are being measured)
    for i in range(1, len(labels_open) - 1):
        label1 = labels_open[i]  # skip the background, label 0
        #x = y_center[i-1]
        #y = x_center[i-1]
        #plt.annotate(label1,xy = (x,y), xytext = (x,y), color = 'r')

    # Subplot 3
    plt.subplot(133)
    plt.imshow(labels_open_eroded, cmap=plt.cm.gray)
    plt.axis('off')
    plt.title('Post-dilation', fontsize=20)
    #plt.scatter(x=y_center, y=x_center, c='r', s=10)

    # Create Figure
    plt.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                        bottom=0.02, left=0.02, right=0.98)

    plt.savefig(png_name)
    if show_image:
        plt.show()

##########
#print "Done"
##########
