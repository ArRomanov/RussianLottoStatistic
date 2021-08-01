#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import datetime
import requests
from lxml import html
from collections import Counter

first_release = 900
try:
    future_release = int(sys.argv[1])
except IndexError:
    future_release = 1400

url_pattern = 'https://www.stoloto.ru/ruslotto/archive/{}'
count_of_nums_in_tour_xpath = 'count(//div[@class="results_table"]//tbody/tr[{}]/td[2]/span)'
num_in_tour_xpath = '//div[@class="results_table"]//tbody/tr[{}]/td[2]/span[{}]/text()'
count_of_not_dropping_xpath = 'count(//div[@class="drawing_win_numbers barrels"]/ul/li)'
not_dropping_nums_xpath = '//div[@class="drawing_win_numbers barrels"]/ul/li[{}]/text()'
pattern_of_number = re.compile('[0-9]')
all_release_of_lotto = range(first_release, future_release)
not_dropping_numbers_full = []


# Получение выпавших чисел всех архивных тиражей, которые выпал в первых семи турах
def get_numbers_of_all_releases():
    numbers_of_all_releases = []
    for release in all_release_of_lotto:
        url = url_pattern.format(release)
        response = requests.get(url)
        page_of_one_release = html.fromstring(response.text)
        seven_tours_of_one_release = get_numbers_of_seven_tours(page_of_one_release)
        numbers_of_all_releases.append(parse_list_to_str(seven_tours_of_one_release, ','))
    return numbers_of_all_releases


# Получение всех выпавших чисел в первых семи турах одного тиража (обработка html-страницы, поиск по xpath)
def get_numbers_of_seven_tours(page):
    numbers_of_tours = []
    get_not_dropping_numbers(page)
    for tour in range(1, 8):
        # в каждом туре получаем количество выпавших чисел и циклом собираем все эти значения и добавляем в общий список
        count_of_nums_in_tour = int(page.xpath(count_of_nums_in_tour_xpath.format(tour)))
        numbers_of_tour_list = [page.xpath(num_in_tour_xpath.format(tour, serial_num))[0] for serial_num in range(1, count_of_nums_in_tour + 1)]
        numbers_of_tours.append(parse_list_to_str(numbers_of_tour_list, ','))
    return numbers_of_tours


def get_not_dropping_numbers(page):
    global not_dropping_numbers_full
    # узнаем количество невыпавших чисел, потом считываем значения и добавляем в список
    count_of_not_dropping = int(page.xpath(count_of_not_dropping_xpath))
    not_dropping_nums = [page.xpath(not_dropping_nums_xpath.format(serial))[0] for serial in
                         range(1, count_of_not_dropping + 1)]
    not_dropping_numbers_full += not_dropping_nums


def parse_list_to_str(list, split_char):
    return split_char.join(list)


def write_results_in_file(results, text):
    file = open('{}.txt'.format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")), 'a')
    file.write(text)
    file.write(results)
    file.close()


if __name__ == '__main__':
    all_numbers = get_numbers_of_all_releases()
    str_of_all_numbers = parse_list_to_str(all_numbers, ',')
    # в общем списке выпавших чисел считаем количество вхождение каждого в общий список и затем сортируем по убыванию
    counter_of_dropping = Counter(str_of_all_numbers.split(','))
    # Сортировка по убыванию кол-ва вхождений
    final_results_for_dropping = counter_of_dropping.most_common(50)
    formatted_dropping = str(final_results_for_dropping) \
        .replace('),', '\n') \
        .replace('(', '   ') \
        .replace('[', ' ') \
        .replace(']', ' ')
    write_results_in_file(formatted_dropping, "'number', count of dropping out\n")

    # в общем списке невыпавших чисел считаем количество вхождение каждого в общий список и затем сортируем по убыванию
    counter_of_not_dropping = Counter(not_dropping_numbers_full)
    final_results_for_not_dropping = counter_of_not_dropping.most_common(50)
    formatted_not_dropping = str(final_results_for_not_dropping) \
        .replace('),', '\n') \
        .replace('(', '   ') \
        .replace('[', ' ') \
        .replace(']', ' ')
    write_results_in_file(formatted_not_dropping, "\n'number', count of not dropping out\n")
