# Shared player

This player is for optional interactive HTML demonstrations. Native animated SVG is the default output and does not require this player or an HTML intermediate.

Copy `assets/technical-animation/` into the document's animation-source directory. It opens through `file://`; ordinary deferred scripts avoid a server requirement.

`player.js` owns playback controls. Replace the example in `scene.js` with scenario-specific states and geometry while keeping control behavior reusable.

```js
window.animationPlayer = window.createTechnicalAnimation({
  root: document,
  duration: 10,
  languages: { en: { name: "English", play: "Play", pause: "Pause" } },
  render: ({ time, duration, progress, speed, language, playing }) => {
    // Set the complete scene state from time and language.
  }
});
```

`languages` contains flat translation keys plus scene-specific data. Elements with `data-copy="key"` receive matching text. Common UI keys are `play`, `pause`, `replay`, `timeline`, `speed`, and `language`; English defaults are provided. `?lang=...` selects a supported initial language. The selector is hidden for a single-language scene. Translate accessible SVG titles/descriptions as well as visible labels.

| Method | Behavior |
| --- | --- |
| `seek(seconds)` | Pause and render the requested time, clamped to `[0, duration]`. |
| `play()` / `pause()` | Start or stop playback at the current time. Playing from the endpoint restarts at zero. |
| `replay()` | Return to zero and start playback. |
| `setSpeed(number)` | Set a finite positive playback multiplier. |
| `setLanguage(key)` | Translate and redraw the current state without restarting. |
| `getState()` | Return time, duration, progress, speed, language, and playback state. |
| `destroy()` | Stop playback and remove listeners. |

Optional controls use `data-control`: `play`, `replay`, `timeline`, `time`, `speed`, `language`, and `language-container`. Preserve labels, focus styling, and native keyboard behavior. Reduced-motion preferences start playback paused; users can explicitly start it.

The renderer hook is `t => window.animationPlayer.seek(t)`. Match export `duration` to the scene, and replace the starter checkpoints with checks for the actual scenario and its languages.
