import os
import subprocess
import time

import ffmpeg


def create_directory(user, working_directory, output_directory_name):
    '''Создаем папку, если она не создана'''
    if not os.path.exists('/'.join((working_directory, output_directory_name))):
        os.makedirs('/'.join((working_directory, output_directory_name)))
        dir = '/'.join((working_directory, output_directory_name))
        command = f'sudo chown www-data:www-data {dir}'
        try:
            subprocess.run(command, shell=True, check=True)
            print(f'Команда {command} выполнена успешно')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка выполнения команды {command}: {e}')

        # Изменения прав доступа на папку
        command = ['sudo', 'chmod', '750', dir]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(f'Права доступа для {dir} успешно изменены на 750.')
        else:
            print(f'Произошла ошибка при изменении прав доступа на {dir}:')
            print(result.stderr.decode())

def convert_file(input_file, working_directory, output_directory_name):
    '''Конвертирование файла'''
    
    # Проверяем, что файл имеет расширение .avi
    #if not input_file.lower().endswith('.avi'):
    #    raise ValueError("Input file must have a .avi extension")

    # Проверяем наличие файла
    file_path = '/'.join((working_directory, input_file))
    if os.path.exists(file_path):
        print(f'Файл {file_path} существует')
    else:
        print(f'Файл {file_path} не существует')
        return

    # Определяем путь для выходного файла
    output_file = '/'.join((working_directory, output_directory_name, '.'.join(input_file.split('.')[:-1]))) + '.mp4'
    # Проверяем, существует ли уже файл
    if os.path.exists(output_file):
        print(f'File {output_file} already exists. Skipping conversion.')
    else:
        # Создаем выходную папку, если ее нет
        create_directory(user, working_directory, output_directory_name)

        # Используем ffmpeg для конвертации
        ffmpeg.input('/'.join((working_directory, input_file))).output(output_file, vcodec='libx264', acodec='aac').run()
        print(f'File has been converted and saved as: {output_file}')
        
        # Изменение владельца файла
        command = f'sudo chown www-data:www-data {output_file}'
        try:
            subprocess.run(command, shell=True, check=True)
            print(f'Команда {command} выполнена успешно')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка выполнения команды {command}: {e}')

        # Изменения прав доступа на файл
        command = ['sudo', 'chmod', '750', output_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(f"Права доступа для файла {output_file} успешно изменены на 750.")
        else:
            print(f"Произошла ошибка при изменении прав доступа файла {output_file}:")
            print(result.stderr.decode())
        
        # Обновление базы данных
        command = f'sudo -u www-data php /var/www/nextcloud/occ files:scan --path {user}/files'
        args = command.split()
        try:
            result = subprocess.run(args, check=True)
            print(f'Команда {command} успешно выполнена!')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка выполнения команды {command}: {e}')


user = 'admin'
working_directory = f'/var/www/nextcloud/data/{user}/files'
output_directory_name = 'OUT'
input_file = 'social_ad.avi'
while True:
    convert_file(input_file, working_directory, output_directory_name)
    time.sleep(3)
