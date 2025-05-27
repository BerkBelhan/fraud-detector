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
    formatted_text = ""
    bilgilendirme = ""
    if len(description.items()) > 6:
        for i, item in description.items():
            if i <= 5:
                continue
            bilgilendirme += f"{i-5}. {item}\n"

    if bilgilendirme != "":
        formatted_text += "Ürün Bilgilendirmesi:\n\n"+ bilgilendirme

    formatted_text += "\nTeknik Özellikler:\n\n"

    for key, value in tech_specs.items():
        formatted_text += f"{key}: {value}\n"

    return formatted_text

def link_parse(url):
    new_url = ""
    if url.startswith("https://"):
        new_url += "https://"
        url = url[8:]
        
    url = url.split('/')
    for i in range(3):
        new_url += url[i] + "/"
    return new_url

def get_description(url):
    url = link_parse(url)
    desc = scrape_descriptions(url)
    return format(desc)


if __name__ == "__main__":
    url = input("Enter the URL: ")
    print(get_description(url))