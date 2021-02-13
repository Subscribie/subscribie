// Define cusom element
// See https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_templates_and_slots
customElements.define('google-signin',
  class extends HTMLElement {
    constructor() {
      super();
      let template = document.getElementById('google-signin-template');
      let templateContent = template.content;

      const shadowRoot = this.attachShadow({mode: 'open'})
        .appendChild(templateContent.cloneNode(true));
    }
  }
);
