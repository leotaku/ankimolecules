import genanki
import pandas
import html

from pathlib import Path

model = genanki.Model(
    1645791274,
    "Auto-Molecule",
    fields=[
        {"name": "Pretty Name"},
        {"name": "PubChem Name"},
        {"name": "Unstructured Data"},
        {"name": "3D SDF"},
        {"name": "2D SDF"},
        {"name": "3D Image"},
        {"name": "2D Image"},
    ],
    templates=[
        {
            "name": "3D to Name",
            "qfmt": "{{3D Image}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Pretty Name}}',
        },
        {
            "name": "2D to Name",
            "qfmt": "{{2D Image}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Pretty Name}}',
        },
    ],
    css="""
.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
""",
)


class Note(genanki.Note):
    def __init__(self, fixed_guid, **kwargs):
        self.fixed_guid = fixed_guid
        super().__init__(model=model, **kwargs)

    @property
    def guid(self):
        return self.fixed_guid


def main():
    notes = pandas.read_csv("ankimolecules.csv")
    notes = notes.where(pandas.notnull(notes), "")
    notes["SDF3D"] = notes["SDF3D"].apply(lambda it: html.escape(it))
    notes["SDF2D"] = notes["SDF2D"].apply(lambda it: html.escape(it))
    notes["embed3d"] = notes["PubChem Name"].apply(lambda it: f'<img src="{it}_3d.png">')
    notes["embed2d"] = notes["PubChem Name"].apply(lambda it: f'<img src="{it}_2d.png">')
    notes["note"] = notes.apply(
        lambda row: Note(
            row["nguid"],
            fields=[
                row["Pretty Name"],
                row["PubChem Name"],
                row["Unstructured Data"],
                row["SDF3D"],
                row["SDF2D"],
                row["embed3d"],
                row["embed2d"],
            ],
        ),
        axis=1,
    )

    decks = []
    for index, (deckname, frame) in enumerate(notes.groupby("cdeck")):
        deck = genanki.Deck(index + 1, deckname)
        for note in frame["note"]:
            deck.add_note(note)
        decks.append(deck)

    package = genanki.Package(decks)
    package.media_files = Path("downloads").glob("*.png")
    package.write_to_file("ankimolecules.apkg")
