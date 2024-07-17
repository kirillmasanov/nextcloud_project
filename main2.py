import os
import shutil
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

def check_in_out_dirs (dir_in_name, dir_out_name):
    '''Проверяет наличие исходных папок'''
    for dir in [dir_in_name, dir_out_name]:
        directory = os.path.join(working_directory, dir)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Папка {directory} успешно создана.")
            # Смена владельца папки
            command = f'sudo chown www-data:www-data {directory}'
            try:
                subprocess.run(command, shell=True, check=True)
                print(f'Команда {command} выполнена успешно')
            except subprocess.CalledProcessError as e:
                print(f'Ошибка выполнения команды {command}: {e}')
            # Изменения прав доступа на папку
            command = ['sudo', 'chmod', '750', directory]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f'Права доступа для {directory} успешно изменены.')
            else:
                print(f'Произошла ошибка при изменении прав доступа на {directory}:')
                print(result.stderr.decode())
            # Обновление базы данных
            command = f'sudo -u www-data php {occ} files:scan --path {user}/files'
            args = command.split()
            try:
                result = subprocess.run(args, check=True)
                print(f'Команда {command} успешно выполнена!')
            except subprocess.CalledProcessError as e:
                print(f'Ошибка выполнения команды {command}: {e}')
        else:
            print(f"Папка {directory} уже существует.")


def add_to_nextcloud (dest_file):
    '''Изменяет владельца, права и обновляет БД Nextcloud'''
    # Изменение владельца файла
    command = f'sudo chown www-data:www-data {dest_file}'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Команда {command} выполнена успешно')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка выполнения команды {command}: {e}')

    # Изменения прав доступа на файл
    command = ['sudo', 'chmod', '750', dest_file]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"Права доступа для файла {dest_file} успешно изменены.")
    else:
        print(f"Произошла ошибка при изменении прав доступа файла {dest_file}:")
        print(result.stderr.decode())
    
    # Обновление базы данных
    command = f'sudo -u www-data php {occ} files:scan --path {user}/files'
    args = command.split()
    try:
        result = subprocess.run(args, check=True)
        print(f'Команда {command} успешно выполнена!')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка выполнения команды {command}: {e}')

while True:
    for root, _, files in os.walk(directory_in):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext.lower() in file_extension_in_list:
                source_file = os.path.join(root, filename)
                # Определяем относительный путь файла от папки 'IN'
                relative_path = os.path.relpath(source_file, directory_in)
                print(f'relative_path: {relative_path}')
                dest_subdir = os.path.dirname(relative_path)
                print(f'dest_subdir: {dest_subdir}')
                dest_subdir_full = os.path.join(directory_out, dest_subdir)
                print(f'dest_subdir_full: {dest_subdir_full}')
                dest_file = os.path.join(dest_subdir_full, os.path.splitext(filename)[0] + '.mp4')
                print(f'dest_file: {dest_file}')
                
                # Создаем подкаталог в папке 'OUT', если его еще нет
                os.makedirs(dest_subdir_full, exist_ok=True)
                
                # Проверяем наличие файла в папке 'OUT'
                if os.path.exists(dest_file):
                    # Создаем файл с текстом "Error"
                    error_file = os.path.join(dest_subdir_full, os.path.splitext(filename)[0] + '.txt')
                    with open(error_file, 'w') as f:
                        f.write("Error")
                    add_to_nextcloud(error_file)
                else:
                    # Используем ffmpeg для конвертации
                    ffmpeg.input(source_file).output(dest_file, vcodec='libx264', acodec='aac').global_args('-threads', '4').run()
                    # Удаляем файл в исходной папке
                    os.remove(source_file)
                    add_to_nextcloud(dest_file)
    time.sleep(3)