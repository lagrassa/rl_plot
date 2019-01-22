import matplotlib.pyplot as plt
import os
import ast
import csv
import os
import numpy as np
import pdb
plt.rcParams['font.size'] = 24


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_line(mean, stdev, color="red", label="missing label", plot_area = None,xaxis=None, n=1) :
    y = mean
    #smooth  
    y_above = [mean[i]+stdev[i]/n for i  in range(mean.shape[0])]
    y_below = [mean[i]-stdev[i]/n for i  in range(mean.shape[0])]
    if plot_area is None:
        display_now = True
        plot_area = plt
    #plot mean
    if xaxis is None:
        coords = list(range(len(mean)))
    else:
        coords = xaxis
    plot_area.plot(coords, y, label=label, color=color)
    plot_area.fill_between(coords, y_below, y_above, color=color, alpha = 0.3)


def get_stdev_and_mean(exp_list, prefix, root_dir = "No root directory", cutoff=None, lengths_array = None):
    if lengths_array is None:
        lengths_list = []
        for exp in exp_list:
            lengths = get_line_out_file(prefix+exp, root_dir = root_dir)
            lengths_list.append(lengths)
        try:
            shortest_length = min([len(l) for l in lengths_list])
        except: 
            pdb.set_trace()
        if cutoff is not None:
            shortest_length = min(cutoff, shortest_length)
            short_length_list = [l[:shortest_length]for l in lengths_list]
            lengths_array = np.vstack(short_length_list)
        else:
            lengths_array = np.array(lengths_list)
    stdevs = np.std(lengths_array, axis=0)
    means = np.mean(lengths_array, axis=0)
    return means, stdevs

def plot_file(filename, label=""):
    means, stdevs = get_stdev_and_mean([filename], "", root_dir = "")
    plot_line(means, stdevs, label=label)
    plt.show()


"""This list of keys will appear in the legend, the list is experiment names
This should plot the average lengths, and then rewards"""
def plot_graph(exp_dict, 
              prefix="", 
              title="No title",
              xlab = "No x label", 
              root_dir = "No root directory",
              plot_area = None,
              cutoff=None,
              lengths_array_index=None,
              ylab = "No y label"):
    colors = ["red", "blue","green", "purple", "gray", "yellow" ]
    color_i = 0
    for exp_name in exp_dict.keys():
        if lengths_array_index is None:
            means, stdevs = get_stdev_and_mean(exp_dict[exp_name], prefix, root_dir = root_dir, cutoff=cutoff)
        else:
            means, stdevs = get_stdev_and_mean(exp_dict[exp_name], prefix, root_dir = root_dir, cutoff=cutoff, lengths_array=exp_dict[exp_name][lengths_array_index])
        plot_line(means, stdevs, color = colors[color_i], label=exp_name, plot_area = plot_area, n = len(exp_dict[exp_name]))
        color_i +=1 
    if plot_area is None:
        plt.xlabel(xlab)
        plt.ylabel(ylab)
    else:
        plot_area.set_xlabel(xlab)
        plot_area.set_ylabel(ylab)

"""Plots 2 plots on top of each other: average reward
and average length of episode
@param exp_dict A dictionary of the form exp_title:{list of experiment data}
"""
def plot_learning_curve(exp_dict, title = "No title", root_dir="No root directory", cutoff=None):
    #plot average length on top        
    f, axarr = plt.subplots(2,sharex=True)
    plt.title(title)
    plot_graph(exp_dict, root_dir = root_dir,  xlab = "Number of episodes", ylab = "Average episode reward", plot_area=axarr[0], cutoff=cutoff)
    #Then rewards
    plt.legend()
    plt.show()


def get_line_out_file(exp, root_dir = "No root directory"):
    float_list = np.load(root_dir+exp)
    smoothed = moving_average(float_list, n = 3)
    return smoothed
"""
@param root - the root name
@param root directory name
not really sure why I didn't just include them together
"""
def get_exps_from_root(root, root_dir="stats/"):
    #finds all experiments with root in the name and a number
    files = os.listdir(root_dir)
    filenames = []
    for f in files:
        if root+"_"in f and ".pyc" not in f:
            filenames.append(f)
    return filenames

        
        
def main():
    import sys
    filename = sys.argv[1]
    if "family" in sys.argv:
        plot_graph({"Experiment":get_exps_from_root(filename, root_dir=".")}, title="Test Title", xlab="Number episodes",
        root_dir="./",
        ylab = "Success rate")  
        plt.show()
    else:
        plot_file(filename, label="")
  
if __name__ == "__main__":            
    main()
   
