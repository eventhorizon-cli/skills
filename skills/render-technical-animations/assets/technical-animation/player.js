/* Shared playback controls. Scene state is derived only from the supplied time. */
(() => {
  "use strict";
  const defaults = { play: "Play", pause: "Pause", replay: "Replay", timeline: "Timeline", speed: "Playback speed", language: "Language" };

  window.createTechnicalAnimation = ({ root = document, duration, languages, render }) => {
    if (!Number.isFinite(duration) || duration <= 0 || typeof render !== "function") {
      throw new Error("A positive duration and a render function are required.");
    }
    const languageKeys = Object.keys(languages || {});
    if (!languageKeys.length) throw new Error("At least one language is required.");
    const queryLanguage = new URLSearchParams(location.search).get("lang");
    let language = languageKeys.includes(queryLanguage) ? queryLanguage : languageKeys[0];
    const control = name => root.querySelector(`[data-control="${name}"]`);
    const playButton = control("play"), timeline = control("timeline"), timeOutput = control("time");
    const speedSelect = control("speed"), languageSelect = control("language");
    const motionPreference = matchMedia("(prefers-reduced-motion: reduce)");
    const listeners = [];
    let time = 0, speed = 1, playing = false, frame = null, previous = null, destroyed = false;

    const on = (element, event, handler) => {
      if (!element) return;
      element.addEventListener(event, handler);
      listeners.push(() => element.removeEventListener(event, handler));
    };
    const state = () => ({ time, duration, progress: time / duration, speed, language, playing });
    const draw = () => {
      if (destroyed) return;
      render(state());
      if (timeline) timeline.value = String(time);
      if (timeOutput) timeOutput.textContent = `${time.toFixed(1)} / ${duration.toFixed(1)} s`;
      if (playButton) {
        playButton.textContent = languages[language][playing ? "pause" : "play"] || defaults[playing ? "pause" : "play"];
        playButton.setAttribute("aria-pressed", String(playing));
      }
    };
    const tick = timestamp => {
      frame = null;
      if (!playing || destroyed) return;
      if (previous !== null) time = (time + (timestamp - previous) * speed / 1000) % duration;
      previous = timestamp;
      draw();
      frame = requestAnimationFrame(tick);
    };
    const pause = () => {
      playing = false;
      previous = null;
      if (frame !== null) cancelAnimationFrame(frame);
      frame = null;
      draw();
    };
    const play = () => {
      if (playing || destroyed) return;
      if (time >= duration) time = 0;
      playing = true;
      previous = null;
      draw();
      frame = requestAnimationFrame(tick);
    };
    const seek = seconds => {
      if (!Number.isFinite(seconds)) throw new Error("Seek time must be finite.");
      time = Math.max(0, Math.min(duration, seconds));
      pause();
    };
    const replay = () => { seek(0); play(); };
    const setSpeed = value => {
      if (!Number.isFinite(value) || value <= 0) throw new Error("Playback speed must be positive.");
      speed = value;
      previous = null;
      if (speedSelect) speedSelect.value = String(speed);
      draw();
    };
    const setLanguage = value => {
      if (!languageKeys.includes(value)) throw new Error(`Unknown language: ${value}`);
      language = value;
      document.documentElement.lang = language;
      root.querySelectorAll("[data-copy]").forEach(element => {
        const key = element.dataset.copy;
        const text = languages[language][key] ?? defaults[key];
        if (text !== undefined) element.textContent = text;
      });
      if (languageSelect) languageSelect.value = language;
      if (control("replay")) control("replay").textContent = languages[language].replay || defaults.replay;
      draw();
    };
    if (timeline) { timeline.min = "0"; timeline.max = String(duration); timeline.step = "any"; }
    if (languageSelect) {
      languageSelect.replaceChildren(...languageKeys.map(key => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = languages[key].name || key;
        return option;
      }));
    }
    if (control("language-container")) control("language-container").hidden = languageKeys.length < 2;
    on(playButton, "click", () => playing ? pause() : play());
    on(control("replay"), "click", replay);
    on(timeline, "input", event => seek(Number(event.target.value)));
    on(speedSelect, "change", event => setSpeed(Number(event.target.value)));
    on(languageSelect, "change", event => setLanguage(event.target.value));
    on(document, "visibilitychange", () => { previous = null; });
    on(motionPreference, "change", event => { if (event.matches) pause(); });
    setLanguage(language);
    if (!motionPreference.matches) play();

    return {
      seek, play, pause, replay, setSpeed, setLanguage, getState: state,
      destroy: () => { pause(); destroyed = true; listeners.forEach(remove => remove()); }
    };
  };
})();
