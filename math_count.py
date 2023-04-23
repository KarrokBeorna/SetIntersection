import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


plt_dict = {}

def count_serial(serial_answer):
    global plt_dict
    plt_dict['SERIAL'] = {1: []}
    with open('report_table.txt', 'w') as f:
        for size, arr in serial_answer.items():
            intersection_set_size_serial = []
            execution_time_serial = []
            for intersection_set_size, execution_time in arr:
                intersection_set_size_serial.append(intersection_set_size)
                execution_time_serial.append(execution_time)

            mean = np.mean(execution_time_serial)

            disp = 0
            length = len(execution_time_serial)
            for time in execution_time_serial:
                disp += (time - mean) ** 2
            disp /= length - 1

            radius = stats.t.ppf((1 + 0.9) / 2, length - 1) * stats.sem(execution_time_serial) / math.sqrt(length)

            plt_dict['SERIAL'][1].append(mean)

            f.write(f'{intersection_set_size}\t{mean/1000:.3f}\t{disp/1000:.3f}\t{radius/1000:.3f}\t{(mean - radius)/1000:.3f}\t{(mean + radius)/1000:.3f}\n')


def count_multithreads(alg, name):
    global plt_dict
    if name == 'OPENMP':
        plt_dict[f'{name}_1'] = {}
        plt_dict[f'{name}_2'] = {}
    else:
        plt_dict[name] = {}
    with open('report_table.txt', 'a') as f:
        for size, dict_ans in alg.items():
            for NUM_THREADS, arr in dict_ans.items():
                intersection_set_size_alg = []
                execution_time_alg = []
                execution_time_alg_with_answer = []
                if len(arr[0]) == 3:
                    for intersection_set_size, execution_time, execution_time_with_answer in arr:
                        intersection_set_size_alg.append(intersection_set_size)
                        execution_time_alg.append(execution_time)
                        execution_time_alg_with_answer.append(execution_time_with_answer)
                else:
                    for intersection_set_size, execution_time in arr:
                        intersection_set_size_alg.append(intersection_set_size)
                        execution_time_alg.append(execution_time)

                mean_1 = np.mean(execution_time_alg)

                disp_1 = 0
                length_1 = len(execution_time_alg)
                for time in execution_time_alg:
                    disp_1 += (time - mean_1) ** 2
                disp_1 /= length_1 - 1

                radius_1 = stats.t.ppf((1 + 0.9) / 2, length_1 - 1) * stats.sem(execution_time_alg) / math.sqrt(length_1)

                if name == 'OPENMP':
                    mean_2 = np.mean(execution_time_alg_with_answer)
                    disp_2 = 0
                    length_2 = len(execution_time_alg_with_answer)
                    for time in execution_time_alg_with_answer:
                        disp_2 += (time - mean_2) ** 2
                    disp_2 /= length_2 - 1
                    radius_2 = stats.t.ppf((1 + 0.9) / 2, length_2 - 1) * stats.sem(execution_time_alg_with_answer) / math.sqrt(length_2)
                    if NUM_THREADS not in plt_dict[f'{name}_1'].keys():
                        plt_dict[f'{name}_1'][NUM_THREADS] = [mean_1]
                        plt_dict[f'{name}_2'][NUM_THREADS] = [mean_2]
                    else:
                        plt_dict[f'{name}_1'][NUM_THREADS].append(mean_1)
                        plt_dict[f'{name}_2'][NUM_THREADS].append(mean_2)
                else:
                    if NUM_THREADS not in plt_dict[name].keys():
                        plt_dict[name][NUM_THREADS] = [mean_1]
                    else:
                        plt_dict[name][NUM_THREADS].append(mean_1)

                if name == 'PTHREADS':
                    f.write(f'{intersection_set_size}\t{mean_1/1000:.2f}\t{disp_1/1000:.2f}\t{radius_1/1000:.2f}\t'
                          f'{(mean_1 - radius_1)/1000:.2f}\t{(mean_1 + radius_1)/1000:.2f}\n')
                else:
                    f.write(f'{intersection_set_size}\t{mean_1/1000:.2f}\t{disp_1/1000:.2f}\t{radius_1/1000:.2f}\t'
                            f'{(mean_1 - radius_1)/1000:.2f}\t{(mean_1 + radius_1)/1000:.2f}\n')
                    f.write(f'{intersection_set_size}\t{mean_2/1000:.2f}\t{disp_2/1000:.2f}\t{radius_2/1000:.2f}\t'
                            f'{(mean_2 - radius_2)/1000:.2f}\t{(mean_2 + radius_2)/1000:.2f}\n')


with open('cmake-build-debug/executionTime_report.txt', 'r') as f:
    serial_answer = {}
    pthreads_answer = {}
    openmp_answer = {}
    sizes = set()
    threads = set()

    for line in f:
        words = line.split(' ')
        if len(words) > 2 and words[2][:3] == 'Set':
            word = words[3][:-1]
            if word[1] == 'e':
                set_size = int(word[0]) * 10 ** int(word[3:])
            else:
                set_size = int(word)
            sizes.add(set_size)
            serial_answer[set_size] = []
            pthreads_answer[set_size] = {}
            openmp_answer[set_size] = {}
        if len(words) == 2:
            NUM_THREADS = int(words[1])
            threads.add(NUM_THREADS)
            if NUM_THREADS not in pthreads_answer[set_size].keys():
                pthreads_answer[set_size][NUM_THREADS] = []
            if NUM_THREADS not in openmp_answer[set_size].keys():
                openmp_answer[set_size][NUM_THREADS] = []
        if len(words) > 3 and words[3] == 'Serial:':
            intersection_set_size_serial = int(words[4])
            execution_time_serial = int(words[9])
            serial_answer[set_size].append([intersection_set_size_serial, execution_time_serial])
        elif len(words) > 3 and words[3] == 'Pthreads:':
            intersection_set_size_pthreads = int(words[4])
            execution_time_pthreads = int(words[9])
            pthreads_answer[set_size][NUM_THREADS].append(
                [intersection_set_size_pthreads, execution_time_pthreads])
        elif len(words) > 3 and words[3] == 'OpenMP:':
            intersection_set_size_openmp = int(words[4])
            execution_time_openmp = int(words[9])
            execution_time_openmp_with_answer = int(words[16])
            openmp_answer[set_size][NUM_THREADS].append(
                [intersection_set_size_openmp, execution_time_openmp, execution_time_openmp_with_answer])

    count_serial(serial_answer)
    count_multithreads(pthreads_answer, 'PTHREADS')
    count_multithreads(openmp_answer, 'OPENMP')


def get_marker(alg):
    if alg == 'SERIAL':
        marker = '-bo'
    elif alg == 'PTHREADS':
        marker = '-rs'
    elif alg == 'OPENMP_1':
        marker = '-k^'
    else:
        marker = '-gv'
    return marker


def add_plot(fig, N_THREADS, x, index_subplot):
    ax = fig.add_subplot(2, 2, index_subplot)
    ax.set_title(f'SERIAL and NUM_THREADS = {N_THREADS}')
    ax.set(xlabel='Set size', ylabel='Exception Time (us)')
    ax.set_xticks(x, sorted(list(sizes)))
    for alg, alg_dict in plt_dict.items():
        marker = get_marker(alg)
        for NUM_THREADS, means in alg_dict.items():
            if NUM_THREADS == N_THREADS or alg == 'SERIAL':
                ax.plot(x, means, marker)
    ax.legend(list(plt_dict.keys()))
    ax.grid(True)


def add_plot_by_threads(fig, index_subplot, set_size, index):
    ax = fig.add_subplot(2, 2, index_subplot)
    ax.set_title(f'SET_SIZE = {set_size}')
    ax.set(xlim=(0, max(threads) + 1), xlabel='NUM_THREADS', ylabel='Exception Time (us)')
    for alg, alg_dict in plt_dict.items():
        marker = get_marker(alg)
        means_by_threads = []
        if alg != 'SERIAL':
            for NUM_THREADS, means in alg_dict.items():
                means_by_threads.append(means[index])
            ax.plot(list(threads), means_by_threads, marker)
    ax.legend(list(plt_dict.keys())[1:])
    ax.grid(True)


x = [a * max(sizes) / len(sizes) for a in range(len(sizes))]

fig = plt.figure(figsize=plt.figaspect(0.5))
fig.subplots_adjust(left=0.05, right=0.97, bottom=0.07, top=0.96, wspace=0.06)

add_plot(fig, 1, x, 1)
add_plot(fig, 2, x, 3)

ax = fig.add_subplot(2, 2, (2, 4), projection='3d')
ax.set(xlim=(min(sizes), max(sizes)), ylim=(0, max(threads) + 1),
       xlabel='Set Size', ylabel='NUM_THREADS', zlabel='Exception Time (us)')
ax.set_xticks(x, sorted(list(sizes)))

for alg, alg_dict in plt_dict.items():
    marker = get_marker(alg)
    for NUM_THREADS, means in alg_dict.items():
        ax.plot(x, means, marker, zs=NUM_THREADS, zdir='y')

fig2 = plt.figure(figsize=plt.figaspect(0.5))
fig2.subplots_adjust(left=0.05, right=0.97, bottom=0.07, top=0.96, wspace=0.06)

add_plot(fig2, 4, x, 1)
add_plot(fig2, 6, x, 3)
add_plot(fig2, 8, x, 2)
add_plot(fig2, 12, x, 4)

fig3 = plt.figure(figsize=plt.figaspect(0.5))
fig3.subplots_adjust(left=0.05, right=0.97, bottom=0.07, top=0.96, wspace=0.13)

add_plot(fig3, 16, x, 1)
add_plot_by_threads(fig3, 3, '100', 1)
add_plot_by_threads(fig3, 2, '100K', 6)
add_plot_by_threads(fig3, 4, '10KK', 9)

plt.show()
