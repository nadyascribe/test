import logging
from datetime import datetime, timedelta

import requests
from pyrate_limiter import Limiter, RequestRate, Duration

from dags.tools import env

logger = logging.getLogger("airflow.task")

_limiter = Limiter(RequestRate(3, 30 * Duration.SECOND))
_default_max_results = 2000


class Params:
    """
    Class for storing parameters for NVD API requests.
    """

    last_mod_start_date: datetime | None
    last_mod_end_date: datetime | None
    pub_start_date: datetime | None
    pub_end_date: datetime | None
    results_per_page: int
    start_index: int

    _latest_pub_date: datetime | None
    _latest_mod_date: datetime | None
    _start: datetime
    _limit_results: int | None

    _max_period_between_days = timedelta(days=120)

    # from docs (https://nvd.nist.gov/developers/vulnerabilities): [YYYY][“-”][MM][“-”][DD][“T”][HH][“:”][MM][“:”][SS]
    _datetime_format = "%Y-%m-%dT%H:%M:%S"

    def __init__(
        self,
        *,
        latest_pub_date: datetime | None,
        latest_mod_date: datetime | None,
        per_page: int | None = _default_max_results,
        limit_results: int | None = env.cloud_imports_limit(),
    ) -> None:
        self.results_per_page = per_page
        self.start_index = 0

        self._limit_results = limit_results
        if self._limit_results is not None and self._limit_results < self.results_per_page:
            self.results_per_page = self._limit_results
        self._latest_mod_date = latest_mod_date
        self._latest_pub_date = latest_pub_date
        tz = next(
            (d.tzinfo for d in (latest_pub_date, latest_mod_date) if d is not None),
            None,
        )
        self._start = datetime.now()
        if tz is not None:
            self._start = self._start.replace(tzinfo=tz)

        (
            self.pub_start_date,
            self.pub_end_date,
            self.last_mod_start_date,
            self.last_mod_end_date,
        ) = (
            None,
            None,
            None,
            None,
        )
        if self._latest_pub_date is not None:
            self.pub_start_date, self.pub_end_date = self._align_period_with_nvd_limit(self._latest_pub_date)

        elif self._latest_mod_date is not None:
            (
                self.last_mod_start_date,
                self.last_mod_end_date,
            ) = self._align_period_with_nvd_limit(self._latest_mod_date)

    def _align_period_with_nvd_limit(self, from_: datetime) -> tuple[datetime, datetime]:
        end = self._start
        if end - from_ > self._max_period_between_days:
            end = from_ + self._max_period_between_days
        return from_, end

    def to_request_params(self) -> dict[str, str]:
        """
        Convert to request params.
        :return:
        """
        res = {
            "startIndex": self.start_index,
            "resultsPerPage": self.results_per_page,
        }
        if self.last_mod_start_date is not None:
            res["lastModStartDate"] = self.last_mod_start_date.strftime(self._datetime_format)
        if self.last_mod_end_date is not None:
            res["lastModEndDate"] = self.last_mod_end_date.strftime(self._datetime_format)
        if self.pub_start_date is not None:
            res["pubStartDate"] = self.pub_start_date.strftime(self._datetime_format)
        if self.pub_end_date is not None:
            res["pubEndDate"] = self.pub_end_date.strftime(self._datetime_format)
        return res

    def prepare_for_next_request(self, total_received_results: int, total_results: int) -> bool:
        """
        Prepare for next request.
        :param total_received_results:
        :param total_results:
        :return: returns False if no more requests needed
        """
        if self._limit_results is not None and total_received_results >= self._limit_results:
            logger.info("limit of %s results reached", self._limit_results)
            return False
        if total_received_results == 0 or (total_results <= self.start_index + self.results_per_page):
            if self._latest_pub_date is not None:
                (
                    self.pub_start_date,
                    self.pub_end_date,
                ) = self._align_period_with_nvd_limit(self.pub_end_date or self._latest_pub_date)
                logger.info(
                    "pub_start_date=%s, pub_end_date=%s",
                    self.pub_start_date,
                    self.pub_end_date,
                )
                return self.pub_start_date != self.pub_end_date
            if self._latest_mod_date is not None:
                (
                    self.last_mod_start_date,
                    self.last_mod_end_date,
                ) = self._align_period_with_nvd_limit(self.last_mod_end_date or self._latest_mod_date)
                logger.info(
                    "last_mod_start_date=%s, last_mod_end_date=%s",
                    self.last_mod_start_date,
                    self.last_mod_end_date,
                )
                return self.last_mod_start_date != self.last_mod_end_date
            logger.info(
                "no more results, total=%s, start_index=%s, results_per_page=%s",
                total_received_results,
                self.start_index,
                self.results_per_page,
            )
            return False

        self.start_index += self.results_per_page
        logger.info("next batch start_index=%s", self.start_index)
        return True


@_limiter.ratelimit("cves", delay=True)
def download_cves(params: Params) -> tuple[list, int]:
    """
    Download CVEs from NVD.
    :param params:
    :return: vulnerabilities batch, total results
    """
    r = requests.get(
        "https://services.nvd.nist.gov/rest/json/cves/2.0",
        params=params.to_request_params(),
        timeout=30,
    )
    r.raise_for_status()
    res_json = r.json()
    logger.info(
        "downloaded %s of %s records",
        len(res_json["vulnerabilities"]),
        res_json["totalResults"],
    )
    return res_json["vulnerabilities"], res_json["totalResults"]
