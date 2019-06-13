import matplotlib.pyplot as plt
import time
import os
import ast
import csv
import os
import numpy as np
import pdb
plt.rcParams['font.size'] = 12


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_line(mean, stdev, color="red", label="missing label", plot_area = None,xaxis=None, n=0.2, eps_per_iter=1) :
    y = mean
    #smooth  
    scale = 1.96
    y_above = [mean[i]+scale*stdev[i]/n for i  in range(mean.shape[0])]
    y_below = [mean[i]-scale*stdev[i]/n for i  in range(mean.shape[0])]
    if plot_area is None:
        display_now = True
        plot_area = plt
    #plot mean
    if xaxis is None:
        coords = list(range(len(mean)))
    else:
        coords = xaxis
    coords = np.array(coords)*eps_per_iter
    plot_area.plot(coords, y, label=label, color=color)
    plot_area.fill_between(coords, y_below, y_above, color=color, alpha = 0.3)


def get_stdev_and_mean(exp_list, prefix, root_dir = "No root directory", cutoff=None, lengths_array = None, smoothing=3, data_cutoff=None):
    if lengths_array is None:
        lengths_list = []
        for exp in exp_list:
            lengths = get_line_out_file(prefix+exp, root_dir = root_dir, smoothing=smoothing)
            if data_cutoff is not None and len(lengths) < data_cutoff:
                print("Excluded ", exp, "because the data was too short at ", len(lengths))
            else:
                lengths_list.append(lengths)
        try:
            shortest_length = min([len(l) for l in lengths_list])
        except: 
            pdb.set_trace()
        if cutoff is not None:
            shortest_length = min(cutoff, shortest_length)
            short_length_list = [l[:shortest_length]for l in lengths_list]
        else:
            #lengths_array = np.array(lengths_list)
            short_length_list = [l[:shortest_length]for l in lengths_list]
        lengths_array = np.vstack(short_length_list)
    stdevs = np.std(lengths_array, axis=0)
    means = np.mean(lengths_array, axis=0)
    return means, stdevs

def plot_file(filename, label="", smoothing=2, data_cutoff=None):
    means, stdevs = get_stdev_and_mean([filename], "", root_dir = "", smoothing=smoothing, data_cutoff=data_cutoff)
    plot_line(means, stdevs, label=label)
    plt.show()


"""This list of keys will appear in the legend, the list is experiment names
This should plot the average lengths, and then rewards"""
def plot_graph(exp_dict, 
              prefix="", 
              title="No title",
              xlab = "No x label", 
              label=None,
              root_dir = "No root directory",
              plot_area = None,
              eps_per_iter=1,
              data_cutoff=None,
              cutoff=None,
              color=None,
              smoothing=3,
              lengths_array_index=None,
              ylim = None,
              ylab = "No y label"):
    colors = ["red", "blue","green", "purple", "gray", "yellow" ]
    color_i = 0
    for exp_name in exp_dict.keys():
        if lengths_array_index is None:
            means, stdevs = get_stdev_and_mean(exp_dict[exp_name], prefix, root_dir = root_dir, cutoff=cutoff, smoothing=smoothing, data_cutoff=data_cutoff)
        else:
            means, stdevs = get_stdev_and_mean(exp_dict[exp_name], prefix, root_dir = root_dir, cutoff=cutoff, lengths_array=exp_dict[exp_name][lengths_array_index], smoothing=smoothing)
        if label is None:
            label = exp_name
        if color is None:
            color = colors[color_i]
        plot_line(means, stdevs, color = color, label=label, plot_area = plot_area, n = 1, eps_per_iter=eps_per_iter)
        color_i +=1 
    if plot_area is None:
        plt.xlabel(xlab)
        plt.ylabel(ylab)
    else:
        plot_area.set_xlabel(xlab)
        plot_area.set_ylabel(ylab)
    if ylim is not None:
        plt.ylim([0,1.0])

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


def get_line_out_file(exp, root_dir = "No root directory", smoothing=3):
    for i in range(200):
        try:
            float_list = np.load(root_dir+exp)
            break
        except OSError:
            pass
        except ValueError:
            pass
        time.sleep(0.1)
    float_list = np.nan_to_num(float_list)
    smoothed = moving_average(float_list, n = smoothing)
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
    if len(files) == 0:
        print("Could not find any files in the directory: ", root_dir)
    for f in files:
        if root+"_"in f and ".pyc" not in f:
            filenames.append(f)
    if len(filenames) == 0:
        print("no files with the root name ",root) 
    return filenames

def plot_family(filename, smoothing=2, display=True, label="", color=None, cutoff=None, eps_per_iter=1, data_cutoff=None, ylim=None, ylab=None):
    root_dir = "."
    if "/" in filename: #then the rootdir is actually something else
        dir_idx = filename.rfind("/")
        root_dir = filename[:dir_idx]
        filename = filename[dir_idx+1:]

    experiments =  get_exps_from_root(filename, root_dir=root_dir)

    if len(experiments) == 0:
        print("No experiments with name", filename, "found")
        return
    if ylab is None:
        ylab = "Success rate"
    plot_graph({"Experiment":experiments}, title="Test Title", xlab="Number episodes",smoothing=smoothing, ylim=ylim,
    root_dir=root_dir+"/", color=color, cutoff=cutoff, eps_per_iter=eps_per_iter,data_cutoff=data_cutoff,
    ylab = ylab,label=label)  
    if display:
        plt.show()

        
def main():
    import sys
    filename = sys.argv[1]
    if "family" in sys.argv:
        plot_family(filename)
    else:
        plot_file(filename, label="")
  
if __name__ == "__main__":            
    main()
   
