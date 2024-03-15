import requests
from bs4 import BeautifulSoup
import MongoDB as mongodb

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

strings = [
    "css-weekly",
    "cssweekly",
    "CSSWeekly",
    "advertise",
    "issues",
    "founderweekly",
    "pythonweekly",
    "us2.campaign-archive",
    "programmerweekly",
    "weekinethereum",
    "substack.com",
    "cloudseclist",
    "https://uxdesignweekly.com",
]

exactStrings = [
    "https://uxdesignweekly.com]",
]

CollectionToMail = {
    "rahul@pythonweekly.com": "Python",
    "info@cloudseclist.com": "CloudSec",
    "jsw@peterc.org": "JavaScript",
    "clint@tldrsec.com": "Cybersecurity",
    "frontend@cooperpress.com": "FrontBackEnd",
    "executiveoffense@mail.beehiiv.com": "Cybersecurity",
    "newsletter@css-weekly.com": "CSS",
    "riskybiznews@substack.com": "Cybersecurity",
    "bluepurple@substack.com": "Cybersecurity",
    "react@cooperpress.com": "React",
    "rahul@founderweekly.com": "Founder",
    "cyficrime@substack.com": "Cybersecurity",
    "hello@awssecuritydigest.com": "CloudSec",
    "bee@securib.ee": "Bee",
    "bee@mail.hivefive.community": "Bee",
    "hello@sourcesmethods.com": "Cybersecurity",
    "blockthreat@substack.com": "Web3",
    "weekinethereum@substack.com": "Web3",
    "node@cooperpress.com": "NodeJS",
    "defihacklabs@substack.com": "Web3",
    "kenny@uxdesignweekly.com": "UX",
    "newsletter@smashingmagazine.com": "UX",
    "tamas@heydesigner.com": "UX",
    "risky-biz@ghost.io": "Cybersecurity",
    "riskybiznews@substack.com": "Cybersecurity",
    "securitypills@mail.beehiiv.com": "Cybersecurity",
    # "comment-reply@wordpress.com": "Cybersecurity",
}

Errored = []


def resolve_url(url):
    try:
        response = requests.get(url, allow_redirects=True, headers=headers, timeout=10)

        if response.status_code == 200 or response.status_code == 999:
            return response.url
        else:
            print(response.status_code)

    except requests.exceptions.RequestException as e:
        print("Error: Unable to fetch the web page:", e)
        Errored.append(url)
        return url

    return None


def extract_links(html, sender, MessageID):
    link_results = []
    try:
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", attrs={"href": True})
        for link in links:
            href = link.get("href")
            if (
                href
                and not href.startswith("#")
                and not href.startswith("javascript:")
                and not href.startswith("/")
                and not href.startswith("mailto:")
            ):
                final_url = resolve_url(href)

                if (
                    final_url
                    and final_url not in link_results
                    and not any(x in final_url for x in strings)
                    and not any(x is final_url for x in exactStrings)
                ):
                    print(final_url)
                    link_results.append(final_url)
        mongodb.DBinsert(list(link_results), CollectionToMail[sender], MessageID)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to fetch the web page:", e)
    except AttributeError as e:
        with open("ServerLogs.txt", "a") as f:
            print("link: " + link, file=f)
    print(link_results)
    return 1
