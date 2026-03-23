constructor() {
    if (Config.#instance) {
        throw new Error('Use Config.getInstance() instead of new.');
    }
    // ...
    Config.#instance = this;
    Object.freeze(this);
}

static getInstance() {
    if (!Config.#instance) {
        Config.#instance = new Config();
    }
    return Config.#instance;
}
