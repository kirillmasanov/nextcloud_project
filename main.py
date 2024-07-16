import ffmpeg
import os
import subprocess


def create_directory(user, working_directory, output_directory_name):
    '''Создаем папку, если она не создана'''
    if not os.path.exists('/'.join((working_directory, output_directory_name))):
        os.makedirs('/'.join((working_directory, output_directory_name)))
        dir = '/'.join((working_directory, output_directory_name))
        command = f'sudo chown www-data:www-data {dir}'
        # Выполнение команды с помощью subprocess
        try:
            subprocess.run(command, shell=True, check=True)
            print(f'Команда {command} выполнена успешно')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка выполнения команды {command}: {e}')

        # Команда для изменения прав доступа на 750
        command = ['sudo', 'chmod', '750', dir]
        # Выполнение команды
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Проверка результата выполнения команды
        if result.returncode == 0:
            print(f'Права доступа для {dir} успешно изменены на 750.')
        else:
            print(f'Произошла ошибка при изменении прав доступа на {dir}:')
            print(result.stderr.decode())

def convert_avi_to_mpeg(input_file, working_directory, output_directory_name):
    # Проверяем, что файл имеет расширение .avi
    if not input_file.lower().endswith('.avi'):
        raise ValueError("Input file must have a .avi extension")

    # Определяем путь для выходного файла
    output_file = '/'.join((working_directory, output_directory_name, '.'.join(input_file.split('.')[:-1]))) + '.mp4'
    print(output_file)
    # Проверяем, существует ли уже файл .mpeg
    if os.path.exists(output_file):
        print(f'File {output_file} already exists. Skipping conversion.')
    else:
        # Создаем выходную папку, если ее нет
        create_directory(user, working_directory, output_directory_name)

        # Используем ffmpeg для конвертации
        ffmpeg.input('/'.join((working_directory, input_file))).output(output_file, vcodec='libx264', acodec='aac').run()
        print(f'File has been converted and saved as: {output_file}')
        
        command = f'sudo chown www-data:www-data {output_file}'
        # Выполнение команды с помощью subprocess
        try:
            subprocess.run(command, shell=True, check=True)
            print("Команда выполнена успешно")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения команды: {e}")

        # Команда для изменения прав доступа на 750
        command = ['sudo', 'chmod', '750', output_file]
        # Выполнение команды
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Проверка результата выполнения команды
        if result.returncode == 0:
            print(f"Права доступа для файла {output_file} успешно изменены на 750.")
        else:
            print(f"Произошла ошибка при изменении прав доступа файла {output_file}:")
            print(result.stderr.decode())
        
        command = f'sudo -u www-data php /var/www/nextcloud/occ files:scan --path {user}/files'
        # Разделение команды на список аргументов
        args = command.split()
        try:
            # Выполнение команды
            result = subprocess.run(args, check=True)
            print(f"Команда {command} успешно выполнена!")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения команды {command}: {e}")


user = 'admin'
working_directory = f'/var/www/nextcloud/data/{user}/files'
output_directory_name = 'OUT'
input_file = 'social_ad.avi'
convert_avi_to_mpeg(input_file, working_directory, output_directory_name)
