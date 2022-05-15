from wtforms import Form, StringField, SelectField


class MusicSearchForm(Form):
    choices = [('Artist', 'Artist'),
               ('Album', 'Album'),
               ('Song', 'Song')]
    select = SelectField('Search for music:', choices=choices)
    search = StringField('')