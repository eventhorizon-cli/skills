#!/usr/bin/env python3
"""Capture a seekable SVG or HTML animation as a GIF when explicitly requested."""
import argparse
import asyncio
import io
import json
import math
import os
import sys
from pathlib import Path
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from PIL import Image
from playwright.async_api import async_playwright


async def prepare_page(browser, url, config, width, height, device_scale_factor, errors):
    page = await browser.new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=device_scale_factor,
        reduced_motion=config.get("reducedMotion", "reduce"),
    )
    page.on("pageerror", lambda error: errors.append(str(error)))
    await page.goto(url, wait_until="load", timeout=30000)
    await page.wait_for_function(config.get("ready", "true"), timeout=30000)
    await page.evaluate("document.fonts.ready.then(() => true)")
    if config.get("css"):
        await page.add_style_tag(content=config["css"])
    region = page.locator(config.get("selector", "body"))
    if await region.count() != 1:
        raise ValueError("Export selector must match exactly one element.")
    await region.wait_for(state="visible")
    return page, region


async def render(args):
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if config.get("reducedMotion", "reduce") not in ("reduce", "no-preference"):
        raise ValueError("reducedMotion must be reduce or no-preference.")
    if Path(args.output).suffix.lower() != ".gif":
        raise ValueError("GIF renderer output must use a .gif extension; author native SVG directly.")
    width, height = int(config.get("width", 1100)), int(config.get("height", 900))
    fps, duration = int(config.get("fps", 20)), float(config["duration"])
    scale = float(config.get("scale", 2))
    output_width = config.get("outputWidth")
    if "outputWidth" in config and (type(output_width) is not int or output_width <= 0):
        raise ValueError("outputWidth must be a positive integer.")
    if width <= 0 or height <= 0 or fps <= 0 or 100 % fps or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Positive dimensions/duration required; fps must divide 100.")
    if not math.isfinite(scale) or scale <= 0 or scale > 4:
        raise ValueError("Scale must be finite, greater than 0, and at most 4.")
    count = round(duration * fps)
    if count < 2 or not math.isclose(count / fps, duration):
        raise ValueError("Duration must contain at least two whole frame intervals.")
    source = args.source
    if urlsplit(source).scheme not in ("http", "https", "file"):
        source = Path(source).resolve(strict=True).as_uri()
    parts = urlsplit(source)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for item in args.query:
        key, separator, value = item.partition("=")
        if not separator:
            raise ValueError("--query must use key=value.")
        query[key] = value
    url = urlunsplit(parts._replace(query=urlencode(query)))
    frames, errors = [], []
    playwright = await async_playwright().start()
    browser = None
    try:
        browser = await playwright.chromium.launch(executable_path=args.browser, headless=True)
        try:
            effective_scale = scale
            if output_width is not None:
                probe_page, probe_region = await prepare_page(browser, url, config, width, height, 1, errors)
                try:
                    probe_box = await probe_region.bounding_box()
                    if probe_box is None or probe_box["width"] <= 0:
                        raise ValueError("Export selector has no measurable CSS width.")
                    effective_scale = output_width / probe_box["width"]
                finally:
                    await asyncio.wait_for(probe_page.close(), timeout=10)

            if not math.isfinite(effective_scale) or effective_scale <= 0 or effective_scale > 4:
                raise ValueError("Required pixel density must be greater than 0 and at most 4; increase the CSS layout width for this outputWidth.")
            page, region = await prepare_page(browser, url, config, width, height, effective_scale, errors)
            for check in config.get("checkpoints", []):
                await page.evaluate(config["seek"], check["time"])
                await page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => resolve(true)))")
                actual = await page.evaluate(check["evaluate"])
                if actual != check["equals"]:
                    raise ValueError(f"Checkpoint at {check['time']}s: expected {check['equals']!r}, got {actual!r}")
            for frame in range(count):
                await page.evaluate(config["seek"], frame / fps)
                # Flush the requested render without allowing wall-clock playback to decide time.
                await page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => resolve(true)))")
                # The source must remain paused; disabling animations here would fast-forward them.
                png = await region.screenshot(type="png", animations="allow", timeout=30000)
                with Image.open(io.BytesIO(png)) as image:
                    if frame == 0 and output_width is not None and image.width != output_width:
                        difference = abs(image.width - output_width)
                        if difference > 1:
                            raise ValueError(
                                f"Captured width {image.width}px differs from outputWidth {output_width}px by "
                                f"{difference}px; at most 1px of browser rounding is allowed."
                            )
                        print(
                            f"Browser rounded outputWidth {output_width}px to {image.width}px (1px difference).",
                            file=sys.stderr,
                            flush=True,
                        )
                    with image.convert("RGB") as rgb_image:
                        frames.append(
                            rgb_image.quantize(
                                colors=256,
                                method=Image.Quantize.MEDIANCUT,
                                dither=Image.Dither.NONE,
                            ).copy()
                        )
                if frames[-1].size != frames[0].size:
                    raise ValueError("Export region changed size during playback.")
                if errors:
                    raise RuntimeError("Page errors: " + "; ".join(errors))
                if frame % 50 == 0:
                    print(f"Captured {frame + 1}/{count} frames", flush=True)
            print(f"Captured all {count} frames; closing browser", flush=True)
        finally:
            try:
                await asyncio.wait_for(browser.close(), timeout=10)
            except asyncio.TimeoutError:
                print("Browser close timed out; stopping Playwright transport.", file=sys.stderr, flush=True)
    finally:
        await asyncio.wait_for(playwright.stop(), timeout=15)
    print("Encoding GIF", flush=True)
    output_size = frames[0].size
    destination = Path(args.output).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".animation-", suffix=".gif", dir=destination.parent)
    os.close(descriptor)
    try:
        frames[0].save(temporary, save_all=True, append_images=frames[1:], duration=1000 // fps, loop=0, disposal=1, optimize=True)
        with Image.open(temporary) as gif:
            if gif.info.get("loop") != 0 or gif.n_frames < 2 or gif.size != frames[0].size:
                raise ValueError("Invalid encoded GIF dimensions, loop, or frame count.")
            encoded_count, elapsed = gif.n_frames, 0
            for i in range(encoded_count):
                gif.seek(i)
                gif.load()
                elapsed += gif.info.get("duration", 0)
            if abs(elapsed - duration * 1000) > 1:
                raise ValueError(f"Unexpected encoded duration: {elapsed}ms")
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
        for frame in frames:
            frame.close()
    print(json.dumps({"output": str(destination), "width": output_size[0], "height": output_size[1],
                      "effective_scale": effective_scale,
                      "frames": encoded_count, "duration_seconds": elapsed / 1000, "loop": 0,
                      "bytes": destination.stat().st_size}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Local SVG/HTML path or URL")
    parser.add_argument("--config", required=True, help="JSON crop, seek, and checkpoint configuration")
    parser.add_argument("--output", required=True, help="Destination GIF")
    parser.add_argument("--query", action="append", default=[], help="URL query key=value; repeatable")
    parser.add_argument("--browser", help="Installed Chrome/Chromium executable; defaults to Playwright Chromium")
    args = parser.parse_args()
    asyncio.run(render(args))


if __name__ == "__main__":
    main()
