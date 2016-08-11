#! /usr/bin/env python

###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson (2016) at University College London            #
#                                                                             #
###############################################################################
#                                                                             #
# This file is part of Galore. Galore is free software: you can redistribute  #
# it and/or modify it under the terms of the GNU General Public License as    #
# published by the Free Software Foundation, either version 3 of the License, #
# or (at your option) any later version.  This program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.  You should have       #
# received a copy of the GNU General Public License along with this program.  #
# If not, see <http://www.gnu.org/licenses/>.                                 #
#                                                                             #
###############################################################################

import os
import numpy as np
import galore
import galore.formats
import argparse

try:
    import matplotlib.pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False

def run(**args):
    if not os.path.exists(args['input']):
        raise Exception("Input file {0} does not exist!".format(args['input']))
    if galore.formats.isdoscar(args['input']):
        raise Exception("DOSCAR not supported yet, sorry")
    else:
        xy_data = np.genfromtxt(args['input'], delimiter=',', comments='#')

    if args['sampling']:
        d = args['sampling']
    elif args['units'] in ('cm', 'cm-1'):
        d = 0.1
    elif args['units'] in ('THz', 'thz'):
        d = 1e-3
    elif args['units'] in ('ev', 'eV'):
        d = 1e-2

    if not args['xmax']:
        # Add 5% to data range if not specified
        args['xmax'] = 1.05 * max(xy_data[:, 0]) - 0.05 * min(xy_data[:, 0])

    x_values = np.arange(args['xmin'], args['xmax'], d)
    data_1d = galore.xy_to_1d(xy_data, x_values)

    broadened_data = data_1d.copy()
    if args['lorentzian']:
        broadened_data = galore.broaden(broadened_data, d=d,
                                        width=args['lorentzian'])

    if args['plot'] or args['plot'] is None:
        if not has_matplotlib:
            print "Can't plot, no Matplotlib"
        else:
            plt.plot(x_values, broadened_data, 'r-')
            plt.xlim([args['xmin'], args['xmax']])
            plt.xlabel(args['units'])

            if not args['ymax']:
                # Add 10% to data range if not specified
                args['ymax'] = 1.05 * max(broadened_data) - 0.05 * args['ymin']
            plt.ylim([args['ymin'], args['ymax']])

            if args['plot']:
                plt.savefig(args['plot'])
            else:
                plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, default='DOSCAR',
                        help='Input data file')
    parser.add_argument(
        '-l',
        '--lorentzian',
        nargs='?',
        default=False,
        const=2,
        type=float,
        help='Apply Lorentzian broadening with specified width.')
    parser.add_argument(
        '--units',
        '--x_units',
        type=str,
        default='cm-1',
        choices=('cm', 'cm-1', 'thz', 'THz', 'ev', 'eV'),
        help='Units for x axis (usually frequency or energy)')
    parser.add_argument(
        '-p',
        '--plot',
        nargs='?',
        default=False,
        const=None,
        help='Plot broadened spectrum. Plot to filename if provided,'
        ' otherwise display to screen.')
    parser.add_argument(
        '-d',
        '--sampling',
        type=float,
        default=False,
        help='Width, in units of x, of x-axis resolution'
        )
    parser.add_argument('--xmin', type=float, default=0,
                        help='Minimum x axis value')
    parser.add_argument('--xmax', type=float, default=False,
                        help='Maximum x axis value')
    parser.add_argument('--ymin', type=float, default=0,
                        help='Minimum y axis value')
    parser.add_argument('--ymax', type=float, default=False,
                        help='Maximum y axis value')
    args = parser.parse_args()
    args = vars(args)
    run(**args)

if __name__ == '__main__':
    main()