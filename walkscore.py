#!/usr/bin/env python
from requests import get
from requests.exceptions import ConnectionError
from re import search
from sys import stderr
from time import sleep
from fileinput import input


def get_walk_score(city, state):
    website = 'http://www.walkscore.com/'
    website += state.upper() + '/' + '_'.join(x.capitalize() for x in
                                              city.split(' '))

    try:
        r = get(website)
    except ConnectionError:
        return((0, 0, 0))

    walk_score = 0
    transit_score = 0
    bike_score = 0

    regex = '%s/score/(\d+).svg'
    walk, transit, bike = (search(regex % 'walk', r.text),
                           search(regex % 'transit', r.text),
                           search(regex % 'bike', r.text))

    if walk:
        walk_score = walk.group(1)

    if transit:
        transit_score = 1

    if bike:
        bike_score = 1

    return((walk_score, transit_score, bike_score))


if __name__ == '__main__':
    for line in input():
        sleep(1)
        split_line = line.replace('\n', '').split(' ')
        city = ' '.join(split_line[:-3])
        state, pop, density = split_line[-3:]

        score = get_walk_score(city, state)

        print '%s,%s,%s,%s,%s,%s,%s' % (city, state, pop, density,
                                        score[0], score[1], score[2])
