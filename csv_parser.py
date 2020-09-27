# -*- coding: utf-8 -*-

import os
import csv
from operator import itemgetter
from pprint import pprint
from threading import Thread
from utils import time_track


class FileManager:
    """
    Gives paths to files as a list of lists from the number of threads
    .
    Отдает пути к файлам в виде списка списков от числа потоков
    """

    def __init__(self, src, numbers_files):
        self.src = os.path.normpath(src)
        self.numbers_files = numbers_files

    def get_group_of_files(self):
        """
        Goes through all directories in the given directory
        collects a new list of file paths
        calls the chunks method, which divides the list of files into a list of filegroups
        .
        Проходит по всем директориям лежащим в переданной директории
        собирает новый список путей к файлам
        вызывает метод chunks, который делит список файлов на список групп файлов
        """
        if os.path.exists(self.src):
            for dirpath, dirnames, filenames in os.walk(self.src):
                files_path = []
                for file in filenames:
                    files_path.append(os.path.join(dirpath, file))
                return list(self.chunks(files_path))
        else:
            raise FileNotFoundError('directory not found')

    def chunks(self, files_path):
        """
        divides the list of files into equal parts,
        the remainder is added to the end of the list
        .
        делит список файлов на равные части и остаток
        """
        for i in range(0, len(files_path), self.numbers_files):
            yield files_path[i:i + self.numbers_files]


class Parser(Thread):
    """
    Takes a group of file paths and parses
    calculate the volatility
    returns the name of trades and their volatility
    .
    Принимает группу путей к файлам и парсит ее
    производит расчет волатильности
    отдает имя бумаг и их волатильность
    """

    def __init__(self, group_file, zero_volatility, all_stat, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_file = group_file
        self.volatility_stat = all_stat
        self.zero_stat = zero_volatility

    def run(self):
        """
        Read a csv file
        Generates group statistics
        Returns a dictionary with values and a dictionary with ticker names,
        which have zero values
        .
        Читает csv файлы
        Формирует статистику по группе
        Возвращает словарь с значениями и словарь с именами тикеров,
        которые имеют нулевые значения
        """
        for file_path in self.group_file:
            with open(file_path, "r") as f_obj:
                reader = csv.reader(f_obj)
                name = f_obj.name[7:-4]
                stat = []
                next(reader)
                for row in reader:
                    stat.append(float(row[2]))
                stat = self.calculate_the_volatility(stat)
                if stat:
                    self.volatility_stat[name] = round(stat, 2)
                else:
                    self.zero_stat[name] = f'{name}'
        return self.volatility_stat, self.zero_stat

    @staticmethod
    def calculate_the_volatility(stat):
        """
        Highly simplified volatility calculation
        half sum = (max price + min price) / 2
        volatility = ((max price - min price) / half sum) * 100%
        .
        Сильно упрощенная версия расчета волатильности бумаг
        используется для примера:
        полусумма = (максимальная цена + минимальная цена) / 2
        волатильность = ((максимальная цена - минимальная цена) / полусумма) * 100%
        """
        max_price = max(stat)
        min_price = min(stat)
        half_sum = (max_price + min_price) / 2
        volatility = ((max_price - min_price) / half_sum) * 100
        return volatility


class ParsersRunner:
    """
    Runs parsers based on a list of filegroups
    The number of items in the list of filegroups depends on
    of the passed number numbers_files - one thread reads as many files
    collects general statistics
    makes formatted output to the console
    .
    запускает парсеры на основании списка групп файлов
    Количество элементов в списке групп файлов зависит от
    переданного числа numbers_files - столько файлов читает один поток
    собирает общую статистику
    делает форматированный вывод на консоль
    """

    def __init__(self, src, numbers_files):
        self.src = src
        self.all_stat = {}
        self.zero_volatility = {}
        self.numbers_files = numbers_files

    @time_track
    def run(self):
        """
        reads the FileManager generator, gives the path lists to the parser
        starts threads
        starts formatted output to the console
        .
        считывает генератор FileManager, отдает парсеру списки путей
        запускает потоки
        запускает форматированный вывод show_statistics()
        """
        path_group = [Parser(group_file=path, zero_volatility=self.zero_volatility, all_stat=self.all_stat) for path in
                      FileManager(src=self.src, numbers_files=self.numbers_files).get_group_of_files()]
        for parser in path_group:
            parser.start()
        for parser in path_group:
            parser.join()

        self.show_statistics()

    def show_statistics(self):
        """
        makes formatted output to the console
        top 3, bot 3 and zero volatility tickers
        .
        Отображает статистику по топ 3 и 3-м последним бумагам по стоимости
        в консоли
        отображает бумаги с нулевой волатильностью
        """
        sort_stat = sorted(self.all_stat.items(), key=itemgetter(1), reverse=True)
        print('Максимальная волатильность:')
        for name, val in sort_stat[:-(len(sort_stat) - 3)]:
            print(f'{name} - {val} %')
        print('Минимальная волатильность:')
        for name, val in sort_stat[(len(sort_stat) - 3):]:
            print(f'{name} - {val} %')
        print('Тикеры с нулевой волатильностью:')
        pprint(', '.join(self.zero_volatility))
