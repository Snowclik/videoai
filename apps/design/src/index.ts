import { SceneGraph } from "@open-pencil/scene-graph";

export function createGraphicDesign() {
  console.log("🎨 Inicializando motor de diseño vectorial OpenPencil...");
  
  const sg = new SceneGraph();
  console.log("✅ SceneGraph creado con éxito.");
  console.log(`📊 Nodos iniciales en el lienzo: ${sg.nodes.size}`);

  return sg;
}

createGraphicDesign();
