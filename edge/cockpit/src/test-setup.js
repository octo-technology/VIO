// happy-dom does not implement visualViewport; Vuetify overlays need it.
if (!window.visualViewport) {
  const et = new EventTarget()
  window.visualViewport = Object.assign(et, {
    offsetTop: 0,
    offsetLeft: 0,
    width: 1024,
    height: 768,
    scale: 1,
  })
}
