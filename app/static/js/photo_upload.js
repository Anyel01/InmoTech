
(function () {
  'use strict';

  const formulario = document.querySelector('[data-formulario-inmueble]');
  if (!formulario) return;

  const campo = formulario.querySelector('[data-fotos]');
  const entrada = formulario.querySelector('#fotos');
  const zona = formulario.querySelector('[data-zona-fotos]');
  const aviso = formulario.querySelector('[data-fotos-error]');
  const listaNuevas = formulario.querySelector('[data-fotos-nuevas]');
  const existentes = Array.from(formulario.querySelectorAll('[data-foto-existente]'));

  const MAX_FOTOS = Number(campo.dataset.max) || 8;
  const MAX_BYTES = 4 * 1024 * 1024;
  const TIPOS = ['image/jpeg', 'image/png', 'image/webp'];
  const ICONOS = { Casa: 'casa', Apartamento: 'apartamento', Lote: 'lote', Local: 'local' };

  let nuevas = []; // { archivo, url }

  function el(etiqueta, clases, texto) {
    const nodo = document.createElement(etiqueta);
    if (clases) nodo.className = clases;
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  function peso(bytes) {
    return bytes < 1024 * 1024
      ? Math.max(1, Math.round(bytes / 1024)) + ' KB'
      : (bytes / (1024 * 1024)).toFixed(1).replace('.', ',') + ' MB';
  }

  function mostrarAviso(mensaje) {
    aviso.textContent = mensaje;
    aviso.hidden = !mensaje;
  }

  function existenteQuitada(item) {
    return item.querySelector('input[name="quitar_fotos"]').checked;
  }

  function existentesVigentes() {
    return existentes.filter(function (item) { return !existenteQuitada(item); });
  }

  function fotosFinales() {
    const portada = formulario.querySelector('input[name="portada"]:checked');
    const vigentes = existentesVigentes();
    const elegida = portada && vigentes.find(function (item) {
      return item.querySelector('input[name="portada"]') === portada;
    });
    const ordenadas = elegida ? [elegida].concat(vigentes.filter(function (i) { return i !== elegida; })) : vigentes;

    return ordenadas
      .map(function (item) { return { url: item.dataset.url, descripcion: item.dataset.descripcion }; })
      .concat(nuevas.map(function (n, i) {
        return { url: n.url, descripcion: 'Foto nueva ' + (i + 1) + ': ' + n.archivo.name };
      }));
  }

  function sincronizarEntrada() {
    const transferencia = new DataTransfer();
    nuevas.forEach(function (n) { transferencia.items.add(n.archivo); });
    entrada.files = transferencia.files;
  }

  function agregar(archivos) {
    let problema = '';
    Array.from(archivos).forEach(function (archivo) {
      if (TIPOS.indexOf(archivo.type) === -1) {
        problema = '«' + archivo.name + '» no es una foto compatible. Usa JPG, PNG o WebP.';
      } else if (archivo.size > MAX_BYTES) {
        problema = '«' + archivo.name + '» pesa ' + peso(archivo.size) + '. Cada foto puede pesar hasta 4 MB.';
      } else if (nuevas.length + existentesVigentes().length >= MAX_FOTOS) {
        problema = 'Cada inmueble admite hasta ' + MAX_FOTOS + ' fotos. Quita alguna para agregar otra.';
      } else {
        nuevas.push({ archivo: archivo, url: URL.createObjectURL(archivo) });
      }
    });
    mostrarAviso(problema);
    refrescar();
  }

  function quitarNueva(posicion) {
    URL.revokeObjectURL(nuevas[posicion].url);
    nuevas.splice(posicion, 1);
    mostrarAviso('');
    refrescar();
  }

  function moverAlInicio(posicion) {
    nuevas.unshift(nuevas.splice(posicion, 1)[0]);
    refrescar();
  }

  function pintarNuevas() {
    listaNuevas.replaceChildren();
    const sinActuales = existentesVigentes().length === 0;

    nuevas.forEach(function (n, i) {
      const item = el('li', 'foto-item');
      if (sinActuales && i === 0) item.append(el('span', 'foto-marca', 'Portada'));

      const imagen = el('img');
      imagen.src = n.url;
      imagen.alt = 'Vista previa de ' + n.archivo.name;
      imagen.title = 'Ampliar';
      imagen.addEventListener('click', function () {
        const lista = fotosFinales();
        const inicio = existentesVigentes().length + i;
        if (window.InmoVisor) window.InmoVisor.abrir(lista, inicio);
      });

      const pie = el('div', 'foto-pie');
      const nombre = el('span', 'foto-nombre', n.archivo.name + ' · ' + peso(n.archivo.size));
      nombre.title = n.archivo.name;

      const acciones = el('div', 'foto-acciones');
      if (sinActuales && i > 0) {
        const portada = el('button', null, 'Usar de portada');
        portada.type = 'button';
        portada.addEventListener('click', function () { moverAlInicio(i); });
        acciones.append(portada);
      }
      const quitar = el('button', 'peligro', 'Quitar');
      quitar.type = 'button';
      quitar.setAttribute('aria-label', 'Quitar la foto ' + n.archivo.name);
      quitar.addEventListener('click', function () { quitarNueva(i); });
      acciones.append(quitar);

      pie.append(nombre, acciones);
      item.append(imagen, pie);
      listaNuevas.append(item);
    });
  }

  function pintarActuales() {
    const portada = formulario.querySelector('input[name="portada"]:checked');
    const vigentes = existentesVigentes();
    const elegida = vigentes.find(function (item) {
      return item.querySelector('input[name="portada"]') === portada;
    }) || vigentes[0];

    existentes.forEach(function (item) {
      item.classList.toggle('quitada', existenteQuitada(item));
      item.querySelector('[data-marca]').hidden = item !== elegida;
    });
  }

  existentes.forEach(function (item) {
    item.querySelector('img').addEventListener('click', function () {
      const url = item.dataset.url;
      const lista = fotosFinales();
      const posicion = lista.findIndex(function (f) { return f.url === url; });
      if (window.InmoVisor) window.InmoVisor.abrir(lista, Math.max(posicion, 0));
    });
  });

  formulario.addEventListener('change', function (e) {
    if (e.target.name === 'quitar_fotos' || e.target.name === 'portada') {
      mostrarAviso('');
      refrescar();
    }
  });

  const vp = {
    foto: document.querySelector('[data-vp-foto]'),
    icono: document.querySelector('[data-vp-icono]'),
    iconoContenedor: document.querySelector('[data-vp-icono]').parentElement,
    cabecera: document.querySelector('[data-vp-cabecera]'),
    operacion: document.querySelector('[data-vp-operacion]'),
    categoria: document.querySelector('[data-vp-categoria]'),
    precio: document.querySelector('[data-vp-precio]'),
    titulo: document.querySelector('[data-vp-titulo]'),
    ubicacion: document.querySelector('[data-vp-ubicacion]'),
    area: document.querySelector('[data-vp-area]'),
    habitaciones: document.querySelector('[data-vp-habitaciones]'),
    banos: document.querySelector('[data-vp-banos]')
  };

  const formatoPesos = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 });

  function textoSeleccionado(id) {
    const seleccion = formulario.querySelector('#' + id);
    return seleccion && seleccion.value ? seleccion.options[seleccion.selectedIndex].text.trim() : '';
  }

  function actualizarVistaPrevia() {
    const valor = function (id) { return formulario.querySelector('#' + id).value; };

    const operacion = valor('operacion');
    vp.operacion.textContent = operacion || 'VENTA';

    const categoria = textoSeleccionado('id_categoria');
    vp.categoria.textContent = categoria || 'Categoría';
    vp.icono.className = 'ico ico-' + (ICONOS[categoria] || 'apartamento');

    const precio = Number(valor('precio'));
    vp.precio.textContent = '$ ' + formatoPesos.format(precio > 0 ? precio : 0) + ' COP';
    vp.titulo.textContent = valor('titulo').trim() || 'Título de tu inmueble';

    const ciudad = textoSeleccionado('id_ciudad');
    const departamento = textoSeleccionado('id_departamento');
    vp.ubicacion.textContent = [ciudad, departamento].filter(Boolean).join(', ') || 'Ciudad, departamento';

    vp.area.textContent = valor('area') || '0';
    vp.habitaciones.textContent = valor('habitaciones') || '0';
    vp.banos.textContent = valor('banos') || '0';

    const portada = fotosFinales()[0];
    vp.foto.hidden = !portada;
    vp.iconoContenedor.hidden = !!portada;
    vp.cabecera.classList.toggle('property-header--foto', !!portada);
    if (portada) vp.foto.src = portada.url;
  }

  formulario.addEventListener('input', actualizarVistaPrevia);
  formulario.addEventListener('change', actualizarVistaPrevia);

  function refrescar() {
    sincronizarEntrada();
    pintarActuales();
    pintarNuevas();
    actualizarVistaPrevia();
  }

  entrada.addEventListener('change', function () {
    const elegidas = Array.from(entrada.files);
    const previas = nuevas.map(function (n) { return n.archivo; });
    const soloNuevas = elegidas.filter(function (archivo) { return previas.indexOf(archivo) === -1; });
    agregar(soloNuevas);
  });

  ['dragenter', 'dragover'].forEach(function (evento) {
    zona.addEventListener(evento, function (e) {
      e.preventDefault();
      zona.classList.add('arrastrando');
    });
  });
  ['dragleave', 'drop'].forEach(function (evento) {
    zona.addEventListener(evento, function () { zona.classList.remove('arrastrando'); });
  });
  zona.addEventListener('drop', function (e) {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files.length) agregar(e.dataTransfer.files);
  });

  refrescar();
})();
