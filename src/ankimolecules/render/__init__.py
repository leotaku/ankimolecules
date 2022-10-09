from operator import truth
import pandas

from aiohttp import web
from pathlib import Path

routes = web.RouteTableDef()
routes.static("/assets", Path(__file__).parent / "assets")


@routes.get("/")
async def index_redirect(request):
    raise web.HTTPFound("/assets/index.html")


notes = pandas.read_csv("ankimolecules.csv")
notes = notes.where(pandas.notnull(notes), "")


@routes.get("/api/suggest/{index}")
async def get_suggestion(request):
    index = int(request.match_info["index"])
    try:
        name = notes["PubChem Name"].iloc[index]
    except IndexError:
        return web.Response(status=404)

    return web.Response(text=name)


@routes.get("/api/{name}_2d.sdf")
async def get_sdf_2d(request):
    name = request.match_info["name"]
    sdf = notes[notes["PubChem Name"] == name]["SDF2D"].iloc[0]

    return web.Response(text=sdf)


@routes.get("/api/{name}_3d.sdf")
async def get_sdf_3d(request):
    name = request.match_info["name"]
    sdf = notes[notes["PubChem Name"] == name]["SDF3D"].iloc[0]

    return web.Response(text=sdf)


@routes.post("/api/{name}.png")
async def post_png(request):
    name = request.match_info["name"]
    Path("downloads").mkdir(parents=True, exist_ok=True)
    filepath = Path("downloads") / f"{name}.png"
    filepath.write_bytes(await request.read())

    return web.Response()


def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == "__main__":
    main()
