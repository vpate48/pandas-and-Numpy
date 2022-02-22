import io, time, json
import requests
from bs4 import BeautifulSoup

def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string): 

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    response = requests.get(url)
    #response.status_code
    return (response.status_code, response.text)
    
    
def read_api_key(filepath):
    """
    Read the Yelp API Key from file.
    
    Args:
        filepath (string): File containing API Key
    Returns:
        api_key (string): The API Key
    """
    
    # feel free to modify this function if you are storing the API Key differently
    with open(filepath, 'r') as f:
        return f.read().replace('\n','')  
    
# 3% credit
def api_get_request(url, headers, url_params):
    """
    Send a HTTP GET request and return a json response 
    
    Args:
        url (string): API endpoint url
        headers (dict): A python dictionary containing HTTP headers including Authentication to be sent
        url_params (dict): The parameters (required and optional) supported by endpoint
        
    Returns:
        results (json): response as json
    """
    http_method = 'GET'
    # See requests.request?
    response = requests.get(url, params=url_params, headers=headers)
    data = json.loads(response.content)
    return data
    
        
def location_search_params(api_key, location, **kwargs):
    """
    Construct url, headers and url_params. Reference API docs (link above) to use the arguments
    """
    # What is the url endpoint for search?
    url = 'https://api.yelp.com/v3/businesses/search'
    # How is Authentication performed?
    headers = {"Authorization": "Bearer "+api_key}
    # SPACES in url is problematic. How should you handle location containing spaces?
    #url_params = location
    url_params={"location": location, "categories":"restaurants", 'url': url.replace(' ', '+'), "location": location.replace(' ', '+')}
    for k, v in kwargs.items():
        url_params[k] = v
    req = requests.get(url=url, params=url_params, headers=headers)
    json.loads(req.text)
    
    return url, headers, url_params

def yelp_search(api_key, location, offset=0):
    """
    Make an authenticated request to the Yelp API.

    Args:
        api_key (string): Your Yelp API Key for Authentication
        location (string): Business Location
        offset (int): param for pagination

    Returns:
        total (integer): total number of businesses on Yelp corresponding to the location
        businesses (list): list of dicts representing each business
    """
    url, headers, url_params = location_search_params(api_key, location, offset=0)
    response_json = api_get_request(url, headers, url_params)
    return response_json["total"], list(response_json["businesses"])


def read_api_key(filepath):
    """
    Read the Yelp API Key from file.
    
    Args:
        filepath (string): File containing API Key
    Returns:
        api_key (string): The API Key
    """
    
    # feel free to modify this function if you are storing the API Key differently
    with open(filepath, 'r') as f:
        return f.read().replace('\n','')
    
def paginated_restaurant_search_requests(api_key, location, total):
    """
    Returns a list of tuples (url, headers, url_params) for paginated search of all restaurants
    Args:
        api_key (string): Your Yelp API Key for Authentication
        location (string): Business Location
        total (int): Total number of items to be fetched
    Returns:
        results (list): list of tuple (url, headers, url_params)
    """
    # HINT: Use total, offset and limit for pagination
    # You can reuse function location_search_params(...)
    results = []
    for i in range(0, total, 20) :
        results.append(location_search_params(api_key, location, offset = i, limit = 20))
    return results

def all_restaurants(api_key, location):
    """
    Construct the pagination requests for ALL the restaurants on Yelp for a given location.

    Args:
        api_key (string): Your Yelp API Key for Authentication
        location (string): Business Location

    Returns:
        results (list): list of dicts representing each restaurant
    """
    # What keyword arguments should you pass to get first page of restaurants in Yelp
    url, headers, url_params = location_search_params(api_key, location, offset=0, limit=20)
    response_json = api_get_request(url, headers, url_params)
    total_items = response_json["total"]
    
    all_restaurants_request = paginated_restaurant_search_requests(api_key, location, total_items)
    results = []
    # Use returned list of (url, headers, url_params) and function api_get_request to retrive all restaurants
    # REMEMBER to pause slightly after each request.
    for restaurants_request in all_restaurants_request:
        url, headers, url_params = restaurants_request
        results = results + api_get_request(url, headers, url_params)['businesses']
        time.sleep(2)
    return results



def parse_api_response(data):
    """
    Parse Yelp API results to extract restaurant URLs.
    
    Args:
        data (string): String of properly formatted JSON.

    Returns:
        (list): list of URLs as strings from the input JSON.
    """
    data = json.loads(data)
    businesses = data['businesses']
    results = []
    for business in businesses:
        results.append(business['url'])
    return results

def parse_page(html):
    """
    Parse the reviews on a single page of a restaurant.
    
    Args:
        html (string): String of HTML corresponding to a Yelp restaurant

    Returns:
        tuple(list, string): a tuple of two elements
            first element: list of dictionaries corresponding to the extracted review information
            second element: URL for the next page of reviews (or None if it is the last page)
    """
    soup = BeautifulSoup(html,'html.parser')

    url_next = soup.find('link',rel='next')
    if url_next:
        url_next = url_next.get('href')
    else:
        url_next = None

    reviews = soup.find_all('div', itemprop="review")
    reviews_list = []

    #HINT: print reviews to see what http tag to extract
    for r in reviews:
        
        author = r.find(itemprop="author").get("content")
        rating = float(r.find(itemprop="ratingValue").get("content"))
        date = r.find(itemprop="datePublished").get("content")
        description = r.find(itemprop="description").text
        
        reviews_list.append({
            "author":author,
            "rating":rating,
            "date":date,
            "description":description
        });
    return (reviews_list, url_next)

def extract_reviews(url, html_fetcher):
    """
    Retrieve ALL of the reviews for a single restaurant on Yelp.

    Parameters:
        url (string): Yelp URL corresponding to the restaurant of interest.
        html_fetcher (function): A function that takes url and returns html status code and content
        

    Returns:
        reviews (list): list of dictionaries containing extracted review information
    """

    code, html = html_fetcher(url) # function implemented in Q0 should work
    reviews, next_url = parse_page(html)
    while next_url != None:
        code, html = html_fetcher(next_url)
        newreviews, next_url = parse_page(html)
        reviews.extend(newreviews)
    return reviews
