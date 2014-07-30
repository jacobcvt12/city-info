#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from requests import get, post
from requests.exceptions import Timeout, ConnectionError
from socket import timeout
from re import sub, search
from time import sleep
from stateabb import state_to_abbrev
from sys import stderr


if __name__ == '__main__':
    map_site = 'http://quickfacts.census.gov/qfd/states/'
    r = get(map_site)
    soup = BeautifulSoup(r.text)

    # exclude last state which is USA
    states = soup.findAll('form')[1].findChild().findChildren()[:-1]

    for state in states:
        location = 'http://quickfacts.census.gov/cgi-bin/qfd/location'
        state_name = state.contents[0]
        state_abbrev = state_to_abbrev[state_name.upper()]
        r = post(location, {'Location': state['value']})

        soup = BeautifulSoup(r.text)
        cities = soup.findAll('form')[2].findChildren()[3].findChildren()

        # remove "select city" and "other places" entries
        cities = cities[1:-1]

        for i, city in enumerate(cities):
            stderr.write('\rDownloading city %d / %d from %s' %
                         (i + 1, len(cities), state_name))
            city_name = sub(' \(.*\)', '', city.contents[0])
            try:
                r = post(location, {'Location': city['value']}, timeout=5)
            except Timeout:
                try:
                    r = post(location, {'Location': city['value']}, timeout=30)
                except Timeout:
                    print '%s %s %s %s' % (city_name, state_abbrev, '0', '0')
                    stderr.write('\n')
                    continue
            except timeout:
                print '%s %s %s %s' % (city_name, state_abbrev, '0', '0')
                stderr.write('\n')
                continue
            except ConnectionError:
                print '%s %s %s %s' % (city_name, state_abbrev, '0', '0')
                stderr.write('\n')
                continue
            line = search('Population, 2013 estimate.*', r.text).group(0)
            regex = '>([1-9](?:\d{0,2})(?:,\d{3})*)'
            population = search(regex, line).group(1)
            line = search('Persons per square mile, 2010.*',
                          r.text).group(0)
            regex = regex[:-1] + '(?:\.\d*[1-9])?|0?\.\d*[1-9]|0)'
            density = search(regex, line).group(1)

            print '%s %s %s %s' % (city_name,
                                   state_abbrev,
                                   population.replace(',', ''),
                                   density.replace(',', ''))
        stderr.write('\n')
