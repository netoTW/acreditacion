/**
 * Esquema de estado de la Plaza.
 *
 * ADR-004: el servidor NO sabe nada del render. Sincroniza un mundo en un plano 2D
 * medido en TILES, no en pixeles. Un render isometrico 2D proyecta (x, y); un render
 * 3D mapea (x, y) al plano del piso. Es el mismo estado.
 *
 * Por eso el spike prueba el SERVIDOR, no el render, y la decision 2D/3D (E-01)
 * queda fuera del camino critico.
 */
const { Schema, MapSchema, defineTypes } = require("@colyseus/schema");

/** Tamano del salon, en tiles. Coincide con la grilla 9x9 de la cascara. */
const MUNDO = { ancho: 9, alto: 9 };

/** Velocidad de caminata, en tiles por segundo. */
const VELOCIDAD = 2.4;

class Participante extends Schema {}
defineTypes(Participante, {
  id: "string",
  nombre: "string",
  cargo: "string",
  color: "string",
  // Posicion actual en el plano del mundo (tiles, continuo).
  x: "number",
  y: "number",
  // Destino al que camina. El cliente PIDE destino; el servidor DECIDE posicion.
  destinoX: "number",
  destinoY: "number",
  // Orientacion en el plano, en radianes. La usa el render 3D; el 2D la ignora.
  rot: "number",
  // Globo de habla.
  mensaje: "string",
  mensajeHasta: "number",
  conectadoEn: "number",
});

class EstadoPlaza extends Schema {
  constructor() {
    super();
    this.participantes = new MapSchema();
    this.anchoMundo = MUNDO.ancho;
    this.altoMundo = MUNDO.alto;
  }
}
defineTypes(EstadoPlaza, {
  participantes: { map: Participante },
  anchoMundo: "number",
  altoMundo: "number",
});

module.exports = { Participante, EstadoPlaza, MUNDO, VELOCIDAD };
