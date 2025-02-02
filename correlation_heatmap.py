# BSD 3-Clause License
#
# Copyright (c) 2020, Frantisek Sabovcik
# Copyright (c) 2019, Drazen Zaric
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from toolz import merge


def plot_heatmap(x, y, label_font=None, removed=None, **kwargs):
    if 'color' in kwargs:
        color = kwargs['color']
    else:
        color = [1] * len(x)

    if 'palette' in kwargs:
        palette = kwargs['palette']
        n_colors = len(palette)
    else:
        n_colors = 256
        palette = sns.color_palette("Blues", n_colors)

    if 'color_range' in kwargs:
        color_min, color_max = kwargs['color_range']
    else:
        color_min, color_max = min(color), max(color)

    def value_to_color(val):
        if color_min == color_max:
            return palette[-1]
        else:
            val_position = float((val - color_min)) / (color_max - color_min)
            val_position = min(max(val_position, 0), 1)
            ind = int(val_position * (n_colors - 1))
            return palette[ind]

    if 'size' in kwargs:
        size = kwargs['size']
    else:
        size = [1] * len(x)

    if 'size_range' in kwargs:
        size_min, size_max = kwargs['size_range'][0], kwargs['size_range'][1]
    else:
        size_min, size_max = min(size), max(size)

    size_scale = kwargs.get('size_scale', 500)

    def value_to_size(val):
        if size_min == size_max:
            return 1 * size_scale
        else:
            val_position = (val - size_min) * 0.99 / (
                size_max - size_min
            ) + 0.01  # position of value in the input range, relative to the length of the input range
            val_position = min(max(val_position, 0), 1)  # bound the position betwen 0 and 1
            return val_position * size_scale

    if 'x_order' in kwargs:
        x_names = [t for t in kwargs['x_order']]
    else:
        x_names = [t for t in sorted(set([v for v in x]))]
    x_to_num = {p[1]: p[0] for p in enumerate(x_names)}

    if 'y_order' in kwargs:
        y_names = [t for t in kwargs['y_order']]
    else:
        y_names = [t for t in sorted(set([v for v in y]))]
    y_to_num = {p[1]: p[0] for p in enumerate(y_names)}

    plot_grid = plt.GridSpec(1, 15, hspace=0.2, wspace=0.1)  # Setup a 1x10 grid
    ax = plt.subplot(plot_grid[:, :-1])  # Use the left 14/15ths of the grid for the main plot

    marker = kwargs.get('marker', 's')

    kwargs_pass_on = {
        k: v
        for k, v in kwargs.items()
        if k not in [
            'color', 'palette', 'color_range', 'size', 'size_range', 'size_scale', 'marker',
            'x_order', 'y_order'
        ]
    }

    ax.scatter(
        x=[x_to_num[v] for v in x],
        y=[y_to_num[v] for v in y],
        marker=marker,
        s=[value_to_size(v) for v in size],
        c=[value_to_color(v) for v in color],
        **kwargs_pass_on
    )
    ax.set_xticks([v for k, v in x_to_num.items()])
    ax.set_xticklabels(
        [k for k in x_to_num],
        rotation=45,
        rotation_mode="anchor",
        y=0.015,
        horizontalalignment='right',
        fontdict={'fontsize': label_font} if label_font else {}
    )

    def mark_red_if_removed(_tick_label):
        if _tick_label.get_text() in removed:
            _tick_label.set_color("crimson")

    ax.set_yticks([v for k, v in y_to_num.items()])
    ax.set_yticklabels(
        [k for k in y_to_num],
        fontdict={'fontsize': label_font} if label_font else {},
        x=0.015,
    )

    if removed:
        for tick_label in ax.get_xticklabels():
            mark_red_if_removed(tick_label)

        for tick_label in ax.get_yticklabels():
            mark_red_if_removed(tick_label)

    ax.grid(False, 'major')
    ax.grid(True, 'minor')
    ax.set_xticks([t + 0.5 for t in ax.get_xticks()], minor=True)
    ax.set_yticks([t + 0.5 for t in ax.get_yticks()], minor=True)

    ax.set_xlim([-0.5, max([v for v in x_to_num.values()]) + 0.5])
    ax.set_ylim([-0.5, max([v for v in y_to_num.values()]) + 0.5])
    ax.set_facecolor('#F1F1F1')

    if color_min < color_max:
        ax = plt.subplot(plot_grid[:, -1])

        col_x = [1.5] * len(palette)
        bar_y = np.linspace(color_min, color_max, n_colors)

        bar_height = bar_y[1] - bar_y[0]
        ax.barh(
            y=bar_y,
            width=[5] * len(palette),
            left=col_x,
            height=bar_height,
            color=palette,
            linewidth=0
        )

        ax.set_xlim(1, 2)
        ax.grid(False)
        ax.set_facecolor('white')
        ax.set_xticks([])
        ax.set_yticks(np.linspace(min(bar_y), max(bar_y), 3))
        ax.yaxis.tick_right()


def plot_correlation_heatmap(data, size_scale=500, marker='s', **kwargs):
    corr = pd.melt(data.reset_index(), id_vars='index')
    corr.columns = ['x', 'y', 'value']
    plot_heatmap(
        corr['x'],
        corr['y'],
        **merge(
            dict(
                color=corr['value'],
                color_range=[-1, 1],
                palette=sns.diverging_palette(20, 220, n=256),
                size=corr['value'].abs(),
                size_range=[0, 1],
                marker=marker,
                x_order=data.columns,
                y_order=data.columns[::-1],
                size_scale=size_scale,
            ),
            kwargs,
        ),
    )
