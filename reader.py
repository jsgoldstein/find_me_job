import argparse
import csv
import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, element


BASE_URL = 'https://www.linkedin.com'

class Job:
    def __init__(self, job_html):
        self.title = Job.read_title(job_html)
        self.company = Job.read_company(job_html)
        self.location = Job.read_location(job_html)
        self.salary_range = Job.read_salary_range(job_html)
        self.date_posted = Job.get_job_post_date(job_html)
    
    def as_csv_line(self):
        return [self.title, self.company, self.location, self.salary_range, self.date_posted]

    @staticmethod
    def read_title(job_html: element.Tag) -> str:
        tag = job_html.find('a', {'class': 'base-card__full-link'})
        assert tag
        return tag.getText().strip()
    
    @staticmethod
    def read_company(job_html: element.Tag) -> str:
        tag = job_html.find('a', {'class': 'hidden-nested-link'})
        assert tag
        return tag.getText().strip()

    @staticmethod
    def read_location(job_html: element.Tag) -> str:
        tag = job_html.find('span', {'class': 'job-search-card__location'})
        assert tag
        return tag.getText().strip()

    @staticmethod
    def read_salary_range(job_html: element.Tag) -> Optional[str]:
        tag = job_html.find('span', {'class': 'job-search-card__salary-info'})
        return ' '.join([s.strip() for s in tag.getText().strip().split('\n')]) if tag else None

    @staticmethod
    def get_job_post_date(job_html: element.Tag) -> datetime.date:
        tag = job_html.find('time')
        assert isinstance(tag, element.Tag)
        t = tag.get('datetime')
        assert isinstance(t, str)
        return datetime.datetime.strptime(t, '%Y-%m-%d').date()


def query_linkedin(query, location) -> List[Job]:
    url = f'{BASE_URL}/jobs/search/'
    params = {
        "keywords" : query, 
        "location" : location,
        "origin": "JOB_SEARCH_PAGE_SEARCH_BUTTON",
        # Use this flag for the previous 24 hours...
        "f_TPR": "r86400"
    }

    # This will get the next 25...
    # "start": 25
    # We want to do this loop at least once, so we start new_jobs with 26 jobs to ensure it runs...
    start = 0
    total_new_jobs = 26
    params["start"] = str(start)

    jobs = []

    while start < total_new_jobs:
        resp = requests.get(url, params=params)
        soup = BeautifulSoup(resp.text, features="html.parser")

        title = soup.title
        assert title
        # total_new_jobs = int(title.getText().split()[0])

        jobs.extend(parse_linkedin(soup))
        start = start + 25

    return jobs


def parse_linkedin(soup: BeautifulSoup) -> List[Job]:
    jobs = soup.find_all("ul", {"class": "jobs-search__results-list"})
    return [Job(j) for j in jobs[0].find_all('li')]


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Crawler")
    parser.add_argument(
        '--query', '-q', type=str, default='data engineer',
        help="The query to submit to LinkedIn. Something like 'data engineer'"
    )
    parser.add_argument(
        '--location', '-l', type=str, default='New York, United States',
        help="The location to submit to LinkedIn. Something like 'New York, United States'."
    )
    parser.add_argument(
        '--output', '-o', type=str,
        default=f'linkedin-jobs-{datetime.datetime.now().date()}.csv',
        help="The location to save the data LinkedIn."
    )

    # Ensure provided locale is valid
    args = parser.parse_args()
    jobs = []
    jobs.extend(
        query_linkedin(args.query, args.location)
    )

    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Job Title", "Company", "Location", "Salary Range", "Date Posted"])
        for job in jobs:
            writer.writerow(job.as_csv_line())


if __name__ == "__main__":
    jobs = main()
