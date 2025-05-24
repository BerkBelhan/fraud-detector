from bs4 import BeautifulSoup
import requests

def fetch(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except:
        return 0
    return response.text

def extract_description(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        desc = soup.find('ul', attrs={'class': 'detail-desc-list'})
        desc = desc.find_all('li')
        tech = soup.find('ul', attrs={'class': 'detail-attr-container'})
        tech = tech.find_all('li', attrs={'class': 'detail-attr-item'})
        dictionary = dict()
        desc_dictionary = dict()
        for i,item in enumerate(desc):
            desc_dictionary[i+1] = item.text
        for item in tech:
            spans = item.find_all('span')
            dictionary[spans[0].text] = spans[1].text
        if desc:
            return [desc_dictionary, dictionary]
    except:
        return 1

def scrape_descriptions(url):
    html = fetch(url)
    if html == 0:
        return 0
    return extract_description(html)

def format(desc):
    if desc == 0:
        return "Linke erişilemiyor"
    if desc == 1:
        return "Ürün açıklaması bulunamadı, site değişmiş olabilir."

    description, tech_specs = desc
    formatted_text = "Ürün Bilgilendirmesi:\n\n"

    for i, item in description.items():
        formatted_text += f"{i}. {item}\n"

    formatted_text += "\nTeknik Özellikler:\n\n"

    for key, value in tech_specs.items():
        formatted_text += f"{key}: {value}\n"

    return formatted_text

def get_description(url):
    desc = scrape_descriptions(url)
    return format(desc)


if __name__ == "__main__":
    url = input("Enter the URL: ")
    desc = scrape_descriptions(url)
    formatted_desc = format(desc)

    print(formatted_desc)