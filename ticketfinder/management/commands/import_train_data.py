import csv
import os
from django.core.management.base import BaseCommand
from ticketfinder.models import TrainJourney
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports train data from CSV files in a specified directory into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_directory', type=str, help='Path to the directory containing CSV files')

    def handle(self, *args, **options):
        directory_path = options['csv_directory']
        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory_path, filename)
                self.stdout.write(self.style.SUCCESS(f'Processing file: {filename}'))
                self.process_csv(file_path)

    def process_csv(self, file_path):
        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    train_journey = TrainJourney(
                        rid=row['rid'],
                        tpl=row['tpl'],
                        pta=self.parse_time(row.get('pta')),
                        ptd=self.parse_time(row.get('ptd')),
                        wta=self.parse_time(row.get('wta')),
                        wtp=self.parse_time(row.get('wtp')),
                        wtd=self.parse_time(row.get('wtd')),
                        arr_et=self.parse_time(row.get('arr_et')),
                        arr_wet=self.parse_time(row.get('arr_wet')),
                        arr_at=self.parse_time(row.get('arr_at')),
                        dep_et=self.parse_time(row.get('dep_et')),
                        dep_wet=self.parse_time(row.get('dep_wet')),
                        dep_at=self.parse_time(row.get('dep_at')),
                        pass_et=self.parse_time(row.get('pass_et')),
                        pass_wet=self.parse_time(row.get('pass_wet')),
                        pass_at=self.parse_time(row.get('pass_at')),  
                        arr_removed=row.get('arr_atRemoved', 'false').lower() == 'true',
                        pass_removed=row.get('pass_atRemoved', 'false').lower() == 'true',
                        cr_code=row.get('cr_code'),
                        lr_code=row.get('lr_code')
                    )
                    train_journey.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error inserting row from {file_path}: {row}'))
                    self.stdout.write(self.style.ERROR(f'Error message: {e}'))

    def parse_time(self, time_str):
        if time_str and time_str.strip():
            time_str = time_str.strip()
            try:
                return datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                try:
                    return datetime.strptime(time_str, '%H:%M:%S').time()
                except ValueError:
                    
                    return None
        else:
            return None
