
(function () {
  'use strict';

  const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)');

  function el(etiqueta, clases, atributos) {
    const nodo = document.createElement(etiqueta);
    if (clases) nodo.className = clases;
    if (atributos) {
      Object.keys(atributos).forEach(function (nombre) {
        if (atributos[nombre] !== null && atributos[nombre] !== undefined) {
          nodo.setAttribute(nombre, atributos[nombre]);
        }
      });
    }
    return nodo;
  }

  function icono(nombre) {
    return el('span', 'ico ico-' + nombre, { 'aria-hidden': 'true' });
  }

  function botonRedondo(clases, etiqueta, nombreIcono) {
    const boton = el('button', 'control-redondo ' + clases, { type: 'button', 'aria-label': etiqueta });
    boton.append(icono(nombreIcono));
    return boton;
  }

  function bloquearPagina(bloquear) {
    document.documentElement.classList.toggle('con-modal', bloquear);
  }

  const Visor = (function () {
    let dialogo, imagen, pie, contador, anterior, siguiente;
    let fotos = [];
    let indice = 0;
    let alCerrar = null;

    function mostrar() {
      const foto = fotos[indice];
      imagen.src = foto.url;
      imagen.alt = foto.descripcion;
      pie.textContent = foto.descripcion;
      contador.textContent = (indice + 1) + ' / ' + fotos.length;
      const unica = fotos.length < 2;
      anterior.hidden = unica;
      siguiente.hidden = unica;
      contador.hidden = unica;

      // Carga por adelantado las vecinas para que el cambio sea inmediato
      [indice - 1, indice + 1].forEach(function (i) {
        if (fotos[i]) new Image().src = fotos[i].url;
      });
    }

    function ir(n) {
      indice = (n + fotos.length) % fotos.length;
      mostrar();
    }

    function construir() {
      dialogo = el('dialog', 'visor', { 'aria-label': 'Foto ampliada' });
      const marco = el('div', 'visor-marco');
      const zona = el('div', 'visor-imagen');
      imagen = el('img');
      zona.append(imagen);

      const cerrar = botonRedondo('visor-cerrar', 'Cerrar la foto ampliada', 'cerrar');
      anterior = botonRedondo('galeria-flecha galeria-prev', 'Foto anterior', 'flecha-izq');
      siguiente = botonRedondo('galeria-flecha galeria-next', 'Foto siguiente', 'flecha-der');

      const barra = el('div', 'visor-pie');
      pie = el('p');
      contador = el('span', 'galeria-contador');
      barra.append(pie, contador);

      marco.append(zona, barra, cerrar, anterior, siguiente);
      dialogo.append(marco);

      cerrar.addEventListener('click', function () { dialogo.close(); });
      anterior.addEventListener('click', function () { ir(indice - 1); });
      siguiente.addEventListener('click', function () { ir(indice + 1); });

      dialogo.addEventListener('click', function (e) {
        if (e.target === dialogo || e.target === marco || e.target === zona) dialogo.close();
      });
      dialogo.addEventListener('keydown', function (e) {
        if (fotos.length < 2) return;
        if (e.key === 'ArrowLeft') { ir(indice - 1); e.preventDefault(); }
        if (e.key === 'ArrowRight') { ir(indice + 1); e.preventDefault(); }
      });
      dialogo.addEventListener('close', function () {
        // Si hay otra ventana modal debajo (vista rápida) la página sigue bloqueada
        if (!document.querySelector('dialog[open]')) bloquearPagina(false);
        if (alCerrar) alCerrar(indice);
        alCerrar = null;
      });

      document.body.append(dialogo);
    }

    function abrir(lista, inicio, cuandoCierre) {
      if (!lista || !lista.length) return;
      if (!dialogo) construir();
      fotos = lista;
      indice = inicio || 0;
      alCerrar = cuandoCierre || null;
      mostrar();
      bloquearPagina(true);
      dialogo.showModal();
    }

    return { abrir: abrir };
  })();

  window.InmoVisor = Visor;

  function iniciarCarrusel(raiz) {
    const escenario = raiz.querySelector('.galeria-escenario');
    const pista = raiz.querySelector('.galeria-pista');
    const slides = Array.from(raiz.querySelectorAll('.galeria-slide'));
    const miniaturas = Array.from(raiz.querySelectorAll('.galeria-miniaturas button'));
    const tiraMiniaturas = raiz.querySelector('.galeria-miniaturas');
    const pie = raiz.querySelector('[data-pie]');
    const contador = raiz.querySelector('[data-contador]');
    const anuncio = raiz.querySelector('[data-anuncio]');
    const total = slides.length;
    let actual = 0;

    raiz.dataset.total = total;
    if (!total) return null;

    function fotos() {
      return slides.map(function (slide) {
        const img = slide.querySelector('img');
        return { url: img.src, descripcion: img.alt };
      });
    }

    function ir(n, avisar) {
      actual = (n + total) % total;
      pista.style.transform = 'translateX(' + (-100 * actual) + '%)';

      slides.forEach(function (slide, i) {
        slide.toggleAttribute('inert', i !== actual);
      });
      miniaturas.forEach(function (miniatura, i) {
        miniatura.setAttribute('aria-current', i === actual ? 'true' : 'false');
      });

      const descripcion = slides[actual].querySelector('img').alt;
      if (pie) pie.textContent = descripcion;
      if (contador) contador.textContent = (actual + 1) + ' / ' + total;
      if (avisar && anuncio) anuncio.textContent = 'Foto ' + (actual + 1) + ' de ' + total + ': ' + descripcion;

      const activa = miniaturas[actual];
      if (activa && tiraMiniaturas) {
        tiraMiniaturas.scrollTo({
          left: activa.offsetLeft - (tiraMiniaturas.clientWidth - activa.offsetWidth) / 2,
          behavior: reducirMovimiento.matches ? 'auto' : 'smooth'
        });
      }
    }

    function ampliar() {
      Visor.abrir(fotos(), actual, function (indiceFinal) { ir(indiceFinal, false); });
    }

    const anterior = raiz.querySelector('.galeria-prev');
    const siguiente = raiz.querySelector('.galeria-next');
    if (anterior) anterior.addEventListener('click', function () { ir(actual - 1, true); });
    if (siguiente) siguiente.addEventListener('click', function () { ir(actual + 1, true); });
    miniaturas.forEach(function (miniatura, i) {
      miniatura.addEventListener('click', function () { ir(i, true); });
    });

    const expandir = raiz.querySelector('.galeria-expandir');
    if (expandir) expandir.addEventListener('click', ampliar);

    raiz.addEventListener('keydown', function (e) {
      if (e.target.closest('input, textarea, select')) return;
      if (e.key === 'ArrowLeft') { ir(actual - 1, true); e.preventDefault(); }
      else if (e.key === 'ArrowRight') { ir(actual + 1, true); e.preventDefault(); }
      else if (e.key === 'Home') { ir(0, true); e.preventDefault(); }
      else if (e.key === 'End') { ir(total - 1, true); e.preventDefault(); }
    });

    // Deslizar con el dedo o arrastrar con el mouse; un toque sin movimiento amplía
    let inicioX = null;
    let arrastro = false;
    escenario.addEventListener('pointerdown', function (e) {
      if (e.target.closest('button')) return;
      inicioX = e.clientX;
      arrastro = false;
    });
    escenario.addEventListener('pointermove', function (e) {
      if (inicioX !== null && Math.abs(e.clientX - inicioX) > 10) arrastro = true;
    });
    escenario.addEventListener('pointerup', function (e) {
      if (inicioX === null) return;
      const desplazamiento = e.clientX - inicioX;
      inicioX = null;
      if (Math.abs(desplazamiento) > 45) ir(actual + (desplazamiento < 0 ? 1 : -1), true);
    });
    escenario.addEventListener('pointercancel', function () { inicioX = null; });
    escenario.addEventListener('click', function (e) {
      if (e.target.closest('button')) return;
      if (arrastro) { arrastro = false; return; }
      ampliar();
    });

    ir(0, false);
    return { ir: ir };
  }

  function construirGaleria(titulo, imagenes) {
    const raiz = el('section', 'galeria', { 'aria-roledescription': 'carrusel', 'aria-label': 'Fotos de ' + titulo });
    const escenario = el('div', 'galeria-escenario');
    const pista = el('ul', 'galeria-pista');

    imagenes.forEach(function (foto, i) {
      const slide = el('li', 'galeria-slide', {
        role: 'group',
        'aria-roledescription': 'diapositiva',
        'aria-label': (i + 1) + ' de ' + imagenes.length
      });
      slide.append(el('img', null, {
        src: foto.url, alt: foto.descripcion, width: 1600, height: 1000,
        loading: i === 0 ? 'eager' : 'lazy', draggable: 'false'
      }));
      pista.append(slide);
    });

    const info = el('div', 'galeria-info');
    info.append(el('p', 'galeria-pie', { 'data-pie': '' }), el('span', 'galeria-contador', { 'data-contador': '' }));

    escenario.append(
      pista, info,
      botonRedondo('galeria-expandir', 'Ampliar la foto', 'ampliar'),
      botonRedondo('galeria-flecha galeria-prev', 'Foto anterior', 'flecha-izq'),
      botonRedondo('galeria-flecha galeria-next', 'Foto siguiente', 'flecha-der')
    );
    raiz.append(escenario);

    const tira = el('ol', 'galeria-miniaturas');
    imagenes.forEach(function (foto, i) {
      const item = el('li');
      const boton = el('button', null, { type: 'button', 'aria-label': 'Ver la foto ' + (i + 1) + ': ' + foto.descripcion });
      boton.append(el('img', null, { src: foto.url, alt: '', loading: 'lazy' }));
      item.append(boton);
      tira.append(item);
    });
    raiz.append(tira, el('div', 'sr-only', { 'aria-live': 'polite', 'data-anuncio': '' }));
    return raiz;
  }

  const VistaRapida = (function () {
    const cache = new Map();
    let dialogo, cuerpo;

    function construir() {
      dialogo = el('dialog', 'rapida', { 'aria-labelledby': 'rapida-titulo' });
      const cerrar = botonRedondo('rapida-cerrar', 'Cerrar la vista rápida', 'cerrar');
      cuerpo = el('div');
      dialogo.append(cerrar, cuerpo);

      cerrar.addEventListener('click', function () { dialogo.close(); });
      dialogo.addEventListener('click', function (e) { if (e.target === dialogo) dialogo.close(); });
      dialogo.addEventListener('close', function () {
        if (!document.querySelector('dialog[open]')) bloquearPagina(false);
      });
      document.body.append(dialogo);
    }

    function estado(mensaje, enlace) {
      cuerpo.className = 'rapida-estado';
      cuerpo.replaceChildren();
      const texto = el('p', 'rapida-titulo-estado', { id: 'rapida-titulo' });
      texto.textContent = mensaje;
      cuerpo.append(texto);
      if (enlace) {
        const a = el('a', 'btn btn-primary', { href: enlace });
        a.textContent = 'Abrir el detalle completo';
        cuerpo.append(a);
      }
    }

    function dato(nombreIcono, texto) {
      const li = el('li');
      li.append(icono(nombreIcono), document.createTextNode(' ' + texto));
      return li;
    }

    function pintar(datos) {
      cuerpo.className = 'rapida-cuerpo';
      cuerpo.replaceChildren();

      const fotos = el('div', 'rapida-fotos');
      if (datos.imagenes.length) {
        const galeria = construirGaleria(datos.titulo, datos.imagenes);
        fotos.append(galeria);
        iniciarCarrusel(galeria);
      } else {
        const vacio = el('p', 'rapida-estado');
        vacio.textContent = 'Este inmueble todavía no tiene fotos.';
        fotos.append(vacio);
      }

      const info = el('div', 'rapida-info');
      const etiquetas = el('div', 'rapida-etiquetas');
      [datos.operacion, datos.categoria].forEach(function (texto) {
        const etiqueta = el('span', 'badge');
        etiqueta.textContent = texto;
        etiquetas.append(etiqueta);
      });

      const titulo = el('h2', null, { id: 'rapida-titulo' });
      titulo.textContent = datos.titulo;
      const precio = el('div', 'rapida-precio');
      precio.textContent = datos.precio;

      const datosLista = el('ul', 'rapida-datos');
      datosLista.append(dato('ubicacion', datos.ubicacion), dato('area', datos.area + ' m²'));
      if (datos.habitaciones > 0) datosLista.append(dato('cama', datos.habitaciones + ' hab'));
      if (datos.banos > 0) datosLista.append(dato('ducha', datos.banos + ' baños'));

      const descripcion = el('p', 'rapida-descripcion');
      descripcion.textContent = datos.descripcion;

      const acciones = el('div', 'rapida-acciones');
      const detalle = el('a', 'btn btn-primary', { href: datos.url });
      detalle.textContent = 'Ver detalle completo';
      const cerrar = el('button', 'btn btn-outline', { type: 'button' });
      cerrar.textContent = 'Cerrar';
      cerrar.addEventListener('click', function () { dialogo.close(); });
      acciones.append(detalle, cerrar);

      info.append(etiquetas, titulo, precio, datosLista, descripcion, acciones);
      cuerpo.append(fotos, info);
    }

    async function abrir(id, urlDetalle) {
      if (!dialogo) construir();
      estado('Cargando el inmueble…');
      bloquearPagina(true);
      dialogo.showModal();

      try {
        let datos = cache.get(id);
        if (!datos) {
          const respuesta = await fetch('/api/inmuebles/' + id);
          if (!respuesta.ok) throw new Error('respuesta ' + respuesta.status);
          datos = await respuesta.json();
          cache.set(id, datos);
        }
        pintar(datos);
      } catch (error) {
        console.error(error);
        estado('No pudimos cargar la vista rápida. Revisa tu conexión o abre el detalle completo.', urlDetalle);
      }
    }

    return { abrir: abrir };
  })();


  function iniciarTarjetas(raiz) {
    const pista = raiz.querySelector('.tarjetas-pista');
    const anterior = raiz.querySelector('[data-tarjetas-prev]');
    const siguiente = raiz.querySelector('[data-tarjetas-next]');
    if (!pista || !anterior || !siguiente) return;

    function actualizar() {
      anterior.disabled = pista.scrollLeft <= 4;
      siguiente.disabled = pista.scrollLeft + pista.clientWidth >= pista.scrollWidth - 4;
    }

    function mover(sentido) {
      pista.scrollBy({
        left: sentido * Math.max(pista.clientWidth * 0.85, 280),
        behavior: reducirMovimiento.matches ? 'auto' : 'smooth'
      });
    }

    anterior.addEventListener('click', function () { mover(-1); });
    siguiente.addEventListener('click', function () { mover(1); });
    pista.addEventListener('scroll', actualizar, { passive: true });
    window.addEventListener('resize', actualizar);
    actualizar();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-carrusel]').forEach(iniciarCarrusel);
    document.querySelectorAll('[data-tarjetas]').forEach(iniciarTarjetas);
  });

  document.addEventListener('click', function (e) {
    const boton = e.target.closest('[data-vista-rapida]');
    if (!boton) return;
    VistaRapida.abrir(boton.dataset.vistaRapida, boton.dataset.urlDetalle);
  });
})();
