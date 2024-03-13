#!/usr/bin/env python
# coding: utf-8

import sys
import os
from bs4 import BeautifulSoup
import frontmatter # pip install python-frontmatter

def convert_environment(environment, soup, environment_spec):
    environment_wrapper = soup.new_tag("div")
    environment_wrapper["class"] = environment_spec["type"] + " card"
    environment_wrapper["id"] = environment["id"]

    environment.wrap(environment_wrapper)
    environment["class"] = "card-body"
    del environment["id"]
    
    card_header = soup.new_tag("div")
    card_header["class"] = "card-header"

    header = soup.new_tag("h5")
    header["class"] = "card-title"
    card_header.insert(0, header)

    environment_wrapper.insert(0, card_header)

def convert_section(s, soup):
    sid = s["id"]
    s["id"] = sid + "-item"
    s["class"] = "accordion-item"

    header = soup.new_tag("h1")
    header["class"] = "accordion-header"
    header["id"] = sid + "-header"
    s.insert(0, header)

    body = soup.new_tag("div")
    body["id"] = sid + "-collapse"
    body["class"] = "accordion-collapse collapse"
    body["aria-labelledby"] = sid + "-header"
    s.insert(1, body)

    H = s.find("h2")
    H.name = "button"
    H["class"] = "accordion-button collapsed"
    H["type"] ="button"
    H["data-bs-toggle"] = "collapse"
    H["data-bs-target"] = "#" + sid + "-collapse"
    H["aria-expanded"] = "false"
    H["aria-controls"] = sid + "-collapse"

    header.insert(0, H)

    B = s.find("div", class_="outline-text-2")
    B["class"] = "accordion-body p-3 m-0"
    B["id"] += "-body"

    body.insert(0, B)

def convert(html):
    section_class = "outline-2"

    soup = BeautifulSoup(html, "lxml")

    sections = soup.find_all("div", class_=section_class)
    if (len(sections) > 0):
        s1 = sections[0]
        accordion = soup.new_tag("div")
        accordion["class"] = "accordion"
        s1.insert_before(accordion)

        for s in sections:
            accordion.append(s)
            convert_section(s, soup)

    # Convert theorem like environments
    environment_specs = [{"type" : "thm", "title": "Theorem"},
                           {"type" : "lem", "title": "Lemma"},
                           {"type" : "defn", "title": "Definition"},
                           {"type" : "eg", "title": "Example"}]

    for environment_spec in environment_specs:
        environments = soup.find_all("div", class_=environment_spec["type"])
        for environment in environments:
            convert_environment(environment, soup, environment_spec)

    return (" ".join(str(c) for c in soup.body.children))

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]

    with open(infile, 'r') as f:
        contents = frontmatter.load(f)

    contents["layout"] = "notes"
    contents.content = convert(contents.content)

    with open(outfile, "w") as f:
        f.write(frontmatter.dumps(contents))
