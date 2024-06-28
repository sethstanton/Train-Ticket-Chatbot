from django.db import models

class TrainTicket(models.Model):
    departure_station = models.CharField(max_length=100)
    arrival_station = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.departure_station} to {self.arrival_station} at £{self.price}"

class TrainStation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=200, blank=True, null=True)  

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class TrainFare(models.Model):
    origin = models.ForeignKey(TrainStation, related_name='fare_origin', on_delete=models.CASCADE)
    destination = models.ForeignKey(TrainStation, related_name='fare_destination', on_delete=models.CASCADE)
    date = models.DateField()
    fare = models.DecimalField(max_digits=6, decimal_places=2)  

    def __str__(self):
        return f"{self.origin} to {self.destination} on {self.date} - £{self.fare}"

class UserQuery(models.Model):
    query_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)  

    def __str__(self):
        return f"Query made at {self.timestamp}"

class TrainJourney(models.Model):
    rid = models.CharField(max_length=20, verbose_name="Train RTTI Identifier")
    tpl = models.CharField(max_length=15, verbose_name="Location TIPOC")
    pta = models.TimeField(null=True, blank=True, verbose_name="Planned Time of Arrival")
    ptd = models.TimeField(null=True, blank=True, verbose_name="Planned Time of Departure")
    wta = models.TimeField(null=True, blank=True, verbose_name="Working Time of Arrival")
    wtp = models.TimeField(null=True, blank=True, verbose_name="Working Time of Passing")
    wtd = models.TimeField(null=True, blank=True, verbose_name="Working Time of Departure")
    arr_et = models.TimeField(null=True, blank=True, verbose_name="Estimated Arrival Time")
    dep_et = models.TimeField(null=True, blank=True, verbose_name="Estimated Departure Time")
    arr_at = models.TimeField(null=True, blank=True, verbose_name="Actual Time of Arrival")
    dep_at = models.TimeField(null=True, blank=True, verbose_name="Actual Time of Departure")
    arr_wet = models.TimeField(null=True, blank=True, verbose_name="Working Estimated Arrival Time")
    dep_wet = models.TimeField(null=True, blank=True, verbose_name="Working Estimated Departure Time")
    pass_et = models.TimeField(null=True, blank=True, verbose_name="Estimated Passing Time")
    pass_wet = models.TimeField(null=True, blank=True, verbose_name="Working Estimated Passing Time")
    pass_at = models.TimeField(null=True, blank=True, verbose_name="Actual Passing Time")
    arr_removed = models.BooleanField(default=False, verbose_name="Arrival Time Replaced")
    pass_removed = models.BooleanField(default=False, verbose_name="Passing Time Replaced")
    cr_code = models.CharField(max_length=10, null=True, blank=True, verbose_name="Cancellation Reason Code")
    lr_code = models.CharField(max_length=10, null=True, blank=True, verbose_name="Late Running Reason Code")

    def __str__(self):
        return f"{self.rid} - {self.tpl} on {self.pta} to {self.ptd}"