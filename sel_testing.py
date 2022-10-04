import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from letter import hasNoneOf, hasXButNotAtY, letterAtXisY, putInDir, letterFrequencySort, findLetterFrequency
import clipboard as c

import time
# from pyshadow.main import Shadow


def expand_shadow_element(el_):
    shadow_r = driver.execute_script('return arguments[0].shadowRoot', el_)
    return shadow_r


def is_list_of_strings(lst):
    if lst and isinstance(lst, list):
        return all(isinstance(elem, str) for elem in lst)
    else:
        return False


def css_shadow_diver(current_driver, css_selectors):
    # check css_selectors is a list of strings
    if not is_list_of_strings(css_selectors):
        raise Exception("css_selctors must be a list of strings")

    shadow_root = current_driver
    for css_selector in css_selectors:
        root_ = shadow_root.find_element(By.CSS_SELECTOR, css_selector)
        shadow_root = expand_shadow_element(root_)
    return shadow_root


def solve_wordle(guess):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    actions = ActionChains(driver)
    # adriver.get("https://www.powerlanguage.co.uk/wordle/")
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    driver.implicitly_wait(2)

    # last_shadow1 = css_shadow_diver(driver, ["game-app", "game-modal", "game-icon[icon='close']"])
    starting_popup = driver.find_element(By.CLASS_NAME, "Modal-module_closeIcon__b4z74")
    # Modal-module_closeIcon__b4z74
    # Modal-module_modalOverlay__81ZCi

    # print("\n\n", starting_popup.get_attribute("xmlns"))
    starting_popup.click()
    driver.implicitly_wait(1)

    # last_shadow2 = css_shadow_diver(driver, ["game-app", " game-theme-manager:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > game-row:nth-child(1)", "div:nth-child(2) > game-tile:nth-child(1)"])
    # enter_letter1 = last_shadow1.find_element(By.CSS_SELECTOR, "svg")
    # enter_letter1.send_keys("a")
    # last_shadow1 = css_shadow_diver(driver, ["game-app"])
    # game_board = last_shadow1.find_element(By.CSS_SELECTOR, "#game")
    # game_board.send_keys("a")
    # arose
    # guess = 'cater'
    fileName = "wordsUsed.txt"
    fileName = putInDir(fileName, "wordle 234")
    fileName = letterFrequencySort(fileName)
    with open(fileName, 'r') as f:
        for idx, _line in enumerate(f):
            # print(idx, _line, end='')
            if _line != "\\n":
                lastLine = _line

    with open(fileName, 'r') as r:
        wordList = r.readlines()
        print(findLetterFrequency(wordList), "\n")

    # last_shadow2 = css_shadow_diver(driver, ["game-app", "#board"])

    print()
    if driver.find_element(By.TAG_NAME, "body").is_displayed() and driver.find_element(By.TAG_NAME, "body").is_enabled():
        # raise Exception("stop")
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.1)  # eye roll
        driver.find_element(By.TAG_NAME, "body").send_keys(f'{guess}')
        # .send_keys(f'{guess}')
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
    else:
        raise Exception("Key send failed")

    """
    actions.send_keys(f'{guess}')
    actions.perform()
    actions.send_keys(Keys.ENTER)
    actions.perform()
    """
    letter_elements = driver.find_elements(By.CLASS_NAME, "Row-module_row__dEHfN")

    whiteListedLetters = []
    whiteListedLettersIdx = []
    done = False
    i = 0
    while not done:
        if i >= len(letter_elements):
            done = True
            break
        letter_el = letter_elements[i].find_elements(By.CLASS_NAME, "Tile-module_tile__3ayIZ")
        i = i + 1
        print("My guess is", f'\"{guess}\"')
        # actions.implicitly_wait(1)
        # driver.implicitly_wait(2)
        time.sleep(1.4)
        letter_evaluations = []
        is_correct = []
        for el in letter_el:
            while el.get_attribute("data-state") == 'tbd':
                time.sleep(0.1)
            letter_evaluations.append(el.get_attribute("data-state"))
            if el.get_attribute("data-state") == 'correct':
                is_correct.append(True)
            else:
                is_correct.append(False)

        if all(is_correct):
            done = True
            break

        print(letter_evaluations)

        if not is_list_of_strings(letter_evaluations):
            raise Exception("")

        for idx, evaluation in enumerate(letter_evaluations):
            # print(evaluation)
            if evaluation == "correct":
                fileName = letterAtXisY(fileName, idx + 1, guess[idx])
                whiteListedLetters.append(guess[idx])
                whiteListedLettersIdx.append(idx)  # needed for finding absent+whitelisted location
            elif evaluation == "present":
                fileName = hasXButNotAtY(fileName, guess[idx], idx + 1)
                whiteListedLetters.append(guess[idx])
                # this case covers when a letter is only in n positions
            elif evaluation == "absent" and guess[idx] in whiteListedLetters:
                fileName = hasXButNotAtY(fileName, guess[idx], idx + 1)
                # actually this whitelisted letter is provably in no more new locations
                # todo: eliminate this letter as a future choice/anchor current letter
                #
                """
                # do testing on this before you deploy it
                for idy, ltr in enumerate(guess):
                    if ltr != guess[idx]:
                        fileName = hasXButNotAtY(fileName, guess[idx], idy + 1)
            """
            elif evaluation == "absent":
                if guess[idx] not in whiteListedLetters:
                    fileName = hasNoneOf(fileName, len(guess), [guess[idx]])
            else:
                raise Exception("Invalid letter evaluation result. Problem with selenium")

        fileName = letterFrequencySort(fileName)

        lastLine = ""
        with open(fileName, 'r') as f:
            for idx, _line in enumerate(f):
                print(idx, _line, end='')
                if _line != "\\n":
                    lastLine = _line

        with open(fileName, 'r') as r:
            wordList = r.readlines()
            print(findLetterFrequency(wordList), "\n")

        # find a new guess
        # choose the word with the best scoring most frequent letters

        guess = lastLine[:len(guess)]
        print(f'\"{guess}\"')
        time.sleep(2)
        driver.find_element(By.TAG_NAME, "body").send_keys(f'{guess}')
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)

    time.sleep(3)
    share_button = driver.find_element(By.CLASS_NAME, "AuthCTA-module_shareButton__SsNA6")
    share_button.click()
    driver.close()
    return None


if __name__ == "__main__":
    wordleListletterFreq = {'e': 783, 'a': 646, 'r': 585, 'i': 442, 'o': 497,
                            't': 479, 'n': 384, 's': 422, 'l': 464, 'c': 317,
                            'u': 308, 'd': 255, 'p': 229, 'm': 203, 'h': 264,
                            'g': 217, 'b': 162, 'f': 145, 'y': 279, 'w': 119,
                            'k': 134, 'v': 110, 'x': 25, 'z': 26, 'j': 17,
                            'q': 20}
    # options = ChromeOptions().setBinary("/Applications/Brave.app/Contents/MacOS/brave")
    # driver = ChromeDriver(options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver = webdriver.Chrome()

    # driver.get("http://selenium.dev")

    starting_word = 'route'
    starting_word = 'saint'

    starting_word = 'cater'
    starting_word = 'artsy'
    starting_word = 'aurei'
    starting_word = 'alert'
    solve_wordle(starting_word)

    # read clipboard contents to variable
    a = c.paste()
    print(a)
    # insert some text into the string
    a = a.replace("Wordle", "WordleBot :robot_face:")

    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    #client.chat_postMessage(channel='#wordlewars', text=a)

    """
    time.sleep(3)
    shareBtnSelectors = ["game-app", f"game-stats[highlight-guess='{i}']", "game-icon[icon='share']"]
    last_shadow = css_shadow_diver(driver, shareBtnSelectors)
    ending_popup = last_shadow.find_element(By.CSS_SELECTOR, "svg")

    results = ending_popup.click()
    driver.implicitly_wait(1)
    print(results)
    time.sleep(5)
    
    """

