import { createStage, generateImage } from "./nglrender.js";

function makeViewer(target) {
  let viewACS = new ChemDoodle.ViewerCanvas(target, 3000, 3000);
  viewACS.styles.backgroundColor = "#00000000";
  viewACS.styles.bonds_width_2D = 0.6;
  viewACS.styles.bonds_saturationWidthAbs_2D = 2.6;
  viewACS.styles.bonds_hashSpacing_2D = 2.5;
  viewACS.styles.atoms_font_size_2D = 10;
  viewACS.styles.atoms_font_families_2D = ["Helvetica", "Arial", "sans-serif"];
  viewACS.styles.bonds_symmetrical_2D = false;
  viewACS.styles.bonds_clearOverlaps_2D = true;
  viewACS.styles.bonds_lewisStyle_2D = false;
  viewACS.styles.atoms_usePYMOLColors = true;
  viewACS.styles.atoms_displayTerminalCarbonLabels_2D = false;
  viewACS.styles.atoms_implicitHydrogens_2D = true;
  viewACS.repaint();

  return viewACS;
}

async function generateImage2d(url, viewer, foo) {
  let data = await fetch(url).then((it) => it.text());
  let mol = ChemDoodle.readMOL(data, 1);

  let hd = new ChemDoodle.informatics.HydrogenDeducer();
  hd.removeHydrogens(mol);
  mol.scaleToAverageBondLength(14.4);

  viewer.loadMolecule(mol);
  viewer.styles.scale = 10;
  viewer.repaint();
  let dataurl = document.getElementById(foo).toDataURL("image/png");
  // viewer.removeMolecule(mol);

  return fetch(dataurl).then((it) => it.blob());
}

let stage = createStage("viewport");

for (let i = 0; ; i++) {
  let name = await fetch(`/api/suggest/${i}`).then((it) => {
    if (it.ok) {
      return it.text();
    } else {
      throw Error("foo");
    }
  });

  let image3d = await generateImage(`/api/${name}_3d.sdf`, stage);
  fetch(`/api/${name}_3d.png`, {
    method: "POST",
    headers: { "Content-Type": "image/png" },
    body: image3d,
  });

  let viewer = makeViewer("render2d");
  let image2d = await generateImage2d(
    `/api/${name}_2d.sdf`,
    viewer,
    "render2d"
  );
  fetch(`/api/${name}_2d.png`, {
    method: "POST",
    headers: { "Content-Type": "image/png" },
    body: image2d,
  });
}
