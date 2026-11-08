/* Replace this example with the architecture's actual states and transitions. */
(() => {
  "use strict";
  const copy = {
    en: {
      name: "English", heading: "A request's path", intro: "One illustrated request passes through a processing stage.",
      context: "One request", timing: "Illustrative timing", source: "Source", processor: "Processor", result: "Result",
      sceneTitle: "Source, processor, and result",
      sceneDescription: "A request moves to the processor, waits while it runs, then produces a result.",
      statusLabel: "Status", stageLabel: "Stage", ready: "Ready", running: "Running", complete: "Complete",
      steps: [
        ["Ready to send", "The source has one request."],
        ["Request in transit", "The request moves from the source to the processor."],
        ["Processing", "The processor handles the request, then sends its result."],
        ["Result received", "This example is complete. The animation repeats."]
      ]
    }
  };
  const byId = id => document.getElementById(id);
  const interpolate = (from, to, progress) => from + (to - from) * Math.max(0, Math.min(1, progress));
  window.animationPlayer = window.createTechnicalAnimation({
    duration: 8,
    languages: copy,
    render: ({ time, language }) => {
      const text = copy[language];
      const phase = time < 1 ? 0 : time < 3 ? 1 : time < 7 ? 2 : 3;
      const x = time < 3 ? interpolate(180, 550, (time - 1) / 2) : time < 5 ? 550 : interpolate(550, 920, (time - 5) / 2);
      byId("request-token").setAttribute("transform", `translate(${x.toFixed(2)} 190)`);
      byId("processor-state").textContent = time < 3 ? text.ready : time < 5 ? text.running : text.complete;
      byId("status").textContent = time < 3 ? text.ready : time < 7 ? text.running : text.complete;
      byId("stage").textContent = `${phase + 1} / 4`;
      byId("step-title").textContent = text.steps[phase][0];
      byId("step-description").textContent = text.steps[phase][1];
    }
  });
})();
