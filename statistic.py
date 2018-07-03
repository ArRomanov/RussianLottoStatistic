'''
Постоянно парсим списки в строки, чтобы не было вложенных списков и,
чтобы в итоге получить строку, аккуратно раделить на числа и посчитать кол-во вхождений всех чисел
'''

import sys
import re
import requests
from lxml import html
from collections import Counter

first_release = 900
try:
    future_release = int(sys.argv[1])
except IndexError:
    future_release = 1239

url_pattern = 'https://www.stoloto.ru/ruslotto/archive/{}'
get_numbers_xpath_pattern = '//div[@class="data_table"]//tbody/tr[{}]/td[2]/text()'
pattern_of_number = re.compile('[0-9]')
all_release_of_lotto = range(first_release, future_release)


def parse_list_to_str(list, split_char):
    return split_char.join(list)


# Получение всех выпавших чисел в первых семи турах одного тиража
def get_numbers_of_seven_tours(page):
    numbers_of_tours = []
    for tour in range(1, 8):
        # С помощью xpath находим на HTML странице числа в таблице результата в зависимости от номера тура
        numbers_of_tour = page.xpath(get_numbers_xpath_pattern.format(tour))
        numbers_of_tour_list = str(numbers_of_tour).split(',')
        # Удаляем из списка все лишние символы и оставляем только числа
        clean_list_of_number = [parse_list_to_str(pattern_of_number.findall(number), '') for number in
                                numbers_of_tour_list]
        numbers_of_tours.append(parse_list_to_str(clean_list_of_number, ','))
    return numbers_of_tours


# Получение всех выпавших архивных тиражей, которые выпал в первых семи турах
def get_numbers_of_all_releases():
    numbers_of_all_releases = []
    for release in all_release_of_lotto:
        url = url_pattern.format(release)
        response = requests.get(url)
        page_of_one_release = html.fromstring(response.text)
        seven_tours_of_one_release = get_numbers_of_seven_tours(page_of_one_release)
        numbers_of_all_releases.append(parse_list_to_str(seven_tours_of_one_release, ','))
    return numbers_of_all_releases


def write_results_in_file(results):
    file = open('favorite_numbers.txt', 'w')
    file.write("The statistic of favorite numbers for 'Russian lottery'\n\n'number', count of dropping out\n")
    file.write(results)
    file.close()


all_numbers = get_numbers_of_all_releases()
str_of_all_numbers = parse_list_to_str(all_numbers, ',')
counter = Counter(str_of_all_numbers.split(','))
# Сортировка по убыванию кол-ва вхождений
final_results = counter.most_common()
formatted_results = str(final_results) \
    .replace('),', '\n') \
    .replace('(', '   ') \
    .replace('[', ' ') \
    .replace(']', ' ')
write_results_in_file(formatted_results)
# print(counter)
