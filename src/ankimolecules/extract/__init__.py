import asyncio
import pandas
import aiohttp
import tempfile
import shutil

from ankipandas import Collection, find_db
from pathlib import Path
from tqdm import tqdm


async def getPubChemSDF(name, record_type, session):
    resp = await session.get(
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/json"
    )
    json = await resp.json()
    identifiers = json["IdentifierList"]["CID"]
    if len(identifiers) != 1:
        raise Exception("Incorrect or imprecise identifier")
    resp = await session.get(
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{identifiers[0]}/sdf?record_type={record_type}"
    )

    if resp.status == 404:
        resp = await session.get(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{identifiers[0]}/sdf?record_type=2d"
        )

    if resp.ok:
        return await resp.text()
    else:
        return ""


async def extract(col):
    # Only consider Auto-Molecule type notes
    notes = col.notes.fields_as_columns()
    notes = notes.query("nmodel=='Auto-Molecule'")

    # Join with cards to get access to deck information
    cards = col.cards[["cdeck", "nid"]].drop_duplicates()
    merged = pandas.merge(notes, cards, on="nid")
    if len(merged) != len(notes):
        raise Exception("Some cards of the same note seem to be in different decks")
    notes = merged

    # Change deck names to user-readable format
    notes["cdeck"] = notes["cdeck"].apply(lambda field: "::".join(field.split("\x1f")))

    # Simplify notes model
    notes = notes[
        [
            "cdeck",
            "nguid",
            "nfld_PubChem Name",
            "nfld_Pretty Name",
            "nfld_Unstructured Data",
        ]
    ].rename(
        columns={
            "nfld_PubChem Name": "PubChem Name",
            "nfld_Pretty Name": "Pretty Name",
            "nfld_Unstructured Data": "Unstructured Data",
        }
    )

    # Download SDF from PubChem
    async with aiohttp.ClientSession() as session:
        for i, row in tqdm(notes.iterrows()):
            notes.at[i, "SDF2D"] = await getPubChemSDF(
                row["PubChem Name"], "2d", session
            )
            notes.at[i, "SDF3D"] = await getPubChemSDF(
                row["PubChem Name"], "3d", session
            )

    # Save to disk
    notes.to_csv("ankimolecules.csv")


def main():
    # Open copy of database so we can keep Anki open
    original_db = find_db()
    with tempfile.TemporaryDirectory() as dirname:
        temp_db = shutil.copy(original_db, Path(dirname))
        col = Collection(path=temp_db)
        asyncio.run(extract(col))
