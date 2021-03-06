/* globals socket */

/* exported armorController */
const armorController = (() => {
  'use strict';
  const DOM = {};

  /* PUBLIC METHODS */
  function init() {
    cacheDom();
    bindSocketIOEvents();
  }

  /* PRIVATE METHODS */
  function bindSocketIOEvents() {
    socket.on('logging', (log) => {
      const logNode = document.createTextNode(log + '\n');
      DOM.$log.appendChild(logNode);
      DOM.$log.parentElement.scrollTop = DOM.$log.parentElement.scrollHeight;
    });
  }

  function cacheDom() {
    DOM.$log = document.getElementById('log');
  }

  return {
    init: init
  };
})();
