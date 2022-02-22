from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
from tqdm import tqdm


#-----------------------------------------------------------
#urls
url_books = 'https://www.litres.ru/pages/my_books_fresh/'
url_login = 'https://www.litres.ru/pages/login/'

#-----------------------------------------------------------
#secrets
#from secret import login, password
login = 'your login for litres'
password = 'your password'


#-----------------------------------------------------------
def check_close(driver):
    """
    wait until user closed browser window
    :param driver:
    :return:
    """
    closed = False
    s=driver.title
    while not closed:
        try:
            s=driver.title
            time.sleep(1)
        except:
            closed = True
#-----------------------------------------------------------
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    #chrome_service = Service("c:/temp/chromedriver.exe")
    chrome_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service = chrome_service, options=chrome_options)
    return driver
#-----------------------------------------------------------
def login_litres(driver):
    driver.get(url_login)

    username_in = driver.find_element(by=By.NAME, value='login')
    username_in.click()
    username_in.send_keys(login)

    password_in = driver.find_element(by=By.ID, value='open_pwd_main')
    password_in.send_keys(password)
    time.sleep(1)
    password_in.send_keys(Keys.RETURN)

    time.sleep(2)
#-----------------------------------------------------------
def scroll_down(driver):
    count = 0
    while True:
        page = driver.find_element(by = By.TAG_NAME, value = "html")

        #todo - it's not good solution
        page.send_keys(Keys.END)
        driver.implicitly_wait(1)
        page.send_keys(Keys.END)
        driver.implicitly_wait(1)
        page.send_keys(Keys.END)
        count +=1
        print(f'scroll down {count}')
        driver.implicitly_wait(1)
        footer = driver.find_element(by=By.CLASS_NAME, value='footer-wrap')
        if footer and footer.is_displayed():
            #print(footer.text)
            loader_button = driver.find_element(by=By.ID, value='arts_loader_button')
            if loader_button and not loader_button.is_displayed():
                break

    print(f'scroll down exit after {count} scrolls')
#-----------------------------------------------------------

def load_books(driver):
    driver.get(url_books)
    time.sleep(2)

    scroll_down(driver)
    time.sleep(2)

    arts = driver.find_elements(By.CLASS_NAME, 'art-item')
    books = []
    print('collect all e-books')
    for art in tqdm(arts[:5]):

        title = art.find_element(by=By.CLASS_NAME, value='art__name__href').get_attribute('title')
        data_type = art.find_element(by=By.CLASS_NAME, value='cover-image-wrapper').find_element(by=By.TAG_NAME,
                                                                                                 value='a').get_attribute(
            'data-type')

        if data_type == 'elektronnaya-kniga':
            art_downloads = art.find_element(by=By.CLASS_NAME, value='art-buttons__download').find_elements(
                by=By.TAG_NAME, value='a')
            links = {format.get_attribute("textContent"): format.get_attribute('href') for format in art_downloads}

        #print(f'{data_type}:{title}:links {links}')
            books.append({"title" : title, "links" : links})

    return books
#-----------------------------------------------------------

def every_downloads_chrome(driver):
    """
    if all downloads complete return true
    :param driver:
    :return Boolean:
    """
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        //var items = chrome.downloads.Manager.get().items_;
        var items = document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList').items
        if (items.length==0){
            return true;
        } else if (items.every(e => e.state === "COMPLETE")){
            return true;
        } else {
            return false;
        }
        """)


def wait_downloads_complete(driver):
    while True:
        if every_downloads_chrome(driver):
            break
        time.sleep(1)

#-----------------------------------------------------------
def download_fb2(driver, books):
    print('\nstart downloading books\n')
    time.sleep(1)

    bar = tqdm(books)
    for book in bar:
        #FB2, EPUB, iOS.EPUB, TXT, RTF, ....
        if 'FB2' in book["links"]:
            link = book["links"]["FB2"]

            bar.set_postfix_str(f' load book {book["title"]}')
            driver.get(link)
        else:
            tqdm.write(f' for book {book["title"]} no FB2 link')

    bar.set_postfix_str('all complete')
    wait_downloads_complete(driver)
    print('all downloaded')
#-----------------------------------------------------------


def litres_loads():
    driver = create_driver()
    driver.maximize_window()
    login_litres(driver)
    books = load_books(driver)
    time.sleep(1)
    print(f'\nbook count {len(books)}')

    download_fb2(driver, books)

    check_close(driver)
    print('FINISH!')
    #driver.close()
#-----------------------------------------------------------



def main():
    litres_loads()


if __name__ == '__main__':
    main()