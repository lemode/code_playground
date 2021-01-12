"""
Background:
* Calculate the mortgage amoritization on the fly
* Select the current period from that schedule
* Create one journal entry to load into Wave Accounting for the current period
* Create multiple journal entries to load into in a specified period

"""

import pandas as pd
import datetime

from dateutil.relativedelta import relativedelta
from code_playground.finance_transactions.src.constants import (
    MortgageConfig as constants,
)


class MortgageService:
    def __init__(self):
        self.df_mortgage_schedule = pd.DataFrame(columns=constants.SCHEDULE_COLUMNS)

    def convert_string_to_date(self, date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%d")

    def get_list_of_dates_rates_changed(self, rate_schedule):

        list_date_keys = rate_schedule.keys()
        list_schedule_dates = []

        for date_keys in list_date_keys:
            schedule_date = self.convert_string_to_date(date_keys)
            list_schedule_dates.append(schedule_date)

        return list_schedule_dates

    def get_start_date(self, rate_schedule):
        """
        Finds the start date of the prime rates schedule
        equivalent to when the morgage loan was created

        Args:
            list_rate_schedule : list - the dates of all the rates within the schedule for the different prime rates
        """
        list_rate_schedule = self.get_list_of_dates_rates_changed(rate_schedule)
        return min(list_rate_schedule)

    def get_end_date(self, start_date, number_of_years):
        return start_date + relativedelta(years=number_of_years)

    def get_date_range_schedule(self, start_date, end_date, rate_schedule):

        # https://stackoverflow.com/questions/22696662/python-list-of-first-day-of-month-for-given-period
        date_range = pd.date_range(
            start_date, end_date, freq="1M"
        ) - pd.offsets.MonthBegin(1)
        return date_range

    def get_period_prime_rate(
        self, period_date, rate_schedule=constants.PRIME_RATES_SCHEDULE
    ):
        """
        Calculate the prime rate for a specific period based on date and rate schedule

        Args:
            period_date : str - the start date of the period you want the rate of
            rate_schedule : dict - the dates where the schedule for all the different prime rates
        """

        period_date = (
            self.convert_string_to_date(period_date).date().strftime("%Y-%m-%d")
        )
        list_rate_schedule = self.get_list_of_dates_rates_changed(rate_schedule)

        min_date = list_rate_schedule[0].date().strftime("%Y-%m-%d")
        max_date = (
            list_rate_schedule[len(list_rate_schedule) - 1].date().strftime("%Y-%m-%d")
        )

        if period_date <= min_date:
            prime_rate = rate_schedule[min_date]
            return prime_rate

        elif period_date >= max_date:
            prime_rate = rate_schedule[max_date]
            return prime_rate
        else:
            for rate_date in list_rate_schedule:
                begin = rate_date.date().strftime("%Y-%m-%d")
                if begin < max_date:
                    end_position = list_rate_schedule.index(rate_date) + 1
                    end = list_rate_schedule[end_position].strftime("%Y-%m-%d")
                    if begin <= period_date < end:
                        prime_rate = rate_schedule[begin]
                        return prime_rate

    def get_rates_schedule(
        self, date_range, rate_schedule=constants.PRIME_RATES_SCHEDULE
    ):
        """
        Calculate mortgage prime  and personal rate schedule based on amounts and schedules

        Args:
            date_range : list - each monthly period within the morgage contract
            rate_schedule : dict - the dates where the schedule for all the different prime rates
        """
        index = 0
        dict = {}

        while index < len(date_range):
            period_date = date_range[index].strftime("%Y-%m-%d")
            period_rate = self.get_period_prime_rate(period_date)
            dict.update({period_date: period_rate})
            index += 1
        return dict


    def handle(self):
        """
        Get mortgage amoritization schedule
        """
        start_date = self.get_start_date(constants.PRIME_RATES_SCHEDULE)
        end_date = self.get_end_date(start_date, constants.NUMBER_OF_YEARS)
        dates = self.get_date_range_schedule(
            start_date, end_date, constants.PRIME_RATES_SCHEDULE
        )
        rates = self.get_prime_rate_schedule(dates)       


if __name__ == "__main__":
    x = MortgageService()
    result = x.handle()
