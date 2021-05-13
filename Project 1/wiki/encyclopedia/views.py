from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import re
from random import choice

from . import util


def validate_title(title):
    """
    Ensures that the 'title' submitted is a unique one.
    """
    entries = util.list_entries()

    if title.lower() in (entry.lower() for entry in entries):
        raise ValidationError(
            _("Entry with the title '%(title)s' already exists."),
            params={'title': title}
        )


# form for creating a new wiki entry
class NewPageForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'id': 'newtitle'}), label="Title", validators=[validate_title])
    content = forms.CharField(widget=forms.Textarea(attrs={'id': 'newcontent'}), label="Content", required=True)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    
    # Headings - convert from .md format to .html format
    try:
        headings = re.findall(r'(#{1,6} [^\r\n]*)[\r\n(\r\n)]', content)
        for heading in headings:
            n = heading.count("#")
            content = re.sub(r'#{%d} ([^\r\n]*)[\r\n(\r\n)]' % n, rf'<h{str(n)}>\1</h{str(n)}>', content, count=1)
    except:
        pass

    # Bold
    try:
        content = re.sub(r'\*{2}([^\r\n]+?)\*{2}', r'<strong>\1</strong>', content)
        content = re.sub(r'_{2}([^\r\n]+?)_{2}', r'<strong>\1</strong>', content)
    except:
        pass

    # Unordered Lists
    try:
        content = re.sub(r'((\* ([^\r\n]*)[\r\n(\r\n)]+)+)', r'<ul>\n\1</ul>\n\n', content)
        content = re.sub(r'\* ([^\r\n]*)[\r\n(\r\n)]', r'<li>\1</li>', content)
    except:
        pass

    # Links
    try:
        content = re.sub(r'\[([^\r\n]+?)\]\(([^\r\n]+?)\)', r'<a href="\2">\1</a>', content)
    except:
        pass

    # Paragraphs
    try:
        content = re.sub(r'[\r\n]+([^\r\n<][^\r\n]*)[\r\n]+', r'\n<p>\1</p>\n', content)
        print(content)
    except:
        pass

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content
    })

def search(request):
    entries = util.list_entries()
    query = request.POST["q"]

    entries_lower = [entry.lower() for entry in entries]
    query_lower = query.lower()

    # redirect user to entry's page if search matches the entry name
    if query_lower in entries_lower:
        i = entries_lower.index(query_lower)
        return redirect(entry, title=entries[i])

    # find all matches to user's search
    matches = [entry for entry in entries if re.search(query, entry, re.IGNORECASE)]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches
    })

def new(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            # get the title and contents if form is valid
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # create and write to a new file for the new entry
            util.save_entry(title, content)

            # redirect user to the new entry's page
            return redirect(entry, title=title)

        else:
            # return all form data to user on same page if form is not valid
            return render(request, "encyclopedia/new.html", {
                "form": form
            })

    # GET request
    return render(request, "encyclopedia/new.html", {
        "form": NewPageForm()
    })

def edit(request):
    if request.method == "GET":
        # retrieve the title and contents for the entry
        title = request.GET["title"]
        content = util.get_entry(title)

        # and send it to the form for user to edit
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })

    else:
        title = request.POST["title"]
        content = request.POST["content"]

        # write to entry's file
        util.save_entry(title, content)

        # redirect user to entry's page
        return redirect(entry, title=title)

def random(request):
    # choose a random entry for user
    random = choice(util.list_entries())
    return redirect(entry, title=random)
