#!/usr/bin/python3
##############################################################################
# AUTHOR: [Loopzen](https://github.com/loopzen/)
# DATE: 2019-20-01
# DESCRIPTION: Google Keep WebScrapping
# - Extract white google keep notes
##############################################################################
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import json
from os.path import expanduser

HOME_FOLDER = expanduser("~")

# CHARGE JSON
with open(HOME_FOLDER + "/src/conf/google_keep_scrapping_config.json", "r") as f:
    config = json.load(f)


class KeepNote:
    def __init__(self, content_element, toolbar_element):
        self.content_element = content_element
        self.toolbar_element = toolbar_element
        self.title = ""
        self.content = "\n"

    def charge_info(self):
        self.title = self.content_element.find_element_by_xpath(
            ".//div[@aria-label='Título']"
        ).text
        # Normal note vs list note
        try:
            self.content += self.content_element.find_element_by_xpath(
                ".//div[@aria-label='Nota']"
            ).text
        except NoSuchElementException:
            self.content += self.charge_checkboxes()

    def __str__(self):
        """Print note info"""
        return "TITULO: {}\nCONTENIDO: {}\n".format(self.title, self.content)

    def archive(self):
        """Archive note"""
        delete_button = self.toolbar_element.find_element_by_xpath(
            ".//div[@aria-label='Archivar']"
        )
        delete_button.click()

    def charge_checkboxes(self):
        """Extract checkboxes information"""
        checkboxes_container = self.content_element.find_element_by_class_name(
            "gkA7Yd-sKfxWe.rymPhb-IZ65Hb-gkA7Yd"
        )
        checkboxes_text = ""
        for checkbox in checkboxes_container.find_elements_by_xpath(
            ".//div[@aria-label='elemento de lista']"
        ):
            checkboxes_text += "- " + checkbox.text + "\n"
        return checkboxes_text

    def write_note_to_file(self):
        """Write note to output file"""
        try:
            fileOutput = open(HOME_FOLDER + config["output"]["path"], "a")
            fileOutput.write("xxxxxxxxxxxxxxxxxxx\n")
            fileOutput.write("TITULO: {}\n".format(self.title))
            fileOutput.write("CONTENT: {}\n".format(self.content))
            fileOutput.close()
        except Exception as e:
            print(e)


def getNoteElements(driver):
    # AUQI leer lasnotas
    elementContainer = driver.find_element_by_class_name(
        "gkA7Yd-sKfxWe.ma6Yeb-r8s4j-gkA7Yd"
    )
    all_notes_container = elementContainer.find_element_by_xpath(".//div[1]")

    notes_elements = all_notes_container.find_elements_by_class_name(
        "IZ65Hb-TBnied.HLvlvd-h1U9Be"
    )
    print("Notas obtenidas: " + str(len(notes_elements)))
    return notes_elements


def extract_notes(notes_elements):
    keep_notes = []
    for note in notes_elements:
        content_element = note.find_element_by_xpath(".//div[@class='IZ65Hb-s2gQvd']")
        toolbar_element = note.find_element_by_xpath(".//div[@class='IZ65Hb-INgbqf']")
        keep_note = KeepNote(content_element, toolbar_element)
        keep_notes.append(keep_note)
    return keep_notes


def main():
    driver = webdriver.Firefox()
    driver.get("https://keep.google.com/")
    # LOGIN
    # account
    driver.find_element_by_id("identifierId").send_keys(config["user"]["name"])
    driver.find_element_by_id("identifierNext").click()
    time.sleep(1)
    # password
    driver.find_element_by_name("password").send_keys(config["user"]["password"])
    driver.find_element_by_id("passwordNext").click()
    # confirmation
    time.sleep(60)
    notes_elements = getNoteElements(driver)
    keep_notes = extract_notes(notes_elements)

    for keep_note in keep_notes:
        keep_note.charge_info()
        keep_note.write_note_to_file()
        keep_note.archive()
        print(keep_note)
    time.sleep(5)
    driver.close()


if __name__ == "__main__":
    main()
