import time
import smtplib
import constants as c
import pandas as pd

with open(f"{c.DOWNLOADS}/robot_conect.txt", "r") as file:
    file_complete = file.read().split("\n")
    ADDRESS = file_complete[0]
    PASS = file_complete[1]


def send_email(subject: str = None, body: str = None):
    """

    :param subject: Text string which will represent subject of a mail
    :param body: Text string which will represent main text of a mail
    :return: None
    """
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()  # identify us with mail server we are using
        smtp.starttls()  # encrypt our traffic
        smtp.ehlo()  # identify us again as an encrypted connection

        smtp.login(ADDRESS, PASS)
        msg = f"Subject: {subject}\n\n{body}"  # weird syntax...has to really be like this by default
        smtp.sendmail(from_addr=ADDRESS, to_addrs=ADDRESS, msg=msg)


class Performance:
    """
    Measure performance of code in seconds
    """

    def __init__(self, ):
        self.start_ = self.start()

    @staticmethod
    def start() -> float:
        """
        Start measuring performance

        :return: float
        """
        return time.perf_counter()

    def end(self) -> float:
        """
        End measuring performance

        :return: float
        """
        return time.perf_counter() - self.start_


def readable_time(seconds: int) -> str:
    """
    Convert seconds into hh:mm:ss

    :returns: str
    """
    mins_secs = divmod(seconds, 60)
    hrs_mins = divmod(mins_secs[0], 60)
    seconds = mins_secs[1]
    minutes = hrs_mins[1]
    hours = hrs_mins[0]
    result = ""

    for digit in (hours, minutes, seconds):
        result += f"0{digit} :" if digit < 10 else f"{digit} :"
    pre_result = list(result[:-1])
    pre_result[2] = "h"
    pre_result[6] = "m"
    pre_result[10] = "s"
    result = "".join(pre_result)

    return result


def csv_concatenation(main_file: str,
                      new_data: pd.DataFrame,
                      index_=False):
    """
    :param main_file: csv file into which we will append new data
    :param new_data: dataframe that will be appended to main file
    :param index_: if False, skip indexing column in pd dataframe
    :return:
    """
    # results already exist, therefore append new to old data
    try:
        df = pd.concat([pd.read_csv(main_file), new_data])
        df.to_csv(main_file, index=index_)

    # inserting results for the first time
    except pd.errors.EmptyDataError:
        new_data.to_csv(main_file, index=index_)
    except FileNotFoundError:
        new_data.to_csv(main_file, index=index_)
