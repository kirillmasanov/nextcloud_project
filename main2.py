import os
import subprocess
import time

import ffmpeg

user = 'admin'
working_directory = f'/var/www/nextcloud/data/{user}/files'
for dir in ['IN', 'OUT']:
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
            print(f'Права доступа для {directory} успешно изменены на 750.')
        else:
            print(f'Произошла ошибка при изменении прав доступа на {directory}:')
            print(result.stderr.decode())
    else:
        print(f"Папка {directory} уже существует.")