from bs4 import BeautifulSoup  # type:ignore
from datetime import datetime
from markdownify import markdownify  # type:ignore
from typing import List, Tuple, Optional
import requests

# The date time format used by Brightspace.
DATE_TIME_FORMAT = "%b %d, %Y %H:%M"


def parse_brightspace_announcements(
        html: str,
        since: datetime = None,
) -> List[Tuple[str, datetime, str]]:
    """
    Parse the Brightspace announcements page and return the
    announcements. This is a list consisting of the title of the
    announcement, its date (as a datetime object) and its message in
    Markdown format.

    If since is not None, only return those announcements that were
    published after the since date.
    """
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.body.find("table", class_="d2l-table").find_all("tr")
    counter = 0
    title = None
    date = None
    announcements = []
    for row in rows:
        # Skip table header
        if "d_gh" not in row.get("class", []):
            if counter % 2 == 0:
                title = row.strong.string
                date = datetime.strptime(row.label.string, DATE_TIME_FORMAT)
            else:
                message = markdownify(
                    row.find("div", class_="drt").decode_contents()
                )
                assert title is not None
                assert date is not None
                announcements += [(title, date, message)]
            counter += 1

    # Reverse announcements, since they are sorted on the page from new to old, but we normally want
    # to send them from old to new.
    announcements.reverse()

    if since:
        return [ann for ann in announcements if ann[1] > since]

    return announcements


def download_brightspace_announcements(
        url: str,
        d2l_session_val: str,
        d2l_secure_session_val: str,
) -> requests.Response:
    """
    Download the Brightspace announcements page. The url must be the url of the
    announcements page, which can be found by clicking the ‘Announcements’ link
    on a Brightspace course page. The d2l_session_val and
    d2l_secure_session_val cookies can be found in your browser’s request
    headers.
    """
    headers = {"Cookie": f"d2lSessionVal={d2l_session_val}; " +
               f"d2lSecureSessionVal={d2l_secure_session_val}"}
    return requests.get(url, headers=headers)


def get_brightspace_announcements(
        url: str,
        d2l_session_val: str,
        d2l_secure_session_val: str,
        since: datetime = None,
) -> Optional[List[Tuple[str, datetime, str]]]:
    """
    Download the Brightspace announcements and parse them. See
    parse_brightspace_announcements and download_brightspace_announcements for
    more information about the parameters.
    """
    req = download_brightspace_announcements(
        url, d2l_session_val, d2l_secure_session_val)

    if req.status_code == requests.codes.ok:
        return parse_brightspace_announcements(req.text, since=since)

    return None
