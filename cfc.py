import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from bs4.element import Comment
import json

url = "" # insert a url here
external_urls = set()
# domain name of the URL without the protocol

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                external_urls.add(href)
            continue
  
    return urls


def get_all_script_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for script_tag in soup.findAll("script"):
        src = script_tag.attrs.get("src")
        if src == "" or src is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        src = urljoin(url, src)
        parsed_src = urlparse(src)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_src.scheme + "://" + parsed_src.netloc + parsed_src.path
        if not is_valid(src):
            # not a valid URL
            continue
        if domain_name not in src:
            # external link
            if src not in external_urls:
                external_urls.add(src)
            continue
  
    return urls

def write_to_file(totals):  # Function used to write to a external JSON file
    json_object = json.dumps(totals)
    with open('json_output', 'w') as outfile:
        json.dump(totals,outfile)


def tag_visible(element): #all tags that have words inside
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_privacy_page_info(url): #function to extract both external hyperlinks on the privacy page and word count
    out_dict = {}
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    privacy_page_url = soup.find("a", text="Privacy policy")['href']
    privacy_page_absolute_url = urljoin(url, privacy_page_url)
    soup = BeautifulSoup(requests.get(privacy_page_absolute_url).content, "html.parser")
    #'''''''''' finds all url's''''''''''''''''''''
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  #filters out to find all text 
    all_visible_text = u" ".join(t.strip() for t in visible_texts)
    out_dict['Privacy Page Word Count'] = len(all_visible_text.split(' ')) #creates a dictionary for the word count.
    out_dict['Privacy Page Links Count'] = len(soup.findAll("a"))
    return out_dict

def compile(url): #a function to compile all the functions together, great encapsulation method for scalability.
    a = get_all_script_links(url)
    b = get_all_website_links(url)
    my_list = list(external_urls)
    privacy_page_info = get_privacy_page_info(url)
    output_data = {
        'External URLs':my_list,
    }
    output_data.update(privacy_page_info)
    write_to_file(output_data)
    print("total external links:", len(list(external_urls)))


if __name__ == "__main__":
   compile(url)
