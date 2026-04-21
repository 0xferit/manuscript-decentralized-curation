# Color Models

**Source:** [Color & Contrast](https://colorandcontrast.com/) — A comprehensive guide to color for UI designers

This note summarizes the main distinctions relevant to UI and digital color work. It replaces incomplete text fragments with a short curated reference.

---

## Key distinctions

- **Color model:** A way to describe color using a set of channels or parameters.
- **Color space:** A specific mathematical implementation of a color model, with defined primaries, white point, and transfer characteristics.
- **Color appearance model:** A model that describes perceived color under viewing conditions; when constrained appropriately, it can be used to derive more uniform color spaces.

In short: a **model** is the conceptual system, while a **space** is a precise implementation of that system.

## Common examples

- **RGB:** An additive color model based on red, green, and blue primaries. This is the basis for most digital displays.
- **sRGB:** The most common RGB color space for web content and general-purpose displays.
- **Display-P3:** A wider-gamut RGB color space used on many modern displays.
- **CMYK:** A subtractive color model based on cyan, magenta, yellow, and black, commonly used in print workflows.
- **RYB:** A traditional subtractive model based on red, yellow, and blue; useful historically and pedagogically, but not the standard model for modern digital imaging.

## Practical guidance

- For **digital interfaces**, think primarily in **RGB-based color spaces** such as **sRGB** and **Display-P3**.
- For **print**, **CMYK** remains the common subtractive workflow.
- Do not treat a color model and a color space as interchangeable terms: the distinction matters when discussing gamut, consistency, and implementation.

## Further reading

- [Color & Contrast](https://colorandcontrast.com/)
- If you need the original explanations and diagrams, consult the source directly rather than relying on extracted bundle fragments.
