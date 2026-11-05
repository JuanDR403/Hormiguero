(() => {
  const SVG = "http://www.w3.org/2000/svg";
  const HORMIGAS_POR_RUTA = 2;
  const MONEDAS_POR_RUTA = 3;
  const ESTADOS = ["Buscando migajas", "Cargando provisiones", "Volviendo al hormiguero", "Vigilando el camino"];

  const escena = document.getElementById("escena-hormigas");
  const capaHormigas = document.getElementById("capa-hormigas");
  const capaMonedas = document.getElementById("capa-monedas");
  const panel = document.getElementById("panel-simulacion");
  const boton = document.getElementById("alternar-simulacion");
  const ficha = document.getElementById("ficha-hormiga");

  const crear = (etiqueta, atributos) => {
    const elemento = document.createElementNS(SVG, etiqueta);
    Object.entries(atributos).forEach(([nombre, valor]) => elemento.setAttribute(nombre, valor));
    return elemento;
  };

  const ubicar = (hormiga) => {
    const punto = hormiga.ruta.getPointAtLength(hormiga.distancia);
    const siguiente = hormiga.ruta.getPointAtLength(hormiga.distancia + 1);
    const angulo = (Math.atan2(siguiente.y - punto.y, siguiente.x - punto.x) * 180) / Math.PI;
    hormiga.nodo.setAttribute("transform", `translate(${punto.x} ${punto.y}) rotate(${angulo})`);
  };

  const mostrarFicha = (hormiga) => {
    const titulo = document.createElement("strong");
    titulo.textContent = `Hormiga #${String(hormiga.id).padStart(2, "0")}`;
    ficha.replaceChildren(
      titulo,
      `Carga: ${hormiga.carga === 1 ? "1 moneda" : `${hormiga.carga} monedas`}`,
      document.createElement("br"),
      `Estado: ${hormiga.estado}`,
    );
    ficha.hidden = false;

    const caja = hormiga.nodo.getBoundingClientRect();
    const margen = 8;
    const x = caja.left + caja.width / 2 - ficha.offsetWidth / 2;
    const y = caja.top - ficha.offsetHeight - margen;
    ficha.style.left = `${Math.max(margen, Math.min(x, innerWidth - ficha.offsetWidth - margen))}px`;
    ficha.style.top = `${y < margen ? caja.bottom + margen : y}px`;
  };

  const crearHormiga = (ruta, longitud, id, indice) => {
    const nodo = crear("g", { class: "hormiga" });
    nodo.append(
      crear("circle", { class: "hormiga-zona", r: 22 }),
      crear("use", { href: "#hormiga", x: -15, y: -10, width: 30, height: 20 }),
    );

    const hormiga = {
      id,
      ruta,
      longitud,
      nodo,
      distancia: (longitud * (indice + Math.random() * 0.5)) / HORMIGAS_POR_RUTA,
      velocidad: 0.03 + Math.random() * 0.025,
      carga: Math.floor(Math.random() * 4),
      estado: ESTADOS[id % ESTADOS.length],
      detenida: false,
    };

    if (hormiga.carga > 0) {
      nodo.append(crear("use", { href: "#moneda", x: -13, y: -6, width: 12, height: 12 }));
    }
    nodo.addEventListener("mouseenter", () => {
      hormiga.detenida = true;
      mostrarFicha(hormiga);
    });
    nodo.addEventListener("mouseleave", () => {
      hormiga.detenida = false;
      ficha.hidden = true;
    });

    capaHormigas.append(nodo);
    ubicar(hormiga);
    return hormiga;
  };

  let siguienteId = 1;
  const hormigas = [...escena.querySelectorAll(".ruta")].flatMap((ruta) => {
    const longitud = ruta.getTotalLength();
    for (let i = 1; i <= MONEDAS_POR_RUTA; i += 1) {
      const punto = ruta.getPointAtLength((longitud * i) / (MONEDAS_POR_RUTA + 1));
      capaMonedas.append(crear("use", { href: "#moneda", x: punto.x - 9, y: punto.y - 9, width: 18, height: 18 }));
    }
    return Array.from({ length: HORMIGAS_POR_RUTA }, (_, indice) => crearHormiga(ruta, longitud, siguienteId++, indice));
  });

  let pausada = false;
  const actualizarPausa = (valor) => {
    pausada = valor;
    boton.textContent = pausada ? "Reanudar hormigas" : "Pausar hormigas";
  };
  boton.addEventListener("click", () => actualizarPausa(!pausada));
  actualizarPausa(matchMedia("(prefers-reduced-motion: reduce)").matches);
  panel.hidden = false;

  let anterior = performance.now();
  const avanzar = (ahora) => {
    const transcurrido = Math.min(ahora - anterior, 50);
    anterior = ahora;
    if (!pausada) {
      hormigas.filter((hormiga) => !hormiga.detenida).forEach((hormiga) => {
        hormiga.distancia = (hormiga.distancia + hormiga.velocidad * transcurrido) % hormiga.longitud;
        ubicar(hormiga);
      });
    }
    requestAnimationFrame(avanzar);
  };
  requestAnimationFrame(avanzar);
})();
