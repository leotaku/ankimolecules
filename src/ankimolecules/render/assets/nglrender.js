import * as NGL from "./vendored/ngl.js";

export function createStage(id) {
  // Create NGL Stage object
  let stage = new NGL.Stage(id, { backgroundColor: "white" });

  // Handle window resizing
  window.addEventListener(
    "resize",
    function (event) {
      stage.handleResize();
    },
    false
  );

  return stage;
}

async function displayMolecule(stage, url) {
  stage.removeAllComponents();
  await stage
    .loadFile(url, { defaultRepresentation: false })
    .then((o) => {
      o.addRepresentation("ball+stick");
      stage.autoView();
    })
    .catch(() => {
      stage.loadFile(url, { defaultRepresentation: true }).then((o) => {
        stage.autoView();
      });
    });

  await new Promise((resolve) => setTimeout(resolve, 100));
  let zoom = stage.getZoom();
  stage.animationControls.zoom(zoom - zoom / 3, 0);
  await new Promise((resolve) => setTimeout(resolve, 100));
}

async function generateSingleImage(stage) {
  let blob = await stage.makeImage({
    antialias: true,
    transparent: true,
    trim: false,
    factor: 1,
  });
  return await createImageBitmap(blob);
}

export async function generateImage(url, stage) {
  let canvas = document.getElementById("render3d");
  let ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  await displayMolecule(stage, url);

  let img = await generateSingleImage(stage);
  canvas.height = img.height * 1.5;
  canvas.width = img.width * 2;

  ctx.drawImage(img, 0, 0);

  stage.viewerControls.spin([0, 1, 0], Math.PI * 0.9);
  stage.viewerControls.spin([1, 0, 0], Math.PI * 0.7);
  img = await generateSingleImage(stage);
  ctx.drawImage(img, 720, 0);

  stage.viewerControls.spin([0, 1, 0], Math.PI * 0.9);
  stage.viewerControls.spin([1, 0, 0], Math.PI * 0.2);
  img = await generateSingleImage(stage);
  ctx.drawImage(img, 480 - 180, 480);

  let resp = await fetch(canvas.toDataURL("image/png"));
  return await resp.blob();
}
