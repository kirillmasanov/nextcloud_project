from datetime import datetime
import os
import shlex
import subprocess
import time

import ffmpeg

user = 'admin'
nextcloud_directory = '/var/www/nextcloud'
occ = f'{nextcloud_directory}/occ'
working_directory = f'{nextcloud_directory}/data/{user}/files'
dir_in_name = 'IN'
dir_out_name = 'OUT'
directory_in = os.path.join(working_directory, dir_in_name)
directory_out = os.path.join(working_directory, dir_out_name)
file_extension_in_list = ['.avi', '.mkv', '.mov', '.mp4']
file_extension_out = '.mp4'

def change_owner (object):
    '''Смена владельца файла/папки'''
    command = f'sudo chown www-data:www-data {object}'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Команда {command} выполнена успешно')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка выполнения команды {command}: {e}')

def change_rights (object):
    '''Изменение прав доступа на файл/папку'''
    command = ['sudo', 'chmod', '750', object]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Произошла ошибка при выполнении команды: {e.stderr.decode()}')
    except Exception as e:
        print(f'Произошла неизвестная ошибка: {str(e)}')

def check_in_out_dirs (dir_in_name, dir_out_name):
    '''Проверяет наличие исходных папок'''
    for dir in [dir_in_name, dir_out_name]:
        directory = os.path.join(working_directory, dir)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Папка {directory} успешно создана.")
            add_to_nextcloud (directory)
        else:
            print(f"Папка {directory} уже существует.")


def add_to_nextcloud (object):
    '''Изменяет владельца, права и обновляет БД Nextcloud'''
    # Изменение владельца файла
    command = f'sudo chown -R www-data:www-data {shlex.quote(object)}'
    print(f'object: {object}')
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Команда {command} выполнена успешно')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка выполнения команды {command}: {e}')

    # Изменения прав доступа на файл
    command = ['sudo', 'chmod', '750', object]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"Права доступа для файла {object} успешно изменены.")
    else:
        print(f"Произошла ошибка при изменении прав доступа файла {object}:")
        print(result.stderr.decode())
    
    # Обновление базы данных
    command = f'sudo -u www-data php {occ} files:scan --path {user}/files'
    args = command.split()
    try:
        result = subprocess.run(args, check=True)
        print(f'Команда {command} успешно выполнена!')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка выполнения команды {command}: {e}')

check_in_out_dirs (dir_in_name, dir_out_name)
while True:
    for root, _, files in os.walk(directory_in):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext.lower() in file_extension_in_list:
                source_file = os.path.join(root, filename)
                # Определяем относительный путь файла от папки 'IN'
                relative_path = os.path.relpath(source_file, directory_in)
                dest_subdir = os.path.dirname(relative_path)
                dest_subdir_full = os.path.join(directory_out, dest_subdir)
                dest_file = os.path.join(dest_subdir_full, os.path.splitext(filename)[0] + '.mp4')
                
                # Создаем подкаталог в папке 'OUT', если его еще нет
                if not os.path.exists(dest_subdir_full):
                    # Создаем подкаталог, если его еще нет
                    os.makedirs(dest_subdir_full, exist_ok=True)
                    add_to_nextcloud(dest_subdir_full)

                # Проверяем наличие файла в папке 'OUT'
                if os.path.exists(dest_file):
                    # Создаем файл с текстом "Error"
                    in_subdir_full = os.path.join(directory_in, dest_subdir)
                    error_file = os.path.join(in_subdir_full, os.path.splitext(filename)[0] + '.txt')
                    if not os.path.exists(error_file):
                        with open(error_file, 'w') as f:
                            current_datetime = datetime.now()
                            ff = os.path.splitext(filename)[0] + '.mp4'
                            f.write(f'{current_datetime}: файл {ff} уже существует!')
                        add_to_nextcloud(error_file)
                else:
                    # Используем ffmpeg для конвертации
                    ffmpeg.input(source_file).output(dest_file, vcodec='libx264', acodec='aac').global_args('-threads', '1').run()
                    # Удаляем файл в исходной папке
                    os.remove(source_file)
                    add_to_nextcloud(dest_file)
    print('boom!')
    time.sleep(3)