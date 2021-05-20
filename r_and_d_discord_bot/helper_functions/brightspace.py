from bs4 import BeautifulSoup
from datetime import datetime
from markdownify import markdownify
from typing import List, Tuple

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

    rows = soup.body.find(id="z_c").find_all("tr")
    counter = 0
    title = None
    date = None
    announcements = []
    for row in rows:
        # Skip table header
        if "d2l-table-row-first" not in row.get("class", []):
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

    if since:
        return [ann for ann in announcements if ann[1] > since]

    return announcements
